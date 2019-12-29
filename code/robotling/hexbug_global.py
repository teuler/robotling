#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# hexbug_global.py
# Global definitions for HexBug robotling
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
except ModuleNotFoundError:
  const = lambda x : x

# ---------------------------------------------------------------------
# Robot state-related definitions
STATE_IDLE       = const(0)
STATE_WALKING    = const(1)
STATE_LOOKING    = const(2)
STATE_ON_HOLD    = const(3)
STATE_OBSTACLE   = const(4)
STATE_CLIFF      = const(5)
STATE_WAKING_UP  = const(6)
STATE_SEEK_BLOB  = const(7)

# NeoPixel colors (r,g,b) for the different states
STATE_COLORS     = bytearray((
                   10,10,10,   # STATE_IDLE
                   20,70,0,    # STATE_WALKING
                   40,30,0,    # STATE_LOOKING
                   20,00,50,   # STATE_ON_HOLD
                   90,30,0,    # STATE_OBSTACLE
                   90,0,30,    # STATE_CLIFF
                   10,60,60,   # STATE_WAKING_UP
                   60,5,0))    # STATE_SEEK_BLOB

# MQTT releated definitions
#
# Message keys
KEY_RAW          = "raw"
KEY_SENSOR       = "sensor"
KEY_COMPASS      = "compass"
KEY_HEADING      = "heading_deg"
KEY_PITCH        = "pitch_deg"
KEY_ROLL         = "roll_deg"
KEY_PHOTODIODE   = "photodiode"
KEY_INTENSITY    = "intensity"
KEY_DISTANCE     = "distance_cm"
KEY_POWER        = "power"
KEY_BATTERY      = "battery_V"
KEY_STATE        = "state"
KEY_MOTORLOAD    = "motor_load"
KEY_STATISTICS   = "stats"
KEY_TURNS        = "turns"
KEY_TIMESTAMP    = "timestamp_s"
KEY_CAM_IR       = "camera_IR"
KEY_IMAGE        = "image"
KEY_SIZE         = "size"
KEY_DEBUG        = "debug"
KEY_BLOBS        = "blobs"

# Limits for telemetry data
LIPO_MAX_V       = 4.2
LIPO_MIN_V       = 3.5
V_MAX            = 5.0
LOAD_MAX         = 1500
LOAD_ARR_LEN     = 200
LOAD_ARR_BOX     = 1
LIGHT_ARR_BOX    = 1

# Experimental parameters
MEM_INC          = 1
MEM_DEC          = 0.25

# ---------------------------------------------------------------------
