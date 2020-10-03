from time import ticks_us, ticks_diff, sleep_ms
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
  sleep_ms(500)

  # Beispielbild einlesen, es entspricht einer 1D Liste von 64 (8x8 pixel)
  # Temperaturwerten (in °Celsius)
  img = list(amg.pixels_64x1)
  print("Image:", img)
  print()

  def find_some_blobs(n):
    # Liest `n` Bilder ein und versucht Blobs zu finden. Dazu wird die
    # Funktion `find_blobs` aus dem Modul `blob` benutzt; `find_blobs` läuft
    # auf dem Mikrokontroller. Die gefundenen Blobs und die mittlere Lauf-
    # zeit von `find_blobs` werden ausgegeben.
    delta = 0
    for i in range(n):
      # Bild einlesen
      img = list(amg.pixels_64x1)

      # Blobs suchen
      # `find_blobs` liefert eine Liste, in der jeder Eintrag aus einer Liste
      # von Parametern besteht, die einen Blob beschreiben:
      # [ID, area, x, x, prob], wobei `ID` der Index des Blobs ist, `area` die
      # Größe, `x`,`y` die Position und `prob` eine Abschätzung, wie sicher
      # die Funktion ist, dass dies ein Blob ist.
      t = ticks_us()
      res = blob.find_blobs(img, (8, 8))
      delta += ticks_diff(ticks_us(), t)

      # Blobs anzeigen, falls welche gefunden wurden
      s = ""
      for b in res:
        if b[1] > 1:
          s += "{0:.0f}-pixel blob at {1:.1f},{2:.1f} ".format(b[1], b[2], b[3])
      if len(s) > 0:
        print("{0:2.0d}: {1}".format(i, s))

      # Kurz warten
      sleep_ms(100)

    # Mittlere Dauer eines `find_blobs`-Aufrufs ausgeben
    print('{:6.3f}ms per call (average)\n'.format(delta/(n*1000)))


  print("Find blobs (just Python):")
  import robotling_lib.misc.blob as blob
  find_some_blobs(100)

  print("Find blobs (ulab):")
  import robotling_lib.misc.blob_ulab as blob
  find_some_blobs(100)

  print("Find blobs (C code in ulab):")
  import robotling_lib.misc.blob_ulab2 as blob
  find_some_blobs(100)

finally:
  i2c.deinit()
