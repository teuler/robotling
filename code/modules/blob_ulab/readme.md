## Fast blob detection

Two functions for blob detection were added to the user module of [ulab](https://github.com/v923z/micropython-ulab): 

- `user.blob(img, dxy, nsd)` accepts an image (`img`), e.g. from the thermal camera, the image shape (`dxy` as 2-element tuple), and a threshold (`nsd`). The image must be an `nparray` (see [ulab](https://micropython-ulab.readthedocs.io/en/latest/index.html)). It then tries to detect "objects" (blobs, that is continuous areas with pixel values above the threshold), and returns a list of these objects. 
- `user.spatial_filter(img, kernel, dxy)` accepts an image (`img`) and a spatial kernel (`kernel`) as well as the image shape (`dxy` as 2-element tuple). The image and the kernel must be of the `nparray` type (see [ulab](https://micropython-ulab.readthedocs.io/en/latest/index.html)). The function convolves the image with the kernel and returns the filtered image.

For a code example, see [`blob_ulab2.py`](https://github.com/teuler/robotling_lib/blob/master/misc/blob_ulab2.py) and [`camera_thermal.py`](https://github.com/teuler/robotling_lib/blob/master/sensors/camera_thermal.py).

To acquire example images:
   ```
   import driver.amg88xx as amg88xx    # IR 8x8 thermal camera (AMG88XX) driver
   [...]
   AMG88XX = amg88xx.AMG88XX(I2C)      # with I2C being an initialized I2C bus instance
   [...]
   img = list(AMG88XX.pixels_64x1)
   ```
With `img` containing a single 8x8 frame from the thermal camera with a temperature values (°C) for each pixel, formated as a 1D list:
   ```
   [21, 21, 22, 23, 23, 21, 20, 20, 21, 21, 24, 24, 25, 22, 21, 21, 20, 21, 23, 25, 26, 25, 
    21, 21, 21, 21, 23, 26, 27, 26, 24, 22, 21, 22, 23, 25, 26, 28, 27, 28, 21, 21, 23, 26, 
    26, 26, 27, 26, 21, 21, 22, 23, 23, 23, 22, 23, 21, 22, 22, 21, 22, 21, 22, 23]
   ```
   
`blob.detect()` requires an image frame (as a linear list, see below), the frame size as a tuple (e.g. `(8,8)` for an 8x8 pixel frame) and a parameter tuple, consisting of the filter mode (`0`, no filter) and a threshold (`0.5`). The latter defines the number of standard deviations a blob maximum must higher that the mean frame intensity to be included as a valid blob.     
   ```
   import ulab as np
   from ulab import user
   [...]
   
   # Gaussian smooth
   np_kernel = np.array([[0.0625,0.125,0.0625], [0.125, 0.25, 0.125 ], [0.0625,0.125,0.0625]])
   np_img = np.array(img)
   dxy = (8, 8)
   nsp = 1.1
   np_imgf = user.spatial_filter(np_img, np_kernel, dxy)
   bloblist = user.blobs(np_imgf, dxy, nsp)
   ```
After blob detection - if blobs were found - `blobList` contains a list of blobs, with each blob represented by a tuple of blob area, index, probability (basically, a z-score), and blob center position in the frame:   
   ```
   [(13, 1, 0.6723409, 4.0, 4.846154)]
   ``` 

_**Important**: This code is preliminary and has not been fully optimized/debugged (see issues below)._

### Building the ESP32 MicroPython firmware with modified `ulab`

For a detailed description, see [here](https://github.com/teuler/robotling/wiki/Adding-native-modules-to-MicroPython-(ESP32)).
