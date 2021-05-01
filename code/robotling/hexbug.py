# ----------------------------------------------------------------------------
# hexbug.py
# Definition of the class `Hexbug`, derived from `Robotling`
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
# Copyright (c) 2018-2020 Thomas Euler
# 2018-09-13, first release.
# 2018-10-29, use pitch/roll to check if robot is tilted.
# 2018-11-03, some cleaning up and commenting of the code
# 2018-11-28, re-organised directory structure, collecting all access to
#             hardware specifics to a set of "adapter classes" in `platform`,
# 2018-12-22, reorganised into a module with the class `Hexbug` and a simpler
#             main program file (`main.py`). All hardware-related settings
#             moved to separate file (`hexbug_config-py`)
# 2019-01-01, vl6180x time-of-flight distance sensor support added
# 2019-04-07, added new "behaviour" (take a nap)
# 2019-05-06, now uses `getHeading3D` instead of `getPitchRoll` to determine
#             if the robot is tilted; the additional compass information
#             (heading) is saved for later use.
# 2019-07-13, added new "behaviour" (find light)
#             `hexbug_config.py` reorganised and cleaned up
# 2019-07-24, added the ability to send telemetry via MQTT (ESP32 only);
#             added a bias factor (`IR_SCAN_BIAS_F`) to the configuration
#             file which allows accounting for a direction bias in the turning
#             motor and let the robot walk "more straight";
#             changed the scan scheme slightly to "left-center-right-center"
#             instead of "left-right-center"
# 2019-08-03, new type of Sharp sensor added (GP2Y0AF15X, 1.5-15 cm)
# 2019-08-19, now an array of IR distance sensors is possible; in this case,
#             the robot's head is not scanning sideways.
# 2019-09-01, Optionally encrypted MQTT messages; also. SSL connections to
#             the broker are now possible
# 2019-12-25, Configuration file split into fixed (`hexbug_global.py`) and
#             robot-dependent definitions
#             New behaviour `lookAtBlob` using the thermal camera.
# 2020-08-21, Refactoring for `robotling_lib`
# 2020-11-15, Further refactoring (platform based on language not board)
# 2021-04-21, Now uses `RobotlingBase`
# 2021-04-29, Some refactoring (e.g. fewer `from xy import *`); configuration
#             parameters now clearly marked as such (`cfg.xxx`)
#
# ----------------------------------------------------------------------------
import array
import random
from micropython import const
import robotling_lib.robotling_board as rb
from robotling_lib.driver import drv8835
from robotling import Robotling
from robotling_board_version import BOARD_VER
from robotling_lib.motors.dc_motor import DCMotor
from robotling_lib.motors.servo import Servo
from robotling_lib.misc.helpers import TemporalFilter
import hexbug_config as cfg
from hexbug_global import *

from robotling_lib.platform.platform import platform as pf
if pf.languageID == pf.LNG_MICROPYTHON:
  import time
  if cfg.SEND_TELEMETRY:
    mqttd = dict()
else:
  import robotling_lib.platform.m4ex.time as time

