### The `blob` module

The module `blob` contains a single function which takes a camera image (as a linear list, here `img`), tries to detect "objects" (blobs), and returns a list of these objects. The following is just a code example; for complete code, see [`hexbug.py`](https://github.com/teuler/robotling/blob/master/code/robotling/hexbug.py).
   ```
   import blob
   import driver.amg88xx as amg88xx    # IR 8x8 thermal camera (AMG88XX) driver
   [...]
   AMG88XX = amg88xx.AMG88XX(I2C)      # with I2C being an initialized I2C bus instance
   [...]
   img = list(AMG88XX.pixels_64x1)
   blobList = blob.detect(img, (8,8), (0, 0.5) )
   ```

`img` contains a single 8x8 frame from the thermal camera with a temperature values (°C) for each pixel, formated as a 1D list:
   ```
   [21, 21, 22, 23, 23, 21, 20, 20, 21, 21, 24, 24, 25, 22, 21, 21, 20, 21, 23, 25, 26, 25, 
    21, 21, 21, 21, 23, 26, 27, 26, 24, 22, 21, 22, 23, 25, 26, 28, 27, 28, 21, 21, 23, 26, 
    26, 26, 27, 26, 21, 21, 22, 23, 23, 23, 22, 23, 21, 22, 22, 21, 22, 21, 22, 23]
   ```
After blob detection - if blobs were found - `blobList` contains a list of blobs, with each blob represented by a tuple of blob area, index, probability (see below), and blob center position in the frame:   
   ```
   [(13, 1, 0.6723409, 4.0, 4.846154)]
   ``` 

_**Important**: This code is preliminary and has not been fully optimized/debugged (see issues below)._

### Known Issues with `blob`:

- Only filter mode 0 (=no filtering) works currently; the other filters crash the ESP32
- The "probability" for a blob can exceed 1.0
