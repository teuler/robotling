# ----------------------------------------------------------------------------
# lsm303.py
# Class for LSM303 accelerometer/magnetometer driver
#
# The MIT License (MIT)
# Copyright (c) 2018-19 Thomas Euler
# 2018-09-13, v1
# 2018-10-26, bug fix sequence of magnetometer values from I2C call is x,z,y
#
# Based on the CircuitPython driver:
# https://github.com/adafruit/Adafruit_CircuitPython_LSM303
#
# The MIT License (MIT)
# Copyright (c) 2017 Dave Astels for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# ----------------------------------------------------------------------------
import time
from micropython import const
from misc.helpers import timed_function

try:
  import struct
except ImportError:
  import ustruct as struct

__version__ = "0.1.0.0"
CHIP_NAME   = "lsm303"
CHAN_COUNT  = const(1)

# pylint: disable=bad-whitespace
_ADDRESS_ACCEL             = const(0x19)  # (0x32 >> 1)       // 0011001x
_ADDRESS_MAG               = const(0x1E)  # (0x3C >> 1)       // 0011110x
_ID                        = const(0xD4)  # (0b11010100)

# Accelerometer registers
_REG_ACCEL_CTRL_REG1_A     = const(0x20)
_REG_ACCEL_CTRL_REG2_A     = const(0x21)
_REG_ACCEL_CTRL_REG3_A     = const(0x22)
_REG_ACCEL_CTRL_REG4_A     = const(0x23)
_REG_ACCEL_CTRL_REG5_A     = const(0x24)
_REG_ACCEL_CTRL_REG6_A     = const(0x25)
_REG_ACCEL_REFERENCE_A     = const(0x26)
_REG_ACCEL_STATUS_REG_A    = const(0x27)
_REG_ACCEL_OUT_X_L_A       = const(0x28)
_REG_ACCEL_OUT_X_H_A       = const(0x29)
_REG_ACCEL_OUT_Y_L_A       = const(0x2A)
_REG_ACCEL_OUT_Y_H_A       = const(0x2B)
_REG_ACCEL_OUT_Z_L_A       = const(0x2C)
_REG_ACCEL_OUT_Z_H_A       = const(0x2D)
_REG_ACCEL_FIFO_CTRL_REG_A = const(0x2E)
_REG_ACCEL_FIFO_SRC_REG_A  = const(0x2F)
_REG_ACCEL_INT1_CFG_A      = const(0x30)
_REG_ACCEL_INT1_SOURCE_A   = const(0x31)
_REG_ACCEL_INT1_THS_A      = const(0x32)
_REG_ACCEL_INT1_DURATION_A = const(0x33)
_REG_ACCEL_INT2_CFG_A      = const(0x34)
_REG_ACCEL_INT2_SOURCE_A   = const(0x35)
_REG_ACCEL_INT2_THS_A      = const(0x36)
_REG_ACCEL_INT2_DURATION_A = const(0x37)
_REG_ACCEL_CLICK_CFG_A     = const(0x38)
_REG_ACCEL_CLICK_SRC_A     = const(0x39)
_REG_ACCEL_CLICK_THS_A     = const(0x3A)
_REG_ACCEL_TIME_LIMIT_A    = const(0x3B)
_REG_ACCEL_TIME_LATENCY_A  = const(0x3C)
_REG_ACCEL_TIME_WINDOW_A   = const(0x3D)

# Magnetometer registers
_REG_MAG_CRA_REG_M         = const(0x00)
_REG_MAG_CRB_REG_M         = const(0x01)
_REG_MAG_MR_REG_M          = const(0x02)
_REG_MAG_OUT_X_H_M         = const(0x03)
_REG_MAG_OUT_X_L_M         = const(0x04)
_REG_MAG_OUT_Z_H_M         = const(0x05)
_REG_MAG_OUT_Z_L_M         = const(0x06)
_REG_MAG_OUT_Y_H_M         = const(0x07)
_REG_MAG_OUT_Y_L_M         = const(0x08)
_REG_MAG_SR_REG_Mg         = const(0x09)
_REG_MAG_IRA_REG_M         = const(0x0A)
_REG_MAG_IRB_REG_M         = const(0x0B)
_REG_MAG_IRC_REG_M         = const(0x0C)
_REG_MAG_TEMP_OUT_H_M      = const(0x31)
_REG_MAG_TEMP_OUT_L_M      = const(0x32)

