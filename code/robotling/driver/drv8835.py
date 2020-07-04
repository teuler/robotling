# ----------------------------------------------------------------------------
# drv8835.py
# Class for Pololu dual-channel DC motor driver DRV8835
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-23, v1
# 2018-11-25, v1.1, now uses dio_*.py to access machine
# ----------------------------------------------------------------------------
import array
from micropython import const
from misc.helpers import timed_function

import robotling_board as rb
from platform.platform import platform
if platform.ID == platform.ENV_ESP32_UPY:
  import platform.esp32.dio as dio
elif platform.ID == platform.ENV_CPY_SAM51:
  import platform.m4ex.dio as dio
else:
  print("ERROR: No matching hardware libraries in `platform`.")

__version__ = "0.1.1.0"
CHIP_NAME   = "drv8835"
CHAN_COUNT  = const(2)
MODE_NONE   = const(0)
MODE_IN_IN  = const(1)
MODE_PH_EN  = const(2)
MOTOR_A     = const(0)
MOTOR_B     = const(1)

# ----------------------------------------------------------------------------
class DRV8835(object):
  """Driver for Pololu dual-channel DC motor H-bridge DRV8835."""

  def __init__(self, mode, freq, pinA_EN, pinA_PHASE, pinB_EN, pinB_PHASE):
    """ Initialises the pins that are connected to the H-bridges
    """
    # Initialize pins depending on mode
    # (Mode is set by jumper J1 on the Robotling board;
    #  w/ J1->Phase/Enable, w/o J1->IN/IN mode)
    self._mode    = MODE_NONE
    self._speed   = array.array('i', [0, 0])
    if mode == MODE_PH_EN:
      self.pinA_EN = dio.PWMOut(pinA_EN, freq=freq, channel=rb.MOTOR_A_CH)
      self.pinA_PH = dio.DigitalOut(pinA_PHASE)
      self.pinB_EN = dio.PWMOut(pinB_EN, freq=freq, channel=rb.MOTOR_B_CH)
      self.pinB_PH = dio.DigitalOut(pinB_PHASE)
      self._mode = MODE_PH_EN

    elif mode == MODE_IN_IN:
      print("IN/IN mode not implemented.")

    f = self.pinA_EN.freq_Hz/10**6
    s = "2x DC motor driver ({0:.3f} MHz)".format(f)
    print("[{0:>12}] {1:35} ({2}): {3}"
          .format(CHIP_NAME, s, __version__,
                  "ok" if self._mode != MODE_NONE else "FAILED"))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setMotorSpeed(self, speed=[0, 0]):
    """ Set speed and direction for both motors, from -100% to 100%;
        Use `None` to indicates that speed of that motor should be kept.
    """
    sp = self._speed
    if self._mode == MODE_PH_EN:
      # Calculate speeds
      spNew = speed[MOTOR_A]
      if not(spNew == None) and (spNew >= -100) and (spNew <= 100):
        sp[MOTOR_A] = spNew
      ASp = abs(int(sp[MOTOR_A]))
      spNew = speed[MOTOR_B]
      if not(spNew == None) and (spNew >= -100) and (spNew <= 100):
        sp[MOTOR_B] = spNew
      BSp = abs(int(sp[MOTOR_B]))

      # Stop motors, then change direction and set new speed
      self.pinA_EN.duty_percent = 0
      self.pinB_EN.duty_percent = 0
      self.pinA_PH.value = sp[MOTOR_A] > 0
      self.pinB_PH.value = sp[MOTOR_B] > 0
      self.pinA_EN.duty_percent = ASp
      self.pinB_EN.duty_percent = BSp

  @property
  def channelCount(self):
    return CHAN_COUNT

# ----------------------------------------------------------------------------
