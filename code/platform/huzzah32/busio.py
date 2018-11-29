# ----------------------------------------------------------------------------
# busio.py
#
# Basic bus support
# (for standard micropython, ESP32, as HUZZAH32 feather)
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-21, v1
# ----------------------------------------------------------------------------
from micropython import const
from machine import SPI, Pin, I2C
from robotling_board_version import BOARD_VER

__version__ = "0.1.0.0"

# ----------------------------------------------------------------------------
class SPIBus(object):
  """SPI bus access."""

  def __init__(self, freq, sc, mo, mi):
    self._spi = SPI(2)
    self._spi.init(baudrate=freq, sck=Pin(sc), mosi=Pin(mo), miso=Pin(mi))

  @property
  def bus(self):
    return self._spi

# ----------------------------------------------------------------------------
class I2CBus(object):
  """I2C bus access."""

  def __init__(self, _freq, scl, sda):
    self._i2cDevList = []
    self._i2c = I2C(scl=Pin(scl), sda=Pin(sda), freq=_freq)
    self._i2cDevList = self._i2c.scan()

  @property
  def bus(self):
    return self._i2c

  @property
  def deviceAddrList(self):
    return self._i2cDevList

# ----------------------------------------------------------------------------