# Magnetometer gains
MAGGAIN_1_3                = const(0x20)  # +/- 1.3
MAGGAIN_1_9                = const(0x40)  # +/- 1.9
MAGGAIN_2_5                = const(0x60)  # +/- 2.5
MAGGAIN_4_0                = const(0x80)  # +/- 4.0
MAGGAIN_4_7                = const(0xA0)  # +/- 4.7
MAGGAIN_5_6                = const(0xC0)  # +/- 5.6
MAGGAIN_8_1                = const(0xE0)  # +/- 8.1

# Magentometer rates
MAGRATE_0_7                = const(0x00)  # 0.75 Hz
MAGRATE_1_5                = const(0x01)  # 1.5 Hz
MAGRATE_3_0                = const(0x62)  # 3.0 Hz
MAGRATE_7_5                = const(0x03)  # 7.5 Hz
MAGRATE_15                 = const(0x04)  # 15 Hz
MAGRATE_30                 = const(0x05)  # 30 Hz
MAGRATE_75                 = const(0x06)  # 75 Hz
MAGRATE_220                = const(0x07)  # 200 Hz

# Conversion constants
_LSM303ACCEL_MG_LSB        = 16704.0
_GRAVITY_STANDARD          = 9.80665      # Earth's gravity in m/s^2
_GAUSS_TO_MICROTESLA       = 100.0        # Gauss to micro-Tesla multiplier
_GAUSS_TO_NANOTESLA        = 100000.0     # Gauss to nano-Tesla multiplier

