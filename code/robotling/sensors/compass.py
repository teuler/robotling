# ----------------------------------------------------------------------------
# compass.py
# Compass based on magnetometer/accelerometer readings from an chip-specific
# driver, such as the LMS303
# Based on Chris H's sketch:
# https://learn.adafruit.com/pages/1341/elements/2996806/download
#
# The MIT License (MIT)
# Copyright (c) 2018-19 Thomas Euler
# 2018-09-26, v1
# 2018-10-26, Non-calibrated, non-tilt corrected compass readout added;
#             the calibrated readout is still unfinished
# 2019-05-06, `getPitchRoll` now returns 4-element tuple, with a -1 at
#             position 1 to be compatible with the data format returned
#             by `getHeading3D`
# 2019-05-25, `streamCalibrationData` prints raw readings to serial property
#             using a format that works with the MotionCal software
#             (see https://www.pjrc.com/store/prop_shield.html)
#             Also, the Compass class attempts to load calibration data
#             from modules like `calib_data_xxx.py` for the supported
#             non-calibrated magnetometer/accelerometer sensors.
#             NOTE: This is under construction, the compass tilt correction
#                   and the calibration does not work yet for the LSM303 nor
#                   the LSM9DS0.
# 2019-12-21, native code generation added (requires MicroPython >=1.12)
#
# ----------------------------------------------------------------------------
import time
import array
import robotling_board as rb
from math import pi, sin, cos, asin, acos, atan2, sqrt
from sensors.sensor_base import SensorBase
from misc.helpers import timed_function

__version__ = "0.1.1.2"

# ----------------------------------------------------------------------------
class Compass(SensorBase):
  """Compass class that uses accelerometer and magnetometer data."""

  def __init__(self, driver):
    super().__init__(driver, 0)
    if driver.isReady:
      # Initialize
      self._acc     = array.array('i', [0,0,0])
      self._mag     = array.array('i', [0,0,0])
      self._mag_off = array.array('f', [0,0,0])
      self._mag_mm  = array.array('f', [1,0,0, 0,1,0, 0,0,1])
      self._mag_fst = 50.0
      self._heading = 0.0
      self._pitch   = 0.0
      self._roll    = 0.0
      self._type    = "Compass"
      self._isCalib = False

      # Retrieve calibration data, if available
      if self._driver.name is "lsm303":
        try:
          import sensors.calib_data_lsm303 as calib
          self._mag_off[0] = calib.XM_OFF
          self._mag_off[1] = calib.YM_OFF
          self._mag_off[2] = calib.ZM_OFF
          self._mag_mm[0]  = calib.MM_00
          self._mag_mm[1]  = calib.MM_01
          self._mag_mm[2]  = calib.MM_02
          self._mag_mm[3]  = calib.MM_10
          self._mag_mm[4]  = calib.MM_11
          self._mag_mm[5]  = calib.MM_12
          self._mag_mm[6]  = calib.MM_20
          self._mag_mm[7]  = calib.MM_21
          self._mag_mm[8]  = calib.MM_22
          self._mag_fst    = calib.MFSTR
          self._isCalib    = True
        except ImportError:
          pass

    s = ", calibrated" if self._isCalib else ""
    print("[{0:>12}] {1:35} ({2}): {3}"
          .format(driver.name, self._type +s, __version__,
                  "ok" if driver._isReady else "FAILED"))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  #@timed_function
  @micropython.native
  def getHeading(self, tilt=False, calib=False, hires=True):
    """ Returns heading with or w/o tilt compensation and/or calibration,
        if available.
        NOTE: The parameter `hires` has no effect; it exists only for
        compatibility reasons.
    """
    if self._driver == None:
      return rb.RBL_ERR_DEVICE_NOT_READY
    Mag = self._mag
    Mag = self._driver.magnetometer_nT
    MOf = self._mag_off
    Mmm = self._mag_mm

    # Apply calibration data
    xmo = Mag[0] -MOf[0]
    ymo = Mag[1] -MOf[1]
    zmo = Mag[2] -MOf[2]
    xmc = Mmm[0]*xmo +Mmm[1]*ymo +Mmm[2]*zmo
    ymc = Mmm[3]*xmo +Mmm[4]*ymo +Mmm[5]*zmo
    zmc = Mmm[6]*ymo +Mmm[7]*ymo +Mmm[8]*zmo

    # Normalize magnetometer readings
    norm = sqrt(xmc**2 +ymc**2 +zmc**2)
    xmn = xmc /norm
    ymn = ymc /norm
    zmn = zmc /norm
    ymn = -ymc
    zmn = -zmc

    if tilt:
      # Tilt compensate magnetic sensor measurements
      # NOTE: Not yet working correctly
      _, _, pit, rol = self.getPitchRoll(radians=True)
      xmc = xmn *cos(pit) +ymn *sin(pit) *sin(rol) +zmn *sin(pit) *cos(rol)
      ymc = zmn *sin(rol) -ymn* cos(rol)

    else:
      xmc = xmn
      ymc = ymn

    # Calculate heading
    self._heading = (atan2(ymc, xmc) *180) /pi #old
    self._heading += 360 if self._heading < 0 else 0
    return self._heading


  #@timed_function
  @micropython.native
  def getHeading3D(self, calib=False):
    """ Returns heading, pitch and roll in [°] with or w/o calibration,
        if available.
    """
    if self.getHeading(tilt=True, calib=calib) == rb.RBL_ERR_DEVICE_NOT_READY:
      return (rb.RBL_ERR_DEVICE_NOT_READY, 0, 0, 0)
    else:
      #print(self._heading)
      return (rb.RBL_OK, self._heading, self._pitch, self._roll)


  #@timed_function
  @micropython.native
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

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def streamCalibrationData(self, n=1000):
    # Initialize
    xg = 0
    yg = 0
    zg = 0
    sf = "Raw:{0},{1},{2},{3},{4},{5},{6},{7},{8}"
    print("Collecting {0} data points data from `{1}` ..."
          .format(n, self._driver.name))

    # Collect data
    for i in range(n):
      xa, ya, za = self._driver.raw_accelerometer
      xm, ym, zm = self._driver.raw_magnetometer
      if self._driver.name is "lsm9ds0":
        xg, yg, zg = self._driver.raw_gyroscope
      s = sf.format(xa, ya, za, xg, yg, zg, xm, ym, zm)
      print(s)
      time.sleep(0.05)

    print("... done.")

# ----------------------------------------------------------------------------
