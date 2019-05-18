# ----------------------------------------------------------------------------
# compass.py
# Compass based on magnetometer/accelerometer readings from an chip-specific
# driver, such as the LMS303
# Based on Chris H's sketch:
# https://learn.adafruit.com/pages/1341/elements/2996806/download
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-26, v1
# 2018-10-26, Non-calibrated, non-tilt corrected compass readout added;
#             the calibrated readout is still unfinished
# 2019-05-06, `getPitchRoll` now returns 4-element tuple, with a -1 at
#             position 1 to be compatible with the data format returned
#             by `getHeading3D`
# ----------------------------------------------------------------------------
import array
import robotling_board as rb
from math import pi, sin, cos, asin, acos, atan2, sqrt
from sensors.sensor_base import SensorBase
from misc.helpers import timed_function

__version__ = "0.1.1.0"

# ----------------------------------------------------------------------------
class Compass(SensorBase):
  """Compass class that uses accelerometer and magnetometer data."""

  def __init__(self, driver):
    super().__init__(driver, 0)
    if driver.isReady:
      # Initialize
      self._acc     = array.array('i', [0,0,0])
      self._mag     = array.array('i', [0,0,0])
      self._heading = 0.0
      self._pitch   = 0.0
      self._roll    = 0.0
      self._type    = "Compass"

    print("[{0:>12}] {1:35} ({2}): {3}"
          .format(driver.name, self._type, __version__,
                  "ok" if driver._isReady else "FAILED"))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  #@timed_function
  def getHeading(self, tilt=False, calib=False, hires=True):
    """ Returns heading with or w/o tilt compensation and/or calibration,
        if available.
        NOTE: The parameter `hires` has no effect; it exists only for
        compatibility reasons.
    """
    if self._driver == None:
      return rb.RBL_ERR_DEVICE_NOT_READY
    Mag  = self._mag
    Mag  = self._driver.magnetometer_nT

    # Normalize magnetometer readings
    norm = sqrt(Mag[0]**2 +Mag[1]**2 +Mag[2]**2)
    xm_n =  Mag[0] /norm
    ym_n = -Mag[1] /norm

    if tilt:
      # Tilt compensate magnetic sensor measurements
      _, pit, rol = self.getPitchRoll(radians=True)
      zm_n = -Mag[2] /norm
      xm_c = xm_n *cos(pit) +zm_n *sin(pit)
      ym_c = ym_n *cos(rol) -zm_n *sin(rol)
      '''
      xm_c = xm_n *cos(pit) +zm_n *sin(pit)
      ym_c = xm_n *sin(rol)*sin(pit) +ym_n *cos(rol) -zm_n *sin(rol)*cos(pit)
      '''
    else:
      xm_c = ym_n
      ym_c = xm_n

    # Calculate heading
    self._heading  = (atan2(-ym_c, xm_c) *180) /pi
    self._heading += 360 if self._heading < 0 else 0
    return self._heading


  #@timed_function
  def getHeading3D(self, calib=False):
    """ Returns heading, pitch and roll in [°] with or w/o calibration,
        if available.
    """
    if self.getHeading(tilt=True, calib=calib) == rb.RBL_ERR_DEVICE_NOT_READY:
      return (rb.RBL_ERR_DEVICE_NOT_READY, 0, 0, 0)
    else:
      return (rb.RBL_OK, self._heading, self._pitch, self._roll)


  #@timed_function
  def getPitchRoll(self, radians=False):
    """ Returns error code, pitch and roll in [°] as a 4-element tuple.
        Note that the second element is -1, such that the data format
        is compatible with that returned by `getHeading3D`
    """
    if self._driver == None:
      return (rb.RBL_ERR_DEVICE_NOT_READY, 0, 0)
    Acc  = self._acc
    Acc  = self._driver.accelerometer

    # Normalize accelerometer readings
    norm = sqrt(Acc[0]**2 +Acc[1]**2 +Acc[2]**2)
    xa_n =  Acc[0] /norm
    ya_n = -Acc[1] /norm
    za_n = -Acc[2] /norm

    # Calulate pitch and roll
    p =  asin(xa_n)
    r = -asin(ya_n)
    self._pitch = p *180/pi
    self._roll  = r *180/pi
    if radians:
      return (rb.RBL_OK, -1, p, r)
    else:
      return (rb.RBL_OK, -1, self._pitch, self._roll)

# ----------------------------------------------------------------------------
