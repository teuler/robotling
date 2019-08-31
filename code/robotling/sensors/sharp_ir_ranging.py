# ----------------------------------------------------------------------------
# sharp_ir_ranging.py
# Analog Sharp IR range sensors
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-23, v1
# 2019-08-03, new type of Sharp sensor added (GP2Y0AF15X, 1.5-15 cm)
# ----------------------------------------------------------------------------
import array
from math import exp
from sensors.sensor_base import SensorBase

__version__ = "0.1.1.0"
CHIP_NAME_0 = "GP2Y0A41SK0F"  # 4 to 30 cm
CHIP_NAME_1 = "GP2Y0AF15X"    # 1.5 to 15 cm

# ----------------------------------------------------------------------------
class SharpIRRangingSensor(SensorBase):
  """Base class for analog Sharp IR ranging sensors."""

  def __init__(self, driver, chan):
    super().__init__(driver, chan)
    self._type = "IR range"
    self._coef = array.array('f', [1,1,1,1])

  @property
  def range_raw(self):
    if self._autoUpdate:
      self._driver.update()
    return self._driver.data[self._chan]

  @property
  def range_cm(self):
    if self._autoUpdate:
      self._driver.update()
    cf = self._coef
    x  = self._driver.data[self._chan]
    return cf[0]+ cf[1]*exp(-cf[2]*x)+cf[3]*exp(-cf[4]*x)

# The following interface classes require an already initialised sensor driver
# instance and the channel assigned to this sensor instance.
# The range ('range_cm') is calibrated for the respective Sharp sensor model
#  using coefficients from a double exponential fit.
#
class GP2Y0A41SK0F(SharpIRRangingSensor):
  """Interface class for Sharp GP2Y0A41SK0F IR ranging sensors (4-30 cm)."""

  def __init__(self, driver, chan):
    super().__init__(driver, chan)
    self._type = "IR ranging (Sharp)"
    self._coef = array.array('f', [-1.995,12.9, 0.000329958, 93.928, 0.003793])
    tx = "{0}, A/D channel #{1}".format(self._type, chan)
    print("[{0:>12}] {1:35} ({2}): ok"
          .format(CHIP_NAME_0, tx, __version__))

class GP2Y0AF15X(SharpIRRangingSensor):
  """Interface class for Sharp GP2Y0AF15X IR ranging sensors (1.5-15 cm)."""

  def __init__(self, driver, chan):
    super().__init__(driver, chan)
    self._type = "IR ranging (Sharp)"
    self._coef = array.array('f', [1.3249, 20.436, 0.0021805, 24.613, 0.064151])
    tx = "{0}, A/D channel #{1}".format(self._type, chan)
    print("[{0:>12}] {1:35} ({2}): ok"
          .format(CHIP_NAME_1, tx, __version__))

# ----------------------------------------------------------------------------
