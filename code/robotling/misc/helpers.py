# ----------------------------------------------------------------------------
# helpers.py
# Different helper functions and classes.
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-13, v1
# 2018-12-22, v1.1 - Added TimeTracker class
# ----------------------------------------------------------------------------
import array

from platform.platform import platform
if (platform.ID == platform.ENV_ESP32_UPY or
    platform.ID == platform.ENV_ESP32_TINYPICO):
  from time import ticks_us, ticks_diff
else:
  from platform.m4ex.time import ticks_us, ticks_diff

__version__ = "0.1.1.0"

# ----------------------------------------------------------------------------
class TemporalFilter(object):
  """Store history of sensor data and provide mean."""

  def __init__(self, n, typeStr="f", initVal=0):
    self._n = max(n, 2)
    self._i = 0
    self._buf = array.array(typeStr, [initVal]*self._n)

  def mean(self, newVal):
    self._buf[self._i] = newVal
    self._i = self._i+1 if self._i < self._n-1 else 0
    av = 0
    for i in range(self._n):
      av += self._buf[i]
    return av /self._n

# ----------------------------------------------------------------------------
class TimeTracker(object):
  """Time tracker with callback support."""

  def __init__(self, period_ms=0, callback=None):
    self._sum_ms = 0
    self._count = 0
    self._per_ms = period_ms
    self._t0_ms = 0
    self._callback = callback
    self.reset()

  def reset(self, period_ms=-1):
    if period_ms >= 0:
      self._per_ms = period_ms
    self._t0_ms = ticks_us()

  def update(self):
    if self._callback:
      self._callback()
    self._sum_ms += ticks_diff(ticks_us(), self._t0_ms) /1000
    self._count  += 1

  @property
  def meanDuration_ms(self):
    return self._sum_ms /self._count

  @property
  def period_ms(self):
    return self._per_ms

# ----------------------------------------------------------------------------
def timed_function(f, *args, **kwargs):
  """ Use as decorator to measure the duration of a function call
  """
  myname = str(f).split(' ')[1]
  def new_func(*args, **kwargs):
    t = ticks_us()
    result = f(*args, **kwargs)
    delta = ticks_diff(ticks_us(), t)
    print('Function {} Time = {:6.3f}ms'.format(myname, delta/1000))
    return result
  return new_func

# ----------------------------------------------------------------------------
