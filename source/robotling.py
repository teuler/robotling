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
# - Compass        : see sensors.compass*.py

# Properties:
# - Battery_V      : battery voltage [V]
# - NeoPixelRGB    : get and set color (assign r,g,b tuple)
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-13, v1
# 2018-11-10, v1.1 compatible to Boris Lovosevic's MicroPython ESP32 port
#
# Open issues:
# - NeoPixels don't yet quite as expected with the LoBo ESP32 MicroPython
# - LSM303: While accelerometer readings are fine, computing a clear heading
#   from the magnetometer does yet work. Potentially a hardware problem with
#   the prototype board. In any case, the compass does not yet work.
#   With the CMPS12 module, the compass works just fine.
#
# ----------------------------------------------------------------------------
import array
from os import uname
from machine import Pin, Signal, ADC, Timer
from micropython import const
from utime import ticks_us, ticks_diff
import robotling_board as rboard
import driver.mcp3208 as mcp3208
import driver.drv8835 as drv8835
import driver.distribution as distr
from driver.helpers import timed_function

__version__ = "0.1.1.0"

NPX0_STEP_SIZE = const(5)
TM_MIN_PERIOD  = const(20)

# ----------------------------------------------------------------------------
class Robotling():
  """Robotling main class."""

  def __init__(self, devices=[]):
    """ Additional onboard components can be listed in "devices" and, if known,
        will be initialized
    """
    print("Robotling v{0:.2f} running MicroPython {1} ({2})"
          .format(distr.BOARD_VER/100, distr.uPyDistr.sysInfo[2],
                  distr.uPyDistr.sysInfo[0]))
    print("Initializing ...")

    # Initialize on-board (feather) hardware
    self._uPyLoBo = distr.uPyDistr.ID == distr.UPY_ESP32_LOBO
    self._p13 = Pin(rboard.RED_LED, Pin.OUT)
    self.onboardLED = Signal(self._p13)
    self._adc_battery = ADC(Pin(rboard.ADC_BAT))
    self._adc_battery.atten(ADC.ATTN_11DB)

    # Initialize analog sensor driver
    self._spi = distr.uPyDistr.getSPIBus(rboard.SPI_FRQ, rboard.SCK,
                                         rboard.MOSI, rboard.MISO)
    self._MCP3208 = mcp3208.MCP3208(self._spi, rboard.CS_ADC)

    # Initialize motor driver
    self._motorDriver = drv8835.DRV8835(drv8835.MODE_PH_EN,
                                        rboard.A_ENAB, rboard.A_PHASE,
                                        rboard.B_ENAB, rboard.B_PHASE)

    # Initialize Neopixel (connector)
    self._NPx = distr.NeoPixel(rboard.NEOPIX, 1)
    self._NPx0_RGB = bytearray([0]*3)
    self._NPx0_curr = array.array("i", [0,0,0])
    self._NPx0_step = array.array("i", [0,0,0])
    self.NeoPixelRGB = 0
    print("NeoPixel ready.")

    # Get I2C bus
    self._i2c = distr.uPyDistr.getI2CBus(rboard.I2C_FRQ, rboard.SCL, rboard.SDA)

    # Initialize further devices depending on the selected onboard components
    # (e.g. which type of magnetometer/accelerometer/gyro, etc.)
    if "lsm303" in devices:
      # Magnetometer and accelerometer break-out, import drivers and
      # initialize lsm303 and respective compass instance
      import driver.lsm303 as lsm303
      from sensors.compass import Compass
      self._LSM303 = lsm303.LSM303(self._i2c)
      self.Compass = Compass(self._LSM303)

    if "compass_cmps12" in devices:
      # Very nice compass module with tilt-compensation built in
      from sensors.compass_cmps12 import Compass
      self.Compass = Compass(self._i2c)

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

    # Update analog sensors
    if self._tmSensors:
      self._MCP3208.update()

    if self._callback:
      self._callback()

    # Update NeoPixel color
    if self._tmNeoPixel:
      self._pulseNeoPixel()

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
    t_ms = self._tm_t_sum /self._tm_t_count
    print("Performance: timer callback {0:6.3f}ms @ {1:.1f}Hz ~{2:.0f}%"
          .format(t_ms, 1000/self._tmPeriod_ms, t_ms /self._tmPeriod_ms *100))
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

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @property
  def NeoPixelRGB(self):
    return self._NPx_RGB

  @NeoPixelRGB.setter
  def NeoPixelRGB(self, value):
    """ Set color of NeoPixel at RBL_NEOPIX by assigning RGB values (and
        stop pulsing, if running)
    """
    try:
      rgb = bytearray([value[0], value[1], value[2]])
    except TypeError:
      rgb = bytearray([value]*3)
    self._NPx.set(rgb, 0, True)
    self._NPx0_pulse = False

  def startPulseNeoPixel(self, value):
    """ Set color of NeoPixel at RBL_NEOPIX and enable pulsing
    """
    try:
      rgb = bytearray([value[0], value[1], value[2]])
    except TypeError:
      rgb = bytearray([value]*3)

    if (rgb != self._NPx0_RGB) or not(self._NPx0_pulse):
      # New color and start pulsing
      c = self._NPx0_curr
      s = self._NPx0_step
      c[0] = rgb[0]
      s[0] = int(rgb[0] /NPX0_STEP_SIZE)
      c[1] = rgb[1]
      s[1] = int(rgb[1] /NPX0_STEP_SIZE)
      c[2] = rgb[2]
      s[2] = int(rgb[2] /NPX0_STEP_SIZE)
      self._NPx0_RGB = rgb
      self._NPx.set(rgb, 0, True)
      self._NPx0_pulse = True

  def _pulseNeoPixel(self):
    """ Update pulsing, if enabled
    """
    if self._NPx0_pulse:
      rgb = self._NPx0_RGB
      for i in range(3):
        self._NPx0_curr[i] += self._NPx0_step[i]
        if self._NPx0_curr[i] > (rgb[i] -self._NPx0_step[i]):
          self._NPx0_step[i] *= -1
        if self._NPx0_curr[i] < abs(self._NPx0_step[i]):
          self._NPx0_step[i] = abs(self._NPx0_step[i])
      self._NPx.set(self._NPx0_curr, 0, True)

# ----------------------------------------------------------------------------
