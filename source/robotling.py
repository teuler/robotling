# ----------------------------------------------------------------------------
# robotling.py
# Definition of the class "Robotling", which subsumises all functions of the
# robotling board.
#
# Objects:
# - onboardLED     : on(), off()
# - _MCP3208       : 8-channel 12-bit A/C converter driver
# - _LSM303        : magnetometer/accelerometer driver
# - _motorDriver   : 2-channel DC motor driver

# Properties:
# - Battery_V      : battery voltage [V]
# - NeoPixelRGB    : get and set color (assign r,g,b tuple)
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-13, v1
# ----------------------------------------------------------------------------
from os import uname
from machine import Pin, Signal, ADC, Timer
from neopixel import NeoPixel
from micropython import const
from utime import ticks_us, ticks_diff
import robotling_board as rboard
import driver.mcp3208 as mcp3208
import driver.drv8835 as drv8835
import driver.lsm303 as lsmM303
import driver.distribution as distr
from sensors.compass import Compass

# ----------------------------------------------------------------------------
NP_MAX_INTENS  = const(35)
NP_MIN_INTENS  = const(0)
NP_STEP_INTENS = const(5)

TM_MIN_PERIOD  = const(20)

# ----------------------------------------------------------------------------
class Robotling():
  """Robotling main class."""

  def __init__(self):
    print("Initializing robotling board ...")

    # Initialize on-board (feather) hardware
    self._p13 = Pin(rboard.RED_LED, Pin.OUT)
    self.onboardLED = Signal(self._p13)
    self._adc_battery = ADC(Pin(rboard.ADC_BAT))
    self._adc_battery.atten(ADC.ATTN_11DB)

    # Initialize analog sensor driver
    self._spi = distr.uPyDistr.getSPIBus(rboard.SPI_FRQ, rboard.SCK,
                                         rboard.MOSI, rboard.MISO)
    self._MCP3208 = mcp3208.MCP3208(self._spi, rboard.CS_ADC)

    # Initialize magnetometer and accelerometer driver
    self._i2c = distr.uPyDistr.getI2CBus(rboard.I2C_FRQ, rboard.SCL, rboard.SDA)
    self._LSM303 = lsmM303.LSM303(self._i2c)

    # Initialize motor driver
    self._motorDriver = drv8835.DRV8835(drv8835.MODE_PH_EN,
                                        rboard.A_ENAB, rboard.A_PHASE,
                                        rboard.B_ENAB, rboard.B_PHASE)
    # Initialize compass
    self.Compass = Compass(self._LSM303)

    # Initialize Neopixel
    self._NPx = NeoPixel(Pin(rboard.NEOPIX, Pin.OUT), 1, bpp=3)
    self._NPx_RGB = bytearray([0]*3)
    self._NPx_intens = NP_MIN_INTENS
    self._NPx_step = NP_STEP_INTENS
    self._NPx_mask = 0x02
    self.NeoPixelRGB = 0
    print("NeoPixel ready.")

    # Timer for heartbeat signal via NeoPixel, sensor update and user
    # callback
    self._tm = None
    self._tmPeriod_ms = 25
    self._tmNeoPixel  = True
    self._tmSensors   = True
    self._callback    = None

    # Performance related
    self._tm_t_sum    = 0
    self._tm_t_count  = 0
    self._lp_t        = ticks_us()
    self._lp_t_sum    = 0
    self._lp_t_count  = 0

    # Done
    print("... done.")

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def update(self, info=None):
    """ Update onboard devices (Neopixel, analog sensors, etc.)
    """
    t = ticks_us()

    # Update NeoPixel color
    if self._tmNeoPixel:
      self._NPx_intens += self._NPx_step
      if self._NPx_intens > (NP_MAX_INTENS -NP_STEP_INTENS):
        self._NPx_step = -NP_STEP_INTENS
      if self._NPx_intens < (NP_MIN_INTENS +NP_STEP_INTENS):
        self._NPx_step =  NP_STEP_INTENS
      r = self._NPx_intens if (self._NPx_mask & 0x01) else 0
      g = self._NPx_intens if (self._NPx_mask & 0x02) else 0
      b = self._NPx_intens if (self._NPx_mask & 0x04) else 0
      self.NeoPixelRGB = (r, g, b)

    # Update analog sensors
    if self._tmSensors:
      self._MCP3208.update()

    if self._callback:
      self._callback()

    self._tm_t_sum   += ticks_diff(ticks_us(), t) /1000
    self._tm_t_count += 1

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def loop_start(self):
    """ To measure the performance of the loops, call this function once at
        the beginning of the main loop
    """
    t = self._lp_t
    self._lp_t_sum   += ticks_diff(ticks_us(), t) /1000
    self._lp_t_count += 1
    t = ticks_us()

  def print_report(self):
    """ Prints a report on memory usage and performance
    """
    import gc
    gc.collect()
    used  = gc.mem_alloc()
    total = gc.mem_free() +used
    print("Memory     : {0:.0f}% of {1:.0f}kB heap RAM used."
          .format(used/total*100, total/1024))
    batt  = self.Battery_V
    print("Battery    : {0:.1f}V, ~{1:.0f}% charged"
          .format(batt, batt/4.2 *100))
    tm_ms = self._tm_t_sum /self._tm_t_count
    print("Performance: timer callback {0:6.3f}ms ({1:.0f}Hz)"
          .format(tm_ms, 1000/tm_ms))
    # Measuring loop timing does currently make not much sense because
    # of the way the obstacle detection works, that is waiting until the
    # head of the robot has turned ...
    #lp_ms = self._lp_t_sum /self._lp_t_count
    #print("Performance: timer callback {0:6.3f}ms ({1:.0f}Hz), "
    #      "loop {2:6.3f}ms ({3:.0f}Hz)"
    #      .format(tm_ms, 1000/tm_ms, lp_ms, 1000/lp_ms))
    print("---")

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def startTimer(self, period=25, neopixel=True, sensors=True, callback=None):
    if self._tm == None:
      self._tm = Timer(1)
      self._tmPeriod_ms = max(period, TM_MIN_PERIOD)
      self._tmNeoPixel  = neopixel
      self._tmSensors   = sensors
      self._callback    = callback
      self._tm.init(period=self._tmPeriod_ms, callback=self.update)

  def stopTimer(self):
    if not(self._tm == None):
      self._tm.deinit()
      self._tm = None
      self.NeoPixelRGB = 0

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def powerDown(self):
    """ Switch off NeoPixel, motor driver, etc.
    """
    self._motorDriver.setMotorSpeed()
    self.NeoPixelRGB = 0


  @property
  def Battery_V(self):
    """ Battery voltage in [V]
    """
    return self._adc_battery.read() *rboard.BAT_N_PER_V


  @property
  def NeoPixelRGB(self):
    return self._NPx_RGB

  @NeoPixelRGB.setter
  def NeoPixelRGB(self, value):
    """ Set color of NeoPixel at RBL_NEOPIX by assigning RGB values
    """
    rgb = self._NPx_RGB
    try:
      if len(value) == 3:
        rgb = value
        self._NPx[0] = rgb
    except TypeError:
      rgb = (value, value, value)
    self._NPx[0] = rgb
    self._NPx.write()

# ----------------------------------------------------------------------------
