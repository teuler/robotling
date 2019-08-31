# ----------------------------------------------------------------------------
# i2c_bits.py
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
class RWBits:
  """
  Multibit register (less than a full byte) that is readable and writeable.
  This must be within a byte register.

  Values are `int` between 0 and 2 ** ``num_bits`` - 1.

  :param int num_bits: The number of bits in the field.
  :param int register_address: The register address to read the bit from
  :param type lowest_bit: The lowest bits index within the byte at ``register_address``
  :param int register_width: The number of bytes in the register. Defaults to 1.
  :param bool lsb_first: Is the first byte we read from I2C the LSB? Defaults to true
  """
  def __init__(self, num_bits, reg_addr, low_bit, reg_wid=1, lsb_first=True):
    self.bit_mask = ((1 << num_bits)-1)  << low_bit
    #print("bitmask: ",hex(self.bit_mask))
    if self.bit_mask >= 1 << (reg_wid *8):
      raise ValueError("Cannot have more bits than register size")
    self.low_bit = low_bit
    self.buf = bytearray(1 + reg_wid)
    self.buf[0] = reg_addr
    self.lsb_first = lsb_first

  def __get__(self, obj, objtype=None):
    obj._i2c.write_then_readinto(obj._i2cAddr, self.buf, self.buf, out_end=1,
                                 in_start=1, stop_=False)
    # Read the number of bytes into a single variable
    reg = 0
    order = range(len(self.buf)-1, 0, -1)
    if not self.lsb_first:
      order = reversed(order)
    for i in order:
      reg = (reg << 8) | self.buf[i]
    return (reg & self.bit_mask) >> self.low_bit

  def __set__(self, obj, value):
    # Shift the value over to the right spot
    value <<= self.low_bit
    obj._i2c.write_then_readinto(obj._i2cAddr, self.buf, self.buf, out_end=1,
                                 in_start=1, stop_=False)
    reg = 0
    order = range(len(self.buf)-1, 0, -1)
    if not self.lsb_first:
      order = range(1, len(self.buf))
    for i in order:
      reg = (reg << 8) | self.buf[i]
    #print("old reg: ", hex(reg))
    # Mask off the bits we're about to change, then or in our new value
    reg &= ~self.bit_mask
    reg |= value
    #print("new reg: ", hex(reg))
    for i in reversed(order):
      self.buf[i] = reg & 0xFF
      reg >>= 8
    obj._i2c.writeto(obj._i2cAddr, self.buf)

class ROBits(RWBits):
  """
  Multibit register (less than a full byte) that is read-only. This must be
  within a byte register.

  Values are `int` between 0 and 2 ** ``num_bits`` - 1.

  :param int num_bits: The number of bits in the field.
  :param int register_address: The register address to read the bit from
  :param type lowest_bit: The lowest bits index within the byte at ``register_address``
  :param int register_width: The number of bytes in the register. Defaults to 1.
  """
  def __set__(self, obj, value):
    raise AttributeError()

# ----------------------------------------------------------------------------
