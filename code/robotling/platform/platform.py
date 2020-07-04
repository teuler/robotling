# ----------------------------------------------------------------------------
# platform.py
# Class that determines board and MicroPython distribution
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-21, v1
# ----------------------------------------------------------------------------
from os import uname
from micropython import const

__version__ = "0.1.0.0"

# ----------------------------------------------------------------------------
class Platform(object):
  """Board type and MicroPython distribution."""

  ENV_UNKNOWN        = const(0)
  ENV_ESP32_UPY      = const(1)
  ENV_ESP32_UPY_LOBO = const(2)
  ENV_ESP32_TINYPICO = const(3)
  ENV_CPY_SAM51      = const(4)

  def __init__(self):
    # Determine distribution, board type and GUID
    self._distID    = ENV_UNKNOWN
    self.sysInfo    = uname()

    if self.sysInfo[0] == "esp32":
      if self.sysInfo[4].upper().find("TINYPICO") >= 0:
        self._envID = ENV_ESP32_TINYPICO
      else:
        self._envID = ENV_ESP32_UPY
    if self.sysInfo[0] == "esp32_LoBo":
      self._envID = ENV_ESP32_UPY_LOBO
    if self.sysInfo[0] == "samd51":
      self._envID = ENV_CPY_SAM51

    try:
      from machine import unique_id
      from binascii import hexlify
      self._boardGUID = b'robotling_' +hexlify(unique_id())
    except ImportError:
      self._boardGUID = b'robotling_n/a'

  @property
  def ID(self):
    return self._envID

  @ID.setter
  def ID(self, value):
    self._envID = value

  @property
  def GUID(self):
    return self._boardGUID

# ----------------------------------------------------------------------------
platform = Platform()

# ----------------------------------------------------------------------------
