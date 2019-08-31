# Publish an MQTT message
# (Script for HUZZAH32 with ESP32)
#
# 1) Replace in the follwing script `wlan_ssid` with your WLAN SSID,
#    `wlan_pwd` with the respective WLAN password, and `mqtt_broker`
#    with the IP address of the MQTT broker (the same as under point 3).
# 2) In a shell, run
#    > .\mosquitto.exe -v
#    from the mosquitto program folder
# 3) In a second shell, run
#    > .\mosquitto_sub.exe -h "IP" -t "client_ID/countdown"
#    from the mosquitto program folder. Replace `IP` with the IP of the
#    broker (e.g. the PC the EPS32 is programmed with) and `client_ID`
#    with the GUID of your ESP32. This GUID can be determined using:
#    > import machine
#    > import binascii
#    > binascii.hexlify(machine.unique_id())
#    For example, if `b'b4e62da1dccd'` is printed, the GUID is
#    `b4e62da1dccd`
# 4) Run this script on the ESP32
#
import network
import time
from machine import Pin, unique_id
from binascii import hexlify
from umqtt.robust import MQTTClient

WLAN_SSID   = "Elchland3"           # WLAN-Name
WLAN_PWD    = "LaufenImWald5519"    # WLAN-Passwort
MQTT_BROKER = "mqtt.eclipse.org"    # IP-Adresse oder URL des MQTT-Brokers
TOPIC       = b"countdown"          # Topic zum Veröffentlichen von Nachrichten
CLIENT_ID   = hexlify(unique_id())  # eindeutige ID des Moduls bestimmen

# Funktion, um eine WLAN-Verbindung herzustellen
def do_connect():
  wlan = network.WLAN(network.STA_IF)
  if not wlan.isconnected():
    wlan.active(True)
    wlan.connect(WLAN_SSID, WLAN_PWD)
    while not wlan.isconnected():
      pass

if __name__ == "__main__":
  # Mit dem WLAN verbinden und einen MQTT-Client erzeugen
  do_connect()
  client = MQTTClient(CLIENT_ID, MQTT_BROKER)
  try:
    # Mit dem MQTT-Client verbinden
    client.connect()
    print("Connected to `{0}`".format(MQTT_BROKER))
    try:
      # Die Zahlen von 10 bis 1 unter dem festgelegten Topic veröffentlichen
      for i in range(10, 0, -1):
        msg = str(i)
        print("Publishing `{0}` under topic `{1}`".format(msg, TOPIC))
        client.publish(CLIENT_ID +"/" +TOPIC, msg)
        time.sleep(1.0)
    finally:
      # Verbindung zum MQTT-Broker beenden
      client.disconnect()
      print("Done.")
  except OSError as err:
    print("Error: Cannot connect to MQTT brocker ({0})".format(err))
