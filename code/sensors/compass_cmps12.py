# ----------------------------------------------------------------------------
# compass_cmps12.py
# Compass based on CMPS12 tilt-compensated compass driver
# For details, see http://www.robot-electronics.co.uk/files/cmps12.pdf
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-10-30, v1
# ----------------------------------------------------------------------------
try:
  import struct
except ImportError:
  import ustruct as struct
from math import radians
from micropython import const
from misc.helpers import timed_function
from sensors.sensor_base import SensorBase
import robotling_board as rb

__version__ = "0.1.0.0"

# pylint: disable=bad-whitespace
_ADDRESS_CMPS12            = const(0x60)  # (0xD0 >> 1)

# Compass registers
_REG_CMD                   = const(0x00)
_REG_BEARING_8BIT          = const(0x01) # 0-255 for a full circle
_REG_BEARING_16BIT_HB      = const(0x02) # 0-3599, w/next
_REG_BEARING_16BIT_LB      = const(0x03)
_REG_PITCH_8BIT_ANGLE      = const(0x04) # signed byte, +/- 90°
_REG_ROLL_8BIT_ANGLE       = const(0x05) # signed byte, +/- 90°
_REG_MAG_X_RAW_HB          = const(0x06) # 16 bit signed int, w/next
_REG_MAG_X_RAW_LB          = const(0x07)
_REG_MAG_Y_RAW_HB          = const(0x08) # 16 bit signed int, w/next
_REG_MAG_Y_RAW_LB          = const(0x09)
_REG_MAG_Z_RAW_HB          = const(0x0A) # 16 bit signed int, w/next
_REG_MAG_Z_RAW_LB          = const(0x0B)
_REG_ACCEL_X_RAW_HB        = const(0x0C) # 16 bit signed int, w/next
_REG_ACCEL_X_RAW_LB        = const(0x0D)
_REG_ACCEL_Y_RAW_HB        = const(0x0E) # 16 bit signed int, w/next
_REG_ACCEL_Y_RAW_LB        = const(0x0F)
_REG_ACCEL_Z_RAW_HB        = const(0x10) # 16 bit signed int, w/next
_REG_ACCEL_Z_RAW_LB        = const(0x11)
_REG_GYRO_X_RAW_HB         = const(0x12) # 16 bit signed int, w/next
_REG_GYRO_X_RAW_LB         = const(0x13)
_REG_GYRO_Y_RAW_HB         = const(0x14) # 16 bit signed int, w/next
_REG_GYRO_Y_RAW_LB         = const(0x15)
_REG_GYRO_Z_RAW_HB         = const(0x16) # 16 bit signed int, w/next
_REG_GYRO_Z_RAW_LB         = const(0x17)
_REG_TEMP_DEG_HB           = const(0x18) # in degrees°, w/next
_REG_TEMP_DEG_LB           = const(0x19)
_REG_BEARING_16BIT_BNO_HB  = const(0x1A) # 0-5759, /16=°, w/next
_REG_BEARING_16BIT_BNO_LB  = const(0x1B)
_REG_PITCH_16BIT_ANGLE_HB  = const(0x1C) # 16bit signed int, +/- 180°, w/next
_REG_PITCH_16BIT_ANGLE_LB  = const(0x1D)
_REG_CALIB_STATE           = const(0x1E) # Calibration state, 0=not, 3=fully

# ----------------------------------------------------------------------------
class Compass(SensorBase):
  """Compass class that uses the tilt-compensated CMPS12 breakout."""

  def __init__(self, i2c):
    """ Requires already initialized I2C bus instance.
    """
    self._i2c = i2c
    self._isReady = False
    super().__init__(None, 0)

    addrList = self._i2c.deviceAddrList
    if (_ADDRESS_CMPS12 in addrList) and (_ADDRESS_CMPS12 in addrList):
      # Get version and initialize
      buf = bytearray(1)
      self._read_bytes(_ADDRESS_CMPS12, _REG_CMD, buf)
      self._version = buf[0]
      self._heading = 0.0
      self._pitch   = 0.0
      self._roll    = 0.0
      self._type    = "compass (CMPS12 v{0})".format(self._version)
      self._isReady = True

    print("{0} {1}.".format(self._type,
                           "is ready" if self._isReady else "not found"))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  #@timed_function
  def getHeading(self, tilt=False, calib=False, hires=True):
    """ Returns heading with or w/o tilt compensation and/or calibration,
        if available.
        NOTE: The CMPS12 has built-in tilt compensation and is pre-calibra-
        ted, therefore the parameters "tilt" and "calib" are only for
        compatibility reasons and have no effect. With "hires"=True, the
        precision is 3599/360°, otherwise 255/360°.
    """
    if not self._isReady:
      return rb.RBL_ERR_DEVICE_NOT_READY
    hd = self._heading
    if hires:
      buf = bytearray(1)
      self._read_bytes(_ADDRESS_CMPS12, _REG_BEARING_8BIT, buf)
      hd  = buf[0]/255 *360
    else:
      buf = bytearray(2)
      self._read_bytes(_ADDRESS_CMPS12, _REG_BEARING_16BIT_HB, buf)
      hd  = ((buf[0] << 8) | buf[1]) /10
    return hd


  #@timed_function
  def getHeading3D(self, calib=False):
    """ Returns heading, pitch and roll in [°] with or w/o calibration,
        if available.
        NOTE: The CMPS12 has built-in tilt compensation and is pre-calibra-
        ted, therefore the parameter "calib" exists only for compatibility
        reasons and has no effect.
    """
    if not self._isReady:
      return (rb.RBL_ERR_DEVICE_NOT_READY, 0, 0, 0)
    hd  = self._heading
    pit = self._pitch
    rol = self._roll
    buf = bytearray(4)
    self._read_bytes(_ADDRESS_CMPS12, _REG_BEARING_16BIT_HB, buf)
    hd, pit, rol = struct.unpack_from('>Hbb', buf[0:4])
    hd /= 10
    return (rb.RBL_OK, hd, pit, rol)


  #@timed_function
  def getPitchRoll(self, radians=False):
    """ Returns error code, pitch and roll in [°] as a tuple
    """
    if not self._isReady:
      return  (rb.RBL_ERR_DEVICE_NOT_READY, 0, 0)
    pit = self._pitch
    rol = self._roll
    buf = bytearray(2)
    self._read_bytes(_ADDRESS_CMPS12, _REG_PITCH_8BIT_ANGLE, buf)
    pit, rol = struct.unpack_from('>bb', buf[0:2])
    if radians:
      return (rb.RBL_OK, radians(pit), radians(rol))
    else:
      return (rb.RBL_OK, pit, rol)


  @property
  def isReady(self):
    return self._isReady

  @property
  def channelCount(self):
    return CHAN_COUNT

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def _read_bytes(self, i2cAddr, regAddr, buf):
    cmd    = bytearray(1)
    cmd[0] = regAddr & 0xff
    self._i2c.writeto(i2cAddr, cmd, False)
    self._i2c.readfrom_into(i2cAddr, buf)

# ----------------------------------------------------------------------------
