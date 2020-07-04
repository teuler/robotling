# ----------------------------------------------------------------------------
# amg88xx.py
# Class for AMG88XX GRID-Eye IR 8x8 thermal camera driver
#
# The MIT License (MIT)
# Copyright (c) 2019 Thomas Euler
# 2019-07-30, v1
#
# Based on the CircuitPython driver:
# https://github.com/adafruit/Adafruit_CircuitPython_AMG88xx
#
# The MIT License (MIT)
#
# Copyright (c) 2017 Dean Miller for Adafruit Industries.
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
from misc.helpers import timed_function
from micropython import const
import errno

from platform.platform import platform
if platform.ID == platform.ENV_ESP32_UPY:
  from platform.esp32.register import i2c_bit, i2c_bits
elif platform.ID == platform.ENV_CPY_SAM51:
  from platform.m4ex.circuitpython.register import i2c_bit, i2c_bits
else:
  print("ERROR: No matching hardware libraries in `platform`.")

__version__ = "0.1.0.0"
CHIP_NAME   = "amg88xx"
CHAN_COUNT  = const(64)

# Registers are defined below in the class.
# These are possible register values.
#
# pylint: disable=bad-whitespace
# I2C address
_AMG88XX_ADDRESS                 = const(0x69)

# Operating Modes
_NORMAL_MODE                     = const(0x00)
_SLEEP_MODE                      = const(0x10)
_STAND_BY_60                     = const(0x20)
_STAND_BY_10                     = const(0x21)

# sw resets
_FLAG_RESET                      = const(0x30)
_INITIAL_RESET                   = const(0x3F)

# frame rates
_FPS_10                          = const(0x00)
_FPS_1                           = const(0x01)

# int enables
_INT_DISABLED                    = const(0x00)
_INT_ENABLED                     = const(0x01)

# int modes
_DIFFERENCE                      = const(0x00)
_ABSOLUTE_VALUE                  = const(0x01)

_INT_OFFSET                      = const(0x010)
_PIXEL_OFFSET                    = const(0x80)
_PIXEL_ARRAY_WIDTH               = const(8)
_PIXEL_ARRAY_HEIGHT              = const(8)
_PIXEL_TEMP_CONVERSION           = .25
_THERMISTOR_CONVERSION           = .0625
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
@micropython.native
def _signed_12bit_to_float(val):
  """ Take first 11 bits as absolute value
  """
  abs_val = (val & 0x7FF)
  if val & 0x800:
    return 0 -float(abs_val)
  return float(abs_val)

@micropython.native
def _twos_comp_to_float(val):
  """ Convert an unsigned integer into a float and return it
  """
  val &= 0xfff
  if val & 0x800:
    val -= 0x1000
  return float(val)

