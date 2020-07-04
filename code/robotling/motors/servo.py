# ----------------------------------------------------------------------------
# servo.py
# Simplified servo interface class(es)
#
# The MIT License (MIT)
# Copyright (c) 2018-2020 Thomas Euler
# 2018-10-09, v1
# 2018-11-25, v1.1, now uses dio_*.py to access machine
# 2018-12-23, v1.2, added `verbose` to print timing information to help
#                   setting up a new servo (range). Now also handles inverted
#                   angle ranges.
# 2018-12-23, v1.3, max duty cycle bug fixed.
# 2020-01-01, v1.4, micropython.native
# ----------------------------------------------------------------------------
import array
from misc.helpers import timed_function
from motors.servo_base import ServoBase

from platform.platform import platform
if platform.ID == platform.ENV_ESP32_UPY:
  import platform.esp32.dio as dio
elif platform.ID == platform.ENV_CPY_SAM51:
  import platform.m4ex.dio as dio
else:
  print("ERROR: No matching hardware libraries in `platform`.")

__version__      = "0.1.4.0"
DEF_RANGE_DEG    = (0, 180)
DEF_RANGE_US     = (600, 2400)

# ----------------------------------------------------------------------------
class Servo(ServoBase):
  """Simplified interface class for servos using PWMOut."""

  def __init__(self, pin, freq=50, us_range=DEF_RANGE_US,
               ang_range=DEF_RANGE_DEG, verbose=False):
    """ Initialises the pin that connects to the servo, with `pin` as a pin
        number, the frequency `freq` of the signal (in Hz), the minimun
        and maximum supported timing (`us_range`), and the respective angular
        range (`ang_range`) covered.
        If `verbose` == True then angle and timing is logged; useful for
        setting up a new servo (range).
    """
    super().__init__(freq, us_range, ang_range, verbose)
    self._pwm      = dio.PWMOut(pin, freq=freq, duty=0)
    self._max_duty = self._pwm.max_duty
    print("Servo at pin {0} ({1} Hz) ready.".format(pin, freq))

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
    """
    self.write_us(0)

  def deinit(self):
    """ Deinitialize PWM for given pin
    """
    try:
      self._pwm.deinit()
    except:
      pass

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @timed_function
  def write_us_timed(self, t_us):
    self._write_us(t_us)

  @micropython.native
  def write_us(self, t_us):
    """ Move to a position given by the timing
    """
    f = self._freq
    r = self._range
    if t_us == 0:
      self._pwm.duty = 0
    else:
      t = min(r[1], max(r[0], t_us))
      if not self._invert:
        d = t *dio.MAX_DUTY *f // 1000000
      else:
        d = (r[1] -t +r[0]) *dio.MAX_DUTY *f // 1000000
      self._pwm.duty = d
      if self._verbose:
        print("angle={0}°, t_us={1}, duty={2}".format(self._angle, t_us, d))

# ----------------------------------------------------------------------------
