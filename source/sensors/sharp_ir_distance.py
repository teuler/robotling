# ----------------------------------------------------------------------------
# sharp_ir_distance.py
# Analog Sharp IR distance sensors
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-23, v1
# ----------------------------------------------------------------------------
import array
from math import exp
from sensors.sensor_base import SensorBase

__version__ = "0.1.0.0"

# ----------------------------------------------------------------------------
class SharpIRDistSensor(SensorBase):
  """Base class for analog Sharp IR distance sensors."""

  def __init__(self, driver, chan):
    super().__init__(driver, chan)
    self._type = "IR distance"
    self._coef = array.array('f', [1,1,1,1])

  @property
  def dist_raw(self):
    if self._autoUpdate:
      self._driver.update()
    return self._driver.data[self._chan]

  @property
  def dist_cm(self):
    if self._autoUpdate:
      self._driver.update()
    cf = self._coef
    x  = self._driver.data[self._chan]
    return cf[0]+ cf[1]*exp(-cf[2]*x)+cf[3]*exp(-cf[4]*x)


class SharpIRDistSensor_GP2Y0A41SK0F(SharpIRDistSensor):
  """Simplified interface class for Sharp GP2Y0A41SK0F IR distance sensors."""

  def __init__(self, driver, chan):
    """ Requires an already initialised sensor driver instance and the
        channel assigned to this sensor instance. The distance ('dist_cm')
        is calibrated for the Sharp GP2Y0A41SK0F (e.g. 0A41SK F 81), using
        coefficients from a double exponential fit.
    """
    super().__init__(driver, chan)
    self._coef = array.array('f', [-1.995,12.9, 0.000329958, 93.928, 0.003793])
    print("Sensor '{0}' on channel #{1} is ready.".format(self._type, chan))

# ----------------------------------------------------------------------------
