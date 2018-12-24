# ----------------------------------------------------------------------------
# aio.py
#
# Basic analog pin support
# (for standard micropython, ESP32, as HUZZAH32 feather)
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-11-25, v1
# ----------------------------------------------------------------------------
from micropython import const
from machine import Pin, ADC

__version__ = "0.1.0.0"

ATTN_0DB    = const(0)  # no attenuation, 0..1V
ATTN_2_5DB  = const(1)  #  2.5 dB
ATTN_6DB    = const(2)  #  6.0 dB
ATTN_11DB   = const(3)  # 11.0 dB, 0..3.3V (full range)

WIDTH_9BIT  = const(0)
WIDTH_10BIT = const(1)
WIDTH_11BIT = const(2)
WIDTH_12BIT = const(3)

ATTN  = bytearray([ADC.ATTN_0DB, ADC.ATTN_2_5DB, ADC.ATTN_6DB, ADC.ATTN_11DB])
WIDTH = bytearray([ADC.WIDTH_9BIT, ADC.WIDTH_10BIT, ADC.WIDTH_11BIT,
                   ADC.WIDTH_12BIT])

# ----------------------------------------------------------------------------
class AnalogIn(object):
  """Basic analog input."""

  def __init__(self, pin, attn=ATTN_11DB, width=WIDTH_12BIT):
    self._pin = ADC(Pin(pin))
    self._pin.atten(ATTN[attn])
    self._pin.width(WIDTH[width])
    self._max_adc = 2**(9 +WIDTH[width]) -1

  def deinit(self):
    self._pin = None

  @property
  def value(self):
    return self._pin.read()

  @property
  def max_adc(self):
    return self._max_adc

# ----------------------------------------------------------------------------
