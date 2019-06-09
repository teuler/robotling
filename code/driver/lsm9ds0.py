# ----------------------------------------------------------------------------
# lsm9ds0.py
# Class for LSM9DS0 accelerometer/magnetometer/gyroscope driver
#
# The MIT License (MIT)
# Copyright (c) 2019 Thomas Euler
# 2019-05-22, v1
#
# Based on the CircuitPython driver:
# https://github.com/adafruit/Adafruit_CircuitPython_LSM9DS0
#
# The MIT License (MIT)
#
# Copyright (c) 2017 Tony DiCola for Adafruit Industries
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
#
# **Hardware:**
# * FLORA `9-DOF Accelerometer/Gyroscope/Magnetometer - LSM9DS0
#   <https://www.adafruit.com/product/2020>`_ (Product ID: 2020)
# ----------------------------------------------------------------------------
import time
from micropython import const
from misc.helpers import timed_function

try:
  import struct
except ImportError:
  import ustruct as struct

__version__ = "0.1.0.0"
CHIP_NAME   = "lsm9ds0"
CHAN_COUNT  = const(1)

# pylint: disable=bad-whitespace
# Internal constants and register values:
_LSM9DS0_ADDRESS_ACCELMAG        = const(0x1D)  # 3B >> 1 = 7bit default
_LSM9DS0_ADDRESS_GYRO            = const(0x6B)  # D6 >> 1 = 7bit default
_LSM9DS0_XM_ID                   = const(0b01001001)
_LSM9DS0_G_ID                    = const(0b11010100)

_LSM9DS0_ACCEL_MG_LSB_2G         = 0.061
_LSM9DS0_ACCEL_MG_LSB_4G         = 0.122
_LSM9DS0_ACCEL_MG_LSB_6G         = 0.183
_LSM9DS0_ACCEL_MG_LSB_8G         = 0.244
_LSM9DS0_ACCEL_MG_LSB_16G        = 0.732 # Is this right? Was expecting 0.488
_LSM9DS0_MAG_MGAUSS_2GAUSS       = 0.08
_LSM9DS0_MAG_MGAUSS_4GAUSS       = 0.16
_LSM9DS0_MAG_MGAUSS_8GAUSS       = 0.32
_LSM9DS0_MAG_MGAUSS_12GAUSS      = 0.48
_LSM9DS0_GYRO_DPS_DIGIT_245DPS   = 0.00875
_LSM9DS0_GYRO_DPS_DIGIT_500DPS   = 0.01750
_LSM9DS0_GYRO_DPS_DIGIT_2000DPS  = 0.07000

_LSM9DS0_TEMP_LSB_DEGREE_CELSIUS = 8  # 1°C = 8, 25° = 200, etc.

_LSM9DS0_REGISTER_WHO_AM_I_G     = const(0x0F)
_LSM9DS0_REGISTER_CTRL_REG1_G    = const(0x20)
_LSM9DS0_REGISTER_CTRL_REG3_G    = const(0x22)
_LSM9DS0_REGISTER_CTRL_REG4_G    = const(0x23)
_LSM9DS0_REGISTER_OUT_X_L_G      = const(0x28)
_LSM9DS0_REGISTER_OUT_X_H_G      = const(0x29)
_LSM9DS0_REGISTER_OUT_Y_L_G      = const(0x2A)
_LSM9DS0_REGISTER_OUT_Y_H_G      = const(0x2B)
_LSM9DS0_REGISTER_OUT_Z_L_G      = const(0x2C)
_LSM9DS0_REGISTER_OUT_Z_H_G      = const(0x2D)
_LSM9DS0_REGISTER_TEMP_OUT_L_XM  = const(0x05)
_LSM9DS0_REGISTER_TEMP_OUT_H_XM  = const(0x06)
_LSM9DS0_REGISTER_STATUS_REG_M   = const(0x07)
_LSM9DS0_REGISTER_OUT_X_L_M      = const(0x08)
_LSM9DS0_REGISTER_OUT_X_H_M      = const(0x09)
_LSM9DS0_REGISTER_OUT_Y_L_M      = const(0x0A)
_LSM9DS0_REGISTER_OUT_Y_H_M      = const(0x0B)
_LSM9DS0_REGISTER_OUT_Z_L_M      = const(0x0C)
_LSM9DS0_REGISTER_OUT_Z_H_M      = const(0x0D)
_LSM9DS0_REGISTER_WHO_AM_I_XM    = const(0x0F)
_LSM9DS0_REGISTER_INT_CTRL_REG_M = const(0x12)
_LSM9DS0_REGISTER_INT_SRC_REG_M  = const(0x13)
_LSM9DS0_REGISTER_CTRL_REG1_XM   = const(0x20)
_LSM9DS0_REGISTER_CTRL_REG2_XM   = const(0x21)
_LSM9DS0_REGISTER_CTRL_REG5_XM   = const(0x24)
_LSM9DS0_REGISTER_CTRL_REG6_XM   = const(0x25)
_LSM9DS0_REGISTER_CTRL_REG7_XM   = const(0x26)
_LSM9DS0_REGISTER_OUT_X_L_A      = const(0x28)
_LSM9DS0_REGISTER_OUT_X_H_A      = const(0x29)
_LSM9DS0_REGISTER_OUT_Y_L_A      = const(0x2A)
_LSM9DS0_REGISTER_OUT_Y_H_A      = const(0x2B)
_LSM9DS0_REGISTER_OUT_Z_L_A      = const(0x2C)
_LSM9DS0_REGISTER_OUT_Z_H_A      = const(0x2D)

