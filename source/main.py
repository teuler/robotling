# ----------------------------------------------------------------------------
# main.py
# Main program; is automatically executed after reboot.
#
# Example code for a "hijacked" HexBug. Uses the IR distance sensor to
# avoid obstacles and cliffs simply by checking if the distance measured is
# within the range expected for the surface in front of the robot (~ 6 cms).
# If a shorter or farer distance is measured, the robot turns in a random
# direction until it detects the ground again. To cover the ground in front
# of the robot, the IR sensor is moved back and forth sideways and the
# average of the measured distances is used for making the obstacle/ground/
# cliff decision.
# In parallel, all motors are stopped and the NeoPixel turns from green to
# violet dif robot is tilted (e.g. falls on the side); for this, pitch/roll
# provided by the compass (time-filtered) are checked.
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-13, first release.
# 2018-10-29, use pitch/roll to check if robot is tilted.
#
# ----------------------------------------------------------------------------
import array
import machine
import time
import random
from micropython import const, mem_info
from robotling import Robotling
from misc.helpers import TemporalFilter
import robotling_board as rboard

from driver.helpers import timed_function

import driver.drv8835 as drv8835
from motors.dc_motor import DCMotor
from motors.servo import Servo
from sensors.sharp_ir_distance import SharpIRDistSensor_GP2Y0A41SK0F

PR_MAX_ANGLE     = const(20)
MAX_IR_SCAN_POS  = const(3)

SPEED_WALK       = const(-12)
SPEED_TURN       = const(5)
SPEED_SCAN       = const(10)

# ----------------------------------------------------------------------------
class HexBug(Robotling):
  """Hijacked-HexBug class"""

  def __init__(self):
    super().__init__()
    # Add the servo that moves the IR distance sensor up and down
    self.ServoDistSensor = Servo(rboard.DIO0, us_range=[500, 1300],
                                 ang_range=[-30, 45])

    # Add IR distance sensor and make sure that for speed reasons only the
    # connected sensor is updated
    self.SensorDistA = SharpIRDistSensor_GP2Y0A41SK0F(self._MCP3208, 0)
    self._MCP3208.channelMask = 0x01

    # Add motors
    self.MotorWalk = DCMotor(self._motorDriver, drv8835.MOTOR_A)
    self.MotorTurn = DCMotor(self._motorDriver, drv8835.MOTOR_B)

    # Flag that indicates when the robot should stop moving
    self.onHold = False
    self.PitchFilter = TemporalFilter(10, "f", 6)
    self.RollFilter  = TemporalFilter(10, "f", 6)

    # Define scan positions to cover the ground before the robot. Currently,
    # the time the motor is running (in [s]) is used to define angular
    # position
    self._distData = array.array("f", [0] *MAX_IR_SCAN_POS)
    self._scanPos  = [-0.25, 0.55, -0.25]


  def stopOnTilt(self):
    """ Callback for robotling timer:
        Stop motors if robot is tilted (e.g. falls on the side) by checking
        pitch/roll provided by the compass; changes also status of NeoPixel
        accordingly and "onHold" property of HexBox instance
    """
    epr = r.Compass.pitch_roll()
    pAv = self.PitchFilter.mean(epr[1])
    rAv = self.RollFilter.mean(epr[2])
    self.onHold = (abs(pAv) > PR_MAX_ANGLE) or (abs(rAv) > PR_MAX_ANGLE)
    if self.onHold:
      # Stop motors and change NeoPixel to lilac
      self._NPx_mask = 0x05
      self.MotorTurn.speed = 0
      self.MotorWalk.speed = 0
    else:
      # Change NeoPixel back to green
      self._NPx_mask = 0x02


  def scanForObstacleOrCliff(self):
    """ Acquires distance data at the scan positions, which are currently
        given in motor run time (in [s]). Returns True if obstacle or cliff
    """
    oc = False
    for iPos, Pos in enumerate(self._scanPos):
      self.MotorTurn.speed = SPEED_SCAN *(-1,1)[Pos < 0]
      time.sleep(abs(Pos))
      self.MotorTurn.speed = 0
      time.sleep(0.01)
      d = self.SensorDistA.dist_cm
      self._distData[iPos] = d
      oc = oc or ((d < 7) or (d > 12))
    return oc

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getDist(self, angle=0, trials=1):
    """ Test function to determine the relevant IR distances.
        Moves IR distance sensor to "angle" and measures/prints distance
        "trial" times.
    """
    self.ServoDistSensor.angle = angle
    time.sleep(0.2)
    for i in range(trials):
      r.update()
      print("{0} cm".format(self.SensorDistA.dist_cm))
      time.sleep(0 if trials <= 1 else 0.25)


# ----------------------------------------------------------------------------
def main():
  # Init some variables
  onObstOrCliff = False

  # Angle the IR sensor towards floor in front
  r.ServoDistSensor.angle = -28

  # Start timer, which acquires sensor readings, updates the NeoPixel and
  # in the callback, checks if the robot is not tilted
  r.startTimer(period=50, callback=r.stopOnTilt)

  # Loop ...
  print("Entering loop ...")
  try:
    try:
      while True:
        r.loop_start()

        if r.onHold:
          # Some problem was detected (e.g. robot tilted etc.), skip all
          # the following code
          continue

        # Check if obstacle or cliff
        onObstOrCliff = r.scanForObstacleOrCliff()

        # Act on sensor data ...
        if not onObstOrCliff:
          # No reason to stop, therefore walk
          r.MotorWalk.speed = SPEED_WALK

        else:
          # Stop, turn in a random direction to check (in the next loop)
          # again for obstacles
          r.MotorWalk.speed = 0
          time.sleep(0.2)
          dir = [-1,1][random.randint(0,1)]
          r.MotorTurn.speed = SPEED_TURN *dir
          time.sleep(2.0)
          r.MotorTurn.speed = 0

        if r._lp_t_count % 5:
          r.print_report()

    except KeyboardInterrupt:
      print("Loop stopped.")

  finally:
    # Make sure that robot is powered down and timer is stopped
    r.stopTimer()
    r.powerDown()
    r.print_report()


# Create instance of HexBug, derived from the Robotling class
r = HexBug()

# Call main
if __name__ == "__main__":
  main()

# ----------------------------------------------------------------------------
