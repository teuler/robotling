# robotling

"robotling" is a simple circuit board to control small robots.

Please check out the [video](https://youtu.be/wil41YtIeN8) and find the details in the [wiki](https://github.com/teuler/robotling/wiki). 

### Release Notes

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