# ----------------------------------------------------------------------------
class LSM303(object):
  """Driver for LSM303 magnetometer/accelerometer."""

  def __init__(self, i2c):
    """ Requires already initialized I2C bus instance.
    """
    self._i2c = i2c
    self._isReady = False

    addrList = self._i2c.deviceAddrList
    if (_ADDRESS_ACCEL in addrList) and (_ADDRESS_MAG in addrList):
      # Enable  accelerometer and magnetometer
      self._write_u8(_ADDRESS_ACCEL, _REG_ACCEL_CTRL_REG1_A, 0x27)
      self._write_u8(_ADDRESS_MAG, _REG_MAG_MR_REG_M, 0x00)

      # Some initial parameters
      self._lsm303mag_gauss_lsb_xy = 1100.0
      self._lsm303mag_gauss_lsb_z = 980.0
      self._mag_gain = MAGGAIN_1_3
      self._mag_rate = MAGRATE_0_7
      self._isReady  = True

    print("[{0:>12}] {1:35} ({2}): {3}"
          .format(CHIP_NAME, "Magnetometer/accelerometer", __version__,
                  "ok" if self._isReady else "NOT FOUND"))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  #@timed_function
  @property
  def raw_accelerometer(self):
    """ The raw accelerometer sensor values.
        A 3-tuple of X, Y, Z axis values that are 16-bit signed integers.
    """
    buf = bytearray(6)
    self._read_bytes(_ADDRESS_ACCEL, _REG_ACCEL_OUT_X_L_A | 0x80, buf)
    return struct.unpack_from('<hhh', buf[0:6])

  @property
  def accelerometer(self):
    """ The processed accelerometer sensor values.
        A 3-tuple of X, Y, Z axis values in meters per second squared that are
        signed floats.
    """
    raw_accel_data = self.raw_accelerometer
    return [n /_LSM303ACCEL_MG_LSB *_GRAVITY_STANDARD for n in raw_accel_data]

  @property
  def raw_magnetometer(self):
    """ The raw magnetometer sensor values.
        A 3-tuple of X, Y, Z axis values that are 16-bit signed integers.
    """
    buf = bytearray(6)
    self._read_bytes(_ADDRESS_MAG, _REG_MAG_OUT_X_H_M, buf)
    x, z, y = struct.unpack_from('>hhh', buf[0:6])
    return (x, y, z)

  @property
  def magnetometer(self):
    """ The processed magnetometer sensor values.
        A 3-tuple of X, Y, Z axis values in microteslas that are signed
        floats.
    """
    mag_x, mag_y, mag_z = self.raw_magnetometer
    return (mag_x /self._lsm303mag_gauss_lsb_xy *_GAUSS_TO_MICROTESLA,
            mag_y /self._lsm303mag_gauss_lsb_xy *_GAUSS_TO_MICROTESLA,
            mag_z /self._lsm303mag_gauss_lsb_z  *_GAUSS_TO_MICROTESLA)

  @property
  def magnetometer_nT(self):
    """ The processed magnetometer sensor values.
        A 3-tuple of X, Y, Z axis values in nanotesla that are signed
        floats.
    """
    mag_x, mag_y, mag_z = self.raw_magnetometer
    return (mag_x /self._lsm303mag_gauss_lsb_xy *_GAUSS_TO_NANOTESLA,
            mag_y /self._lsm303mag_gauss_lsb_xy *_GAUSS_TO_NANOTESLA,
            mag_z /self._lsm303mag_gauss_lsb_z  *_GAUSS_TO_NANOTESLA)

  @property
  def mag_gain(self):
    """ The magnetometer's gain.
    """
    return self._mag_gain

  @mag_gain.setter
  def mag_gain(self, value):
    assert value in (MAGGAIN_1_3, MAGGAIN_1_9, MAGGAIN_2_5, MAGGAIN_4_0,
                     MAGGAIN_4_7, MAGGAIN_5_6, MAGGAIN_8_1)
    self._mag_gain = value
    self._write_u8(_ADDRESS_MAG, _REG_MAG_CRB_REG_M, value)
    if self._mag_gain == MAGGAIN_1_3:
      self._lsm303mag_gauss_lsb_xy = 1100.0
      self._lsm303mag_gauss_lsb_z  = 980.0
    elif self._mag_gain == MAGGAIN_1_9:
      self._lsm303mag_gauss_lsb_xy = 855.0
      self._lsm303mag_gauss_lsb_z  = 760.0
    elif self._mag_gain == MAGGAIN_2_5:
      self._lsm303mag_gauss_lsb_xy = 670.0
      self._lsm303mag_gauss_lsb_z  = 600.0
    elif self._mag_gain == MAGGAIN_4_0:
      self._lsm303mag_gauss_lsb_xy = 450.0
      self._lsm303mag_gauss_lsb_z  = 400.0
    elif self._mag_gain == MAGGAIN_4_7:
      self._lsm303mag_gauss_lsb_xy = 400.0
      self._lsm303mag_gauss_lsb_z  = 355.0
    elif self._mag_gain == MAGGAIN_5_6:
      self._lsm303mag_gauss_lsb_xy = 330.0
      self._lsm303mag_gauss_lsb_z  = 295.0
    elif self._mag_gain == MAGGAIN_8_1:
      self._lsm303mag_gauss_lsb_xy = 230.0
      self._lsm303mag_gauss_lsb_z  = 205.0

  @property
  def mag_rate(self):
    """ The magnetometer update rate.
    """
    return self._mag_rate

  @mag_rate.setter
  def mag_rate(self, value):
    assert value in (MAGRATE_0_7, MAGRATE_1_5, MAGRATE_3_0, MAGRATE_7_5,
                     MAGRATE_15, MAGRATE_30, MAGRATE_75, MAGRATE_220)
    self._mag_rate = value
    reg_m = ((value & 0x07) << 2) & 0xff
    self._write_u8(_ADDRESS_MAG, _REG_MAG_CRA_REG_M, reg_m)

  @property
  def isReady(self):
    return self._isReady

  @property
  def channelCount(self):
    return CHAN_COUNT

  @property
  def name(self):
    return CHIP_NAME

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def _write_u8(self, i2cAddr, regAddr, val):
    buf    = bytearray(2)
    buf[0] = regAddr & 0xff
    buf[1] = val & 0xff
    self._i2c.writeto(i2cAddr, buf)

  def _read_bytes(self, i2cAddr, regAddr, buf):
    cmd    = bytearray(1)
    cmd[0] = regAddr & 0xff
    self._i2c.writeto(i2cAddr, cmd, False)
    self._i2c.readfrom_into(i2cAddr, buf)

# ----------------------------------------------------------------------------
