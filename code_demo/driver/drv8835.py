# ----------------------------------------------------------------------------
# drv8835.py
# Class for Pololu dual-channel DC motor driver DRV8835
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-23, v1
# ----------------------------------------------------------------------------
import array
from micropython import const
from machine import Pin, PWM
import driver.distribution as distr
from driver.helpers import timed_function

__version__ = "0.1.0.0"
CHIP_NAME   = "drv8835"
CHAN_COUNT  = const(2)
MODE_NONE   = const(0)
MODE_IN_IN  = const(1)
MODE_PH_EN  = const(2)
MOTOR_A     = const(0)
MOTOR_B     = const(1)
PWN_FRQ     = const(50000)

# ----------------------------------------------------------------------------
class DRV8835(object):
  """Driver for Pololu dual-channel DC motor H-bridge DRV8835."""

  def __init__(self, mode, pinA_EN, pinA_PHASE, pinB_EN, pinB_PHASE):
    """ Initialises the pins that are connected to the H-bridges
    """
    # Initialize pins depending on mode
    # (Mode is set by jumper J1 on the Robotling board;
    #  w/ J1->Phase/Enable, w/o J1->IN/IN mode)
    self._mode    = MODE_NONE
    self._speed   = array.array('i', [0, 0])
    self.maxSpeed = distr.uPyDistr.maxPWMDuty
    if mode == MODE_PH_EN:
      self.pinA_EN = PWM(Pin(pinA_EN))
      self.pinA_EN.init(freq=PWN_FRQ, duty=0)
      self.pinA_PH = Pin(pinA_PHASE, Pin.OUT)
      self.pinB_EN = PWM(Pin(pinB_EN))
      self.pinB_EN.init(freq=PWN_FRQ, duty=0)
      self.pinB_EN.duty(0)
      self.pinB_PH = Pin(pinB_PHASE, Pin.OUT)
      self._mode = MODE_PH_EN
    elif mode == MODE_IN_IN:
      print("IN/IN mode not yet implemented.")

    print("[{0:7}] {1:27}: {2}"
          .format(CHIP_NAME, "2-channel DC motor driver",
                  "ok" if self._mode != MODE_NONE else "FAILED"))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setMotorSpeed(self, speed=[0, 0]):
    """ Set speed and direction for both motors, from -100% to 100%;
        Use 'None' to indicates that speed of that motor should be kept.
    """
    sp = self._speed
    ms = self.maxSpeed
    if self._mode == MODE_PH_EN:
      # Cache pins
      AEn = self.pinA_EN.duty
      APh = self.pinA_PH.value
      BEn = self.pinB_EN.duty
      BPh = self.pinB_PH.value

      # Calculate speeds
      spNew = speed[MOTOR_A]
      if not(spNew == None) and (spNew >= -100) and (spNew <= 100):
        sp[MOTOR_A] = spNew
      ASp = abs(int(sp[MOTOR_A]/100.0 *ms))
      spNew = speed[MOTOR_B]
      if not(spNew == None) and (spNew >= -100) and (spNew <= 100):
        sp[MOTOR_B] = spNew
      BSp = abs(int(sp[MOTOR_B]/100.0 *ms))

      # Stop motors, then change direction and set new speed
      AEn(0)
      BEn(0)
      APh(sp[MOTOR_A] > 0)
      BPh(sp[MOTOR_B] > 0)
      AEn(ASp)
      BEn(BSp)

  @property
  def channelCount(self):
    return CHAN_COUNT

# ----------------------------------------------------------------------------
