# ----------------------------------------------------------------------------
# robotling_board.py
# Global definitions for robotling board.
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-13, v1
# ----------------------------------------------------------------------------
from micropython import const
from pins_huzzah32 import *
from robotling_board_version import BOARD_VER

__version__ = "0.1.0.0"

# ----------------------------------------------------------------------------
# Robotling board connections/pins
#
SCK     = GPIO5_SCK
MOSI    = GPIO18_MOSI
MISO    = GPIO19_MISO
CS_ADC  = GPIO4_A5
SPI_FRQ = const(4000000)

SCL     = GPIO22_SCL
SDA     = GPIO23_SDA
I2C_FRQ = const(100000)

A_ENAB  = GPIO26_A0
A_PHASE = GPIO14_A6
B_ENAB  = GPIO21
B_PHASE = GPIO25_A1

ENAB_5V = GPIO16_RX

RED_LED = GPIO13_LED
ADC_BAT = GPIO35_BAT

if BOARD_VER == 100:
  NEOPIX  = GPIO15_A8    # Connect Neopixel to DIO #0
  DIO0    = GPIO27_A10
  DIO1    = GPIO13_LED
  DIO2    = GPIO33_A9
  DIO3    = GPIO15_A8

elif BOARD_VER == 110:
  NEOPIX  = GPIO15_A8    # -> Neopixel connector
  DIO0    = GPIO27_A10
  DIO1    = GPIO13_LED
  DIO2    = GPIO33_A9
  DIO3    = GPIO32_A7

elif BOARD_VER == 120:
  NEOPIX  = GPIO15_A8    # -> Neopixel connector
  DIO0    = GPIO27_A10
  DIO1    = GPIO13_LED
  DIO2    = GPIO33_A9
  DIO3    = GPIO32_A7

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
