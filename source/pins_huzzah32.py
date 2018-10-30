# ----------------------------------------------------------------------------
# pins_huzzah32.py
# Hardware specific pin definitions.
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-10-03, v1
# ----------------------------------------------------------------------------
from micropython import const

__version__ = "0.1.0.0"

# ----------------------------------------------------------------------------
# Adafruit Huzzah32
# (USB connector down, from the top)
#
# Left column:
GPIO23_SDA  = const(23)  # 23, I2C (SDA)
GPIO22_SCL  = const(22)  # 22, I2C (SCL)
GPIO14_A6   = const(14)  # 14, A6, ch2
GPIO32_A7   = const(32)  # 32, A7, ch1
GPIO15_A8   = const(15)  # 15, A8, ch2
GPIO33_A9   = const(33)  # 33, A9, ch1
GPIO27_A10  = const(27)  # 27, A10, ch2
GPIO12_A11  = const(12)  # 12, A11, ch2, w/pull-down, required for boot
GPIO13_LED  = const(13)  # 13, A12, ch1, w/red onboard LED

# Right column:
GPIO21      = const(21)  # 21
GPIO17_TX   = const(17)  # 17, TX (Serial1)
GPIO16_RX   = const(16)  # 16, RX (Serial1)
GPIO19_MISO = const(19)  # 19, SPI (MISO)
GPIO18_MOSI = const(18)  # 18, SPI (MOSI)
GPIO5_SCK   = const(5)   #  5, SPI (SCK)
GPIO4_A5    = const(4)   #  4, A5
GPIO36_A4   = const(36)  # 36, A4, not output-enabled!
GPIO39_A3   = const(39)  # 39, A3, not output-enabled!
GPIO34_A2   = const(34)  # 34, A2, not output-enabled!
GPIO25_A1   = const(25)  # 25, A1, DAC1
GPIO26_A0   = const(26)  # 26, A0, DAC2

# Internal:
GPIO35_BAT  = const(35)  # 35, A13, connected to VBAT

# ----------------------------------------------------------------------------
