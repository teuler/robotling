# ----------------------------------------------------------------------------
# camera_thermal.py
# ...
#
# The MIT License (MIT)
# Copyright (c) 2019 Thomas Euler
# 2019-08-01, v1
# 2019-12-15, v1.1
#
# Known issues with `blob`:
# - if more than one valid blobs are returned, the entries except for the
#   first seem not to contain vaild data
# - only mode=0 seems not to crash the ESP32 ...
# - the "probability" for a blob can exceed 1.0 (???)
#
# ----------------------------------------------------------------------------
import blob
from sensors.sensor_base import CameraBase

__version__ = "0.1.1.0"

# ----------------------------------------------------------------------------
class Camera(CameraBase):
  """Camera class for the AMG88XX GRID-Eye IR 8x8 thermal camera."""

  def __init__(self, driver):
    super().__init__(driver)
    self._type = "thermal camera (8x8 pixels)"
    if driver.isReady:
      # Initialize
      self._dxy = self.resolution
      self._params = None
      self._img64x1 = []
      self._blobList = []

    print("[{0:>12}] {1:35} ({2}): {3}"
          .format(driver.name, self._type, __version__,
                  "ok" if driver._isReady else "FAILED"))

  def detectBlobs(self, filter=0, nsd=0.7):
    """ Acquire image and detect blobs, using filter mode `filter` (with
        0=no filter, 1=n/a, 2=sharpen) and threshold for blob detection
        of `nsd` (in number of standard deviations)
    """
    self._img64x1 = []
    self._blobList = []
    if self._driver.isReady:
      self._params = (filter, nsd)
      self._img64x1 = list(self._driver.pixels_64x1)
      #print(self._img64x1)
      self._blobList = blob.detect(self._img64x1, self._dxy, self._params)
      #print(self._blobList)

  @property
  def blobsRaw(self):
    """ Return raw blob list
    """
    return self._blobList

  @property
  def imageLinear(self):
    """ Return current image as a 1D list
    """
    return self._img64x1

  def getBestBlob(self, minArea, minP):
    """ Return the (corrected) position of the best blob that meets the
        given criteria: minimal area `minArea` and probabilty >= `minP`
        (check known issues with `blob`; the "probability" can exceed 1.0 ...)
    """
    if len(self._blobList) > 0:
      area = self._blobList[0][0]
      prob = self._blobList[0][2]
      if area >= minArea and prob >= minP:
        # Return coordinates of that blob
        # (Note that the coordinates are adjusted here to match the view
        #  of the robot with the _AMG88XX mounted with the cable connector up)
        return (self._blobList[0][3] -self._dxy[0]/2,
                self._blobList[0][4] -self._dxy[1]/2)
    else:
      return None

# ----------------------------------------------------------------------------
