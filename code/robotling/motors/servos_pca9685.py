# ----------------------------------------------------------------------------
# servos_pca9685.py
# Class for servos controlled by the PCA9685 16-channel servo driver
#
# The MIT License (MIT)
# Copyright (c) 2020 Thomas Euler
# 2020-01-04, v1
#
# The MIT License (MIT)
#
# Copyright (c) 2016 Radomir Dopieralski, written for Adafruit Industries
# Copyright (c) 2017 Scott Shawcroft for Adafruit Industries LLC
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
from misc.helpers import timed_function
from micropython import const
from motors.servo_base import ServoBase

from platform.platform import platform
if (platform.ID == platform.ENV_ESP32_UPY or
    platform.ID == platform.ENV_ESP32_TINYPICO):
  from platform.esp32.register import i2c_bit, i2c_bits
  from platform.esp32.register.i2c_struct import UnaryStruct
  from platform.esp32.register.i2c_struct_array import StructArray
elif platform.ID == platform.ENV_CPY_SAM51:
  from platform.m4ex.circuitpython.register import i2c_bit, i2c_bits
  from platform.m4ex.circuitpython.i2c_struct import UnaryStruct
  from platform.m4ex.circuitpython.i2c_struct_array import StructArray
else:
  print("ERROR: No matching hardware libraries in `platform`.")

__version__      = "0.1.0.0"
CHIP_NAME        = "pca9685"
CHAN_COUNT       = const(16)
DEF_RANGE_DEG    = (0, 180)
DEF_RANGE_US     = (600, 2400)

_PCA9685_ADDRESS = const(0x40)
_REF_CLOCK_FREQ  = const(25000000)
_MAX_DUTY        = const(0xFFFF)

# ----------------------------------------------------------------------------
class PWMChannel(ServoBase):
  """Basically a servo connected to a single PCA9685 channel."""

  def __init__(self, pca, index):
    self._pca = pca
    self._index = index
    super().__init__(pca.frequency, DEF_RANGE_US, DEF_RANGE_DEG, False)

  @property
  def angle(self):
    """ Report current angle (in degrees)
    """
    return self._angle

  @angle.setter
  def angle(self, value):
    """ Move to the specified angle (in degrees)
    """
    self.write_us(self.angle_in_us(value))

  def off(self):
    """ Turn servo off
        TODO: Check if this really works
    """
    self.duty_cycle = 0

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @timed_function
  def write_us_timed(self, t_us):
    self._write_us(t_us)

  #@micropython.native
  def write_us(self, t_us):
    """ Move to a position given by the timing
    """
    if t_us == 0:
      self._pca.pwm_regs[self._index] = (0, 0)
    elif t_us < 0:
      self._pca.pwm_regs[self._index] = (0x1000, 0)
    else:
      f = self._freq
      r = self._range
      t = min(r[1], max(r[0], t_us))
      if not self._invert:
        d = int(t *_MAX_DUTY *f // 1000000)
      else:
        d = int((r[1] -t +r[0]) *_MAX_DUTY *f // 1000000)
      # Shift value by 4 because the PCA9685 is only 12 bits
      self._pca.pwm_regs[self._index] = (0, (int(d) + 1) >> 4)
      if self._verbose:
        print("angle={0}°, t_us={1}, duty={2}".format(self._angle, t_us, d))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  # Previous methods and properties of `PWMChannel`
  @property
  def frequency(self):
    """ The overall PWM frequency in Hertz (read-only). A PWMChannel's
        frequency cannot be set individually. All channels share a common
        frequency, set by PCA9685.frequency.
    """
    return self._pca.frequency

  @frequency.setter
  def frequency(self, _):
    raise NotImplementedError("frequency cannot be set on individual channels")

  @property
  def duty_cycle(self):
    """ 16 bit value that dictates how much of one cycle is high (1) versus
        low (0). 0xffff will always be high, 0 will always be low and 0x7fff
        will be half high and then half low.
    """
    pwm = self._pca.pwm_regs[self._index]
    if pwm[0] == 0x1000:
      return 0xffff
    return pwm[1] << 4

  @duty_cycle.setter
  def duty_cycle(self, value):
    if not 0 <= value <= 0xffff:
      raise ValueError("Out of range")
    if value == 0xffff:
      self._pca.pwm_regs[self._index] = (0x1000, 0)
    else:
      # Shift our value by four because the PCA9685 is only 12 bits but our
      # value is 16
      self._pca.pwm_regs[self._index] = (0, (value + 1) >> 4)

# ----------------------------------------------------------------------------
class PCAChannels: # pylint: disable=too-few-public-methods
  """Lazily creates and caches channel objects as needed."""

  def __init__(self, pca):
    self._pca = pca
    self._channels = [None] *len(self)

  def __len__(self):
    return CHAN_COUNT

  def __getitem__(self, index):
    if not self._channels[index]:
      self._channels[index] = PWMChannel(self._pca, index)
    return self._channels[index]

# ----------------------------------------------------------------------------
class PCA9685:
  """ Initialise the PCA9685 chip at ``address`` on ``i2c_bus``.
      The internal reference clock is 25mhz but may vary slightly with
      environmental conditions and manufacturing variances. Providing a more
      precise ``reference_clock_speed`` can improve the accuracy of the
      frequency and duty_cycle computations. See the ``calibration.py``
      example for how to derive this value by measuring the resulting pulse
      widths.

      Requires already initialized I2C bus instance `i2c`, the I2C address
      of the PCA9685 (`addr`) as well as the frequency of the internal
      reference clock in Hz (`clock_freq`).
  """
  # Set up the registers
  mode1_reg = UnaryStruct(0x00, '<B')
  prescale_reg = UnaryStruct(0xFE, '<B')
  pwm_regs = StructArray(0x06, '<HH', 16)

  def __init__(self, i2c, addr=_PCA9685_ADDRESS, clock_freq=_REF_CLOCK_FREQ):
    self._i2c = i2c
    self._i2cAddr = addr
    self.reference_clock_speed = clock_freq
    # Sequence of 16 `PWMChannel` objects. One for each channel.
    self.channels = PCAChannels(self)
    self.reset()
    self._isReady = True

    print("[{0:>12}] {1:35} ({2}): {3}"
          .format(CHIP_NAME, "PCA9685 16-channel servo driver", __version__,
                  "ok" if self._isReady else "NOT FOUND"))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def reset(self):
    """ Reset the chip.
    """
    self.mode1_reg = 0x00 # Mode1

  @property
  def frequency(self):
    """ The overall PWM frequency in Hertz.
    """
    return self.reference_clock_speed / 4096 / self.prescale_reg

  @frequency.setter
  def frequency(self, freq):
    prescale = int(self.reference_clock_speed / 4096.0 / freq + 0.5)
    if prescale < 3:
      raise ValueError("PCA9685 cannot output at the given frequency")
    old_mode = self.mode1_reg # Mode 1
    self.mode1_reg = (old_mode & 0x7F) | 0x10 # Mode 1, sleep
    self.prescale_reg = prescale # Prescale
    self.mode1_reg = old_mode # Mode 1
    time.sleep(0.005)
    self.mode1_reg = old_mode | 0xa1 # Mode 1, autoincrement on

  def __enter__(self):
    return self

  def __exit__(self, exception_type, exception_value, traceback):
    self.deinit()

  def deinit(self):
    """ Stop using the pca9685.
    """
    self.reset()

# ----------------------------------------------------------------------------
