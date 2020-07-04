#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# hexbug_gui.py
# GUI for HexBug robotling
#
# The MIT License (MIT)
# Copyright (c) 2018-2019 Thomas Euler
# 2019-05-06, v1
#
# The GUID of the hexbug to connect to must be passed as argument:
#   --guid or -g
# for instance:
#   blue:   python .\hexbug_gui.py -g robotling_b4e62da1dccd
#   orange: python .\hexbug_gui.py -g robotling_30aea413e508
#   black:  python .\hexbug_gui.py -g robotling_240ac4a23164
# with:
#   robotling_b4e62da1dccd - blue hexbug
#   robotling_30aea413e508 - orange hexbug
#
# ---------------------------------------------------------------------
import sys
#sys.path.append("..")

import time
import numpy as np
import modules.front_pygame as front
import paho.mqtt.client as mqtt
import json
import threading
import modules.data_buffer as db
import hexbug_mqtt as hx

WIN_SIZE          = (2, 6) # in standard widget sizes
WIN_POSITION      = (0, 0)

WIN_NAME          = "robotling_front_end"
WIN_ICON          = "robotling.png"
WIN_FLAGS         = 0

LOOP_WAIT_MS      = 10
MQTT_ROOT_TOPIC   = ""

try:
  import robotling.NETWORK as nw
  MQTT_BROKER     = nw.my_mqtt_srv
  MQTT_PORT       = nw.my_mqtt_port
  MQTT_ALIVE_S    = nw.my_mqtt_alive_s
except:
  print("Error retrieving broker info from `robotling.NETWORK.py` ...")
  exit()

