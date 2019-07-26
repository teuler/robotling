# robotling

[<img align="right" src="https://github.com/teuler/robotling/blob/master/pictures/IMG_4857a_sm.png" alt="Drawing" width="320"/>](https://github.com/teuler/robotling/blob/master/pictures/IMG_4857a.png)

"robotling" is a simple circuit board to control small robots. Check out the videos ([video 1](https://youtu.be/wil41YtIeN8), [video 2](https://youtu.be/cLstXW3RsBA)) and find the details in the German [wiki](https://github.com/teuler/robotling/wiki). 

### Release Notes

* 2019-07-25
  - Now an option was added to send telemetry via WLAN using the MQTT protocol (ESP32 only).
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