# ----------------------------------------------------------------------------
class AMG88XX:
  """Driver for the AMG88xx GRID-Eye IR 8x8 thermal camera."""

  # Set up the registers
  _pctl    = i2c_bits.RWBits(8, 0x00, 0)
  _rst     = i2c_bits.RWBits(8, 0x01, 0)
  _fps     = i2c_bit.RWBit(0x02, 0)
  _inten   = i2c_bit.RWBit(0x03, 0)
  _intmod  = i2c_bit.RWBit(0x03, 1)

  _intf    = i2c_bit.RWBit(0x04, 1)
  _ovf_irs = i2c_bit.RWBit(0x04, 2)
  _ovf_ths = i2c_bit.RWBit(0x04, 3)

  _intclr  = i2c_bit.RWBit(0x05, 1)
  _ovs_clr = i2c_bit.RWBit(0x05, 2)
  _ovt_clr = i2c_bit.RWBit(0x05, 3)

  _mamod   = i2c_bit.RWBit(0x07, 5)

  _inthl   = i2c_bits.RWBits(8, 0x08, 0)
  _inthh   = i2c_bits.RWBits(4, 0x09, 0)
  _intll   = i2c_bits.RWBits(8, 0x0A, 0)
  _intlh   = i2c_bits.RWBits(4, 0x0B, 0)
  _ihysl   = i2c_bits.RWBits(8, 0x0C, 0)
  _ihysh   = i2c_bits.RWBits(4, 0x0D, 0)

  _tthl   = i2c_bits.RWBits(8, 0x0E, 0)
  _tthh   = i2c_bits.RWBits(4, 0x0F, 0)

  def __init__(self, i2c):
    """ Requires already initialized I2C bus instance.
    """
    self._i2c = i2c
    self._i2cAddr = _AMG88XX_ADDRESS
    self._isReady = False
    self._imgData = bytearray(_PIXEL_ARRAY_WIDTH *_PIXEL_ARRAY_HEIGHT)

    try:
      # Enter normal mode, software reset, disable interrupts by default,
      # and set to 10 FPS
      self._pctl = _NORMAL_MODE
      self._rst = _INITIAL_RESET
      self._inten = False
      self._fps = _FPS_10
      self._isReady = True
    except OSError as ex:
      if ex.args[0] == errno.ENODEV:
        pass

    print("[{0:>12}] {1:35} ({2}): {3}"
          .format(CHIP_NAME, "GRID-Eye IR 8x8 thermal camera", __version__,
                  "ok" if self._isReady else "NOT FOUND"))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @property
  def temperature(self):
    """ Temperature of the sensor in Celsius
    """
    raw = (self._tthh << 8) | self._tthl
    return _signed_12bit_to_float(raw) * _THERMISTOR_CONVERSION

  #@timed_function
  @micropython.native
  @property
  def pixels_8x8(self):
    """ Return pixel as an _PIXEL_ARRAY_WIDTH x _PIXEL_ARRAY_HEIGHT temperature
        2D float list (in °C), with [row][col].
    """
    retbuf = [[0]*_PIXEL_ARRAY_WIDTH for _ in range(_PIXEL_ARRAY_HEIGHT)]
    buf = bytearray(2)
    pos = bytearray(1)

    for row in range(0, _PIXEL_ARRAY_HEIGHT):
      for col in range(0, _PIXEL_ARRAY_WIDTH):
        i = row *_PIXEL_ARRAY_HEIGHT +col
        pos[0] = _PIXEL_OFFSET +(i << 1)
        self._i2c.writeto(_AMG88XX_ADDRESS, pos, stop_=False)
        self._i2c.readfrom_into(_AMG88XX_ADDRESS, buf)
        raw = (buf[1] << 8) | buf[0]
        retbuf[row][col] = _twos_comp_to_float(raw) *_PIXEL_TEMP_CONVERSION
    return retbuf

  #@timed_function
  @micropython.native
  @property
  def pixels_64x1(self):
    """ Returns temperature image as linear bytearray (in °C) of the length
        _PIXEL_ARRAY_WIDTH x _PIXEL_ARRAY_HEIGHT.
        Reads the data in one go and is therefore muchg faster than `pixels`!
    """
    npx = _PIXEL_ARRAY_HEIGHT*_PIXEL_ARRAY_WIDTH *2
    buf = bytearray(npx)
    pos = bytearray(1)
    pos[0] = _PIXEL_OFFSET
    self._i2c.writeto(_AMG88XX_ADDRESS, pos, stop_=False)
    self._i2c.readfrom_into(_AMG88XX_ADDRESS, buf)

    for i in range(0, npx, 2):
      raw = (buf[i+1] << 8) | buf[i]
      raw &= 0xfff
      raw -= 0x1000 if raw & 0x800 else 0
      self._imgData[i//2] = int(raw *_PIXEL_TEMP_CONVERSION)
    return self._imgData

  @property
  def isReady(self):
    return self._isReady

  @property
  def channelCount(self):
    return _PIXEL_ARRAY_WIDTH *_PIXEL_ARRAY_HEIGHT

  @property
  def width(self):
    return _PIXEL_ARRAY_WIDTH

  @property
  def height(self):
    return _PIXEL_ARRAY_HEIGHT

  @property
  def name(self):
    return CHIP_NAME

# ----------------------------------------------------------------------------
