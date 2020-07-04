#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# data_buffer.py
# Simple buffer for data with running mean functionality
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2019-05-01, v1
#
# ---------------------------------------------------------------------
import numpy as np

# ---------------------------------------------------------------------
class DataStack(object):
  """Store history of data and provide mean of last n values."""

  def __init__(self, n, initVal=0):
    self._nMax = max(n, 2)
    self._data = np.array([initVal]*self._nMax)
    self._nData = 0

  def shift(self, newVal=0):
    self._data[:-1] = self._data[1:]
    self._data[-1] = newVal
    self._nData = min(self._nData +1, self._nMax)

  @property
  def data(self):
    return self._data

  def _check(self, nBox):
    if self._nData == 0:
      return 0
    elif nBox > 0 and nBox <= self._nData:
      return nBox
    elif nBox > self._nData:
      return self._nData
    else:
      return self._nMax

  def mean(self, nBox=0):
    n = self._check(nBox)
    if n > 0:
      return np.mean(self._data[self._nMax -n:])
    return 0

  def diff(self, nBox=3):
    n = self._check(nBox)
    if n > 0:
      m = np.mean(self._data[self._nMax -n -1:-1])
      if not m == 0:
        return self._data[-1] /m
    return 0

# ---------------------------------------------------------------------
def filter(_newV, _VArr, _nBox=0):
  """ Adds new value to the end of the array (_VArr[1]) and deletes
      first array entry if maximal entry number (_VArr[0]) is reached.
      Returns mean of the _nBox last entries of the array
  """
  data = _VArr[1]
  data.append(_newV)
  if len(data) > _VArr[0]:
    data.pop(0)
  if (_nBox <= 0) or (_nBox > len(data)):
    return np.mean(data)
  else:
    n = len(data)
    return np.mean(data[n-_nBox:n])

# ---------------------------------------------------------------------
