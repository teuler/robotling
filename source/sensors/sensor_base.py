# ----------------------------------------------------------------------------
# sensor_base.py
# Base class for simplified sensor interface
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-23, v1
# ----------------------------------------------------------------------------
import array
from math import exp

__version__ = "0.1.0.0"

# ----------------------------------------------------------------------------
class SensorBase(object):
  """Base class for sensors."""

  def __init__(self, driver, chan=0):
    self._driver = driver
    self._chan   = min(max(chan, 0), driver.channelCount-1)
    self._type   = "n/a"
    self._autoUpdate = False

  @property
  def autoUpdate(self):
    return self._autoUpdate

  @autoUpdate.setter
  def autoUpdate(self, value):
    self._autoUpdate = value

# ----------------------------------------------------------------------------