# ----------------------------------------------------------------------------
class HexBug(Robotling):
  """Hijacked-HexBug class"""

  def __init__(self, devices):
    super().__init__(devices)

    # Check if VL6180X time-of-flight ranging sensor is present, if not, add
    # analog IR ranging sensor (expected to be connected to A/D channel #0)
    self.RangingSensor = []
    try:
      self.RangingSensor.append(self._VL6180X)
      if not self.RangingSensor[0].isReady:
        raise AttributeError
    except AttributeError:
      if cfg.IR_SCAN_SENSOR == 1:
        # New, smaller sensor GP2Y0AF15X (1.5-15 cm)
        from robotling_lib.sensors.sharp_ir_ranging import GP2Y0AF15X as GP2Y
      else:
        # Default to GP2Y0A41SK0F (4-30 cm)
        from robotling_lib.sensors.sharp_ir_ranging import GP2Y0A41SK0F as GP2Y

      # For compatibility: if `AI_CH_IR_RANGING` is a constant then a
      # single IR sensor is defined, meaning that the robot's head scans
      # as usual. Otherwise, a list of ranging sensors is initialized.
      # In this case, it is assumed that an array of IR sensors is attached
      # and scanning is not needed (new).
      self.RangingSensor = []
      isList = type(cfg.AI_CH_IR_RANGING) is list
      AInCh = AI_CH_IR_RANGING if isList else [cfg.AI_CH_IR_RANGING]
      for pin in AInCh:
        self.RangingSensor.append(GP2Y(self._MCP3208, pin))
        self._MCP3208.channelMask |= 0x01 << pin
      self.nRangingSensor = len(self.RangingSensor)
    print("Using {0}x {1} as ranging sensor(s)"
          .format(self.nRangingSensor, self.RangingSensor[0].name))

    # Define scan positions to cover the ground before the robot. Currently,
    # the time the motor is running (in [s]) is used to define angular
    # position
    self._scanPos  = cfg.IR_SCAN_POS
    self._iScanPos = [0] *len(cfg.IR_SCAN_POS)
    self.onTrouble = False

    # Apply bias to scan position (times) to account for a directon bias
    # in the turning motor
    for iPos, pos in enumerate(cfg.IR_SCAN_POS):
      f = (1. +cfg.IR_SCAN_BIAS_F) if pos > 0 else (1. -cfg.IR_SCAN_BIAS_F)
      self._scanPos[iPos] *= f

    # Determine the number of different scan positions to dimension
    # the distance data array
    l = []
    for iPos, pos in enumerate(cfg.IR_SCAN_POS_DEG):
      if iPos == 0 or not pos in l:
        l.append(pos)
        self._iScanPos[iPos] = iPos
      else:
        for j in range(len(l)):
          if l[j] == pos:
            self._iScanPos[iPos] = j
            break
    # Generate array for distance data and filters for smoothing distance
    # readings, if requested
    self._distData = array.array("i", [0] *len(l))
    if cfg.DIST_SMOOTH >= 2:
      self._distDataFilters = []
      for iPos in range(len(l)):
        self._distDataFilters.append(TemporalFilter(cfg.DIST_SMOOTH))

    # Add the servo that moves the ranging sensor up and down
    self.ServoRangingSensor = Servo(
        cfg.DO_CH_DIST_SERVO, freq=rb.SERVO_FRQ,
        us_range=[cfg.MIN_US_SERVO, cfg.MAX_US_SERVO],
        ang_range=[cfg.MIN_DIST_SERVO, cfg.MAX_DIST_SERVO]
      )

    # Add motors
    self.MotorWalk = DCMotor(self._motorDriver, drv8835.MOTOR_A)
    self.MotorTurn = DCMotor(self._motorDriver, drv8835.MOTOR_B)
    self._turnBias = 0
    self.turnStats = 0

    # If load sensing is enabled and supported by the board, create filters
    # to smooth the load readings from the motors and change analog sensor
    # update mask accordingly
    if BOARD_VER >= 120 and cfg.USE_LOAD_SENSING:
      self.walkLoadFilter = TemporalFilter(5)
      self.turnLoadFilter = TemporalFilter(5)
      self._loadData      = array.array("i", [0]*2)
      self._MCP3208.channelMask |= 0xC0

    # If to use compass, initialize target heading
    if cfg.DO_WALK_STRAIGHT and not cfg.DO_FIND_LIGHT:
      self.cpsTargetHead = self.Compass.getHeading()

    # If "find light" behaviour is activated, activate the AI channels to which
    # the photodiodes are connected and create a filter to smooth difference
    # in light intensity readings (`lightDiff`)
    self.lightDiff = 0
    if cfg.DO_FIND_LIGHT:
      self._MCP3208.channelMask |= 1 << cfg.AI_CH_LIGHT_R | 1 << cfg.AI_CH_LIGHT_L
      self.LightDiffFilter = TemporalFilter(5, "i")

    # Flag that indicates when the robot should stop moving
    self.onHold = False

    if cfg.SEND_TELEMETRY and pf.ID == pf.ENV_ESP32_UPY:
      from robotling_lib.remote.mqtt_telemetry import Telemetry
      self.onboardLED.on()
      self._t = Telemetry(self.ID)
      self._t.connect()
      self.onboardLED.off()

    # Create filters for smoothing the pitch and roll readings
    self.PitchFilter = TemporalFilter(8)
    self.RollFilter  = TemporalFilter(8)

    self.tTemp = time.ticks_us()
    self.debug = []

    # Report memory
    self.printMemory()

    # Starting state
    self.state = STATE_IDLE

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def housekeeper(self, info=None):
    """ Does the hexbug-related housekeeping:
        - Stop motors if robot is tilted (e.g. falls on the side) by checking
          pitch/roll provided by the compass
        - Changes also color of NeoPixel depending on the robot's state
    """
    aid = self._MCP3208.data

    # Check if robot is tilted ...
    ehpr = self.Compass.getHeading3D()
    pAv  = self.PitchFilter.mean(ehpr[2])
    rAv  = self.RollFilter.mean(ehpr[3])
    self.onHold = (abs(pAv) > cfg.PIRO_MAX_ANGLE) or (abs(rAv) > cfg.PIRO_MAX_ANGLE)
    if self.onHold:
      # Stop motors
      self.MotorTurn.speed = 0
      self.MotorWalk.speed = 0
      self.ServoRangingSensor.off()
      self.state = STATE_ON_HOLD

    # Save heading
    self.currHead = ehpr[1]

    if cfg.DO_FOLLOW_BLOB and self.Camera:
      self.Camera.detectBlobs(kernel=cfg.BLOB_FILTER, nsd=cfg.BLOB_MIN_N_SD)

    if cfg.USE_LOAD_SENSING:
      self._loadData[0] = int(self.walkLoadFilter.mean(self._MCP3208.data[6]))
      self._loadData[1] = int(self.turnLoadFilter.mean(self._MCP3208.data[7]))

    if cfg.DO_FIND_LIGHT:
      dL = aid[cfg.AI_CH_LIGHT_R] -aid[cfg.AI_CH_LIGHT_L]
      self.lightDiff = int(self.LightDiffFilter.mean(dL))

    if cfg.SEND_TELEMETRY and self._t._isReady:
      # Collect the data ...
      mqttd[KEY_STATE] = self.state
      mqttd[KEY_TIMESTAMP] = time.ticks_ms() /1000.
      mqttd[KEY_POWER] = {KEY_BATTERY: self.Battery_V}
      if cfg.USE_LOAD_SENSING:
        mqttd[KEY_POWER].update({KEY_MOTORLOAD: list(self._loadData)})
      mqttd[KEY_SENSOR] = {KEY_DISTANCE: list(self._distData)}
      _temp = {
          KEY_HEADING:
          ehpr[1], KEY_PITCH: ehpr[2], KEY_ROLL: ehpr[3]
        }
      mqttd[KEY_SENSOR].update({KEY_COMPASS: _temp})
      if cfg.DO_FIND_LIGHT:
        _temp = {
            KEY_INTENSITY:
            [aid[cfg.AI_CH_LIGHT_L], aid[cfg.AI_CH_LIGHT_R]]
          }
        mqttd[KEY_SENSOR].update({KEY_PHOTODIODE: _temp})
      if cfg.DO_FOLLOW_BLOB and self.Camera:
        mqttd[KEY_CAM_IR] = {
            KEY_SIZE:
            (8,8), KEY_BLOBS: self.Camera.blobsRaw
          }
        mqttd[KEY_CAM_IR].update({KEY_IMAGE: self.Camera.imageLinear})
      if len(self.debug) > 0:
        mqttd[KEY_DEBUG] = self.debug
        self.debug = []
      # ... and publish
      self._t.publishDict(KEY_RAW, mqttd)

    # Change NeoPixel according to state
    i = self.state *3
    self.startPulsePixel(STATE_COLORS[i:i+3])

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def onLoopStart(self):
    """ To measure the performance of the loops, call this function once at
        the beginning of the main loop
    """
    pass

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def _nextTurnDir(self, lastTurnDir):
    if not lastTurnDir == 0:
      # Just turned but not sucessful, therefore remember that
      # direction
      self.turnStats += MEM_INC if lastTurnDir > 0 else -MEM_INC
    if self.turnStats == 0:
      return [-1,1][random.randint(0,1)]
    else:
      return 1 if self.turnStats > 0 else -1

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def scanForObstacleOrCliff(self):
    """ Acquires distance data at the scan positions, currently given in motor
        run time (in [s]). Returns -1=obstacle, 1=cliff, and 0=none.
    """
    bias = 0
    isBlob = False

    if cfg.DO_FIND_LIGHT:
      bias = -self.lightDiff

    elif cfg.DO_WALK_STRAIGHT:
      # Using the compass, determine current offset from target heading and
      # set a new bias (in [ms]) by which the head position is corrected. This
      # is done by biasing the head direction after scanning for obstacles
      # NOTE: NOT YET FULLY IMPLEMENTED
      dh = self.currHead -self.cpsTargetHead
      tb = dh *cfg.HEAD_ADJUST_FACT if abs(dh) > cfg.HEAD_ADJUST_THR else 0

    # ****************************************
    # ****************************************
    # ****************************************
    """
    elif cfg.DO_FOLLOW_BLOB:
      # TODO
      xy = self.Camera.getBestBlob(5, 0.60)
      isBlob = not xy is None
    """
    # ****************************************
    # ****************************************
    # ****************************************

    o = False
    c = False
    l = len(self._scanPos) -1
    self.ServoRangingSensor.angle = cfg.SCAN_DIST_SERVO
    if self.nRangingSensor == 1:
      # Only one ranging sensor, therefore scan the head back and forth
      # (as determined in `hexbug_config.py`) to cover the ground in front
      # of the robot
      for iPos, Pos in enumerate(self._scanPos):
        # Turn head into scan position; in the first turn account for a
        # turning bias resulting from the find light behaviour
        b = 0 if iPos < l else bias
        self.MotorTurn.speed = cfg.SPEED_SCAN *(-1,1)[Pos < 0]
        self.spin_ms(abs(Pos) +b)
        self.MotorTurn.speed = 0
        # Measure distance for this position ...
        d = int(self.RangingSensor[0].range_cm)
        self._distData[self._iScanPos[iPos]] = d
        # ... check if distance within the danger-free range
        o = o or (d < cfg.DIST_OBST_CM)
        c = c or (d > cfg.DIST_CLIFF_CM)
    else:
      # Several ranging sensors installed in an array, therefore head scans
      # are not needed
      for iPos in range(self.nRangingSensor):
        # Read distance from this ranging sensor ...
        d = int(self.RangingSensor[iPos].range_cm)
        if cfg.DIST_SMOOTH >= 2:
          d = int(self._distDataFilters[iPos].mean(d))
        self._distData[iPos] = d
        # ... check if distance within the danger-free range
        o = o or (d < cfg.DIST_OBST_CM)
        c = c or (d > cfg.DIST_CLIFF_CM)

      if True: #not DO_FOLLOW_BLOB: #isBlob:
        # Turn the head slighly to acount for (1) any bias that keeps the
        # robot from walking straight and (2) any turning bias resulting from
        # the find light behaviour
        self.MotorTurn.speed = cfg.SPEED_SCAN *(-1,1)[cfg.IR_SCAN_BIAS_F < 0]
        td = abs(cfg.IR_SCAN_BIAS_F *200) +bias
        self.spin_ms(td)
        self.MotorTurn.speed = 0
        # Make sure that the robot waits a minimum duration before returning
        # to the main loop
        sd = cfg.SPEED_BACK_DELAY//3 -td
        if sd > 0:
          self.spin_ms(sd)

    # ****************************************
    # ****************************************
    # ****************************************
    """
    if isBlob:
      self.debug.append("{0:.2f},{1:.2f} -> {2} ({3:.2f})".format(xy[0], xy[1],
                        "turn left" if xy[0] < 0 else "turn right",
                        abs(xy[0]/4)))
      print(self.debug[0])
      #self.MotorWalk.speed = 0
      c = 0
      d = 0
      if abs(xy[0]) > 0.1:
        d = 1 if xy[0] > 0 else -1
      self.MotorTurn.speed = int(SPEED_SCAN *d *abs(xy[0]/4) *5)
      self.spin_ms(100)
      self.MotorTurn.speed = 0
    """
    # ****************************************
    # ****************************************
    # ****************************************

    # Remember turning bias and return result
    self._turnBias = bias
    return 1 if c else -1 if o else 0

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def lookAround(self):
    """ Make an appearance of "looking around"
    """
    # Stop all motors and change state
    self.MotorWalk.speed = 0
    self.MotorTurn.speed = 0
    prevState = self.state
    self.state = STATE_LOOKING
    maxPit = max(cfg.MAX_DIST_SERVO, cfg.MIN_DIST_SERVO)

    # Move head and IR distance sensor at random, as if looking around
    nSacc = random.randint(4, 10)
    yaw = 0
    pit = cfg.SCAN_DIST_SERVO
    try:
      for i in range(nSacc):
        if self.onHold:
          break
        dYaw = random.randint(-800, 800)
        yaw += dYaw
        dir  = -1 if dYaw < 0 else 1
        pit += random.randint(-10,15)
        pit  = min(max(0, pit), maxPit)
        self.ServoRangingSensor.angle = pit
        self.MotorTurn.speed = cfg.SPEED_TURN *dir
        self.spin_ms(abs(dYaw))
        self.MotorTurn.speed = 0
        self.spin_ms(random.randint(0, 500))
    finally:
      # Stop head movement, if any, move the IR sensor back into scan
      # position and change back state
      self.MotorTurn.speed = 0
      self.ServoRangingSensor.angle = cfg.SCAN_DIST_SERVO
      self.state = prevState

      # If compass is used, set new target heading
      if cfg.DO_WALK_STRAIGHT and not cfg.DO_FIND_LIGHT:
        self._targetHead = self.Compass.getHeading()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def lookAtBlob(self, minBlobArea, minBlobProb):
    """ Look at (heat) blob
    """
    # Stop all motors and change state
    self.MotorWalk.speed = 0
    self.MotorTurn.speed = 0
    prevState = self.state
    self.state = STATE_SEEK_BLOB
    maxPit = max(cfg.MAX_DIST_SERVO, cfg.MIN_DIST_SERVO)
    dxy = self.Camera.resolution
    dx2 = dxy[0]/2
    pit = cfg.SCAN_DIST_SERVO
    pBl = minBlobProb/100
    xF  = TemporalFilter(3)
    yF  = TemporalFilter(3)

    # Move head towards a blob if one is detected
    try:
      for i in range(cfg.BLOB_ROUNDS):
        if self.onHold:
          break
        xy = self.Camera.getBestBlob(minBlobArea, pBl)
        if not xy is None:
          # Suitable blob found
          xBl = xF.mean(xy[0])
          yBl = yF.mean(xy[1])
          xdir = 0
          if abs(xBl) > cfg.BLOB_MIN_XY_OFFS:
            xdir = 1 if xBl > 0 else -1
          ydir = 0
          if abs(yBl) > cfg.BLOB_MIN_XY_OFFS:
            ydir = cfg.BLOB_YSTEP if yBl > 0 else -cfg.BLOB_YSTEP
          pit += ydir *abs(yBl/dx2)
          pit = int(min(max(-maxPit, pit), maxPit))
          self.ServoRangingSensor.angle = pit
          ssc = cfg.SPEED_SCAN
          self.MotorTurn.speed = int(ssc *xdir *abs(xBl/dx2) *cfg.BLOB_TSF)
          self.spin_ms(cfg.BLOB_SPIN_MS)
          self.MotorTurn.speed = 0
        else:
          self.spin_ms(cfg.BLOB_SPIN_MS)
    finally:
      # Stop head movement, if any, move the IR sensor back into scan
      # position and change back state
      self.MotorTurn.speed = 0
      self.ServoRangingSensor.angle = cfg.SCAN_DIST_SERVO
      self.state = prevState

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def nap(self):
    """ Take a nap
    """
    # Remember state, switch off motors and move sensor arm into neutral
    prevState = self.state
    self.state = gkb.STATE_WAKING_UP
    self.housekeeper()
    self.MotorWalk.speed = 0
    self.MotorTurn.speed = 0
    self.ServoRangingSensor.angle = 0

    # Dim the NeoPixel
    for i in range(10, -1, -1):
      self.dimPixel(i/10.0)
      self.spin_ms(250)

    # "Drop" sensor arm
    for p in range(0, cfg.SCAN_DIST_SERVO, -1):
      self.ServoRangingSensor.angle = p
      self.spin_ms(10)

    # Flash NeoPixel ...
    self.dimPixel(1.0)
    self.spin_ms(100)
    self.dimPixel(0.0)

    # ... and enter sleep mode for a random number of seconds
    self.sleepLightly(random.randint(cfg.NAP_FROM_S, cfg.NAP_TO_S))

    # Wake up, resume previous state and move sensor arm into scan position
    self.state = prevState
    self.ServoRangingSensor.angle = cfg.SCAN_DIST_SERVO
    self.housekeeper()

    # Bring up NeoPixel again
    for i in range(0, 11):
      self.dimPixel(i/10.0)
      self.spin_ms(250)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getDist(self, angle=0, trials=1, channel=0):
    """ Test function to determine the relevant IR distances.
        Moves IR ranging sensor to "angle" and measures/prints distance
        "trial" times.
    """
    self.ServoRangingSensor.angle = angle
    self.spin_ms(200)
    for i in range(trials):
      self.update()
      s = ""
      for ir in self.RangingSensor:
        s += "{0} ".format(ir.range_cm)
      print(s)
      self.spin_ms(0 if trials <= 1 else 250)

# ----------------------------------------------------------------------------
