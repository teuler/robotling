# ----------------------------------------------------------------------------
# i2c_bit.py
#
# The MIT License (MIT)
# Copyright (c) 2019 Thomas Euler
# 2019-07-30, v1
#
# Based on the CircuitPython driver:
# https://github.com/adafruit/Adafruit_CircuitPython_Register
#
# The MIT License (MIT)
#
# Copyright (c) 2016 Scott Shawcroft for Adafruit Industries
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
# pylint: disable=too-few-public-methods
# ----------------------------------------------------------------------------
class RWBit:
  """
  Single bit register that is readable and writeable.

  Values are `bool`

  :param int register_address: The register address to read the bit from
  :param type bit: The bit index within the byte at ``register_address``
  :param int register_width: The number of bytes in the register. Defaults to 1.
  :param bool lsb_first: Is the first byte we read from I2C the LSB? Defaults to true
  """
  def __init__(self, reg_addr, bit, reg_width=1, lsb_first=True):
    # the bitmask *within* the byte!
    self.bit_mask = 1 << (bit%8)
    self.buf = bytearray(1 + reg_width)
    self.buf[0] = reg_addr
    if lsb_first:
      # the byte number within the buffer
      self.byte = bit //8 +1
    else:
      # the byte number within the buffer
      self.byte = reg_width -(bit //8)

  def __get__(self, obj, objtype=None):
    obj._i2c.write_then_readinto(obj._i2cAddr, self.buf, self.buf, out_end=1,
                                 in_start=1, stop_=False)
    return bool(self.buf[self.byte] & self.bit_mask)

  def __set__(self, obj, value):
    obj._i2c.write_then_readinto(obj._i2cAddr, self.buf, self.buf, out_end=1,
                                 in_start=1, stop_=False)
    if value:
      self.buf[self.byte] |= self.bit_mask
    else:
      self.buf[self.byte] &= ~self.bit_mask
    obj._i2c.writeto(obj._i2cAddr, self.buf)


class ROBit(RWBit):
  """
  Single bit register that is read only. Subclass of `RWBit`.

  Values are `bool`

  :param int register_address: The register address to read the bit from
  :param type bit: The bit index within the byte at ``register_address``
  :param int register_width: The number of bytes in the register. Defaults to 1.
  """
  def __set__(self, obj, value):
    raise AttributeError()

# ----------------------------------------------------------------------------
