# ----------------------------------------------------------------------------
# servo.py
# Simplified servo interface class(es)
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-10-09, v1
# 2018-11-25, v1.1, now uses dio_*.py to access machine
# 2018-12-23, v1.2, added `verbose` to print timing information to help
#                   setting up a new servo (range). Now also handles inverted
#                   angle ranges.
# 2018-12-23, v1.3, max duty cycle bug fixed.
# ----------------------------------------------------------------------------
import array

from platform.platform import platform
if platform.ID == platform.ENV_ESP32_UPY:
  import platform.huzzah32.dio as dio
elif platform.ID == platform.ENV_CPY_SAM51:
  import platform.m4ex.dio as dio
else:
  print("ERROR: No matching hardware libraries in `platform`.")

__version__ = "0.1.3.0"

# ----------------------------------------------------------------------------
class Servo(object):
  """Simplified interface class for servos."""

  def __init__(self, pin, freq=50, us_range=[600, 2400],
               ang_range=[0, 180], verbose=False):
    """ Initialises the pin that connects to the servo, with `pin` as a pin
        number, the frequency `freq` of the signal (in Hz), the minimun
        and maximum supported timing (`us_range`), and the respective angular
        range (`ang_range`) covered.
        If `verbose` == True then angle and timing is logged; useful for
        setting up a new servo (range).
    """
    self._range      = array.array('i', [0]*6)
    self._range[0]   = us_range[0]
    self._range[1]   = us_range[1]
    self._range[2]   = us_range[1] -us_range[0]
    self._invert     = ang_range[0] > ang_range[1]
    self._range[3]   = min(ang_range[0], ang_range[1])
    self._range[4]   = max(ang_range[0], ang_range[1])
    self._range[5]   = abs(ang_range[1] -ang_range[0])
    self._verbose    = verbose
    self._t_us       = 0
    self._freq       = freq
    self._angle      = 0
    self._pwm        = dio.PWMOut(pin, freq=freq, duty=0)
    self._max_duty   = self._pwm.max_duty
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
    r = self._range
    self._angle = min(r[4], max(r[3], value))
    self._write_us(r[0] +r[2] *(self._angle -r[3]) //r[5])

  def off(self):
    """ Turn servo off
    """
    self._write_us(0)

  def deinit(self):
    """ Deinitialize PWM for given pin
    """
    try:
      self._pwm.deinit()
    except:
      pass

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
      t = min(r[1], max(r[0], t_us))
      if not self._invert:
        d = t *dio.MAX_DUTY *self._freq // 1000000
      else:
        d = (r[1] -t +r[0]) *dio.MAX_DUTY *self._freq // 1000000
      self._pwm.duty = d
      if self._verbose:
        print("angle={0}°, t_us={1}, duty={2}".format(self._angle, t_us, d))

# ----------------------------------------------------------------------------
