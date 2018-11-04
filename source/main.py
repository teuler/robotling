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
# 2018-11-03, some cleaning up and commenting of the code
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
import driver.drv8835 as drv8835
from driver.helpers import timed_function
from motors.dc_motor import DCMotor
from motors.servo import Servo
from sensors.sharp_ir_distance import SharpIRDistSensor_GP2Y0A41SK0F

# Tilt-sensing
PIRO_MAX_ANGLE   = const(25)   # Maximal tilt (i.e. pitch/roll) allowed
                               # .. before robot responds
# Obstacle/cliff detection
MAX_IR_SCAN_POS  = const(3)    # Scan positions to check for obstacles/cliffs
DIST_OBST_CM     = const(7)    # Lower distances are considered obstacles
DIST_CLIFF_CM    = const(13)   # Farer distances are considered cliffs
MIN_DIST_SERVO   = const(-30)  # Limits of servo that holds the arm with the
MAX_DIST_SERVO   = const(45)   # .. IR distance sensor in [°]
SCAN_DIST_SERVO  = const(-25)  # Angle of IR distance sensor arm

# Period of timer that keeps sensor values updated, the NeoPixel pulsing,
# and checks for tilt (in [ms])
TM_PERIOD        = const(50)

# Default motor speeds ..
SPEED_WALK       = const(-12)  # .. for walking forwards
SPEED_TURN       = const(5)    # .. for turning head when changing direction
SPEED_SCAN       = const(10)   # .. for turning head when scanning

# Robot states
STATE_IDLE       = const(0)
STATE_WALKING    = const(1)
STATE_LOOKING    = const(2)
STATE_ON_HOLD    = const(3)
STATE_OBSTACLE   = const(4)
STATE_CLIFF      = const(5)

# NeoPixel colors (r,g,b) for the different states
STATE_COLORS     = bytearray((
                   10,10,10,   # STATE_IDLE
                   20,70,0,    # STATE_WALKING
                   40,30,0,    # STATE_LOOKING
                   20,00,50,   # STATE_ON_HOLD
                   90,30,0,    # STATE_OBSTACLE
                   90,0,30))   # STATE_CLIFF

# ----------------------------------------------------------------------------
class HexBug(Robotling):
  """Hijacked-HexBug class"""

  def __init__(self, devices):
    super().__init__(devices)
    # Add the servo that moves the IR distance sensor up and down
    self.ServoDistSensor = Servo(rboard.DIO0, us_range=[500, 1300],
                                 ang_range=[MIN_DIST_SERVO, MAX_DIST_SERVO])

    # Add IR distance sensor and make sure that for speed reasons only the
    # connected sensor is updated
    self.SensorDistA = SharpIRDistSensor_GP2Y0A41SK0F(self._MCP3208, 0)
    self._MCP3208.channelMask = 0x01

    # Add motors
    self.MotorWalk = DCMotor(self._motorDriver, drv8835.MOTOR_A)
    self.MotorTurn = DCMotor(self._motorDriver, drv8835.MOTOR_B)

    # Flag that indicates when the robot should stop moving
    self.onHold = False
    self.PitchFilter = TemporalFilter(8, "f", 6)
    self.RollFilter  = TemporalFilter(8, "f", 6)

    # Define scan positions to cover the ground before the robot. Currently,
    # the time the motor is running (in [s]) is used to define angular
    # position
    self._distData = array.array("f", [0] *MAX_IR_SCAN_POS)
    self._scanPos  = [-250, 550, -350]
    self.onTrouble = False

    # Starting state
    self.state = STATE_IDLE


  def stopOnTilt(self):
    """ Callback for robotling timer:
        Stop motors if robot is tilted (e.g. falls on the side) by checking
        pitch/roll provided by the compass; changes also color of NeoPixel
        depending on the robot's state
    """
    epr = r.Compass.getPitchRoll()
    pAv = self.PitchFilter.mean(epr[1])
    rAv = self.RollFilter.mean(epr[2])
    self.onHold = (abs(pAv) > PIRO_MAX_ANGLE) or (abs(rAv) > PIRO_MAX_ANGLE)
    if self.onHold:
      # Stop motors
      self.MotorTurn.speed = 0
      self.MotorWalk.speed = 0
      self.ServoDistSensor.off()
      self.state = STATE_ON_HOLD

    # Change NeoPixel according to state
    i = self.state *3
    self.startPulseNeoPixel(STATE_COLORS[i:i+3])


  def scanForObstacleOrCliff(self):
    """ Acquires distance data at the scan positions, currently given in motor
        run time (in [s]). Returns -1=obstacle, 1=cliff, and 0=none.
    """
    o = False
    c = False
    for iPos, Pos in enumerate(self._scanPos):
      self.MotorTurn.speed = SPEED_SCAN *(-1,1)[Pos < 0]
      time.sleep_ms(abs(Pos))
      self.MotorTurn.speed = 0
      time.sleep_ms(10)
      d = self.SensorDistA.dist_cm
      self._distData[iPos] = d
      o = o or (d < DIST_OBST_CM)
      c = c or (d > DIST_CLIFF_CM)
    #print(o,c,self._distData)
    return 1 if c else -1 if o else 0


  def lookAround(self):
    """ Make an appearance of "looking around"
    """
    # Stop all motors and change state
    self.MotorWalk.speed = 0
    self.MotorTurn.speed = 0
    prevState  = self.state
    self.state = STATE_LOOKING

    # Move head and IR distance sensor at random, as if looking around
    nSacc = random.randint(8,20)
    yaw   = 0
    pit   = SCAN_DIST_SERVO
    try:
      for i in range(nSacc):
        if r.onHold:
          break
        dYaw = random.randint(-800,800)
        yaw += dYaw
        dir  = -1 if dYaw < 0 else 1
        pit += random.randint(-10,15)
        pit  = min(max(0, pit), MAX_DIST_SERVO)
        self.ServoDistSensor.angle = pit
        self.MotorTurn.speed = SPEED_TURN *dir
        time.sleep_ms(abs(dYaw))
        self.MotorTurn.speed = 0
        time.sleep_ms(random.randint(0,500))
    finally:
      # Stop head movement, if any, move the IR sensor back into scan
      # position and change back state
      self.MotorTurn.speed = 0
      self.ServoDistSensor.angle = SCAN_DIST_SERVO
      self.state = prevState

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getDist(self, angle=0, trials=1):
    """ Test function to determine the relevant IR distances.
        Moves IR distance sensor to "angle" and measures/prints distance
        "trial" times.
    """
    self.ServoDistSensor.angle = angle
    time.sleep_ms(200)
    for i in range(trials):
      r.update()
      print("{0} cm".format(self.SensorDistA.dist_cm))
      time.sleep_ms(0 if trials <= 1 else 250)


