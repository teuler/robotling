# ----------------------------------------------------------------------------
# robotling.py
# Definition of the class `Robotling`, which subsumises all functions of the
# robotling board.
#
# The MIT License (MIT)
# Copyright (c) 2018-2020 Thomas Euler
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
# 2020-08-21, v1.9, Refactoring for `robotling_lib`
# 2020-11-15, v1.9, Further refactoring (platform based on language not board)
# 2021-04-18, v1.9, Small bug fixes, works w/ MicroPython v1.14
# 2021-04-21, v1.9, Now uses `RobotlingBase`
# 2021-04-29, v1.9, Some refactoring
#
# Open issues:
# - NeoPixels don't yet quite as expected with the LoBo ESP32 MicroPython
# - LSM303: While accelerometer readings are fine, computing a clear heading
#   from the magnetometer does yet work. Potentially a hardware problem with
#   the prototype board. In any case, the compass does not yet work.
#   With the CMPS12 module, the compass works just fine.
# ----------------------------------------------------------------------------
import gc
import array
import robotling_lib.robotling_board as rb
import robotling_lib.driver.drv8835 as drv8835
from robotling_board_version import BOARD_VER
from robotling_lib.robotling_base import RobotlingBase

from robotling_lib.platform.platform import platform as pf
if pf.languageID == pf.LNG_MICROPYTHON:
  import robotling_lib.platform.esp32.board_huzzah32 as board
  from robotling_lib.platform.esp32.dio import DigitalOut
  from robotling_lib.platform.esp32.aio import AnalogIn
  from robotling_lib.platform.esp32.busio import  I2CBus
  from robotling_lib.platform.esp32.neopixel import NeoPixel
  from machine import deepsleep, lightsleep
  import time
elif pf.languageID == pf.LNG_CIRCUITPYTHON:
  import board
  from robotling_lib.platform.circuitpython.dio import DigitalOut
  from robotling_lib.platform.circuitpython.aio import AnalogIn
  from robotling_lib.platform.circuitpython.busio import I2CBus
  from robotling_lib.platform.circuitpython.neopixel import NeoPixel
  import robotling_lib.platform.circuitpython.time as time
else:
  print("ERROR: No matching hardware libraries in `platform`.")

__version__ = "0.1.9.4"

