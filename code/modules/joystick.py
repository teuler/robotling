##!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# joystick.py
# Joystick class
#
# The MIT License (MIT)
# Copyright (c) 2020 Thomas Euler
# 2012-2017,  First version (w/ Arduino translating)
# 2020-06-05, Update; new wireless standard controller, based on pygame
#
# ----------------------------------------------------------------------------
import pygame
import numpy as np

LIM             = 0.1

AXS_LX          = 0
AXS_LY          = 1
AXS_RX          = 4
AXS_RY          = 3

BTN_A_ID        = 0
BTN_B_ID        = 1
BTN_X_ID        = 2
BTN_Y_ID        = 3
BTN_LB_ID       = 4
BTN_RB_ID       = 5
BTN_BACK_ID     = 6
BTN_START_ID    = 7
BTN_STICK_L_ID  = 8
BTN_STICK_R_ID  = 9

# ---------------------------------------------------------------------
class Stick(object):
  def __init__(self, jstick, xyIDs=[0,1]):
    self._ix = xyIDs[0]
    self._iy = xyIDs[1]
    self._JS = jstick
    self._xy = np.zeros(2)

  @property
  def xy(self):
    temp = np.array([self._JS.get_axis(self._ix), self._JS.get_axis(self._iy)])
    if abs(self._xy -temp).any() > LIM:
      self._xy = temp
      return self._xy
    else:
      return None

  @property
  def last_xy(self):
    return self._xy

# ---------------------------------------------------------------------
class Button(object):
  def __init__(self, jstick, bID):
    self._ib = bID
    self._JS = jstick
    self._pressed = False

  @property
  def pressed(self):
    temp = self._JS.get_button(self._ib)
    if temp is not self._pressed:
      self._pressed = temp
      return self._pressed
    else:
      return None

  @property
  def last_pressed(self):
    return self._pressed

# ---------------------------------------------------------------------
class Hat(object):
  def __init__(self, jstick, hID):
    self._ih = hID
    self._JS = jstick
    self._val = np.array([0,0], dtype=np.int8)

  @property
  def value(self):
    temp = np.array(self._JS.get_hat(self._ih), dtype=np.int8)
    if abs(temp -self._val).any() > 0:
      self._val = temp
      return self._val
    else:
      return None

  @property
  def last_value(self):
    return self._val

# ---------------------------------------------------------------------
# Class representing joystick data
# ---------------------------------------------------------------------
class Joystick(object):
  def __init__(self, joystick_ID):
    """ Initialise joystick number `joystick_ID`
    """
    self.isReady = False
    self._jsID = joystick_ID
    pygame.init()
    pygame.joystick.init()
    n = pygame.joystick.get_count()
    if joystick_ID >= 0 and joystick_ID < n:
      # Joystick with that ID was found, initialize it
      self._JS = pygame.joystick.Joystick(joystick_ID)
      self._JS.init()

      # Create controller elements
      self.StickL = Stick(self._JS, [AXS_LX, AXS_LY])
      self.StickR = Stick(self._JS, [AXS_RX, AXS_RY])

      self.BtnL = Button(self._JS, BTN_LB_ID)
      self.BtnR = Button(self._JS, BTN_RB_ID)
      self.BtnBack = Button(self._JS, BTN_BACK_ID)
      self.BtnStart = Button(self._JS, BTN_START_ID)
      self.BtnA = Button(self._JS, BTN_A_ID)
      self.BtnB = Button(self._JS, BTN_B_ID)
      self.BtnX = Button(self._JS, BTN_X_ID)
      self.BtnY = Button(self._JS, BTN_Y_ID)
      self.BtnStickL = Button(self._JS, BTN_STICK_L_ID)
      self.BtnStickR = Button(self._JS, BTN_STICK_R_ID)

      self.HatL = Hat(self._JS, 0)
      self.isReady = True

# ---------------------------------------------------------------------
