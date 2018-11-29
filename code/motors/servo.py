# ----------------------------------------------------------------------------
# servo.py
# Simplified servo interface class(es)
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-10-09, v1
# 2018-11-25, v1.1, now uses dio_*.py to access machine
# ----------------------------------------------------------------------------
import array

from platform.platform import platform
if platform.ID == platform.ENV_ESP32_UPY:
  import platform.huzzah32.dio as dio
elif platform.ID == platform.ENV_CPY_SAM51:
  import platform.m4ex.dio as dio
else:
  print("ERROR: No matching hardware libraries in `platform`.")

__version__ = "0.1.1.0"

# ----------------------------------------------------------------------------
class Servo(object):
  """Simplified interface class for servos."""

  def __init__(self, pin, freq=50, us_range=[600, 2400], ang_range=[0, 180]):
    """ Initialises the pin that connects to the servo, with `pin` as a pin
        number, the frequency `freq` of the signal (in Hz), the minimun
        and maximum supported timing (`us_range`), and the respective angular
        range (`ang_range`) covered.
    """
    self._range    = array.array('i', [0]*6)
    self._range[0] = us_range[0]
    self._range[1] = us_range[1]
    self._range[2] = us_range[1] -us_range[0]
    self._range[3] = ang_range[0]
    self._range[4] = ang_range[1]
    self._range[5] = abs(ang_range[1] -ang_range[0])
    self._t_us     = 0
    self._freq     = freq
    self._angle    = 0
    self._pwm      = dio.PWMOut(pin, freq=freq, duty=0)
    self._max_duty = self._pwm.max_duty
    print("Servo is ready.")

  @property
  def angle(self):
    """ Report current angle (in degrees)
    """
    return self._angle

  @angle.setter
  def angle(self, value):
    """ Move to the specified angle (in degrees)
    """
    a = self._angle
    a = min(self._range[4], max(self._range[3], value))
    self._write_us(self._range[0] +self._range[2]
                   *(a -self._range[3]) //self._range[5])

  def off(self):
    """ Turn servo off
    """
    self._write_us(0)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def _write_us(self, t_us):
    t  = self._t_us
    md = self._max_duty
    f  = self._freq
    r  = self._range
    if t_us == 0:
      t = 0
      self._pwm.duty = 0
    else:
      self._pwm.duty = min(r[1], max(r[0], t_us)) *1024 *self._freq // 1000000

# ----------------------------------------------------------------------------
