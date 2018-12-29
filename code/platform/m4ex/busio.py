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
    self._spi = SPI(sc, mo, mi)
    if not self._spi.try_lock():
      print("ERROR: busio.SPIBus: no lock for configure()")
    else:
      try:
        self._spi.configure(baudrate=freq)
      finally:
        self._spi.unlock()

  @property
  def bus(self):
    return self._spi

  def write_readinto(self, wbuf, rbuf):
    if self._spi.try_lock():
      try:
        self._spi.write_readinto(wbuf, rbuf)
      finally:
        self._spi.unlock()

# ----------------------------------------------------------------------------
class I2CBus(object):
  """I2C bus access."""

  def __init__(self, _freq, _scl, _sda):
    self._i2cDevList = []
    self._i2c = I2C(scl=_scl, sda=_sda, frequency=_freq)
    if not self._i2c.try_lock():
      print("ERROR: busio.I2CBus: no lock for scan()")
    else:
      try:
        self._i2cDevList = self._i2c.scan()
      finally:
        self._i2c.unlock()

  def deinit(self):
    self._i2c.deinit()

  @property
  def bus(self):
    return self._i2c

  @property
  def deviceAddrList(self):
    return self._i2cDevList

  def writeto(self, addr, buf, stop_=True):
    if self._i2c.try_lock():
      try:
        self._i2c.writeto(addr, buf, stop=stop_)
      finally:
        self._i2c.unlock()

  def readfrom_into(self, addr, buf):
    if self._i2c.try_lock():
      try:
        self._i2c.readfrom_into(addr, buf)
      finally:
        self._i2c.unlock()

# ----------------------------------------------------------------------------
