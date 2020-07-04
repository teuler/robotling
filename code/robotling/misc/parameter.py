#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# parameter.py
# Class capsulating a scalar or vector with automatic limit checking and
# blending
#
# The MIT License (MIT)
# Copyright (c) 2020 Thomas Euler
# 2020-05-18, First version
#
# ----------------------------------------------------------------------------

try:
  ModuleNotFoundError
except NameError:
  ModuleNotFoundError = ImportError
try:
  # Micropython imports
  from ulab import compare
  import ulab as np
  MICROPYTHON = True
except ModuleNotFoundError:
  # Standard Python imports
  import numpy as np
  MICROPYTHON = False

# ----------------------------------------------------------------------------
class Parameter(object):
  """ Encapsulates a skalar or vector parameters and makes sure that it stays
      within a given range. Also, if requested, enables smooth blending between
      the current and a target value
  """
  def __init__(self, val, _minmax, lim=0, max_steps=0, unit="-"):
    # Convert into np.array
    if MICROPYTHON:
      try:
        _val = np.array(val)
        self._min = np.array(_minmax[0])
        self._max = np.array(_minmax[1])
      except ValueError:
        _val = np.array([val])
        self._min = np.array([_minmax[0]])
        self._max = np.array([_minmax[1]])

    else:
      if isinstance(val, list) or isinstance(val, np.ndarray):
        _val = np.array(val)
        self._min = np.array(_minmax[0])
        self._max = np.array(_minmax[1])
      else:
        _val = np.array([val])
        self._min = np.array([_minmax[0]])
        self._max = np.array([_minmax[1]])

    n = len(_val)
    if n != len(self._min) or n != len(self._max):
      raise ValueError("Parameters are not consistent")

    # Initialize other variables
    self._target = np.array([0] *n)
    self._inc = np.array([0] *n)
    self._lim = lim
    self._dim = n
    self._nInc = 0
    self._maxStep = 0
    self._unit = unit
    self._set_val(_val)
    self._maxStep = max_steps

  def __str__(self):
    _sval = ""
    _smin = ""
    _smax = ""
    for i in range(self._dim):
      _sval += "{0},".format(self._val[i])
      _smin += "{0},".format(self._min[i])
      _smax += "{0},".format(self._max[i])
    return "{0} {1} ({2} ... {3})".format(_sval[:-1], self._unit,
                                          _smin[:-1], _smax[:-1])

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def update(self):
    if self._nInc > 0:
      self._val = self._val +self._inc
      self._nInc -= 1

  def _get_val(self):
    return self._val[0] if self._dim == 1 else self._val

  def _set_val(self, val):
    if val is None:
      return
    if MICROPYTHON:
      try:
        newVal = compare.clip(np.array(val), self._min, self._max)
      except ValueError:
        newVal = compare.clip(np.array([val]), self._min, self._max)
      if self._maxStep == 0:
        self._val = newVal
      else:
        for i in range(self._dim):
          if abs(self._val[i] -newVal[i]) <= self._lim:
            self._inc[i] = 0
            self._val[i] = newVal[i]
          else:
            self._target[i] = newVal[i]
            self._nInc = self._maxStep
            self._inc[i] = (newVal[i] -self._val[i]) /self._maxStep
    else:
      newVal = np.clip(np.array(val), self._min, self._max)
      if self._maxStep == 0:
        self._val = newVal
      else:
        for i in range(self._dim):
          if abs(self._val[i] -newVal[i]) <= self._lim:
            self._inc[i] = 0
            self._val[i] = newVal[i]
          else:
            self._target[i] = newVal[i]
            self._nInc = self._maxStep
            self._inc[i] = (newVal[i] -self._val[i]) /self._maxStep

  val = property(_get_val, _set_val)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @property
  def x(self):
    return self._val[0]

  @property
  def y(self):
    if self._dim < 2:
      raise ValueError("Dimension out of range")
    else:
      return self._val[1]

  @property
  def z(self):
    if self._dim < 3:
      raise ValueError("Dimension out of range")
    else:
      return self._val[2]

  def __len__(self):
    return self._dim

# ----------------------------------------------------------------------------
