# ----------------------------------------------------------------------------
# servos_mini_maestro_18.py
# Class for servos controlled by the Mini Maestro 18-channel servo driver
#
# The MIT License (MIT)
# Copyright (c) 2020 Thomas Euler
# 2020-05-01, v1
#
# The MIT License (MIT)
# Copyright (c) 2016 Steven L. Jacobs (Maestro Python library)
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
  from machine import UART
elif platform.ID == platform.ENV_CPY_SAM51:
  pass
else:
  print("ERROR: No matching hardware libraries in `platform`.")

__version__      = "0.1.0.0"
CHIP_NAME        = "minMaestro18"
CHAN_COUNT       = const(18)
DEF_RANGE_DEG    = (0, 180)
DEF_RANGE_US     = (600, 2400)


_ADDRESS         = const(0x0C)
_FREQ            = const(50)
_BAUDRATE        = const(57600)
_UART_CH         = const(1)

_START           = const(0xAA)
_SET_TARGET      = const(0x04)
_SET_SPEED       = const(0x07)
_SET_ACCEL       = const(0x09)
_MULT_TARGETS    = const(0x1F)
_IS_MOVING       = const(0x13)
_GET_ERROR       = const(0x21)
_GET_POSITION    = const(0x10)

# ----------------------------------------------------------------------------
class ServoChannel(ServoBase):
  """ A servo connected to a single Mini Maestro channel.
      Note that internally position is given in 0.25 us-steps, thus the
      resolution factor (`_resolution`)
  """
  def __init__(self, mm18, index):
    self._mm18 = mm18
    self._index = index
    self._resolution = 4
    self._prepared = False
    self._cmd = bytearray([_START, mm18._iDev, _SET_TARGET, index, 0, 0])
    super().__init__(mm18.frequency, DEF_RANGE_US, DEF_RANGE_DEG, False)

  @property
  def angle(self):
    """ Report current angle (in degrees)
    """
    return self._angle *self._sign

  @angle.setter
  def angle(self, value):
    """ Move to the specified angle (in degrees)
    """
    self.write_us(self.angle_in_us(value))

  def off(self):
    """ Turn servo off
    """
    self.write_us(0)

  @property
  def is_moving(self):
    """ Check if all servos reached their targets. This is useful only if speed
        and/or acceleration have been set on one or more of the channels.
    """
    self._mm18._uart.write(self._cmdStart +chr(_IS_MOVING))
    return self._mm18._uart.readchar() == chr(0)

  def change_behavior(self, speed, accel):
    super().change_behavior(speed, accel)
    self.set_speed(speed)
    self.set_acceleration(accel)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def write_us(self, t_us, prepare_only=False):
    """ Move to a position given by the timing `t_us`; if `prepare_only` is
        True, the command for the move is stored and can be triggered using
        `MiniMaestro18.execute()`
    """
    if t_us == 0:
      d = 0
    else:
      r = self._range
      t = min(r[1], max(r[0], t_us))
      if not self._invert:
        d = int(t) *self._resolution
      else:
        d = int((r[1] -t +r[0]) *self._resolution)
    self._cmd[4] = d & 0x7F
    self._cmd[5] = (d >> 7) & 0x7F
    self._prepared = prepare_only
    self._mm18._nPrepared += 1 if prepare_only else 0
    if not prepare_only:
      self._mm18._uart.write(self._cmd)
    if self._verbose:
      print("angle={0}°, t_us={1}, duty={2}".format(self._angle, t_us, d))

  def set_speed(self, speed):
    """ Set speed of channel
        Speed is measured as 0.25 us / 10 ms; for the standard 1 ms pulse
        width change to move a servo between extremes, a speed of 1 will take
        1 minute, and a speed of 60 would take 1 second.
    """
    self._mm18._uart.write(bytearray([_START, self._mm18._iDev,
                                      _SET_SPEED, self._index,
                                      speed & 0x7F, (speed >> 7) & 0x7F]))

  def set_acceleration(self, accel):
    """ Set acceleration of channel
        This provide soft starts and finishes when servo moves to target
        position. Valid values are from 0 to 255. 0=unrestricted, 1 is slowest
        start. A value of 1 will take the servo about 3s to move between 1ms
        to 2 ms range.
    """
    self._mm18._uart.write(bytearray([_START, self._mm18._iDev,
                                      _SET_ACCEL, self._index,
                                      accel & 0x7F, (accel >> 7) & 0x7F]))

  def get_error(self):
    """ Get last error and reset red LED
    """
    self._mm18._uart.write(bytearray([_START, self._mm18._iDev, _GET_ERROR]))
    res = self._mm18._uart.read()
    if len(res) == 2:
      return res[0] +(res[1] << 8)
    else:
      return 0xFFFF

  def get_position_us(self):
    """ Get the current position
    """
    cmd = bytearray([_START, self._mm18._iDev, _GET_POSITION, self._index])
    self._mm18._uart.write(cmd)
    res = self._mm18._uart.read()
    if len(res) == 2:
      return res[0] +(res[1] << 8)
    else:
      return 0

# ----------------------------------------------------------------------------
class ServoChannels: # pylint: disable=too-few-public-methods
  """Lazily creates and caches channel objects as needed.
  """
  def __init__(self, mm18):
    self._mm18 = mm18
    self._channels = [None] *len(self)

  def __len__(self):
    return CHAN_COUNT

  def __getitem__(self, index):
    if not self._channels[index]:
      self._channels[index] = ServoChannel(self._mm18, index)
    return self._channels[index]

# ----------------------------------------------------------------------------
class MiniMaestro18:
  """ Initialise the Mini Maestro 16 device `dev` via UART channel `ch` and
      on pins `tx`,`rx` with BAUD rate `baud`.
  """
  def __init__(self, _tx, _rx, ch=_UART_CH, baud=_BAUDRATE, dev=_ADDRESS):
    try:
      self._uart = UART(ch, baudrate=baud, tx=_tx, rx=_rx)
      self._iDev = dev
      self.channels = ServoChannels(self)
      self.reset()
      self._isReady = True
    except:
      pass
    print("[{0:>12}] {1:35} ({2}): {3}"
          .format(CHIP_NAME,
                  "MiniMaestro 18-channel servo driver", __version__,
                  "ok" if self._isReady else "NOT FOUND"))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def reset(self):
    """ Reset the controller
    """
    self._isReady = False
    self._nPrepared = 0

  def execute(self):
    """ If servo movements were prepared (`servo.write_us(..., True)`), then
        all these movements are executed in one command.
        Note that this works only with continuous blocks of servos.
    """
    if self._nPrepared > 0:
      cmd = bytearray([_START, self._iDev, _MULT_TARGETS, 0, 0])
      nCh = 0
      for iCh, Ch in enumerate(self.channels):
        if Ch._prepared:
          cmd = cmd +bytearray([Ch._cmd[4], Ch._cmd[5]])
          if nCh == 0:
            cmd[4] = iCh
          nCh += 1
      cmd[3] = nCh
      self._uart.write(cmd)
    self._nPrepared = 0

  @property
  def frequency(self):
    return _FREQ

  @frequency.setter
  def frequency(self, freq):
    # TODO: Allow changing the frequency [Hz]
    pass

  def __enter__(self):
    return self

  def __exit__(self, exception_type, exception_value, traceback):
    self.deinit()

  def deinit(self):
    """ Release the UART
    """
    self._uart.deinit()
    self.reset()

# ----------------------------------------------------------------------------
