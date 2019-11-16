# robotling

"robotling" is a simple circuit board to control small robots. Check out the videos (videos [1](https://youtu.be/wil41YtIeN8), [2](https://youtu.be/cLstXW3RsBA), and [3](https://www.youtube.com/watch?v=XF0T9Dlb07M)) and find the details in the German [wiki](https://github.com/teuler/robotling/wiki). 

<p align="center">
  <img width="280" height="376" src="https://github.com/teuler/robotling/blob/master/pictures/IMG_4857a_sm.png"></img>
  <img width="280" height="376" src="https://github.com/teuler/robotling/blob/master/pictures/IMG_5354.jpg"></img>
  <img width="280" height="376" src="https://github.com/teuler/robotling/blob/master/pictures/pic_board_1_2_a_sm.png"></img>
</p>

### Atom and pymakr under Linux (Ubuntu 18.04)

Currently, the plugin "pymakr" causes errors if install using the usual way from inside Atom. Instead, download the `develop` branch from [GitHub](https://github.com/pycom/pymakr-atom) and follow the instructions under "Manual install" in the readme file.

### Release Notes

* 2019-11-15
  - New articel in the German Make: magazine (["Krabbelroboter sendet Telemetrie"](https://www.heise.de/select/make/2019/7/1573927054956141)). 
* 2019-08-31
  - New type of Sharp sensor added (GP2Y0AF15X, 1.5-15 cm) to `sensors\sharp_ir_ranging.py`. This allows using a triple IR distance sensor array such that the robot's head does not need to scan sideways.
  - I2C frequency increased to 400 kHz in `robotling_board.py`. The I2C frequency used is now also printed when the robot boots.
  - Robotling v1.3 board in `robotling_board_version.py`.
  - In case of an uncaught Python exception, the firmware tries to send a last MQTT message containing the traceback, allowing to get information on code errors even when the robot is not attached via USB.
  - Wiki page [Telemetrie über MQTT](https://github.com/teuler/robotling/wiki/Telemetrie-%C3%BCber-das-MQTT-Protokoll)
  
* 2019-07-25
  - Now an option was added to send telemetry via WLAN using the MQTT protocol (ESP32 only). An example script (`test_mqtt.py`) that demonstrates how to subcribe to robotling telemetry on a PC was added to `../code`. 
  - `hexbug.py` - Bias factor (`IR_SCAN_BIAS_F`) added to the configuration file `hexbug_config.py`; it allows correcting for a direction bias in the turning motor. Also, the scan scheme was slightly changed from "left-right-center" to "left-center-right-center", which helps the robot to walk more straight.
  - `telemetry.py`- Encapsules the MQTT functionality. 
  - `main.py` - Simple "memory" was added to remember the direction of successful turns (experimental).
  - `robotling.py` - Now the keyword "wlan" can be added as a device to `MORE_DEVICES` in `hexbug_config.py` to activate the network (instead of changing `boot.py`)
* 2019-07-22
  - Robotling code moved from `../code` to `../code/robotling`
* 2019-07-16 - Release v1.7
  - New wiki pages ['Sensors etc.'](https://github.com/teuler/robotling/wiki/Sensoren-etc) with supported sensors and ['Verhalten'](https://github.com/teuler/robotling/wiki/Verhalten) with behaviours added
  - Wiki pages ['Demo'](https://github.com/teuler/robotling/wiki/Demo) and ['Erweiterungen und Modifikationen'](https://github.com/teuler/robotling/wiki/Erweiterungen-und-Modifikationen) updated 
  - Code Release [v1.7](https://github.com/teuler/robotling/releases)
* 2019-05-18 - Release v1.6
  - Added new "behaviour" (take a nap) based on deepsleep/lightsleep support for ESP32
  - Cleaned up the code
  - Changed `hexbug_config.py`to make it also standard Python compatible (for future extension)
  - Now uses `getHeading3D` instead of `getPitchRoll` to determine if the robot is tilted; the additional 
    compass information (heading) is saved (for future extension).
  - Driver for LSM9DS0 magnetometer/accelerometer/gyroscope added.
* 2019-03-17 - Release v1.5
  - Some code improvements (handing devices, cleaning up)
  - Tested w/ MicroPython v1.10
  - New pictures
  - A new wiki page with extentions and modifications
* 2019-03-02
  - New pictures, annotated pictures of board v1.2
  - some new text on memory and performance
* 2019-01-12 
  - A few bug fixes
  - More drivers (dotstar, VL6180X). 
  - Works now also with the M4 Express Feather from Adafruit (and CircuitPython).
* 2018-12-28 - Release v1.3  
  Eliminated the need for a timer. Added `spin_ms()`, which needs to be called once per loop and instead of `sleep_ms()` to keep board
  updated. This solution is superior to the use of a timer, because (i) it is deterministic (avoids randomly interrupting the program 
  flow and, hence, inconsistencies) and (ii) makes the code compatible to CircuitPython, which does not (yet?) support timers.
* 2018-12-24 - Release v1.2  
  Now board v1.2 included, some code refactoring and improvements
* 2018-11-29 - Release v1.1  
  First complete version for board v1.0 and huzzah32
* 2018-11-18 - Initial release 

### Unresolved Issues

  - Tilt correction and calibration for LSM303 and LSM9DS0 compass function is not yet implemented.
