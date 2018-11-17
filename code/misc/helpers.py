# ----------------------------------------------------------------------------
# helpers.py
# Different helper functions and classes.
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-13, v1
# ----------------------------------------------------------------------------
import array

__version__ = "0.1.0.0"

# ----------------------------------------------------------------------------
class TemporalFilter(object):
  """Store history of sensor data and provide mean of last n values."""

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
