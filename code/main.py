# ----------------------------------------------------------------------------
# main.py
# Main program; is automatically executed after reboot.
#
# For decription, see `hexbug.py`
#
# The MIT License (MIT)
# Copyright (c) 2019 Thomas Euler
# 2018-12-22, reorganised into a module with the class `Hexbug` and a simpler
#             main program file (`main.py`). All hardware-related settings
#             moved to separate file (`hexbug_config-py`)
# 2018-12-28, adapted to using the new `spin_ms()` function to keep the
#             robotling board updated; does not require a Timer anymore.
#             For details, see `robotling.py`.
# 2019-04-07, added new "behaviour" (take a nap)
# ----------------------------------------------------------------------------
from hexbug import *

# ----------------------------------------------------------------------------
def main():
  # Setup the robot's spin function
  r.spin_ms(period_ms=TM_PERIOD, callback=r.housekeeper)

  # Angle the IR sensor towards floor in front
  r.ServoRangingSensor.angle = SCAN_DIST_SERVO
  r.spin_ms(100)

  # Loop ...
  print("Entering loop ...")
  try:
    try:
      lastDir = 0

      while True:
        try:
          r.onLoopStart()

          if r.onHold:
            # Some problem was detected (e.g. robot tilted etc.), skip all
            # the following code
            lastDir = 0
            continue

          # Sometines just look around
          if random.randint(1,1000) <= DO_LOOK_AROUND:
            r.lookAround()
            continue

          # Sleep sometimes
          if random.randint(1,1000) <= DO_TAKE_NAPS:
            r.nap()
            continue

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
            r.spin_ms(200)
            if lastDir == 0:
              dir = [-1,1][random.randint(0,1)]
              lastDir = dir
            else:
              dir = lastDir
            r.MotorTurn.speed = SPEED_TURN *dir
            r.spin_ms(SPEED_TURN_DELAY)
            r.MotorTurn.speed = 0

          else:
            # Cliff detected -> Stop, walk back a tad, turn in a random
            # direction to check (in the next spin) again for obstacles
            r.state = STATE_CLIFF
            r.MotorWalk.speed = 0
            r.spin_ms(500)
            r.MotorWalk.speed = -SPEED_WALK
            r.spin_ms(SPEED_BACK_DELAY)
            r.MotorWalk.speed = 0
            if lastDir == 0:
              dir = [-1,1][random.randint(0,1)]
              lastDir = dir
            else:
              dir = lastDir
            dir = [-1,1][random.randint(0,1)]
            r.MotorTurn.speed = SPEED_TURN *dir
            r.spin_ms(SPEED_TURN_DELAY*2)
            r.MotorTurn.speed = 0

        finally:
          # Make sure the robotling board get updated at least once per loop
          r.spin_ms()

    except KeyboardInterrupt:
      print("Loop stopped.")

  finally:
    # Make sure that robot is powered down
    r.ServoRangingSensor.off()
    r.powerDown()
    r.printReport()

# ----------------------------------------------------------------------------
# Create instance of HexBug, derived from the Robotling class
r = HexBug(MORE_DEVICES)

# Call main
if __name__ == "__main__":
  main()


# ----------------------------------------------------------------------------
