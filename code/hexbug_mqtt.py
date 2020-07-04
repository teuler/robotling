#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# hexbug_mqtt.py
# MQTT message-based representation of the hexbug robotling
#
# The MIT License (MIT)
# Copyright (c) 2018-19 Thomas Euler
# 2019-05-04, v1
#
# ---------------------------------------------------------------------
import time
import numpy as np
import json
import threading
import modules.data_buffer as db
from robotling.hexbug_config import *
from robotling.hexbug_global import *


# ----------------------------------------------------------------------------
# Robot states
class RStates:
  IDLE            = STATE_IDLE
  WALKING         = STATE_WALKING
  LOOKING         = STATE_LOOKING
  ON_HOLD         = STATE_ON_HOLD
  OBSTACLE        = STATE_OBSTACLE
  CLIFF           = STATE_CLIFF
  WAKING_UP       = STATE_WAKING_UP
  SEEK_BLOB       = STATE_SEEK_BLOB

RStateStr = dict([
  (RStates.IDLE,      "Idle"),
  (RStates.WALKING,   "Walking"),
  (RStates.LOOKING,   "Looking"),
  (RStates.ON_HOLD,   "On hold (tilted)"),
  (RStates.OBSTACLE,  "Obstacle detected"),
  (RStates.CLIFF,     "Cliff detected"),
  (RStates.WAKING_UP, "Sleeping/waking up"),
  (RStates.SEEK_BLOB, "Follow blob")])

# ----------------------------------------------------------------------------
class HexBug(object):
  """Hijacked-HexBug representation"""

  def __init__(self, isVerbose=True):
    self.sCurrMsg = ""
    self.nMsg = 0
    self.nMsgCorrupt = 0
    self.Data = dict()
    self.freqMsgFilter = db.DataStack(50, 25)
    self.freqMsg = 0
    self._tLastMsg = time.time()
    self._isNewMsg = False
    self._Lock = threading.Lock()
    self._isVerbose = isVerbose

  def setNewMQTTMsg(self, msg):
    """ Acquire lock and save the passed MQTT message as a string
    """
    try:
      self._Lock.acquire()
      self.sCurrMsg = msg.payload.decode('utf-8')
      self._isNewMsg = True
    finally:
      self._Lock.release()

    if self._isNewMsg:
      self.nMsg += 1
      t = time.time()
      self.freqMsgFilter.shift(1/(t -self._tLastMsg))
      self.freqMsg = self.freqMsgFilter.mean(nBox=50)
      self._tLastMsg = t

  def processLatestMQTTMsg(self):
    """ Convert latest MQTT message string into a directory
    """
    res = False
    if self._isNewMsg and len(self.sCurrMsg) > 0:
      try:
        self._Lock.acquire()
        try:
          self.Data = json.loads(str(self.sCurrMsg))
          self._isNewMsg = False
          res = True
        except:
          self.nMsgCorrupt += 1
      finally:
        self._Lock.release()
    return res

  def getData(self, keyStrList):
    """ Returns data for `keyStrList` or `None`, if the keys were not found.
       `keyStrList` can be a list of strings, e.g. if the key is composed
       (e.g. ["sensor","compass","heading_deg"]), or a string, such as
       "sensor/compass/heading_deg"
    """
    try:
      if not isinstance(keyStrList,list):
        keyStrList = keyStrList.split("/")
      n =  len(keyStrList)
      if n == 1:
        return self.Data[keyStrList[0]]
      elif n == 2:
        return self.Data[keyStrList[0]][keyStrList[1]]
      elif n == 3:
        return self.Data[keyStrList[0]][keyStrList[1]][keyStrList[2]]
      else:
        print("ERROR: `keyStrList` contains no or more than 3 keys")
    except KeyError:
      if self._isVerbose:
        print("ERROR: Key `{0}`not found".format(keyStrList))
    return None

  def getStatsStr(self):
    """ Return statistics on received messages as a string
    """
    return "{0} @ {1:.1f} Hz, {2} corrupt".format(self.nMsg, self.freqMsg,
                                                  self.nMsgCorrupt)

# ---------------------------------------------------------------------
