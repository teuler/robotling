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
# 2019-09-01, Optionally encrypt messages, defined by `my_mqtt_encrypt_key`
#             and `my_mqtt_encrypt_CBC` in `NETWORK.py`. Also. SSL
#             connections to the broker are possible
#
# ----------------------------------------------------------------------------
import network
import ujson
import errno
from umqtt.robust import MQTTClient
from misc.helpers import timed_function

__version__ = "0.1.2.0"

# ----------------------------------------------------------------------------
class Telemetry():
  """Telemetry via the MQTT protocoll."""

  def __init__(self, ID, broker=""):
    self._isReady = False
    self._broker = broker
    self._clientID = ID
    self._client = None
    self._rootTopic = self._clientID +"/"
    self._doEncrypt = False
    try:
      from NETWORK import my_mqtt_encrypt_key, my_mqtt_encrypt_CBC
      if my_mqtt_encrypt_key is not None:
        from ucryptolib import aes
        self.AES = aes(my_mqtt_encrypt_key, 2, my_mqtt_encrypt_CBC)
        self._doEncrypt = True
    except ImportError:
      pass

  def connect(self):
    """ Try to connect to MQTT broker
    """
    print("Initializing telemetry via MQTT ...")
    self.sta_if = network.WLAN(network.STA_IF)
    if not self.sta_if.isconnected():
      print("Error: Not connected to network")
    else:
      from NETWORK import my_mqtt_usr, my_mqtt_pwd, my_mqtt_srv, my_mqtt_port
      if len(self._broker) == 0:
        self._broker = my_mqtt_srv
      _sll = my_mqtt_port == 8883
      self._client = MQTTClient(self._clientID, self._broker, ssl=_sll)
      self._client.set_last_will(self._rootTopic, b'link/down')
      try:
        if self._client.connect() == 0:
          print("[{0:>12}] {1}".format("topic", self._rootTopic))
          self._client.publish(self._rootTopic, b'link/up')
          self._isReady = True
      except:
        print("Error: MQTT brocker {} not responding".format(self._broker))
    print("... done." if self._isReady else "... FAILED")
    return self._isReady

  def subscribe(self, topic, callBack):
    """ Subscribe to topic and define call back function
    """
    self._client.set_callback(callBack)
    t = self._rootTopic +topic
    self._client.subscribe(t)
    print("Subscribed to `{0}`".format(t))

  def spin(self):
    """ Needs to be called frequently to check for new messages
    """
    self._client.check_msg()

  def publishDict(self, t, d):
    """ Publish a dictionary as a message under <standard topic>/<t>
    """
    if self._isReady:
      if not self._doEncrypt:
        self._client.publish(self._rootTopic +t, ujson.dumps(d))
      else:
        s = ujson.dumps(d)
        b = self.AES.encrypt(bytearray(s +" "*(16 -len(s) %16)))
        self._client.publish(self._rootTopic +t, b)

  def publish(self, t, m):
    """ Publish a message under <standard topic>/<t>
        TODO: implement encryption here as well
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

  @property
  def connected(self):
    return self._isReady

# ----------------------------------------------------------------------------
