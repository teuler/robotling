# ----------------------------------------------------------------------------
# robotling.py
# Definition of the class `Robotling`, which subsumises all functions of the
# robotling board.
#
# The MIT License (MIT)
# Copyright (c) 2018-19 Thomas Euler
# 2018-09-13, v1
# 2018-11-10, v1.1, Compatible to Boris Lovosevic's MicroPython ESP32 port
# 2018-12-22, v1.2, Class `Robotling` now more restricted to the board-
#                   related functions
# 2018-12-28, v1.3, Added `spin_ms()`, which needs to be called once per loop
#                   and instead of `sleep_ms()` to keep board updated. This
#                   solution is superior to the use of a timer, because a) it
#                   is deterministic (avoids randomly interrupting the program
#                   flow and, hence, inconsistencies) and b) makes the code
#                   compatible to CircuitPython, which does not (yet?) support
#                   timers.
# 2019-01-01, v1.4, vl6180x time-of-flight distance sensor support added
# 2019-01-20, v1.5, DotStar feather support added
# 2018-03-25, v1.6, deepsleep/lightsleep support for ESP32
# 2019-05-23        LSM9DS0 accelerometer/magnetometer/gyroscope support added
# 2019-07-13, v1.7, `hexbug_config.py` reorganised and cleaned up
# 2019-07-25,       Added `wlan` to the list of possible devices
# 2019-08-03, v1.8, AMG88XX (8x8 IR camera) driver added
#                   `I2C_FRQ` increased; from specs this should be compatible
#                   with all currently supported I2C devices
# 2019-12-21, v1.9, Micropython 1.12.0
#                   - hardware I2C bus option added
#                   - native code generation added (needs MicroPython >=1.12)
#                   Define PWM frequencies for servos and DC motors to account
#                   for the fact the the ESP32 port supports only a single
#                   frequency for all PWM pins (see `robotling_board.py`)
#
# Open issues:
# - NeoPixels don't yet quite as expected with the LoBo ESP32 MicroPython
# - LSM303: While accelerometer readings are fine, computing a clear heading
#   from the magnetometer does yet work. Potentially a hardware problem with
#   the prototype board. In any case, the compass does not yet work.
#   With the CMPS12 module, the compass works just fine.
# ----------------------------------------------------------------------------
import array
import random
from micropython import const
import robotling_board as rb
import driver.mcp3208 as mcp3208
import driver.drv8835 as drv8835
from misc.helpers import timed_function, TimeTracker
from robotling_board_version import BOARD_VER

from platform.platform import platform
if platform.ID == platform.ENV_ESP32_UPY:
  import platform.huzzah32.board as board
  import platform.huzzah32.dio as dio
  import platform.huzzah32.aio as aio
  import platform.huzzah32.busio as busio
  from platform.huzzah32.neopixel import NeoPixel
  from machine import deepsleep, lightsleep
  import time
else:
  import board
  import platform.m4ex.dio as dio
  import platform.m4ex.aio as aio
  import platform.m4ex.busio as busio
  from platform.m4ex.neopixel import NeoPixel
  import platform.m4ex.time as time

__version__ = "0.1.9.0"

