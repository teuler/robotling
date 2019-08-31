# Subscribe to an MQTT message and switch onboard LED accordingly
# (Script for HUZZAH32 with ESP32)
#
# 1) Replace in the follwing script `wlan_ssid` with your WLAN SSID,
#    `wlan_pwd` with the respective WLAN password, and `mqtt_broker`
#    with the IP address of the MQTT broker (the same as under point 3).
# 2) In a shell, run
#    > .\mosquitto.exe -v
#    from the mosquitto program folder
# 3) In a second shell, run
#    > .\mosquitto_pub.exe -h "IP" -t "led" -m "0"
#    from the mosquitto program folder. Replace `IP` with the IP of the
#    broker (e.g. the PC the EPS32 is programmed with) and the string after
#    `-m` (the message) with `0` and `1` toi switch the red user LED on the
#    ESP32 board off or on, respectively.
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
TOPIC       = b"led"                # Aboniertes Topic
CLIENT_ID   = hexlify(unique_id())  # eindeutige ID des Moduls bestimmen

# Funktion, um eine WLAN-Verbindung herzustellen
def do_connect():
  wlan = network.WLAN(network.STA_IF)
  if not wlan.isconnected():
    wlan.active(True)
    wlan.connect(WLAN_SSID, WLAN_PWD)
    while not wlan.isconnected():
      pass

# Funktion, die automatisch beim Eintreffen von Nachrichten aufgerufen wird
def on_message(topic, msg):
  print("Received message `{0}` under topic {1}".format(msg, topic))
  if topic == CLIENT_ID +"/" +TOPIC:
    # LED je nach dem Nachrichteninhalt an- oder ausschalten
    led.value(int(msg))
    print("LED switched {0}".format("OFF" if int(msg) == 0 else "ON"))

if __name__ == "__main__":
  # Mit dem WLAN verbinden, einen MQTT-Client erzeugen und diesem die Funktion
  # mitteilen, die beim Eintreffen von Nachrichten aufgerufen werden solll
  do_connect()
  client = MQTTClient(CLIENT_ID, MQTT_BROKER)
  client.set_callback(on_message)
  # LED-Objekt für Pin #13 (rote LED auf dem HUZZAH32-Board) anlegen
  led = Pin(13, Pin.OUT, value=0)
  try:
    # Mit dem MQTT-Client verbinden und TOPIC abonnieren
    client.connect()
    client.subscribe(CLIENT_ID +"/" +TOPIC)
    print("Connected to `{0}`, subscribed to `{1}`".format(MQTT_BROKER, TOPIC))
    try:
      while True:
        # Nachprüfen, ob neue MQTT-Nachrichten eingetroffen sind; anstatt zu
        # warten, kann hier auch etwas anderes erledigt werden
        client.check_msg()
        time.sleep(0.02)
    finally:
      # Verbindung zum MQTT-Broker beenden
      client.disconnect()
      print("Done.")
  except OSError as err:
    print("Error: Cannot connect to MQTT brocker ({0})".format(err))