_GYROTYPE                        = True
_XMTYPE                          = False

# Conversion constants
_GRAVITY_STANDARD                = 9.80665     # Earth's gravity in m/s^2
_GAUSS_TO_NANOTESLA              = 100000.0    # Gauss to nano-Tesla multiplier

# User facing constants/module globals.
ACCELRANGE_2G                    = (0b000 << 3)
ACCELRANGE_4G                    = (0b001 << 3)
ACCELRANGE_6G                    = (0b010 << 3)
ACCELRANGE_8G                    = (0b011 << 3)
ACCELRANGE_16G                   = (0b100 << 3)
MAGGAIN_2GAUSS                   = (0b00 << 5)  # +/- 2 gauss
MAGGAIN_4GAUSS                   = (0b01 << 5)  # +/- 4 gauss
MAGGAIN_8GAUSS                   = (0b10 << 5)  # +/- 8 gauss
MAGGAIN_12GAUSS                  = (0b11 << 5)  # +/- 12 gauss
GYROSCALE_245DPS                 = (0b00 << 4)  # +/- 245 degrees per second rotation
GYROSCALE_500DPS                 = (0b01 << 4)  # +/- 500 degrees per second rotation
GYROSCALE_2000DPS                = (0b10 << 4)  # +/- 2000 degrees per second rotation
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
def _twos_comp(val, bits):
  """ Convert an unsigned integer in 2's compliment form of the specified bit
      length to its signed integer value and return it.
  """
  if val & (1 << (bits -1)) != 0:
    return val -(1 << bits)
  return val

