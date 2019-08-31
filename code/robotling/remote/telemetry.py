# ----------------------------------------------------------------------------
# telemetry.py
# Telemetry via the MQTT protocol (test).
#
# The MIT License (MIT)
# Copyright (c) 2018-19 Thomas Euler
# 2018-11-11, v1
# 2019-07-25, Added `connect` as method;
#             switched from `umqtt.simple` to `umqtt.robust` because it
#             automatically reconnects when the network is unstable
#             (i.e. after sleep)
# ----------------------------------------------------------------------------
import network
import ujson
import errno
from umqtt.robust import MQTTClient
from misc.helpers import timed_function

__version__ = "0.1.1.0"

# ----------------------------------------------------------------------------
class Telemetry():
  """Telemetry via the MQTT protocoll."""

  def __init__(self, ID, broker=""):
    self._isReady   = False
    self._broker    = broker
    self._clientID  = ID
    self._client    = None
    self._rootTopic = self._clientID +"/"

  def connect(self):
    """ Try to connect to MQTT broker
    """
    print("Initializing telemetry via MQTT ...")
    self.sta_if = network.WLAN(network.STA_IF)
    if not self.sta_if.isconnected():
      print("Error: Not connected to network")
    else:
      from NETWORK import my_mqtt_usr, my_mqtt_pwd, my_mqtt_srv
      if len(self._broker) == 0:
        self._broker = my_mqtt_srv
      self._client = MQTTClient(self._clientID, self._broker)
      self._client.set_last_will(self._rootTopic, b'link/down')
      try:
        if self._client.connect() == 0:
          print("[{0:>12}] {1}".format("topic", self._rootTopic))
          self._client.publish(self._rootTopic, b'link/up')
          self._isReady = True
      except:
        print("Error: MQTT brocker {} not responding".format(self._broker))
    print("... done." if self._isReady else "... FAILED")

  def publishDict(self, t, d):
    """ Publish a dictionary as a message under <standard topic>/<t>
    """
    if self._isReady:
      self._client.publish(self._rootTopic +t, ujson.dumps(d))

  def publish(self, t, m):
    """ Publish a message under <standard topic>/<t>
    """
    if self._isReady:
      try:
        self._client.publish(self._rootTopic +t, m)
      except OSError as error:
        if error.args[0] != errno.ECONNRESET:
          print("Error: publish caused {0}".format(error.args[0]))

  def disconnect(self):
    """ Disconnect from MQTT broker
    """
    if self._isReady:
      self._client.disconnect()
      self._isReady = False

# ----------------------------------------------------------------------------
