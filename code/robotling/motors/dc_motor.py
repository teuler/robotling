# ----------------------------------------------------------------------------
# dc_motor.py
# Simplified motor interface class(es)
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-23, v1
# ----------------------------------------------------------------------------
__version__ = "0.1.0.0"

# ----------------------------------------------------------------------------
class DCMotor(object):
  """Simplified interface class for H-bridge controlled DC motors."""

  def __init__(self, driver, chan):
    """ Requires an already initialised DC motor driver instance and the
        channel assigned to this motor instance
    """
    self._driver = driver
    self._chan   = min(max(chan, 0), driver.channelCount-1)
    self._spArr  = [None]*driver.channelCount
    self._speed  = 0
    print("DC motor {0} is ready.".format(["A", "B", "C", "D"][self._chan]))

  @property
  def speed(self):
    return self._speed

  @speed.setter
  def speed(self, value):
    self._speed  = min(max(value, -100), 100)
    self._spArr[self._chan] = self._speed
    self._driver.setMotorSpeed(self._spArr)

# ----------------------------------------------------------------------------