# ----------------------------------------------------------------------------
class Robotling(RobotlingBase):
  """Robotling main class.

  Objects:
  -------
  - power5V        : on(), off()
  - Compass        : see sensors.compass*.py

  Methods:
  -------
  - update()
    Update onboard devices (Neopixel, analog sensors, etc.). Call frequently
    to keep sensors updated and NeoPixel pulsing!
  - sleepLightly(), sleepDeeply()

  Properties:
  ----------
  - Battery_V      : battery voltage [V]
  - NeoPixelRGB    : get and set color (assign r,g,b tuple)
  - ID             : GUID of board/feather

  Internal objects:
  ----------------
  - _LSM303        : magnetometer/accelerometer driver (if available)
  - _LSM9DS0       : accelerometer/magnetometer/gyroscope driver (if available)
  - _VL6180X       : time-of-flight distance sensor driver (if available)
  - _AMG88XX       : GRID-Eye IR 8x8 thermal camera driver (if available)
  - _DS            : DotStar array feather (if available)
  - _motorDriver   : 2-channel DC motor driver
  """

  def __init__(self, devices=[]):
    """ Additional onboard components can be listed in `devices` and, if known,
        will be initialized
    """
    si = pf.sysInfo
    print("Robotling (board v{0:.2f}, software v{1}) w/{2} {3} ({4})"
          .format(BOARD_VER/100, __version__, pf.language, si[2], si[0]))
    print("Initializing ...")

    # Initialize base object
    super().__init__(neoPixel=True, MCP3208=True)
    print("[{0:>12}] {1:35}".format("GUID", self.ID))

    # Initialize on-board (feather) hardware
    self._adc_battery = AnalogIn(rb.ADC_BAT)
    if BOARD_VER >= 120:
      self.power5V = DigitalOut(rb.ENAB_5V, value=True)

    # Initialize motor driver
    self._motorDriver = drv8835.DRV8835(
        drv8835.MODE_PH_EN, rb.MOTOR_FRQ,
        rb.A_ENAB, rb.A_PHASE, rb.B_ENAB, rb.B_PHASE
      )

    # Get hardware I2C bus (#0)
    self._I2C = I2CBus(freq=rb.I2C_FRQ, scl=rb.SCL, sda=rb.SDA, scan=True)

    # Reset potential "device" objects
    gc.collect()
    self._devices = devices
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
      from robotling_lib.sensors import compass
      from robotling_lib.driver import lsm303
      self._LSM303 = lsm303.LSM303(self._I2C)
      self.Compass = compass.Compass(self._LSM303)

    if "lsm9ds0" in devices:
      # Magnetometer/accelerometer/gyroscope break-out, import drivers and
      # initialize lsm9ds0 and respective compass instance
      from robotling_lib.sensors import compass
      from robotling_lib.driver import lsm9ds0
      self._LSM9DS0 = lsm9ds0.LSM9DS0(self._I2C)
      self.Compass = compass.Compass(self._LSM9DS0)

    if "compass_cmps12" in devices:
      # Very nice compass module with tilt-compensation built in
      from robotling_lib.sensors import compass_cmps12
      self.Compass = compass_cmps12.Compass(self._I2C)

    if "vl6180x" in devices:
      # Time-of-flight distance sensor
      from robotling_lib.sensors.adafruit_tof_ranging import \
        AdafruitVL6180XRangingSensor
      self._VL6180X = AdafruitVL6180XRangingSensor(i2c=self._I2C)

    if "dotstar_feather" in devices:
      # DotStar array is mounted
      from robotling_lib.driver import dotstar
      self._DS = dotstar.DotStar(0,0, 6*12, auto_write=False, spi=self._SPI)
      self._iDS = 0
      self._DS[0] = 0
      self._DS.show()

    if "amg88xx" in devices:
      # IR 8x8 thermal camera (AMG88XX) is mounted
      from robotling_lib.driver import amg88xx
      from robotling_lib.sensors import camera_thermal
      self._AMG88XX = amg88xx.AMG88XX(self._I2C)
      self.Camera = camera_thermal.Camera(self._AMG88XX)

    if "wlan" in devices:
      # Connect to WLAN, if not already connected
      self.connectToWLAN()

    # Done
    print("... done.")

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def update(self):
    """ Update onboard devices (Neopixel, analog sensors, etc.) immediately.
        User has to take care that this function is called regularly to keep
        sensors updated and NeoPixel pulsing.
    """
    super().updateStart()
    if self._spin_callback:
      self._spin_callback()
    super().updateEnd()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def printReport(self):
    """ Prints a report on memory usage and performance
    """
    super().printReport()
    batt  = self.Battery_V
    print("Battery    : {0:.1f}V, ~{1:.0f}% charged"
          .format(batt, batt/4.2 *100))
    print("---")

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def sleepDeeply(self, dur_s=10, keep5V=False):
    """ Switch off 5V power supply, if requested, and send microcontroller to
        deep sleep. After the given time, the controller reboots.
        (Works currently only for ESP32 and for robotling boards >= v1.2)
    """
    if BOARD_VER >= 120 and pf.ID == pf.ENV_ESP32_UPY:
      self.power5V.value = keep5V
      deepsleep(dur_s *1000)

  def sleepLightly(self, dur_s=10, keep5V=False):
    """ Switch off 5V power supply, if requested, and send microcontroller to
        light sleep. After the given time, the code excecution continues.
        (Works currently only for ESP32 and for robotling boards >= v1.2)
    """
    if BOARD_VER >= 120 and pf.ID == pf.ENV_ESP32_UPY:
      self.power5V.value = keep5V
      lightsleep(dur_s *1000)
      self.power5V.on()

  def powerDown(self):
    """ Switch off NeoPixel, motor driver, etc.
    """
    self._motorDriver.setMotorSpeed()
    super().powerDown()

  @property
  def Battery_V(self):
    """ Battery voltage in [V]
    """
    return rb.battery_convert(self._adc_battery.value)

# ----------------------------------------------------------------------------
