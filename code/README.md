This folder contains python code that runs on a PC, e.g. to communicate with a robotling via WLAN, as well as hexbug/robotling configuration examples:  
- `test_mqtt.py` - Simple example script that illustrates how to receive MQTT telemetry from a robotling
- `hexbug_relay.py` Script that resends HexBug robotling MQTT messages under "proper" topics
- "Typical" configuration examples for different robotlings:
  - `hexbug_config.py__blue_1IR` - one IR distance sensor, WiFi, LSM9DS0-type compass
  - `hexbug_config.py__black3IR` - three [smaller IR sensors](https://github.com/teuler/robotling/wiki/Sensoren-etc#GP2Y0AF15X), WiFi, CMPS12-type compass, and an [AMG88XX GRID-Eye IR 8x8 thermal camera](https://learn.adafruit.com/adafruit-amg8833-8x8-thermal-camera-sensor?view=all) from Adafruit


The subfolder `robotling` contains the code that runs on the roboter.  

The folder `modules/blob` contains the C code for a simple module that takes a camera image (i.e. from the thermal camera), detects "blobs" and returns them as a list. This module has to be built into the Micropython firmware; see [notes](https://github.com/teuler/robotling/tree/master/code/modules/blob) in the `module/blob` folder.  

The subfolder `firmware` contains precompiled images of the current MicroPython firmware including `umqtt` and `blob`.

