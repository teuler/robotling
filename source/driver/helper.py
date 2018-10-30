# ----------------------------------------------------------------------------
# helper.py
# Helper functions.
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-21, v1
# ----------------------------------------------------------------------------
import utime

# ----------------------------------------------------------------------------
def timed_function(f, *args, **kwargs):
  myname = str(f).split(' ')[1]
  def new_func(*args, **kwargs):
    t = utime.ticks_us()
    result = f(*args, **kwargs)
    delta = utime.ticks_diff(utime.ticks_us(), t)
    print('Function {} Time = {:6.3f}ms'.format(myname, delta/1000))
    return result
  return new_func

# ----------------------------------------------------------------------------
