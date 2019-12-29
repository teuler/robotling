# ----------------------------------------------------------------------------
# dio.py
#
# Basic digital pin support
# (for standard micropython, ESP32, as HUZZAH32 feather)
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-11-25, v1
# 2019-12-25, Note that the ESP32 Microsoft port supports only one frequency
#             for all PWM objects.
# ----------------------------------------------------------------------------
from micropython import const
from machine import Pin, PWM

__version__ = "0.1.0.0"

PULL_UP     = const(0)
PULL_DOWN   = const(1)
MAX_DUTY    = const(1023)

# ----------------------------------------------------------------------------
class DigitalOut(object):
  """Basic digital output."""

  def __init__(self, pin, value=False):
    self._pin = Pin(pin, Pin.OUT)
    self._pin.value(value)

  def deinit(self):
    self._pin = None

  @property
  def value(self):
    return self._pin.value()

  @value.setter
  def value(self, value):
    self._pin.value(value)

  def on(self):
    self._pin.value(1)

  def off(self):
    self._pin.value(0)

# ----------------------------------------------------------------------------
class DigitalIn(object):
  """Basic digital input."""

  def __init__(self, pin, pull=None):
    if pull == PULL_UP:
      self._pin = Pin(pin, Pin.IN, Pin.PULL_UP)
    elif pull == PULL_DOWN:
      self._pin = Pin(pin, Pin.IN, Pin.PULL_DOWN)
    else:
      self._pin = Pin(pin, Pin.IN)

  def deinit(self):
    self._pin = None

  @property
  def value(self):
    return self._pin.value()

# ----------------------------------------------------------------------------
class PWMOut(object):
  """PWM output."""

  def __init__(self, pin, freq=50, duty=0, verbose=False):
    self._pin = PWM(Pin(pin))
    self._pin.init(freq=freq, duty=duty)
    if verbose:
      self.__logFrequency()

  def deinit(self):
    self._pin.deinit()

  @property
  def duty_percent(self):
    """ duty in percent
    """
    return self._pin.duty() /MAX_DUTY *100

  @duty_percent.setter
  def duty_percent(self, value):
    self._pin.duty(int(min(max(0, value/100.0 *MAX_DUTY), MAX_DUTY)))

  @property
  def duty(self):
    """ duty as raw value
    """
    return self._pin.duty()

  @duty.setter
  def duty(self, value):
    self._pin.duty(int(value))

  @property
  def freq_Hz(self):
    """ frequency in [Hz]
    """
    return self._pin.freq()

  @freq_Hz.setter
  def freq_Hz(self, value):
    self._pin.freq(value)
    self.__logFrequency()

  @property
  def max_duty(self):
    return MAX_DUTY

  def __logFrequency(self):
    print("PWM frequency is {0} Hz".format(self._pin.freq()))

# ----------------------------------------------------------------------------