# ----------------------------------------------------------------------------
def main():
  # Angle the IR sensor towards floor in front
  r.ServoDistSensor.angle = SCAN_DIST_SERVO

  # Start timer, which acquires sensor readings, updates the NeoPixel and
  # in the callback, checks if the robot is not tilted
  r.startTimer(period=TM_PERIOD, callback=r.stopOnTilt)

  # Loop ...
  print("Entering loop ...")
  try:
    try:
      lastDir = 0

      while True:
        r.loop_start()

        if r.onHold:
          # Some problem was detected (e.g. robot tilted etc.), skip all
          # the following code
          lastDir = 0
          continue

        # Sometines just look around
        if random.randint(0,15) < 2:
          r.lookAround()
          continue

        """
        print("{0:.1f}°".format(r.Compass.getHeading()))
        """

        # Check if obstacle or cliff
        r.onTrouble = r.scanForObstacleOrCliff()

        # Act on sensor data ...
        if r.onTrouble == 0:
          # No reason to stop, therefore walk
          r.state = STATE_WALKING
          r.MotorWalk.speed = SPEED_WALK

        elif r.onTrouble < 0:
          # Obstacle detected -> Stop, turn in a random direction to check
          # (in the next spin) again for obstacles
          r.state = STATE_OBSTACLE
          r.MotorWalk.speed = 0
          time.sleep_ms(200)
          if lastDir == 0:
            dir = [-1,1][random.randint(0,1)]
            lastDir = dir
          else:
            dir = lastDir
          r.MotorTurn.speed = SPEED_TURN *dir
          time.sleep_ms(1500)
          r.MotorTurn.speed = 0

        else:
          # Cliff detected -> Stop, walk back a tad, turn in a random
          # direction to check (in the next spin) again for obstacles
          r.state = STATE_CLIFF
          r.MotorWalk.speed = 0
          time.sleep_ms(200)
          r.MotorWalk.speed = -SPEED_WALK
          time.sleep_ms(1000)
          r.MotorWalk.speed = 0
          if lastDir == 0:
            dir = [-1,1][random.randint(0,1)]
            lastDir = dir
          else:
            dir = lastDir
          dir = [-1,1][random.randint(0,1)]
          r.MotorTurn.speed = SPEED_TURN *dir
          time.sleep_ms(2500)
          r.MotorTurn.speed = 0

    except KeyboardInterrupt:
      print("Loop stopped.")

  finally:
    # Make sure that robot is powered down and timer is stopped
    r.stopTimer()
    r.ServoDistSensor.off()
    r.powerDown()
    r.print_report()


# Create instance of HexBug, derived from the Robotling class
r  = HexBug(["lsm303"])
#r = HexBug(["compass_cmps12"])

# Call main
if __name__ == "__main__":
  main()

"""
try:
  while True:

    print("{0:.1f}°".format(r.Compass.getHeading()))
    _, pitch, roll = r.Compass.getPitchRoll()
    print("pitch={0:.1f}°, roll={1:.1f}°".format(pitch, roll))

    _, head, pitch, roll = r.Compass.getHeading3D()
    print("heading={0:.1f}°, pitch={1:.1f}°, roll={2:.1f}°"
          .format(head, pitch, roll))
    time.sleep_ms(1000)
except KeyboardInterrupt:
  print("Loop stopped.")
"""


# ----------------------------------------------------------------------------
