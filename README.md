# robotling

"robotling" is a simple circuit board to control small robots. Check out the videos (videos [1](https://youtu.be/wil41YtIeN8), [2](https://youtu.be/cLstXW3RsBA), [3](https://www.youtube.com/watch?v=XF0T9Dlb07M), and with thermal camera, [4](https://youtu.be/qpSQO51BuJs), [5](https://youtu.be/tlYXab0FZrY)) and find the details in the German [wiki](https://github.com/teuler/robotling/wiki). 

<p align="center">
  <img width="720" src="https://github.com/teuler/robotling/blob/master/pictures/IMG_5737a.png"></img>
</p>

### Release Notes

<img align="right" width="320" src="https://github.com/teuler/robotling/blob/master/pictures/pic_board_1_2_a_sm.png"></img>

* 2021-09-22
  - New firmware based on MicroPython v1.17 (w/`ulab`)
  - 
* 2021-05-02
  - Some refactoring: Configuration parameters now clearly marked as such (`cfg.xxx`)

* 2021-05-01 - Release v1.9

* 2021-04-26
  - [Instructions](https://github.com/teuler/robotling/wiki/Adding-native-modules-to-MicroPython-(ESP32)) for building MicroPython (release 1.14) w/`ulab` and `umqtt` updated. 
  - New pre-built ESP32 [firmware](https://github.com/teuler/robotling/tree/master/code/firmware_esp32) based on MicroPython v1.14 (w/`ulab` and `umqtt`)
  - Small bug fixes, now compatible w/ MicroPython v1.14 and "vanilla" v1.15 ([esp32-20210420-unstable-v1.15.bin](https://micropython.org/resources/firmware/esp32-20210420-unstable-v1.15.bin)).
  - Now uses `RobotlingBase` (from [`robotling_lib`](https://github.com/teuler/robotling_lib)), so better separate standard hardware and additional hardware defined in `devices` (in [hexbug_config.py](https://github.com/teuler/robotling/blob/master/code/robotling/hexbug_config.py)). 
  - As [`robotling_lib`](https://github.com/teuler/robotling_lib) now includes `simple.py` and `robust.py` from [micropython-lib](https://github.com/micropython/micropython-lib) as fall-back, MQTT can now be used with the standard MicroPython firmware, which does not inlcude `umqtt`.
  - Added [instructions](https://github.com/teuler/robotling/wiki/Adding-native-modules-to-MicroPython-(ESP32)#-building-micropython-v115-and-higher-with-ulab-included) how to build the ESP32 firmware for MicroPython 1.15 with `ulab` included. 

* 2021-04-05 
  - Link to new Make: article added. 
* 2020-08-30 (Blob detection revisited)
  - [Three versions](https://github.com/teuler/robotling/wiki/Verhalten#SeekBlob) of the blob detection and image filter code, demonstrating differences in speed between a pure MicroPython version and those that use [`ulab`](https://micropython-ulab.readthedocs.io/en/latest/ulab.html) or even user-written C functions added to `ulab`.
* 2020-08-21 (Refactoring)
  - Since it was difficult to maintain different versions of the robotling code all accessing the same set of driver etc. libraries, these files have now been moved to a separate repository ([`robotling_lib`](https://github.com/teuler/robotling_lib)). 
  - Wiki updated accordingly.
  - New Wiki page on [adding native modules to MicroPython](https://github.com/teuler/robotling/wiki/Adding-native-modules-to-MicroPython-(ESP32)).

* 2020-07-04 (Code updates)
  - Simple GUI to show robot status via MQTT (`hexbug.gui.py`) 
  - Support for [TinyPICO](https://www.tinypico.com/) added
  - Configurations for different hardware combinations
  - General class to manage and control a set of servos ([`servo_manager.py`](https://github.com/teuler/robotling/blob/master/code/robotling/motors/servo_manager.py)) and inprovements in Servo class
   - Class for [PCA9685 16-channel servo driver](https://www.adafruit.com/product/815) ([`servos_pca9685.py`](https://github.com/teuler/robotling/blob/master/code/robotling/motors/servos_pca9685.py))
   - Class for [18-channel Mini Maestro servo driver](https://www.pololu.com/product/1354) ([`servos_mini_maestro_18.py`](https://github.com/teuler/robotling/blob/master/code/robotling/motors/servos_mini_maestro_18.py))

* 2019-12-30 (requires MicroPython 1.12.x)
  - [Thermal camera](https://github.com/teuler/robotling/wiki/Sensoren-etc#AMG88XX) support added ([`amg88xx.py`](https://github.com/teuler/robotling/blob/master/code/robotling/driver/amg88xx.py) and [`camera_thermal.py`](https://github.com/teuler/robotling/blob/master/code/robotling/sensors/camera_thermal.py); new behaviour [`lookAtBlob`](https://github.com/teuler/robotling/wiki/Verhalten#SeekBlob) using the thermal camera (see videos [4](https://youtu.be/qpSQO51BuJs), [5](https://youtu.be/tlYXab0FZrY)). _Note that the blob detection (not the camera itself) requires a custom MicroPython [firmware](https://github.com/teuler/robotling/tree/master/code/firmware_esp32) that includes the module [`blob`](https://github.com/teuler/robotling/tree/master/code/modules/blob) (coded in C for speed reasons)._  
  - Configuration file split into fixed ([`hexbug_global.py`](https://github.com/teuler/robotling/blob/master/code/robotling/hexbug_global.py)) and robot-dependent definitions
  - Code adapted to MicroPython release 1.12.x, including hardware I2C bus option added and native code generation added for time critical routines (ESP32 only)
  - PWM frequencies for servos and DC motors are now defined in `robotling_board.py` to account for the fact that the ESP32 port supports only a single frequency for all standard PWM pins. In addition, [`drv8835.py`](https://github.com/teuler/robotling/blob/master/code/robotling/driver/drv8835.py) now uses the RMT feature of the ESP32 for PWM to run the DC motors. This allows using a different frequency than the normal PWM functions.

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
