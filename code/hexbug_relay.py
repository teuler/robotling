#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# hexbug_relay.py
# Resends HexBug robotling MQTT messages under "proper" topics
#
# The MIT License (MIT)
# Copyright (c) 2018-2019 Thomas Euler
# 2019-08-26, v1
#
# The GUID of the hexbug to connect to must be passed as argument:
#   --guid or -g
# for instance:
#   python .\hexbug_relay.py -g robotling_b4e62da1dccd
#
# ---------------------------------------------------------------------
import json
import threading
import time
import paho.mqtt.client as mqtt

try:
  import robotling.NETWORK as nw
  MQTT_BROKER     = nw.my_mqtt_srv
  MQTT_PORT       = nw.my_mqtt_port
  MQTT_ALIVE_S    = nw.my_mqtt_alive_s
except:
  print("Error retrieving broker info from `robotling.NETWORK.py` ...")
  exit()

# ---------------------------------------------------------------------
def onConnect(client, userdata, flags, rc):
  global isConnected
  if rc == 0:
    print("Successfully connected to `{0}`".format(MQTT_BROKER))
    print("Subscribing to `{0}` ...".format(MQTT_ROOT_TOPIC))
    client.subscribe(MQTT_ROOT_TOPIC +"/raw")
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
def parseCmdLn():
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_argument('-g', '--guid', type=str, default="")
  return parser.parse_args()

def parseRawMsg(d):
  for k, v in d.items():
    if isinstance(v, dict):
      for p in parseRawMsg(v):
        yield [k] + p
    else:
      yield [k, v]

# ---------------------------------------------------------------------
if __name__ == '__main__':

  # Initialize variables
  Lock = threading.Lock()
  isConnected = False
  isNewMsg = False
  lastMsg = ""

  # Check for command line parameter(s)
  args = parseCmdLn()
  MQTT_ROOT_TOPIC = args.guid
  if len(MQTT_ROOT_TOPIC) == 0:
    print("No robotling GUID given (parameter --guid or -g)")

  # Create MQTT client
  Client = mqtt.Client()
  Client.on_connect = onConnect
  Client.on_message = onMessage
  Client.on_disconnect = onDisconnect

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
          # New valid data available, resend under "proper" topics
          for ln in parseRawMsg(data):
            topic = MQTT_ROOT_TOPIC +"/"
            msg = str(ln.pop())
            for j, s in enumerate(ln):
              if j > 0 and len(ln) > 1:
                topic += "/"
              topic += s
            print(s, msg)  
            Client.publish(topic, payload=msg, qos=0, retain=False)

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
