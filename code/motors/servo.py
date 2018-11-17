# ----------------------------------------------------------------------------
# servo.py
# Simplified servo interface class(es)
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-10-09, v1
# ----------------------------------------------------------------------------
import array
from machine import PWM, Pin

__version__ = "0.1.0.0"

# ----------------------------------------------------------------------------
class Servo(object):
  """Simplified interface class for servos."""

  def __init__(self, pin, freq=50, us_range=[600, 2400], ang_range=[0, 180]):
    """ Initialises the pin that connects to the servo, with "pin" as a pin
        number, the frequency "freq" of the signal (in Hz), the minimun
        and maximum supported timing ("us_range"), and the respective angular
        range ("ang_range") covered.
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
    self._pwm      = PWM(Pin(pin), freq=freq, duty=0)
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
    t = self._t_us
    if t_us == 0:
      t = 0
      self._pwm.duty(0)
    else:
      t = min(self._range[1], max(self._range[0], t_us))
      self._pwm.duty(t *1024 *self._freq // 1000000)

# ----------------------------------------------------------------------------