# ----------------------------------------------------------------------------
class LSM9DS0:
  """Driver for the LSM9DS0 accelerometer/magnetometer/gyroscope."""

  def __init__(self, i2c):
    """ Requires already initialized I2C bus instance.
    """
    self._i2c = i2c
    self._isReady = False

    # Check ID registers.
    xmID = self._read_u8(_XMTYPE, _LSM9DS0_REGISTER_WHO_AM_I_XM)
    gID  = self._read_u8(_GYROTYPE, _LSM9DS0_REGISTER_WHO_AM_I_G)
    if xmID == _LSM9DS0_XM_ID and gID == _LSM9DS0_G_ID:
      # Enable the accelerometer continous
      self._write_u8(_XMTYPE, _LSM9DS0_REGISTER_CTRL_REG1_XM, 0x67)
      self._write_u8(_XMTYPE, _LSM9DS0_REGISTER_CTRL_REG5_XM, 0b11110000)

      # enable mag continuous
      self._write_u8(_XMTYPE, _LSM9DS0_REGISTER_CTRL_REG7_XM, 0b00000000)

      # enable gyro continuous
      self._write_u8(_GYROTYPE, _LSM9DS0_REGISTER_CTRL_REG1_G, 0x0F)

      # enable the temperature sensor (output rate same as the mag sensor)
      reg = self._read_u8(_XMTYPE, _LSM9DS0_REGISTER_CTRL_REG5_XM)
      self._write_u8(_XMTYPE, _LSM9DS0_REGISTER_CTRL_REG5_XM, reg | (1 << 7))

      # Set default ranges for the various sensors
      self._accel_mg_lsb = None
      self._mag_mgauss_lsb = None
      self._gyro_dps_digit = None
      self.accel_range = ACCELRANGE_2G
      self.mag_gain = MAGGAIN_8GAUSS #MAGGAIN_2GAUSS
      self.gyro_scale = GYROSCALE_245DPS
      self._isReady  = True

    print("[{0:>12}] {1:35} ({2}): {3}"
          .format(CHIP_NAME, "Magnetometer/accelerometer/gyro", __version__,
                  "ok" if self._isReady else "NOT FOUND"))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @property
  def accel_range(self):
    """ The accelerometer range.  Must be a value of:
          - ACCELRANGE_2G
          - ACCELRANGE_4G
          - ACCELRANGE_6G
          - ACCELRANGE_8G
          - ACCELRANGE_16G
    """
    reg = self._read_u8(_XMTYPE, _LSM9DS0_REGISTER_CTRL_REG2_XM)
    return (reg & 0b00111000) & 0xFF

  @accel_range.setter
  def accel_range(self, val):
    assert val in (ACCELRANGE_2G, ACCELRANGE_4G, ACCELRANGE_6G,
                   ACCELRANGE_8G, ACCELRANGE_16G)
    reg = self._read_u8(_XMTYPE, _LSM9DS0_REGISTER_CTRL_REG2_XM)
    reg = (reg & ~(0b00111000)) & 0xFF
    reg |= val
    self._write_u8(_XMTYPE, _LSM9DS0_REGISTER_CTRL_REG2_XM, reg)
    if val == ACCELRANGE_2G:
      self._accel_mg_lsb = _LSM9DS0_ACCEL_MG_LSB_2G
    elif val == ACCELRANGE_4G:
      self._accel_mg_lsb = _LSM9DS0_ACCEL_MG_LSB_4G
    elif val == ACCELRANGE_6G:
      self._accel_mg_lsb = _LSM9DS0_ACCEL_MG_LSB_6G
    elif val == ACCELRANGE_8G:
      self._accel_mg_lsb = _LSM9DS0_ACCEL_MG_LSB_8G
    elif val == ACCELRANGE_16G:
      self._accel_mg_lsb = _LSM9DS0_ACCEL_MG_LSB_16G

  @property
  def mag_gain(self):
    """ The magnetometer gain.  Must be a value of:
          - MAGGAIN_2GAUSS
          - MAGGAIN_4GAUSS
          - MAGGAIN_8GAUSS
          - MAGGAIN_12GAUSS
    """
    reg = self._read_u8(_XMTYPE, _LSM9DS0_REGISTER_CTRL_REG6_XM)
    return (reg & 0b01100000) & 0xFF

  @mag_gain.setter
  def mag_gain(self, val):
    assert val in (MAGGAIN_2GAUSS, MAGGAIN_4GAUSS, MAGGAIN_8GAUSS,
                   MAGGAIN_12GAUSS)
    reg = self._read_u8(_XMTYPE, _LSM9DS0_REGISTER_CTRL_REG6_XM)
    reg = (reg & ~(0b01100000)) & 0xFF
    reg |= val
    self._write_u8(_XMTYPE, _LSM9DS0_REGISTER_CTRL_REG6_XM, reg)
    if val == MAGGAIN_2GAUSS:
      self._mag_mgauss_lsb = _LSM9DS0_MAG_MGAUSS_2GAUSS
    elif val == MAGGAIN_4GAUSS:
      self._mag_mgauss_lsb = _LSM9DS0_MAG_MGAUSS_4GAUSS
    elif val == MAGGAIN_8GAUSS:
      self._mag_mgauss_lsb = _LSM9DS0_MAG_MGAUSS_8GAUSS
    elif val == MAGGAIN_12GAUSS:
      self._mag_mgauss_lsb = _LSM9DS0_MAG_MGAUSS_12GAUSS

  @property
  def gyro_scale(self):
    """ The gyroscope scale.  Must be a value of:
          - GYROSCALE_245DPS
          - GYROSCALE_500DPS
          - GYROSCALE_2000DPS
    """
    reg = self._read_u8(_GYROTYPE, _LSM9DS0_REGISTER_CTRL_REG4_G)
    return (reg & 0b00110000) & 0xFF

  @gyro_scale.setter
  def gyro_scale(self, val):
    assert val in (GYROSCALE_245DPS, GYROSCALE_500DPS, GYROSCALE_2000DPS)
    reg = self._read_u8(_GYROTYPE, _LSM9DS0_REGISTER_CTRL_REG4_G)
    reg = (reg & ~(0b00110000)) & 0xFF
    reg |= val
    self._write_u8(_GYROTYPE, _LSM9DS0_REGISTER_CTRL_REG4_G, reg)
    if val == GYROSCALE_245DPS:
      self._gyro_dps_digit = _LSM9DS0_GYRO_DPS_DIGIT_245DPS
    elif val == GYROSCALE_500DPS:
      self._gyro_dps_digit = _LSM9DS0_GYRO_DPS_DIGIT_500DPS
    elif val == GYROSCALE_2000DPS:
      self._gyro_dps_digit = _LSM9DS0_GYRO_DPS_DIGIT_2000DPS

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @property
  def raw_accelerometer(self):
    """ Read the raw accelerometer sensor values and return it as a 3-tuple
    of X, Y, Z axis values that are 16-bit unsigned values.
    """
    buf = bytearray(6)
    self._read_bytes(_XMTYPE, 0x80 | _LSM9DS0_REGISTER_OUT_X_L_A, buf)
    return struct.unpack_from('<hhh', buf[0:6])

  @property
  def accelerometer(self):
    """ The accelerometer X, Y, Z axis values as a 3-tuple of m/s^2 values.
    """
    raw = self.raw_accelerometer
    return [x *self._accel_mg_lsb /1000.0 *_GRAVITY_STANDARD for x in raw]

  @property
  def raw_magnetometer(self):
    """ Read the raw magnetometer sensor values and return it as a 3-tuple
        of X, Y, Z axis values that are 16-bit unsigned values.
    """
    buf = bytearray(6)
    self._read_bytes(_XMTYPE, 0x80 | _LSM9DS0_REGISTER_OUT_X_L_M, buf)
    return struct.unpack_from('<hhh', buf)

  @property
  def magnetometer(self):
    """ The magnetometer X, Y, Z axis values as a 3-tuple of gauss values.
    """
    raw = self.raw_magnetometer
    return [x *self._mag_mgauss_lsb /1000.0 for x in raw]

  @property
  def magnetometer_nT(self):
    """ The magnetometer X, Y, Z axis values as a 3-tuple of nanotesla values.
    """
    raw = self.raw_magnetometer
    return [x *self._mag_mgauss_lsb /1000.0 *_GAUSS_TO_NANOTESLA for x in raw]

  @property
  def raw_gyroscope(self):
    """ Read the raw gyroscope sensor values and return it as a 3-tuple of
        X, Y, Z axis values that are 16-bit unsigned values.
    """
    buf = bytearray(6)
    self._read_bytes(_GYROTYPE, 0x80 | _LSM9DS0_REGISTER_OUT_X_L_G, buf)
    return struct.unpack_from('<hhh', buf)

  @property
  def gyroscope(self):
    """ The gyroscope X, Y, Z axis values as a 3-tuple of °/s values.
    """
    raw = self.raw_gyroscope
    return [x *self._gyro_dps_digit for x in raw]

  def raw_temperature(self):
    """ Read the raw temperature sensor value and return it as a 16-bit
        unsigned value.
    """
    buf = bytearray(2)
    self._read_bytes(_XMTYPE, 0x80 | _LSM9DS0_REGISTER_TEMP_OUT_L_XM, buf)
    temp = ((buf[1] << 8) | buf[0]) >> 4
    return _twos_comp(temp, 12)

  @property
  def temperature(self):
    """ The temperature of the sensor in degrees Celsius.
        (This is just a guess since the starting point (21C here) isn't
         documented)
    """
    return 21.0 +self.raw_temperature()/8

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
  def _read_u8(self, sensor_type, regAddr):
    """ Read an 8-bit unsigned value from the specified 8-bit address.
        The sensor_type boolean should be _MAGTYPE when talking to the
        magnetometer, or _XGTYPE when talking to the accel or gyro.
    """
    buf = bytearray(1)
    self._read_bytes(sensor_type, regAddr, buf)
    return buf[0]

  def _read_bytes(self, sensor_type, regAddr, buf):
    """ Read a count number of bytes into buffer from the provided 8-bit
        register address. The sensor_type boolean should be _MAGTYPE when
        talking to the magnetometer, or _XGTYPE when talking to the accel or
        gyro.
    """
    if sensor_type == _GYROTYPE:
      i2cAddr = _LSM9DS0_ADDRESS_GYRO
    else:
      i2cAddr = _LSM9DS0_ADDRESS_ACCELMAG
    cmd    = bytearray(1)
    cmd[0] = regAddr & 0xff
    self._i2c.writeto(i2cAddr, cmd, False)
    self._i2c.readfrom_into(i2cAddr, buf)

  def _write_u8(self, sensor_type, regAddr, val):
    """ Write an 8-bit unsigned value to the specified 8-bit address.
        The sensor_type boolean should be _MAGTYPE when talking to the
        magnetometer, or _XGTYPE when talking to the accel or gyro.
    """
    if sensor_type == _GYROTYPE:
      i2cAddr = _LSM9DS0_ADDRESS_GYRO
    else:
      i2cAddr = _LSM9DS0_ADDRESS_ACCELMAG
    buf    = bytearray(2)
    buf[0] = regAddr & 0xff
    buf[1] = val & 0xff
    self._i2c.writeto(i2cAddr, buf)

# ----------------------------------------------------------------------------
