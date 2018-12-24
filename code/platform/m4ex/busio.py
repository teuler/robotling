# ----------------------------------------------------------------------------
# busio.py
#
# Basic bus support
# (for CircuitPython, M4 express)
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-12-09, v1
# ----------------------------------------------------------------------------
from micropython import const
from busio import SPI, I2C

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

  def __init__(self, _freq, _scl, _sda):
    self._i2cDevList = []
    self._i2c = I2C(scl=_scl, sda=_sda, frequency=_freq)
    self._i2cDevList = self._i2c.scan()

  def deinit(self):
    self._i2c.deinit()

  @property
  def bus(self):
    return self._i2c

  @property
  def deviceAddrList(self):
    return self._i2cDevList

# ----------------------------------------------------------------------------