# ----------------------------------------------------------------------------
class Robotling():
  """Robotling main class.

  Objects:
  -------
  - onboardLED     : on(), off()
  - power5V        : on(), off()
  - Compass        : see sensors.compass*.py

  Methods:
  -------
  - update()
    Update onboard devices (Neopixel, analog sensors, etc.). Call frequently
    to keep sensors updated and NeoPixel pulsing!
  - spin_ms(dur_ms=0, period_ms=-1, callback=None)
    Instead of using a timer that calls `update()` at a fixed frequency (e.g.
    at 20 Hz), one can regularly, calling `spin()` once per main loop and
    everywhere else instead of `time.sleep_ms()`. For details, see there.
  - powerDown()
    Switch off NeoPixel, motor driver, etc.
  - startPulseNeoPixel()
    Set color of NeoPixel at RBL_NEOPIX and enable pulsing
  - sleepLightly(), sleepDeeply()
  - connectToWLAN()

  Properties:
  ----------
  - Battery_V      : battery voltage [V]
  - NeoPixelRGB    : get and set color (assign r,g,b tuple)
  - ID             : GUID of board/feather

  Internal objects:
  ----------------
  - _MCP3208       : 8-channel 12-bit A/C converter driver
  - _LSM303        : magnetometer/accelerometer driver (if available)
  - _LSM9DS0       : accelerometer/magnetometer/gyroscope driver (if available)
  - _VL6180X       : time-of-flight distance sensor driver (if available)
  - _AMG88XX       : GRID-Eye IR 8x8 thermal camera driver (if available)
  - _DS            : DotStar array feather (if available)
  - _motorDriver   : 2-channel DC motor driver
  - _spinTracker   : Tracks performance of `spin_ms()` function

  Internal methods:
  ----------------
  - _pulseNeoPixel()
    Update pulsing, if enabled
  """

  HEARTBEAT_STEP_SIZE  = const(5)   # Step size for pulsing NeoPixel
  MIN_UPDATE_PERIOD_MS = const(20)  # Minimal time between update() calls
  APPROX_UPDATE_DUR_MS = const(8)   # Approx. duration of the update/callback

  def __init__(self, devices=[]):
    """ Additional onboard components can be listed in `devices` and, if known,
        will be initialized
    """
    print("Robotling (board v{0:.2f}, software v{1}) w/ MicroPython {2} ({3})"
          .format(BOARD_VER/100, __version__, platform.sysInfo[2],
                  platform.sysInfo[0]))
    print("Initializing ...")

    # Initialize some variables
    self._devices = devices
    self._ID = platform.GUID
    print("[{0:>12}] {1:35}".format("GUID", self.ID))

    # Initialize on-board (feather) hardware
    self.onboardLED = dio.DigitalOut(rb.RED_LED, value=False)
    self._adc_battery = aio.AnalogIn(rb.ADC_BAT)

    if BOARD_VER >= 120:
      self.power5V = dio.DigitalOut(rb.ENAB_5V, value=True)

    # Initialize analog sensor driver
    self._SPI = busio.SPIBus(rb.SPI_FRQ, rb.SCK, rb.MOSI, rb.MISO)
    self._MCP3208 = mcp3208.MCP3208(self._SPI, rb.CS_ADC)

    # Initialize motor driver
    self._motorDriver = drv8835.DRV8835(drv8835.MODE_PH_EN, rb.MOTOR_FRQ,
                                        rb.A_ENAB, rb.A_PHASE,
                                        rb.B_ENAB, rb.B_PHASE)

    # Initialize Neopixel (connector)
    self._NPx = NeoPixel(rb.NEOPIX, 1)
    self._NPx0_RGB = bytearray([0]*3)
    self._NPx0_curr = array.array("i", [0,0,0])
    self._NPx0_step = array.array("i", [0,0,0])
    self.NeoPixelRGB = 0
    print("[{0:>12}] {1:35}".format("Neopixel", "ready"))

    # Get hardware I2C bus (#0)
    self._I2C = busio.I2CBus(rb.I2C_FRQ, rb.SCL, rb.SDA, code=0)

    # Reset potential "device" objects
    self._VL6180X = None
    self._DS = None
    self._AMG88XX = None
    self.Compass = None
    self.Camera = None

    # Initialize further devices depending on the selected onboard components
    # (e.g. which type of magnetometer/accelerometer/gyro, etc.)
    if "lsm303" in devices:
      # Magnetometer and accelerometer break-out, import drivers and
      # initialize lsm303 and respective compass instance
      import driver.lsm303 as lsm303
      from sensors.compass import Compass
      self._LSM303 = lsm303.LSM303(self._I2C)
      self.Compass = Compass(self._LSM303)

    if "lsm9ds0" in devices:
      # Magnetometer/accelerometer/gyroscope break-out, import drivers and
      # initialize lsm9ds0 and respective compass instance
      import driver.lsm9ds0 as lsm9ds0
      from sensors.compass import Compass
      self._LSM9DS0 = lsm9ds0.LSM9DS0(self._I2C)
      self.Compass = Compass(self._LSM9DS0)

    if "compass_cmps12" in devices:
      # Very nice compass module with tilt-compensation built in
      from sensors.compass_cmps12 import Compass
      self.Compass = Compass(self._I2C)

    if "vl6180x" in devices:
      # Time-of-flight distance sensor
      from sensors.adafruit_tof_ranging import AdafruitVL6180XRangingSensor
      self._VL6180X = AdafruitVL6180XRangingSensor(i2c=self._I2C)

    if "dotstar_feather" in devices:
      # DotStar array is mounted
      from driver.dotstar import DotStar
      self._DS = DotStar(0,0, 6*12, auto_write=False, spi=self._SPI)
      self._iDS = 0
      self._DS[0] = 0
      self._DS.show()

    if "amg88xx" in devices:
      # IR 8x8 thermal camera (AMG88XX) is mounted
      import driver.amg88xx as amg88xx
      from sensors.camera_thermal import Camera
      self._AMG88XX = amg88xx.AMG88XX(self._I2C)
      self.Camera = Camera(self._AMG88XX)

    if "wlan" in devices:
      # Connect to WLAN, if not already connected
      self.connectToWLAN()

    # Initialize spin function-related variables
    self._spin_period_ms = 0
    self._spin_t_last_ms = 0
    self._spin_callback = None
    self._spinTracker = TimeTracker()

    # Done
    print("... done.")

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def update(self):
    """ Update onboard devices (Neopixel, analog sensors, etc.) immediately.
        User has to take care that this function is called regularly to keep
        sensors updated and NeoPixel pulsing.
    """
    self._spinTracker.reset()
    self._MCP3208.update()
    self._pulseNeoPixel()
    if self._spin_callback:
      self._spin_callback()
    self._spinTracker.update()

  def spin_ms(self, dur_ms=0, period_ms=-1, callback=None):
    """ If not using a Timer to call `update()` regularly, calling `spin()`
        once per main loop and everywhere else instead of `time.sleep_ms()`
        is an alternative to keep the robotling board updated.
        e.g. "spin(period_ms=50, callback=myfunction)"" is setting it up,
             "spin(100)"" (~sleep for 100 ms) or "spin()" keeps it running.
    """
    if self._spin_period_ms > 0:
      p_ms = self._spin_period_ms
      p_us = p_ms *1000
      d_us = dur_ms *1000

      if dur_ms > 0 and dur_ms < (p_ms -APPROX_UPDATE_DUR_MS):
        time.sleep_ms(int(dur_ms))

      elif dur_ms >= (p_ms -APPROX_UPDATE_DUR_MS):
        # Sleep for given time while updating the board regularily; start by
        # sleeping for the remainder of the time to the next update ...
        t_us  = time.ticks_us()
        dt_ms = time.ticks_diff(time.ticks_ms(), self._spin_t_last_ms)
        if dt_ms > 0 and dt_ms < p_ms:
          time.sleep_ms(dt_ms)

        # Update
        self.update()
        self._spin_t_last_ms = time.ticks_ms()

        # Check if sleep time is left ...
        d_us = d_us -int(time.ticks_diff(time.ticks_us(), t_us))
        if d_us <= 0:
          return

        # ... and if so, pass the remaining time by updating at regular
        # intervals
        while time.ticks_diff(time.ticks_us(), t_us) < (d_us -p_us):
          time.sleep_us(p_us)
          self.update()

        # Remember time of last update
        self._spin_t_last_ms = time.ticks_ms()

      else:
        # No sleep duration given, thus just check if time is up and if so,
        # call update and remember time
        d_ms = time.ticks_diff(time.ticks_ms(), self._spin_t_last_ms)
        if d_ms > self._spin_period_ms:
          self.update()
          self._spin_t_last_ms = time.ticks_ms()

    elif period_ms > 0:
      # Set up spin parameters and return
      self._spin_period_ms = period_ms
      self._spin_callback = callback
      self._spinTracker.reset(period_ms)
      self._spin_t_last_ms = time.ticks_ms()

    else:
      # Spin parameters not setup, therefore just sleep
      time.sleep_ms(dur_ms)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def connectToWLAN(self):
    """ Connect to WLAN if not already connected
    """
    if platform.ID == platform.ENV_ESP32_UPY:
      import network
      from NETWORK import my_ssid, my_wp2_pwd
      if not network.WLAN(network.STA_IF).isconnected():
        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
          print('Connecting to network...')
          sta_if.active(True)
          sta_if.connect(my_ssid, my_wp2_pwd)
          while not sta_if.isconnected():
            self.onboardLED.on()
            time.sleep(0.05)
            self.onboardLED.off()
            time.sleep(0.05)
          print("[{0:>12}] {1}".format("network", sta_if.ifconfig()))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def printReport(self):
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
    avg_ms = self._spinTracker.meanDuration_ms
    dur_ms = self._spinTracker.period_ms
    print("Performance: spin: {0:6.3f}ms @ {1:.1f}Hz ~{2:.0f}%"
          .format(avg_ms, 1000/dur_ms, avg_ms /dur_ms *100))
    print("---")

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def sleepDeeply(self, dur_s=10, keep5V=False):
    """ Switch off 5V power supply, if requested, and send microcontroller to
        deep sleep. After the given time, the controller reboots.
        (Works currently only for ESP32 and for robotling boards >= v1.2)
    """
    if BOARD_VER >= 120 and platform.ID == platform.ENV_ESP32_UPY:
      self.power5V.value = keep5V
      deepsleep(dur_s *1000)

  def sleepLightly(self, dur_s=10, keep5V=False):
    """ Switch off 5V power supply, if requested, and send microcontroller to
        light sleep. After the given time, the code excecution continues.
        (Works currently only for ESP32 and for robotling boards >= v1.2)
    """
    if BOARD_VER >= 120 and platform.ID == platform.ENV_ESP32_UPY:
      self.power5V.value = keep5V
      lightsleep(dur_s *1000)
      self.power5V.on()

  def powerDown(self):
    """ Switch off NeoPixel, motor driver, etc.
    """
    self._motorDriver.setMotorSpeed()
    self.NeoPixelRGB = 0

  @property
  def Battery_V(self):
    """ Battery voltage in [V]
    """
    return self._adc_battery.value *rb.BAT_N_PER_V

  @property
  def ID(self):
    return self._ID

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
      s[0] = int(rgb[0] /self.HEARTBEAT_STEP_SIZE)
      c[1] = rgb[1]
      s[1] = int(rgb[1] /self.HEARTBEAT_STEP_SIZE)
      c[2] = rgb[2]
      s[2] = int(rgb[2] /self.HEARTBEAT_STEP_SIZE)
      self._NPx0_RGB = rgb
      self._NPx.set(rgb, 0, True)
      self._NPx0_pulse = True
      self._NPx0_fact = 1.0

  def dimNeoPixel(self, factor=1.0):
    self._NPx0_fact = max(min(1, factor), 0)

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

        if self._NPx0_fact < 1.0:
          self._NPx0_curr[i] = int(self._NPx0_curr[i] *self._NPx0_fact)

      self._NPx.set(self._NPx0_curr, 0, True)

      if not self._DS == None:
        self._DS[random.randint(0, 71)] = self._NPx0_curr
        self._DS.show()

# ----------------------------------------------------------------------------
