# ---------------------------------------------------------------------
# hexbug_config.py
# Configuration file for HexBug robotling
#
# *** Blue HexBug ***
# ---------------------------------------------------------------------
# Allow to use robotling GUI running on a PC to use the same
# configuration file as the MicroPython code
try:
  from micropython import const
  from robotling_board import *
except ModuleNotFoundError:
  const = lambda x : x
  DIO0  = None

# Tilt-sensing
PIRO_MAX_ANGLE   = const(25)   # Maximal tilt (i.e. pitch/roll) allowed
                               # .. before robot responds
# Obstacle/cliff detection
# (Scan positions for obstacles/cliffs checks as head turn durations list [ms])
IR_SCAN_POS      = [-450, 500, -250]
AI_CH_IR_RANGING = const(0)    # Analog-In channel for IR distance sensor
DIST_OBST_CM     = const(7)    # Lower distances are considered obstacles
DIST_CLIFF_CM    = const(16)   # Farer distances are considered cliffs

# Servo settings
DO_CH_DIST_SERVO = DIO0        # Digital-Out channel for distance sensor servo
MIN_DIST_SERVO   = const(45)   # Limits of servo that holds the arm with the
MAX_DIST_SERVO   = const(-45)  # .. IR distance sensor in [°]
MIN_US_SERVO     = const(1322) # Minimum timing of servo in [us]
MAX_US_SERVO     = const(2350) # Maximum timing of servo in [us]
SCAN_DIST_SERVO  = const(-25)  # Angle of IR distance sensor arm

# Period of timer that keeps sensor values updated, the NeoPixel pulsing,
# and checks for tilt (in [ms])
TM_PERIOD        = const(50)

# Default motor speeds ..
SPEED_WALK       = const(-75)  # -55,-70 .. for walking forwards
SPEED_TURN       = const(35)   # +25,+30 .. for turning head when changing direction
SPEED_TURN_DELAY = const(900)  #
SPEED_BACK_DELAY = const(500)  #
SPEED_SCAN       = const(55)   # 40 .. for turning head when scanning

# Options, depending on board and sensor complement
USE_LOAD_SENSING = const(0)    # Use AI channels #6,7 for load-sensing (> v1.1)
USE_POWER_SHD    = const(0)    # Use ENAB_5V (voltage regulator off)   (> v1.1)

# Options, "behaviours"
DO_LOOK_AROUND   = const(30)   # Use "looking around", as probabilty, [‰]
DO_TAKE_NAPS     = const(0)    # Use "nap", as probability, [‰], e.g. 10

# Additional devices plugged into the robotling board
#MORE_DEVICES    = ["compass_cmps12"]
#MORE_DEVICES    = ["compass_cmps12", "vl6180x"]
MORE_DEVICES     = ["lsm303"]
#MORE_DEVICES    = ["lsm303", "dotstar_feather"]
#MORE_DEVICES    = ["lsm9ds0"]
