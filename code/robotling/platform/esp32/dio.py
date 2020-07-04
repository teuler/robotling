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
# 2019-12-30, RMT feature eabled
# 2020-01-18, Buzzer class added
# ----------------------------------------------------------------------------
import time
from micropython import const
from machine import Pin, PWM
from esp32 import RMT

__version__     = "0.1.1.0"

PULL_UP         = const(0)
PULL_DOWN       = const(1)
MAX_DUTY        = const(1023)
RMT_MAX_CHAN    = const(7)
RMT_CLOCK_DIV   = const(80)
RMT_MAX_DUTY    = const(4000)
RMT_DUTY_SCALER = const(40)

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

  def __init__(self, pin, freq=50, duty=0, verbose=False, channel=-1):
    if channel in [i for i in range(RMT_MAX_CHAN)]:
      self._chanRMT = channel
      self._pin = RMT(channel, pin=Pin(pin), clock_div=RMT_CLOCK_DIV)
      self.__setRMTDuty(duty)
      self._pin.loop(True)
    else:
      self._chanRMT = -1
      self._pin = PWM(Pin(pin))
      self._pin.init(freq=freq, duty=duty)
    self._verbose = verbose
    if self._verbose:
      self.__logFrequency()

  def deinit(self):
    self._pin.deinit()

  @property
  def duty_percent(self):
    """ duty in percent
    """
    if self._chanRMT < 0:
      return self._pin.duty() /MAX_DUTY *100
    else:
      return self._dutyRMT /RMT_DUTY_SCALER

  @duty_percent.setter
  def duty_percent(self, value):
    if self._chanRMT < 0:
      self._pin.duty(int(min(max(0, value/100.0 *MAX_DUTY), MAX_DUTY)))
    else:
      self.__setRMTDuty(min(max(0, value/100. *RMT_MAX_DUTY), RMT_MAX_DUTY))

  @property
  def duty(self):
    """ duty as raw value
    """
    if self._chanRMT < 0:
      return self._pin.duty()
    else:
      return self._dutyRMT

  @duty.setter
  def duty(self, value):
    if self._chanRMT < 0:
      self._pin.duty(int(value))
    else:
      self.__setRMTDuty(value)

  @property
  def freq_Hz(self):
    """ frequency in [Hz]
    """
    if self._chanRMT < 0:
      return self._pin.freq()
    else:
      return self._pin.source_freq() /RMT_CLOCK_DIV

  @freq_Hz.setter
  def freq_Hz(self, value):
    if self._chanRMT < 0:
      self._pin.freq(value)
    else:
      if value == 0:
        self._pin.loop(False)
      else:
        self._pin.loop(True)
        d2 = int((self._pin.source_freq() /RMT_CLOCK_DIV) /value //2)
        self._pin.write_pulses((d2, d2))
    if self._verbose:
      self.__logFrequency()

  @property
  def max_duty(self):
    if self._chanRMT < 0:
      return MAX_DUTY
    else:
      return RMT_MAX_DUTY

  def __logFrequency(self):
    print("PWM frequency is {0:.1f} kHz".format(self.freq_Hz/1000))

  def __setRMTDuty(self, value):
    self._dutyRMT = int(min(max(1, value), RMT_MAX_DUTY))
    self._pin.write_pulses((self._dutyRMT, RMT_MAX_DUTY -self._dutyRMT))

# ----------------------------------------------------------------------------
class Buzzer(object):
  """Buzzer."""

  def __init__(self, pin, channel):
    self._buzz = PWMOut(pin, channel=channel)
    self._buzz.duty_percent = 0
    self._freq = 0
    self._mute = False

  @property
  def freq_Hz(self):
    return self._freq

  @freq_Hz.setter
  def freq_Hz(self, value):
    if value >= 0:
      self._buzz.freq_Hz = value
      self._freq = value

  @property
  def mute(self):
    return self._mute

  @mute.setter
  def mute(self, value):
    self._mute = value != 0

  def beep(self, freq=440):
    if not self._mute:
      self.freq_Hz = freq
      time.sleep_ms(100)
      self.freq_Hz = 0

  def warn(self):
    if not self._mute:
      self.freq_Hz = 110
      time.sleep_ms(250)
      self.freq_Hz = 0

  def deinit(self):
    self._buzz.deinit()

# ----------------------------------------------------------------------------
