#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
#
# The MIT License (MIT)
# Copyright (c) 2020 Thomas Euler
#
# The port to which the MicroPython board is connected
#   --port or -p
# ---------------------------------------------------------------------
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import json
import time
import pyboard
import numpy as np
import pygame
import front_pygame as front

WIN_SIZE  = (1, 2) # in standard widget sizes
WIN_POS   = (0, 0)
WIN_NAME  = "amg8833_test"

RANGE_T_C = (19, 34)
PIX_SIZE  = (18, 18)

script_initialize_amg8833 = [
  'from robotling_lib.driver.amg88xx import AMG88XX',
  'import robotling_lib.platform.esp32.busio as busio',
  'import robotling_lib.platform.esp32.dio as dio',
  'power5V = dio.DigitalOut(16, value=True)',
  'i2c = busio.I2CBus(400000, 22, 23)',
  'amg = AMG88XX(i2c)',
]

script_get_image = [
  'img_raw = list(amg.pixels_64x1)',
  'print(img_raw)'
]

script_import_blob = [
  'import robotling_lib.misc.blob_ulab2 as blob'
]

script_get_blobs = [
  'blob_list = blob.find_blobs_timed(img_raw, (8, 8))',
  'print(blob_list)'
]

# ---------------------------------------------------------------------
class FrontEndGUI(object):

  def __init__(self, pyb):
    """ Initialize GUI window
    """
    # Create window
    self.Win = front.Window(WIN_POS, WIN_SIZE, WIN_NAME, font_fact=1.6)
    self.Win.onEvent = self.onEventCallback

    # PyBoard instance
    self._pb = pyb

    # Define IR camera widget
    self.CameraIR = front.WidgetCamera(self.Win, (0 , 0), 0)
    self.CameraIR.setLabels("Sensors", "8x8 thermal camera")
    self.CameraIR.setValProperties("T", "°C", RANGE_T_C, PIX_SIZE, False)
    self.CameraIR.draw(cmap_name="inferno")
    self._doSmooth = False

  def onEventCallback(self, event):
    if event.type == pygame.KEYDOWN:
      if event.key == 115: # "s"
        self._doSmooth = not self._doSmooth
        self.CameraIR.vals[0]["smooth"] = self._doSmooth

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def run(self):
    """ Run main loop
    """
    while(True):
      # Update GUI
      self.update()
      self.Win.update()

      # Check if user wants to quit
      if self.Win.doQuit():
        return

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def update(self):
    """ Update GUI
    """
    # Thermal camera image
    data, blobs = get_image_blobs(self._pb)
    self.CameraIR.update(data, (8,8), blobs)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def kill(self):
    """ Destroy window
    """
    self.Win.close()

# ---------------------------------------------------------------------
def parseCmdLn():
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_argument('-p', '--port', type=str, default="COM3")
  return parser.parse_args()

# ---------------------------------------------------------------------
def run_on_board(pb, code, wait_s=0, no_print=False):
  """ Run the lines of code in the list `code` on the connected
      MicroPython board
  """
  for ln in code:
    res = pb.exec(ln)
    if len(res) > 0 and not no_print:
      res = res[:-2].decode()
      print(res)
  if wait_s > 0:
    time.sleep(wait_s)
  return res

def get_image_blobs(pb):
  """ Get an image from the sensor connected to the MicroPython board,
      find blobs and return the image as well as a list of blobs
  """
  raw = json.loads(run_on_board(pb, script_get_image, no_print=True))
  img = np.flip(np.transpose(np.reshape(raw, (8, 8))))
  blobs = json.loads(run_on_board(pb, script_get_blobs, no_print=False))
  return img, blobs

# ---------------------------------------------------------------------
if __name__ == '__main__':
  # Check for command line parameter(s)
  args = parseCmdLn()
  port = args.port

  # Connect to board
  try:
    pb = pyboard.Pyboard(port)
    pb.enter_raw_repl()
    print("Connected to MicroPython board via {0}".format(port))
  except pyboard.PyboardError:
    print("ERROR: Could not connect to board")
    exit()

  # Connect to AMG8833 sensor via the board
  print("Searching for sensor ...")
  _ = run_on_board(pb, script_initialize_amg8833, wait_s=0.4)
  _ = run_on_board(pb, script_import_blob)

  # Initialize GUI
  gui = FrontEndGUI(pb)

  print("Starting loop ...")
  gui.run()

  # Clean up
  print("Cleaning up ...")
  gui.kill()
  pb.exit_raw_repl()
  print("... done.")

# ---------------------------------------------------------------------
