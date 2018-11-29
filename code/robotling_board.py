# ----------------------------------------------------------------------------
# robotling_board.py
# Global definitions for robotling board.
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-13, v1
# ----------------------------------------------------------------------------
from micropython import const
from robotling_board_version import BOARD_VER
from platform.platform import platform

__version__ = "0.1.0.0"

# ----------------------------------------------------------------------------
# Robotling board connections/pins
#
if platform.ID == platform.ENV_ESP32_UPY:
  import platform.huzzah32.board as board

  SCK     = board.SCK
  MOSI    = board.MOSI
  MISO    = board.MISO
  CS_ADC  = board.D4
  SPI_FRQ = const(4000000)

  SCL     = board.SCL
  SDA     = board.SDA
  I2C_FRQ = const(100000)

  A_ENAB  = board.D26
  A_PHASE = board.D14
  B_ENAB  = board.D21
  B_PHASE = board.D25

  ENAB_5V = board.D16

  RED_LED = board.LED
  ADC_BAT = board.BAT

  if BOARD_VER == 100:
    NEOPIX  = board.D15    # Connect Neopixel to DIO #0
    DIO0    = board.D27
    DIO1    = board.LED
    DIO2    = board.D33
    DIO3    = board.D15

  elif BOARD_VER >= 110:
    NEOPIX  = board.D15    # -> Neopixel connector
    DIO0    = board.D27
    DIO1    = board.LED
    DIO2    = board.D33
    DIO3    = board.D32

elif platform.ID == platform.ENV_CPY_SAM51:
  import board
  # TODO:
  # ***********************
  # ***********************
  # ***********************


# ----------------------------------------------------------------------------
# The battery is connected to the pin via a voltage divider (1/2), and thus
# an effective voltage range of up to 7.8V (ATTN_11DB, 3.9V); the resolution
# is 12 bit (WITDH_12BIT, 4096):
# V = adc /4096 *2 *3.9 *0.901919 = 0.001717522
# (x2 because of voltage divider, x3.9 for selected range (ADC.ATTN_11DB)
#  and x0.901919 as measured correction factor)
BAT_N_PER_V   = 0.001717522

# ----------------------------------------------------------------------------
# Error codes
#
RBL_OK                      = const(0)
RBL_ERR_DEVICE_NOT_READY    = const(-1)
RBL_ERR_SPI                 = const(-2)
# ...

# ----------------------------------------------------------------------------
