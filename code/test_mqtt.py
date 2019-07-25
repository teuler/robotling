#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# test_mqtt.py
# Simple example script that illustrates how to receive MQTT telemetry
# from a robotling
#
# The MIT License (MIT)
# Copyright (c) 2019 Thomas Euler
# 2019-07-25, v1
#
# ---------------------------------------------------------------------
import json
import threading
import time
import paho.mqtt.client as mqtt

# ---------------------------------------------------------------------
# USER SECTION ==>
MQTT_ROOT_TOPIC = "robotling_b4e62da1dccd"  # replace by robotling GUID
MQTT_BROKER     = "test.mosquitto.org"      # replace by IP address
# <==
# ---------------------------------------------------------------------
MQTT_PORT       = 1883
MQTT_ALIVE_S    = 60

# ---------------------------------------------------------------------
def onConnect(client, userdata, flags, rc):
  global isConnected
  if rc == 0:
    print("Successfully connected to `{0}`".format(MQTT_BROKER))
    print("Subscribing to `{0}` ...".format(MQTT_ROOT_TOPIC))
    client.subscribe(MQTT_ROOT_TOPIC)
    isConnected = True
  else:
    print("Broker `{0}` replied `{1}`".format(MQTT_BROKER, rc))

def onDisconnect(client, userdata, rc):
  global isConnected
  print("Disconnected from broker `{0}`".format(MQTT_BROKER))
  isConnected = False

def onMessage(client, userdata, msg):
  global lastMsg, isNewMsg
  try:
    Lock.acquire()
    lastMsg = msg.payload.decode('utf-8')
    isNewMsg = True
  finally:
    Lock.release()

# ---------------------------------------------------------------------
if __name__ == '__main__':

  # Create MQTT client
  Client = mqtt.Client()
  Client.on_connect = onConnect
  Client.on_message = onMessage
  Client.on_disconnect = onDisconnect

  # Initialize variables
  Lock = threading.Lock()
  isConnected = False
  isNewMsg = False
  lastMsg = ""

  try:
    while True:
      if not isConnected:
        # If not connected, try to connect to broker and start the client's
        # internal loop thread ...
        try:
          print("Trying to connect to `{0}` ...".format(MQTT_BROKER))
          Client.connect(MQTT_BROKER, port=MQTT_PORT, keepalive=MQTT_ALIVE_S)
          Client.loop_start()
          isConnected = True
        except ConnectionRefusedError:
          time.sleep(0.5)
      else:
        # Is connected to broker ...
        data = None
        if isNewMsg and len(lastMsg) > 0:
          try:
            Lock.acquire()
            try:
              # Load data from last message and decode it
              # (convert it into a dictionary)
              data = json.loads(str(lastMsg))
            except:
              print("Corrupt message")
          finally:
            Lock.release()
            isNewMsg = False

        if data:
          # New valid data available, print some data
          print("sensor/distance_cm=", data["sensor"]["distance_cm"])
          print("power/battery_V=", data["power"]["battery_V"])

      # Sleep for a bit
      time.sleep(0.05)

  except KeyboardInterrupt:
    print("User aborted loop")

  # Stop MQTT client and disconnect
  print("Stop MQTT client loop and disconnect ...")
  Client.loop_stop()
  Client.disconnect()
  print("... done.")

# ---------------------------------------------------------------------
