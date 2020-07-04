# ----------------------------------------------------------------------------
# board_huzzah.py
# Hardware specific pin definitions.
#
# The MIT License (MIT)
# Copyright (c) 2018-2020 Thomas Euler
# 2018-10-03, v1
# ----------------------------------------------------------------------------
from micropython import const

__version__ = "0.1.0.0"

# ----------------------------------------------------------------------------
# Adafruit Huzzah32
# (USB connector down, from the top)
#
# Left column:
D23  = const(23)  # 23, I2C (SDA)
D22  = const(22)  # 22, I2C (SCL)
D14  = const(14)  # 14, A6, ch2
D32  = const(32)  # 32, A7, ch1
D15  = const(15)  # 15, A8, ch2
D33  = const(33)  # 33, A9, ch1
D27  = const(27)  # 27, A10, ch2
D12  = const(12)  # 12, A11, ch2, w/pull-down, required for boot
D13  = const(13)  # 13, A12, ch1, w/red onboard LED

# Right column:
D21  = const(21)  # 21
D17  = const(17)  # 17, TX (Serial1)
D16  = const(16)  # 16, RX (Serial1)
D19  = const(19)  # 19, SPI (MISO)
D18  = const(18)  # 18, SPI (MOSI)
D5   = const(5)   #  5, SPI (SCK)
D4   = const(4)   #  4, A5
D36  = const(36)  # 36, A4, not output-enabled!
D39  = const(39)  # 39, A3, not output-enabled!
D34  = const(34)  # 34, A2, not output-enabled!
D25  = const(25)  # 25, A1, DAC1
D26  = const(26)  # 26, A0, DAC2

# Alternaternative pins names
SDA  = const(23)  #
SCL  = const(22)  #
A0   = const(26)
A1   = const(25)
A2   = const(34)
A3   = const(39)
A4   = const(36)
A5   = const(4)
A6   = const(14)  # ch2
A7   = const(32)  # ch1
A8   = const(15)  # ch2
A9   = const(33)  # ch1
A10  = const(27)  # ch2
A11  = const(12)  # ch2
LED  = const(13)  # red onboard LED
TX   = const(17)  # Serial1
RX   = const(16)  # Serial1
MISO = const(19)
MOSI = const(18)
SCK  = const(5)
DAC1 = const(25)
DAC2 = const(26)

# Internal:
D35  = const(35)  # 35, A13, connected to VBAT
BAT  = const(35)

# ----------------------------------------------------------------------------
