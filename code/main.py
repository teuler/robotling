# ----------------------------------------------------------------------------
# main.py
# Main program; is automatically executed after reboot.
#
# For decription, see `hexbug.py`
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-12-22, reorganised into a module with the class `Hexbug` and a simpler
#             main program file (`main.py`). All hardware-related settings
#             moved to separate file (`hexbug_config-py`)
# ----------------------------------------------------------------------------
from hexbug import *

# ----------------------------------------------------------------------------
def main():
  # Angle the IR sensor towards floor in front
  r.ServoDistSensor.angle = SCAN_DIST_SERVO

  # Start timer, which acquires sensor readings, updates the NeoPixel and
  # in the callback, checks if the robot is not tilted
  r.startTimer(TM_PERIOD)

  # Loop ...
  print("Entering loop ...")
  try:
    try:
      lastDir = 0

      while True:
        r.onLoopStart()

        if r.onHold:
          # Some problem was detected (e.g. robot tilted etc.), skip all
          # the following code
          lastDir = 0
          continue

        # Sometines just look around
        if random.randint(0,15) == 0:
          r.lookAround()
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
          time.sleep_ms(200)
          if lastDir == 0:
            dir = [-1,1][random.randint(0,1)]
            lastDir = dir
          else:
            dir = lastDir
          r.MotorTurn.speed = SPEED_TURN *dir
          time.sleep_ms(SPEED_TURN_DELAY)
          r.MotorTurn.speed = 0

        else:
          # Cliff detected -> Stop, walk back a tad, turn in a random
          # direction to check (in the next spin) again for obstacles
          r.state = STATE_CLIFF
          r.MotorWalk.speed = 0
          time.sleep_ms(500)
          r.MotorWalk.speed = -SPEED_WALK
          time.sleep_ms(SPEED_BACK_DELAY)
          r.MotorWalk.speed = 0
          if lastDir == 0:
            dir = [-1,1][random.randint(0,1)]
            lastDir = dir
          else:
            dir = lastDir
          dir = [-1,1][random.randint(0,1)]
          r.MotorTurn.speed = SPEED_TURN *dir
          time.sleep_ms(SPEED_TURN_DELAY*2)
          r.MotorTurn.speed = 0

    except KeyboardInterrupt:
      print("Loop stopped.")

  finally:
    # Make sure that robot is powered down and timer is stopped
    r.stopTimer()
    r.ServoDistSensor.off()
    r.powerDown()
    r.printReport()

# ----------------------------------------------------------------------------
# Create instance of HexBug, derived from the Robotling class
r = HexBug(MORE_DEVICES)

# Call main
if __name__ == "__main__":
  main()

# ----------------------------------------------------------------------------
