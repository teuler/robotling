# ----------------------------------------------------------------------------
# compass.py
# ...
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-26, v1
# 2018-10-26, Non-calibrated, non-tilt corrected compass readout added;
#             the calibrated readout is still unfinished
#
# Based on Chris H's sketch:
# https://learn.adafruit.com/pages/1341/elements/2996806/download
#
# ----------------------------------------------------------------------------
import array
import robotling_board as rboard
from math import pi, sin, cos, asin, acos, atan2, sqrt
from sensors.sensor_base import SensorBase
from driver.helpers import timed_function

__version__ = "0.1.0.0"

# ----------------------------------------------------------------------------
class Compass(SensorBase):
  """Compass class that uses accelerometer and magnetometer data."""

  def __init__(self, driver):
    self._driver    = None
    if driver.isReady:
      super().__init__(driver, 0)
      self._acc     = array.array('i', [0,0,0])
      self._mag     = array.array('i', [0,0,0])
      self._heading = 0.0
      self._pitch   = 0.0
      self._roll    = 0.0
      self._type    = "compass (LSM303)"
      print("Compass is ready.")


  #@timed_function
  def pitch_roll(self, radians=False, verbose=False):
    """ Returns error code, pitch and roll in [°] as a tuple
    """
    if self._driver == None:
      return (rboard.RBL_ERR_DEVICE_NOT_READY, 0, 0)
    pit  = self._pitch
    rol  = self._roll
    Acc  = self._acc
    Acc  = self._driver.accelerometer

    # Normalize accelerometer readings
    norm = sqrt(Acc[0]**2 +Acc[1]**2 +Acc[2]**2)
    xa_n =  Acc[0] /norm
    ya_n = -Acc[1] /norm
    za_n = -Acc[2] /norm

    # Calulate pitch and roll
    p    =  asin(xa_n)
    r    = -asin(ya_n)
    pit  = p *180/pi
    rol  = r *180/pi
    if verbose:
      print("pitch={0:.1f}°, roll={1:.1f}°".format(pit, rol))
    if radians:
      return (rboard.RBL_OK, p, r)
    else:
      return (rboard.RBL_OK, pit, rol)


  #@timed_function
  #@property
  def heading(self):
    """ Heading w/o calibration and w/o tilt compensation, but faster
    """
    if self._driver == None:
      return rboard.RBL_ERR_DEVICE_NOT_READY
    hd   = self._heading
    Mag  = self._mag
    Mag  = self._driver.magnetometer_nT

    # Normalize magnetometer readings
    norm = sqrt(Mag[0]**2 +Mag[1]**2 +Mag[2]**2)
    x_n  =  Mag[0] /norm
    y_n  = -Mag[1] /norm

    # Calculate heading
    hd   = (atan2(-y_n, x_n) *180) /pi
    if hd < 0:
      hd += 360
    return hd


  #@timed_function
  #@property
  def heading_tilt(self):
    """ Heading w/o calibration but w/ tilt compensation
    """
    if self._driver == None:
      return rboard.RBL_ERR_DEVICE_NOT_READY
    hd   = self._heading
    Mag  = self._mag
    Mag  = self._driver.magnetometer_nT
    pit, rol = self.pitch_roll(radians=True)

    # Normalize magnetometer readings
    norm = sqrt(Mag[0]**2 +Mag[1]**2 +Mag[2]**2)
    xm_n =  Mag[0] /norm
    ym_n = -Mag[1] /norm
    zm_n = -Mag[2] /norm

    # Tilt compensate magnetic sensor measurements
    xm_c = xm_n *cos(pit) +zm_n *sin(pit)
    ym_c = ym_n *cos(rol) -zm_n *sin(rol)
    '''
    xm_c = xm_n *cos(pit) +zm_n *sin(pit)
    ym_c = xm_n *sin(rol)*sin(pit) +ym_n *cos(rol) -zm_n *sin(rol)*cos(pit)
    '''
    # Calculate heading
    hd   = (atan2(-ym_c, xm_c) *180) /pi
    if hd < 0:
      hd += 360
    return hd


  @property
  def heading_calibrated(self):
    """ From the notes mentioned above:
        This is a single sketch for tilt compensated compass using an
        LSM303DLHC. It does not use any libraries, other than wire, because I
        found a number of errors in libraries that are out there.The biggest
        problem is with libraries that rely on the application note for the
        lsm303. That application note seems to include assumptions that are
        wrong, and I was not able to get it to produce reliable tilt
        compensated heading values.  If you look at how pitch, roll and
        heading are calculated below, you will see that the formula have some
        of the factors from the application note, but other factors are not
        included.

        Somehow the matrix manupulations that are described in the application
        note introduce extra factors that are wrong. For example, the pitch
        and roll calculation should not depend on whether you rotate pitch
        before roll, or vice versa. But if you go through the math using the
        application note, you will find that they give different formula.

        Same with Heading.  When I run this sketch on my Adafruit break-out
        board, I get very stable pitch, roll and heading, and the heading is
        very nicely tilt compensated, regardless of pitch or roll.
    """
    if self._driver == None:
      return rboard.RBL_ERR_DEVICE_NOT_READY
    Acc = self._acc                      # Ax, Ay, Az
    Mag = self._mag                      # Mx, My, Mz
    Acc = self._driver.accelerometer
    Mag = self._driver.magnetometer_nT
    hd  = self._heading                  # Heading
    MPr = array.array("f", [0,0,0])      # Xm_print, Ym_print, Zm_print
    MOf = array.array("f", [0,0,0])      # Xm_off, Ym_off, Zm_off
    MCa = array.array("f", [0,0,0])      # Xm_cal, Ym_cal, Zm_cal
    MNo = array.array("f", [0])          # Norm_m
    APr = array.array("f", [0,0,0])      # Xa_print, Ya_print, Za_print
    AOf = array.array("f", [0,0,0])      # Xa_off, Ya_off, Za_off
    ACa = array.array("f", [0,0,0])      # Xa_cal, Ya_cal, Za_cal
    ANo = array.array("f", [0])          # Norm_a
    Af  = array.array("f", [0,0,0])      # fXa, fYa, fZa
    Mf  = array.array("f", [0,0,0])      # fXm, fYm, fZm
    alp = array.array("f", [0.15])       # alpha
    Mfc = array.array("f", [0,0])        # fXm_comp, fYm_comp
    pit = array.array("f", [0,0])        # pitch, pitch_print
    rol = array.array("f", [0,0])        # roll, roll_print

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Apply calibration to accelerometer data
    # TODO: Calculated by Magneto 1.2 ??
    '''
    AOf[0] = Acc[0]/16.0 +14.510699
    AOf[1] = Acc[1]/16.0 -17.648453
    AOf[2] = Acc[2]/16.0 - 6.134981
    '''
    AOf[0] = Acc[0] +0.0
    AOf[1] = Acc[1] +0.0
    AOf[2] = Acc[2] +0.0

    ACa[0] =  1.0*AOf[0] +0.0*AOf[1] +0.0*AOf[2]
    ACa[1] =  0.0*AOf[0] +1.0*AOf[1] +0.0*AOf[2]
    ACa[2] =  0.0*AOf[0] +0.0*AOf[1] +1.0*AOf[2]
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # Original code did not appear to normalize, and this seems to help
    ANo = sqrt(ACa[0]**2 +ACa[1]**2 +ACa[2]**2)
    ACa[0] = ACa[0] /ANo
    ACa[1] = -ACa[1] /ANo
    ACa[2] = -ACa[2] /ANo

    # Low-Pass filter
    Af[0] =  ACa[0] *alp[0] +(Af[0] *(1.0 -alp[0]))
    Af[1] =  ACa[1] *alp[0] +(Af[1] *(1.0 -alp[0]))
    Af[2] =  ACa[2] *alp[0] +(Af[2] *(1.0 -alp[0]))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Apply calibration to magnetometer data
    # (Calculated using Magneto 1.2, see
    #  https://forum.arduino.cc/index.php?topic=265541.0)
    """
    MOf[0] = Mag[0] -6411.570727
    MOf[1] = Mag[1] +16910.902706
    MOf[2] = Mag[2] +7054.170391
    """
    MOf[0] = (Mag[0] -(+4000)) /4636.36
    MOf[1] = (Mag[1] -(-23272.7)) /13454.5
    MOf[2] = (Mag[2] -(-26122.5)) /39081.6

    MCa[0] =  1.000000*MOf[0] +0.000000*MOf[1] +0.000000*MOf[2]
    MCa[1] =  0.000000*MOf[0] +1.000000*MOf[1] +0.000000*MOf[2]
    MCa[2] =  0.000000*MOf[0] +0.000000*MOf[1] +1.000000*MOf[2]
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # Original code did not appear to normalize, and this seems to help
    MNo = sqrt(MCa[0]**2 +MCa[1]**2 +MCa[2]**2)
    MCa[0] =  MCa[0] /MNo
    MCa[1] = -MCa[1] /MNo
    MCa[2] = -MCa[2] /MNo

    # Low-Pass filter
    """
    Mf[0] =  MCa[0] *alp[0] +(Mf[0] *(1.0 -alp[0]))
    Mf[1] =  MCa[1] *alp[0] +(Mf[1] *(1.0 -alp[0]))
    Mf[2] =  MCa[2] *alp[0] +(Mf[2] *(1.0 -alp[0]))
    """
    Mf[0] =  MCa[0]
    Mf[1] =  MCa[1]
    Mf[2] =  MCa[2]

    # Pitch and roll
    pit[0] =  asin(Af[0])
    rol[0] = -asin(Af[1])
    pit[1] = pit[0] *180.0 /pi
    rol[1] = rol[0] *180.0 /pi

    # Tilt compensated magnetic sensor measurements
    Mfc[0] = Mf[0] *cos(pit[0]) +Mf[2] *sin(pit[0])
    Mfc[1] = Mf[1] *cos(rol[0]) -Mf[2] *sin(rol[0])
    hd = (atan2(-Mfc[1], Mfc[0]) *180.0) /pi
    if hd < 0:
      hd += 360

    print("pitch={0}, roll={1}, heading={2}°".format(pit[1], rol[1], hd))
    return hd

# ----------------------------------------------------------------------------
