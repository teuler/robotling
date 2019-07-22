# ----------------------------------------------------------------------------
# dio.py
#
# Basic digital pin support
# (for CircuitPython, M4 express)
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-11-25, v1
# ----------------------------------------------------------------------------
from micropython import const
from digitalio import DigitalInOut, Pull, Direction
from pulseio import PWMOut as PWMOut_

__version__ = "0.1.0.0"

PULL_UP      = const(0)
PULL_DOWN    = const(1)
MAX_DUTY     = const(65535)

# ----------------------------------------------------------------------------
class DigitalOut(object):
  """Basic digital output."""

  def __init__(self, pin, value=False):
    self._pin = DigitalInOut(pin)
    self._pin.switch_to_output(value=value)

  def deinit(self):
    self._pin.deinit()

  @property
  def value(self):
    return self._pin.value

  @value.setter
  def value(self, value):
    self._pin.value = value

  def on(self):
    self._pin.value = 1

  def off(self):
    self._pin.value = 0

# ----------------------------------------------------------------------------
class DigitalIn(object):
  """Basic digital input."""

  def __init__(self, pin, pull=None):
    self._pin = DigitalInOut(pin)
    if pull == PULL_UP:
      self._pin.switch_to_input(pull=Pull.UP)
    elif pull == PULL_DOWN:
      self._pin.switch_to_input(pull=Pull.DOWN)
    else:
      self._pin.switch_to_input()

  def deinit(self):
    self._pin.deinit()

  @property
  def value(self):
    return self._pin.value

# ----------------------------------------------------------------------------
class PWMOut(object):
  """PWM output."""

  def __init__(self, pin, freq=5000, duty=0):
    self._pID = pin
    self._pin = PWMOut_(pin, frequency=int(freq), duty_cycle=duty)

  def deinit(self):
    self._pin.deinit()

  @property
  def duty_percent(self):
    """ duty in percent
    """
    return self._pin.duty_cycle /MAX_DUTY *100

  @duty_percent.setter
  def duty_percent(self, value):
    self._pin.duty_cycle = int(min(max(0, value/100.0 *MAX_DUTY), MAX_DUTY))

  @property
  def duty(self):
    """ duty as raw value
    """
    return self._pin.duty_cycle

  @duty.setter
  def duty(self, value):
    self._pin.duty_cycle = int(value)

  @property
  def freq_Hz(self):
    """ frequency in [Hz]
    """
    return self._pin.frequency

  @freq_Hz.setter
  def freq_Hz(self, value):
    # Frequency cannot be changed unless variable frequency option is set,
    # therefore here just recreate instance with same duty cycle but new
    # frequency
    d = self._pin.duty_cycle
    self._pin.deinit()
    self._pin = PWMOut_(self._pID, frequency=int(value), duty_cycle=d)

  @property
  def max_duty(self):
    return MAX_DUTY

# ----------------------------------------------------------------------------
