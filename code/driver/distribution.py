# ----------------------------------------------------------------------------
# distribution.py
# Class that gives access to the distribution-dependent MicroPython details.
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-21, v1
# ----------------------------------------------------------------------------
import utime
from os import uname
from micropython import const
from machine import SPI, Pin, I2C
from robotling_board_version import BOARD_VER

__version__ = "0.1.0.0"

UPY_UNKNOWN                = const(0)
UPY_ESP32                  = const(1)
UPY_ESP32_LOBO             = const(2)

# ----------------------------------------------------------------------------
class uPyDistribution(object):
  """Access to the distribution-dependent MicroPython details."""

  def __init__(self):
    # Determine implementation, set ID and properties
    self._ID         = UPY_UNKNOWN
    self._maxPWMDuty = const(4095)
    self._spi        = None
    self._i2c        = None
    self._i2cDevList = []
    self.sysInfo     = uname()
    if self.sysInfo[0] == "esp32_LoBo":
      self._ID = UPY_ESP32_LOBO
      self._maxPWMDuty = const(100)

    elif self.sysInfo[0] == "esp32":
      self._ID = UPY_ESP32
      self._maxPWMDuty = const(4095)


  @property
  def ID(self):
    return self._ID

  @property
  def maxPWMDuty(self):
    return self._maxPWMDuty

  def getSPIBus(self, freq, sc, mo, mi): #, _cs):
    if self._spi == None:
      if self._ID == UPY_ESP32_LOBO:
        self._spi = SPI(2, baudrate=freq, sck=sc, mosi=mo, miso=mi) #cs=_cs)
      elif self._ID == UPY_ESP32:
        self._spi = SPI(2)
        self._spi.init(baudrate=freq, sck=Pin(sc), mosi=Pin(mo), miso=Pin(mi))
    return self._spi

  def getI2CBus(self, _freq, scl, sda):
    if self._i2c == None:
      if self._ID == UPY_ESP32_LOBO:
        self._i2c = I2C(0, sda=Pin(sda), scl=Pin(scl), freq=_freq)
      elif self._ID == UPY_ESP32:
        self._i2c = I2C(scl=Pin(scl), sda=Pin(sda), freq=_freq)

      self._i2cDevList = self._i2c.scan()
    return self._i2c

  @property
  def i2cDevAddrList(self):
    return self._i2cDevList

# ----------------------------------------------------------------------------
uPyDistr = uPyDistribution()

# ----------------------------------------------------------------------------
if uPyDistr.ID == UPY_ESP32_LOBO:
  from machine import Neopixel as NeoPixelBase
else:
  from neopixel import NeoPixel as NeoPixelBase

class NeoPixel(object):
  """Distribution-independent NeoPixel class"""

  def __init__(self, pin, nLEDs):
    """ Requires a pin index (not object) and the number of NeoPixels
    """
    self._isLoBo = uPyDistr.ID == UPY_ESP32_LOBO
    if self._isLoBo:
      self._NPx = NeoPixelBase(Pin(pin, Pin.OUT), 1, NeoPixelBase.TYPE_RGB)
    else:
      self._NPx = NeoPixelBase(Pin(pin, Pin.OUT), 1, bpp=3)

  def set(self, rgb, iNP=0, show=False):
    """ Takes an RGB value as a tupple for the NeoPixel with the index "iNP",
        update all NeoPixels if "show"==True
    """
    if self._isLoBo:
      self._NPx.set(iNP, (rgb[0] << 16) | (rgb[1] << 8) | rgb[2], 0, 1, show)
    else:
      self._NPx[iNP] = rgb
      if show:
        self._NPx.write()

  def show(self):
    if self._isLoBo:
      self._NPx.show()
    else:
      self._NPx.write()

# ----------------------------------------------------------------------------
