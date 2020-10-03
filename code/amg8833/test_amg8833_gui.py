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
script_get_blob_list = [
  'blob_list = blob.find_blobs_timed(img_raw, (8, 8))'
]
script_print_blob_list = [
  'print(blob_list)'
]

# ---------------------------------------------------------------------
class FrontEndGUI(object):

  def __init__(self, pyb):
    """ Initialize GUI window
    """
    # Create window
    self.Win = front.Window(WIN_POS, WIN_SIZE, WIN_NAME, font_fact=1.0)
    self.Win.onEvent = self.onEventCallback

    # PyBoard instance
    self._pb = pyb
    self._t_ms = 0
    self._info = "MPy"

    # Define IR camera widget
    self.CameraIR = front.WidgetCamera(self.Win, (0 , 0), 0)
    self.CameraIR.setLabels("AMG8833 8x8 thermal camera", "n/a")
    self.CameraIR.setValProperties("T", "°C", RANGE_T_C, PIX_SIZE, False)
    self.CameraIR.draw(cmap_name="inferno")
    self._doSmooth = False

  def onEventCallback(self, event):
    if event.type == pygame.KEYDOWN:
      if event.key == 115: # "s"
        self._doSmooth = not self._doSmooth
        self.CameraIR.vals[0]["smooth"] = self._doSmooth
      elif event.key == 49: # "1"
        _ = run_on_board(pb, ["import robotling_lib.misc.blob as blob"])
        self._info = "MPy"
      elif event.key == 50: # "2"
        _ = run_on_board(pb, ["import robotling_lib.misc.blob_ulab as blob"])
        self._info = "MPy +ulab"
      elif event.key == 51: # "3"
        _ = run_on_board(pb, ["import robotling_lib.misc.blob_ulab2 as blob"])
        self._info = "ulab +C code"

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
    data, blobs, t_ms = get_image_blobs(self._pb)
    self._t_ms = (self._t_ms +t_ms) /2
    s = "{0} blobs, {1:6.3f} ms/call ({2})".format(len(blobs), self._t_ms, self._info)
    self.CameraIR.setLabels("AMG8833 8x8 thermal camera", s)
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
    if len(res) > 0:
      res = res[:-2].decode()
      if not no_print:
        print(res)
  if wait_s > 0:
    time.sleep(wait_s)
  return res

def get_image_blobs(pb):
  """ Get an image from the sensor connected to the MicroPython board,
      find blobs and return the image, a list of blobs, and the time it
      took to find the blobs (in [ms])
  """
  raw = json.loads(run_on_board(pb, script_get_image, no_print=True))
  img = np.flip(np.transpose(np.reshape(raw, (8, 8))))
  time_str = run_on_board(pb, script_get_blob_list, no_print=True)
  t_ms = float(time_str.split("= ")[1].split("m")[0])
  blobs_str = run_on_board(pb, script_print_blob_list, no_print=True)
  blobs_str = blobs_str.replace("nan", "0")
  blobs = json.loads(blobs_str.replace('(', '[').replace(')', ']'))
  return img, blobs, t_ms

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
  _ = run_on_board(pb, ["import robotling_lib.misc.blob as blob"])

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