# ---------------------------------------------------------------------
class FrontEndGUI(object):

  def __init__(self):
    """ Initialize GUI window
    """
    # Create window
    self.Win = front.Window(WIN_POSITION, WIN_SIZE, WIN_NAME, WIN_ICON)

    # Initialize
    rgV1   = [0., hx.V_MAX]
    rgPerc = [0, 100]
    rgLDif = [-1500, 1500]
    rgInt  = [0, 1500]

    # Define comparison functions
    def fLower(_x, _xWarn, _xDanger):
      res = front.IS_OK
      if _x < _xWarn:
        res = front.IS_WARN
      if _x < _xDanger:
        res = front.IS_DANGER
      return res

    def fRange(_x, _xWarn, _xDanger):
      if (_x < _xWarn) or (_x > _xDanger):
        return front.IS_DANGER
      else:
        return front.IS_OK

    # Array for timestamps
    self.timeData = db.DataStack(hx.LOAD_ARR_LEN, 0)

    # Define widgets
    #
    # Connection to MQTT broker
    x1 = 0
    y1 = 0
    self.Link = front.WidgetInfo(self.Win, (x1, y1))
    self.Link.setLabels("MQTT", "Connection status",
                        ["MQTT broker", "Root topic", "Statistics"])
    self.Link.draw()

    # Status
    x1 = 0
    y1 += self.Link.height
    self.State = front.WidgetInfo(self.Win, (x1, y1))
    self.State.setLabels("Status", "Robot(ling) status",
                        ["Current", "Debug"])
    self.State.draw()

    # Compass
    x1 = 0
    y1 += self.State.height
    self.Compass = front.WidgetCompass(self.Win, (x1, y1))
    self.Compass.setLabels("Sensors", "Compass")
    self.Compass.setProperties(hx.PIRO_MAX_ANGLE)
    self.Compass.draw()

    # IR distance array
    x1 = 0
    y1 += self.Compass.height
    rgDist = [hx.DIST_OBST_CM, hx.DIST_CLIFF_CM ]
    self.IRDistArray = front.WidgetDistanceArray(self.Win, (x1, y1))
    self.IRDistArray.setLabels("Sensors", "IR distance array")
    self.IRDistArray.setValProperties("Distance", "cm", rgDist, rgDist, fRange,
                                      hx.IR_SCAN_POS_DEG, hx.IR_SCAN_CONE_DEG)
    self.IRDistArray.draw()
    '''
    # ****************
    # ****************
    x1 = 0
    y1 += self.IRDistArray.height
    tf1 = "{0}"
    rgIRDist = [0, 35]
    self.PlotIRDist = front.WidgetPlot(self.Win, (x1, y1), (2,1))
    self.PlotIRDist.setLabels("Sensors", "IR distance history")
    self.IRLData = db.DataStack(hx.LOAD_ARR_LEN, 0)
    self.IRCData = db.DataStack(hx.LOAD_ARR_LEN, 0)
    self.IRRData = db.DataStack(hx.LOAD_ARR_LEN, 0)
    self.PlotIRDist.addValProperties("Left", "-", rgIRDist, rgIRDist, fRange,
                                     front.Color.PLOT_GR, (0,0), txtFormat=tf1)
    self.PlotIRDist.addValProperties("Center", "-", rgIRDist, rgIRDist, fRange,
                                     front.Color.PLOT_OR, (0,0), txtFormat=tf1)
    self.PlotIRDist.addValProperties("Right", "-", rgIRDist, rgIRDist, fRange,
                                     front.Color.PLOT_YE, (0,0), txtFormat=tf1)
    rgIRDistF = [-5, 5]
    self.nFiltArrIRDist = hx.LOAD_ARR_LEN
    self.IRLDataF = db.DataStack(self.nFiltArrIRDist, 0)
    self.IRCDataF = db.DataStack(self.nFiltArrIRDist, 0)
    self.IRRDataF = db.DataStack(self.nFiltArrIRDist, 0)
    self.PlotIRDist.addValProperties("f(Left)", "-", rgIRDistF, rgIRDistF, fRange,
                                     front.Color.PLOT_GR, (1,0), txtFormat=tf1)
    self.PlotIRDist.addValProperties("f(Center)", "-", rgIRDistF, rgIRDistF, fRange,
                                     front.Color.PLOT_OR, (1,0), txtFormat=tf1)
    self.PlotIRDist.addValProperties("f(Right)", "-", rgIRDistF, rgIRDistF, fRange,
                                     front.Color.PLOT_YE, (1,0), txtFormat=tf1)
    self.PlotIRDist.draw()
    # ****************
    # ****************
    '''

    # Main battery
    x1 = 0
    y1 += self.IRDistArray.height
    #y1 += self.Compass.height
    self.Batt1 = front.WidgetStatusBar(self.Win, (x1, y1))
    sFormat = "U = {0:.2f}V ({1:.0f}%)"
    self.Batt1.setLabels("Battery", "Main power", "LiPo",
                         sFormat, 1)
    wV = hx.LIPO_MAX_V *0.7
    dV = hx.LIPO_MIN_V
    self.Batt1Filter = db.DataStack(30, hx.LIPO_MIN_V)
    self.Batt1.addValProperties("voltage", "V", rgV1, [wV, dV], fLower)
    self.Batt1.addValProperties("charge", "%", rgPerc, [60., 20.], fLower)
    self.Batt1.draw()

    # Motor load, if provided
    x1  = self.Link.width
    y1  = 0
    tf1 = "{0}"
    rgLoad = [-50, hx.LOAD_MAX]
    self.LoadTData = db.DataStack(hx.LOAD_ARR_LEN, 0)
    self.LoadWData = db.DataStack(hx.LOAD_ARR_LEN, 0)
    self.PlotLoad = front.WidgetPlot(self.Win, (x1, y1), (1,1))
    self.PlotLoad.setLabels("Sensors", "Motor load")
    self.PlotLoad.addValProperties("M(walk)", "-", rgLoad, rgLoad, fRange,
                                   front.Color.PLOT_BL, (0,0), txtFormat=tf1)
    self.PlotLoad.addValProperties("M(turn)", "-", rgLoad, rgLoad, fRange,
                                   front.Color.PLOT_GR, (0,0), txtFormat=tf1)
    self.PlotLoad.draw()

    # Photodiode light intensity, if provided
    x1  = self.Link.width
    y1  = self.PlotLoad.height
    tf1 = "{0}"
    self.LightLData = db.DataStack(hx.LOAD_ARR_LEN, 0)
    self.LightRData = db.DataStack(hx.LOAD_ARR_LEN, 0)
    self.PlotLight = front.WidgetPlot(self.Win, (x1, y1), (1,1))
    self.PlotLight.setLabels("Sensors", "Photodiode (intensity)")
    self.PlotLight.addValProperties("L", "-", rgInt, rgInt, fRange,
                                    front.Color.PLOT_YE, (0,0), txtFormat=tf1)
    self.PlotLight.addValProperties("R", "-", rgInt, rgInt, fRange,
                                    front.Color.PLOT_OR, (0,0), txtFormat=tf1)
    self.PlotLight.draw()

    # IR camera
    x1  = self.Link.width
    y1 += self.PlotLoad.height
    self.CameraIR = front.WidgetCamera(self.Win, (x1, y1))
    self.CameraIR.setLabels("Sensors", "8x8 thermal camera")
    self.CameraIR.setValProperties("temp.", "°C", (18, 37), (16,16), True)
    self.CameraIR.draw()
    self.icr_nFr = 0
    self.icr_Frames = np.zeros((100,8,8), dtype=np.uint8)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def run(self):
    """ Run main loop
    """
    global dtGUIUpdate_s, roundGUI

    while(True):
      # Update GUI
      t0 = time.time()
      self.update()
      self.Win.update()
      dtGUIUpdate_s = time.time() -t0
      roundGUI += 1

      # Check if user wants to quit
      if self.Win.doQuit():
        return

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def update(self):
    """ Update GUI
    """
    global isConnected, Client, Robot

    if not isConnected:
      # Try to connect to broker and start loop thread ...
      try:
        Client.connect(MQTT_BROKER, port=MQTT_PORT, keepalive=MQTT_ALIVE_S)
        Client.loop_start()
        isConnected = True
      except ConnectionRefusedError:
        self.Link.update(["n/a", "n/a", Robot.getStatsStr()])
        return

    # Is connected ...
    self.Link.update([MQTT_BROKER, MQTT_ROOT_TOPIC, Robot.getStatsStr()])
    if Robot.processLatestMQTTMsg():
      # New message received and successfully converted
      #
      # Robot(ling) status and timestamp
      d = Robot.getData("debug")
      sDebug = str(d) if d is not None else "n/a"
      d = Robot.getData("state")
      sState = hx.RStateStr[d] if d is not None else "n/a"
      if d is None:
        # No status published, it is likely that the rrobot's software
        # crashed. Print content of `debug` into the history
        print("ERROR: Last message from robot: -----")
        print(sDebug +"-------------------------------------")
        sDebug = "ERROR (see history)"
      self.State.update([sState, sDebug])
      data = Robot.getData(hx.KEY_TIMESTAMP)
      if data is not None:
        self.timeData.shift(data)

      # Main battery
      data = Robot.getData("power/battery_V")
      self.Batt1.isActive = not data is None
      if self.Batt1.isActive:
        self.Batt1Filter.shift(data)
        V = self.Batt1Filter.mean(25)
        C = (V -hx.LIPO_MIN_V)/(hx.LIPO_MAX_V -hx.LIPO_MIN_V) *100
        self.Batt1.update([V, C])
        self.Batt1.txtInfo = "n/a"

      # Compass
      h = Robot.getData("sensor/compass/heading_deg")
      p = Robot.getData("sensor/compass/pitch_deg")
      r = Robot.getData("sensor/compass/roll_deg")
      self.Compass.isActive = not h is None
      if self.Compass.isActive:
        self.Compass.update([h, p, r])

      # IR distance array
      data = Robot.getData("sensor/distance_cm")
      self.IRDistArray.isActive = not data is None
      if self.IRDistArray.isActive:
        self.IRDistArray.update(data)
        '''
        # ****************
        # ****************
        self.IRLData.shift(data[0])
        self.IRCData.shift(data[1])
        self.IRRData.shift(data[2])
        self.nBoxIRDist = 2
        self.IRLDataF.shift(self.IRLData.diff(nBox=self.nBoxIRDist))
        self.IRCDataF.shift(self.IRCData.diff(nBox=self.nBoxIRDist))
        self.IRRDataF.shift(self.IRRData.diff(nBox=self.nBoxIRDist))
        self.PlotIRDist.update([self.IRLData.data, self.IRCData.data,
                                self.IRRData.data, self.IRLDataF.data,
                                self.IRCDataF.data, self.IRRDataF.data])
        # ****************
        # ****************
        '''

      # Motor load, if provided
      data = Robot.getData("power/motor_load")
      self.PlotLoad.isActive = not data is None
      if self.PlotLoad.isActive:
        self.LoadTData.shift(data[0])
        self.LoadWData.shift(data[1])
        self.PlotLoad.update([self.LoadTData.data, self.LoadWData.data])

      # Light intensity difference, if provided
      data = Robot.getData("sensor/photodiode/intensity")
      self.PlotLight.isActive = not data is None
      if self.PlotLight.isActive:
        self.LightLData.shift(data[0])
        self.LightRData.shift(data[1])
        self.PlotLight.update([self.LightLData.data, self.LightRData.data])

      # Thermal camera image, if provided
      data = Robot.getData("camera_IR/image")
      size = Robot.getData("camera_IR/size")
      blobs = Robot.getData("camera_IR/blobs")
      self.CameraIR.isActive = not data is None
      if self.CameraIR.isActive:
        self.CameraIR.update(data, size, blobs)
        '''
        if self.icr_nFr < self.icr_Frames.shape[0]:
           self.icr_Frames[self.icr_nFr] = np.reshape(data, size)
           self.icr_nFr += 1
        else:
          from tempfile import TemporaryFile
          outfile = TemporaryFile()
          np.save("thermodata", self.icr_Frames)
          quit()
        '''

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def kill(self):
    """ Destroy window
    """
    self.Win.close()

