# ----------------------------------------------------------------------------
# board_tinypico.py
# Hardware specific pin definitions.
#
# The MIT License (MIT)
# Copyright (c) 2020 Thomas Euler
# 2020-01-06, v1
# ----------------------------------------------------------------------------
from micropython import const

__version__ = "0.1.0.0"

# ----------------------------------------------------------------------------
# TinyPico
# (USB connector down, from the top)
#
# Left column:
D25  = const(25)  # 25, A8, ch2, DAC1
D26  = const(26)  # 26, A9, ch2, DAC2
D27  = const(27)  # 27, A7, ch2
D15  = const(15)  # 15, A3, ch2
D14  = const(14)  # 14, A6, ch2
D04  = const(4)   # 4,  A0, ch2

# Right column:
D33  = const(33)  # 33, A5, ch1
D32  = const(32)  # 32, A4, ch1
D21  = const(21)  # 21, I2C, sda
D22  = const(22)  # 21, I2C, scl
D05  = const(5)   # 5,  SPI (SS)
D18  = const(18)  # 18, SPI (SCK)
D19  = const(19)  # 19, SPI (MISO)
D23  = const(23)  # 23, SPI (MOSI)

# Alternaternative pins names
A0   = const(4)
A3   = const(15)
A4   = const(32)
A5   = const(33)
A6   = const(14)
A7   = const(27)
A8   = const(25)
A9   = const(26)
SDA  = const(21)
SCL  = const(22)
MISO = const(19)
MOSI = const(23)
SCK  = const(18)
DAC1 = const(25)
DAC2 = const(26)

# Internal:
D35  = const(35)  # 35, A13, connected to VBAT
BAT  = const(35)
CHRG = const(34)  # Battery charge
DSCL = const(12)  # APA102 Dotstar, clock
DSDT = const(2)   # APA102 Dotstar, data
DSPW = const(13)  # APA102 Dotstar, power

# ----------------------------------------------------------------------------
