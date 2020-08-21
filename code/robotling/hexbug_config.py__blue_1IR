#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# hexbug_config.py
# Configuration file for HexBug robotling
#
# *** Blue HexBug ***
# ---------------------------------------------------------------------
# Allow to use robotling GUI running on a PC to use the same
# configuration file as the MicroPython code
try:
  ModuleNotFoundError
except NameError:
  ModuleNotFoundError = ImportError
try:
  from micropython import const
  from robotling_lib.robotling_board import *
except ModuleNotFoundError:
  const = lambda x : x
  DIO0  = None

# ---------------------------------------------------------------------
# USER SECTION
# ==>
#
# Tilt-sensing
PIRO_MAX_ANGLE   = const(25)   # Maximal tilt (i.e. pitch/roll) allowed
                               # .. before robot responds

# Obstacle/cliff detection
#
# Scan positions as list of head turn durations in [ms] and as a list
# of approx. angular positions ([°]).
IR_SCAN_POS      = [-300, 300, 300, -300]
IR_SCAN_POS_DEG  = [-35, 0, 35, 0]
IR_SCAN_BIAS_F   = -0.1        # To account for bias in turning motor:
                               # .. pos > 0 --> pos*(1+IR_SCAN_BIAS_F)
                               # .. pos < 0 --> pos*(1-IR_SCAN_BIAS_F)
IR_SCAN_CONE_DEG = const(30)   # Angular width of scan cone (only for GUI)
IR_SCAN_SENSOR   = const(0)    # 0=GP2Y0A41SK0F (4-30 cm)
                               # 1=GP2Y0AF15X (1.5-15 cm)
AI_CH_IR_RANGING = 0           # Analog-In channel(s) for IR distance sensor(s)
DIST_OBST_CM     = const(7)    # 7  Lower distances are considered obstacles
DIST_CLIFF_CM    = const(13)   # 13 Farer distances are considered cliffs
DIST_SMOOTH      = const(0)

# Light intensity measurements
AI_CH_LIGHT_R    = const(3)
AI_CH_LIGHT_L    = const(2)

# Servo settings
DO_CH_DIST_SERVO = DIO0        # Digital-Out channel for distance sensor servo
MIN_DIST_SERVO   = const(45)   # Limits of servo that holds the arm with the
MAX_DIST_SERVO   = const(-45)  # .. IR distance sensor in [°]
MIN_US_SERVO     = const(1200) # 1322 Minimum timing of servo in [us]
MAX_US_SERVO     = const(2350) # Maximum timing of servo in [us]
SCAN_DIST_SERVO  = const(-25)  # Angle of IR distance sensor arm

# Period of timer that keeps sensor values updated, the NeoPixel pulsing,
# and checks for tilt (in [ms])
TM_PERIOD        = const(50)

# Default motor speeds ..
SPEED_WALK       = const(-75)  # .. for walking forwards
SPEED_TURN       = const(35)   # .. for turning head when changing direction
SPEED_SCAN       = const(55)   # .. for turning head when scanning
SPEED_TURN_DELAY = const(450)  # Duration for turning in new direction
SPEED_BACK_DELAY = const(500)  # Duration for backing up (cliff)
"""
SPEED_WALK       = const(0)    # .. for walking forwards
SPEED_TURN       = const(0)    # .. for turning head when changing direction
SPEED_SCAN       = const(0)    # .. for turning head when scanning
SPEED_TURN_DELAY = const(450)  # Duration for turning in new direction
SPEED_BACK_DELAY = const(500)  # Duration for backing up (cliff)
"""
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Options, depending on board and sensor complement
USE_LOAD_SENSING = const(1)    # Use AI channels #6,7 for load-sensing (> v1.1)
USE_POWER_SHD    = const(1)    # Use ENAB_5V (voltage regulator off)   (> v1.1)
SEND_TELEMETRY   = const(1)    # only w/ESP32

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# "Behaviours" and their parameters
#
# Look around
DO_LOOK_AROUND   = const(20)   # =probabilty ([‰]) to activate behaviour

# Take a nap
# If activated, the roboter falls asleep from time to time. When this happens,
# the processor and all on-board electronics go to deep sleep or are turned
# off. The roboter wakes up after a random number of seconds.
# (only with ESP32, needs `USE_POWER_SHD` enabled)
DO_TAKE_NAPS     = const(0)    # =probability ([‰]) to activate behaviour
NAP_FROM_S       = const(5)    # range of random numbers to sleep ...
NAP_TO_S         = const(20)   # ... in [s]

# Find light source
# Uses a photodiode pair to home in on a light source. Give pins that connect
# to the photodiodes in `AI_CH_LIGHT_R` and `AI_CH_LIGHT_L` (above)
# (obviously, does not work together `DO_WALK_STRAIGHT`)
DO_FIND_LIGHT    = const(1)    # 1=enabled

# Follow the heat "blob"
# ...
DO_FOLLOW_BLOB   = const(0)    # 1=enabled

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# "Behaviors", not yet fully implemented/tested
#
# Use the compass to walk straight ahead
DO_WALK_STRAIGHT = const(0)
HEAD_ADJUST_FACT = const(-1)   #
HEAD_ADJUST_THR  = const(5)    # [°]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Additional devices plugged into the robotling board
# Possible devices:
# - Compass modules     : "compass_cmps12", "lsm303", "lsm9ds0"
# - ToF distance sensor : "vl6180x"
# - Display             : "dotstar_feather"
# - WLAN                : "wlan"
# - Cameras             : "amg88xx"
MORE_DEVICES     = ["wlan", "lsm9ds0"]

# <==
# ---------------------------------------------------------------------
