# ----------------------------------------------------------------------------
# sensor_base.py
# Base class for simplified sensor interface
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-23, v1
# 2019-08-01, class `CameraBase` added
# ----------------------------------------------------------------------------
__version__ = "0.1.0.0"

# ----------------------------------------------------------------------------
class SensorBase(object):
  """Base class for sensors."""

  def __init__(self, driver, chan=0):
    self._driver = driver
    if not driver == None:
      self._chan = min(max(chan, 0), driver.channelCount-1)
    else:
      self._chan = chan
    self._type = "n/a"
    self._version = 0
    self._autoUpdate = False

  @property
  def autoUpdate(self):
    return self._autoUpdate

  @autoUpdate.setter
  def autoUpdate(self, value):
    self._autoUpdate = value

  @property
  def name(self):
    return self._type

# ----------------------------------------------------------------------------
class CameraBase(SensorBase):
  """Base class for cameras."""

  def __init__(self, driver):
    super().__init__(driver, 0)
    self.rows = driver.height
    self.cols = driver.width

  @property
  def resolution(self):
    return (self.rows, self.cols)

# ----------------------------------------------------------------------------
