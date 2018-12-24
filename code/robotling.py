# ----------------------------------------------------------------------------
# robotling.py
# Definition of the class `Robotling`, which subsumises all functions of the
# robotling board.
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-13, v1
# 2018-11-10, v1.1 - Compatible to Boris Lovosevic's MicroPython ESP32 port
# 2018-12-22, v1.2 - Class `Robotling` now more restricted to the board-
#                    related functions
#
# Open issues:
# - NeoPixels don't yet quite as expected with the LoBo ESP32 MicroPython
# - LSM303: While accelerometer readings are fine, computing a clear heading
#   from the magnetometer does yet work. Potentially a hardware problem with
#   the prototype board. In any case, the compass does not yet work.
#   With the CMPS12 module, the compass works just fine.
# ----------------------------------------------------------------------------
import array
from micropython import const
import robotling_board as rb
import driver.mcp3208 as mcp3208
import driver.drv8835 as drv8835
from misc.helpers import timed_function
from robotling_board_version import BOARD_VER

from platform.platform import platform
if platform.ID == platform.ENV_ESP32_UPY:
  import platform.huzzah32.board as board
  import platform.huzzah32.dio as dio
  import platform.huzzah32.aio as aio
  import platform.huzzah32.busio as busio
  from platform.huzzah32.neopixel import NeoPixel
  from time import ticks_us, ticks_diff
else:
  import board
  import platform.m4ex.dio as dio
  import platform.m4ex.aio as aio
  import platform.m4ex.busio as busio
  from platform.m4ex.neopixel import NeoPixel
  from platform.m4ex.utime import ticks_us, ticks_diff

__version__ = "0.1.2.0"

# ----------------------------------------------------------------------------
class Robotling():
  """Robotling main class.

  Objects:
  -------
  - onboardLED     : on(), off()
  - Compass        : see sensors.compass*.py

  Methods:
  -------
  - update()
    Update onboard devices (Neopixel, analog sensors, etc.). Call frequently
    to keep sensors updated and NeoPixel pulsing!
  - powerDown()
    Switch off NeoPixel, motor driver, etc.
  - startPulseNeoPixel()
    Set color of NeoPixel at RBL_NEOPIX and enable pulsing

  Properties:
  ----------
  - Battery_V      : battery voltage [V]
  - NeoPixelRGB    : get and set color (assign r,g,b tuple)
  - ID             : GUID of board/feather

  Internal objects:
  ----------------
  - _MCP3208       : 8-channel 12-bit A/C converter driver
  - _LSM303        : magnetometer/accelerometer driver (if available)
  - _motorDriver   : 2-channel DC motor driver

  Internal methods:
  ----------------
  - _pulseNeoPixel()
    Update pulsing, if enabled
  """

  HEARTBEAT_STEP_SIZE  = const(5)   # Step size for pulsing NeoPixel
  MIN_UPDATE_PERIOD_MS = const(20)  # Minimal time between update() calls

  def __init__(self, devices=[]):
    """ Additional onboard components can be listed in `devices` and, if known,
        will be initialized
    """
    print("Robotling v{0:.2f} running MicroPython {1} ({2})"
          .format(BOARD_VER/100, platform.sysInfo[2], platform.sysInfo[0]))
    print("Initializing ...")

    # Define a unique ID
    self._ID = platform.GUID

    # Initialize on-board (feather) hardware
    self.onboardLED = dio.DigitalOut(rb.RED_LED, value=False)
    self._adc_battery = aio.AnalogIn(rb.ADC_BAT)

    # Initialize analog sensor driver
    self._SPI = busio.SPIBus(rb.SPI_FRQ, rb.SCK, rb.MOSI, rb.MISO)
    self._MCP3208 = mcp3208.MCP3208(self._SPI, rb.CS_ADC)

    # Initialize motor driver
    self._motorDriver = drv8835.DRV8835(drv8835.MODE_PH_EN,
                                        rb.A_ENAB, rb.A_PHASE,
                                        rb.B_ENAB, rb.B_PHASE)

    # Initialize Neopixel (connector)
    self._NPx = NeoPixel(rb.NEOPIX, 1)
    self._NPx0_RGB = bytearray([0]*3)
    self._NPx0_curr = array.array("i", [0,0,0])
    self._NPx0_step = array.array("i", [0,0,0])
    self.NeoPixelRGB = 0
    print("NeoPixel ready.")

    # Get I2C bus
    self._I2C = busio.I2CBus(rb.I2C_FRQ, rb.SCL, rb.SDA)

    # Initialize further devices depending on the selected onboard components
    # (e.g. which type of magnetometer/accelerometer/gyro, etc.)
    if "lsm303" in devices:
      # Magnetometer and accelerometer break-out, import drivers and
      # initialize lsm303 and respective compass instance
      import driver.lsm303 as lsm303
      from sensors.compass import Compass
      self._LSM303 = lsm303.LSM303(self._I2C)
      self.Compass = Compass(self._LSM303)

    if "compass_cmps12" in devices:
      # Very nice compass module with tilt-compensation built in
      from sensors.compass_cmps12 import Compass
      self.Compass = Compass(self._I2C)

    # Done
    print("... done.")

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def update(self):
    """ Update onboard devices (Neopixel, analog sensors, etc.).
        Call frequently to keep sensors updated and NeoPixel pulsing!
    """
    self._MCP3208.update()
    self._pulseNeoPixel()

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
