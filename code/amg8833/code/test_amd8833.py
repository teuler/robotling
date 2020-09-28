import time
from robotling_lib.driver.amg88xx import AMG88XX
import robotling_lib.platform.esp32.busio as busio
import robotling_lib.platform.esp32.dio as dio

# Die 5V-Spannungsversorgung muss aktiviert werden, falls die Wärmebildkamera
# an ein Robotling-Board angeschlossen ist
dio.DigitalOut(16, value=True)

try:
  # I2C-Objekt erstellen, 400 kHz Busfrequenz, SCL an Pin 22, SDA and Pin 23
  i2c = busio.I2CBus(400000, 22, 23)

  # Wärmebildkamera-Treiber starten und etwas warten
  amg = AMG88XX(i2c)
  time.sleep_ms(500)

  # Bild einlesen, es entspricht einer 1D Liste von 64 (8x8 pixel)
  # Temperaturwerten (in °Celsius)
  img = list(amg.pixels_64x1)
  print("Image:", img)

  print("Find blobs (just Python):")
  import robotling_lib.misc.blob as blob
  res = blob.find_blobs_timed(img, (8, 8))
  print("Blobs:", res)

  print("Find blobs (ulab):")
  import robotling_lib.misc.blob_ulab as blob
  res = blob.find_blobs_timed(img, (8, 8))
  print("Blobs:", res)

  print("Find blobs (C code in ulab):")
  import robotling_lib.misc.blob_ulab2 as blob
  res = blob.find_blobs_timed(img, (8, 8))
  print("Blobs:", res)

finally:
  i2c.deinit()
