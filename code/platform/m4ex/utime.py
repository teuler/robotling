# ----------------------------------------------------------------------------
# utime.py
#
# Very basic time support analog to the MicroPython implementation
# (for CircuitPython, M4 express)
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-12-22, v1
# ----------------------------------------------------------------------------
import time as time_

__version__ = "0.1.0.0"

# ----------------------------------------------------------------------------
def ticks_diff(ticks1, ticks2):
  return ticks1 -ticks2

def ticks_us():
  return int(time_.monotonic() *1000000)
# ----------------------------------------------------------------------------