# ---------------------------------------------------------------------
# MQTT-related
#
# ---------------------------------------------------------------------
def onConnect(client, userdata, flags, rc):
  """ The callback for when the client receives a CONNACK response from
      the server/broker. Subscribing in on_connect() means that if we
      lose the connection and reconnect then subscriptions will be
      renewed.
  """
  global isConnected
  if rc == 0:
    print("MQTT: Successfully connected to `{0}`".format(MQTT_BROKER))
    print("MQTT: Subscribing to `{0}` ...".format(MQTT_ROOT_TOPIC))
    client.subscribe(MQTT_ROOT_TOPIC)
    isConnected = True
  else:
    print("MQTT: Broker `{0}` replied `{1}`".format(MQTT_BROKER, rc))

def onDisconnect(client, userdata, rc):
  """ Called when the client disconnects from the broker.
  """
  global isConnected
  print("MQTT: Disconnected from broker `{0}`".format(MQTT_BROKER))
  isConnected = False

def onMessage(client, userdata, msg):
  """ The callback for when a PUBLISH message is received from the server;
      passes the latest MQTT message from robotling to the robot's
      representation object
  """
  global Robot
  Robot.setNewMQTTMsg(msg)

def onLog(client, userdata, level, buf):
  print("***", level, buf)

# ---------------------------------------------------------------------
def parseCmdLn():
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_argument('-g', '--guid', type=str, default="")
  return parser.parse_args()

# ---------------------------------------------------------------------
if __name__ == '__main__':

  # Initialize
  isConnected = False
  dtGUIUpdate_s = 0
  roundGUI = 0

  # Check for command line parameter(s)
  args = parseCmdLn()
  MQTT_ROOT_TOPIC = args.guid +"/raw"
  if len(MQTT_ROOT_TOPIC) == 0:
    print("No robotling GUID given (parameter --guid or -g)")

  # Robotling-related data
  Robot = hx.HexBug(isVerbose=False)

  # Create MQTT client
  Client = mqtt.Client()
  Client.on_connect = onConnect
  Client.on_message = onMessage
  Client.on_disconnect = onDisconnect
  #Client.on_log = onLog

  # Create GUI front end and run loop
  GUI = FrontEndGUI()
  GUI.run()

  # Clean up GUI
  GUI.kill()

  if isConnected:
    # Stop MQTT client
    print("MQTT: Stopping client loop ...")
    Client.loop_stop()
    print("MQTT: Disconnecting from broker ...")
    Client.disconnect()
    print("... done.")

# ---------------------------------------------------------------------
