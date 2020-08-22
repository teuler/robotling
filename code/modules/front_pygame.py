#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# front_pygame.py
# Simple widget-based GUI that uses the drawing functions of pygame
#
# The MIT License (MIT)
# Copyright (c) 2018-19 Thomas Euler
# 2019-05-01, v1
# 2019-08-03, `WidgetCamera` added
#
# ---------------------------------------------------------------------
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import numpy as np
import matplotlib.pyplot as plt
import pygame
import pygame.gfxdraw
from pygame.locals import *

# ---------------------------------------------------------------------
WG_STATUS_WIDTH  = 300
WG_STATUS_HEIGHT = 100
WG_FR_LN_THICK   = 1
WG_FR_LN_STYLE   = 8
WG_FR_BD_X       = 4
WG_FR_BD_Y       = 4
WG_FONT          = "roboto"
if os.name in ["posix"]:
  WG_FONT_FACTOR = 1.0
else:
  WG_FONT_FACTOR = 1.0
WG_FONT_SIZE1    = int(12 *WG_FONT_FACTOR)
WG_FONT_SIZE2    = int(15 *WG_FONT_FACTOR)
WG_FONT_SIZE1L   = int(21 *WG_FONT_FACTOR)
WG_FONT_SIZE2L   = int(18 *WG_FONT_FACTOR)
WG_DX_SPACE      = 2
WG_DY_SPACE      = 1
WG_ADAPT_PLT_LBL = False
WG_PLT_LBL_WIDTH = WG_STATUS_WIDTH //5
WG_PLT_LN_THICK  = 1
WG_ANTIALIAS_TXT = True
WG_IRCAM_PALETTE = "inferno"
IS_OK            = 0
IS_WARN          = 1
IS_DANGER        = 2

# ---------------------------------------------------------------------
class Color:
  """
  BKG_WIN = (0, 0, 0)
  BKG     = (25, 13, 13)
  BKG_PLT = (35, 23, 23)
  STD     = (250, 150, 100)
  STD_LOW = (75, 45, 45)
  HIGH    = (255, 255, 255)
  H_INACT = (150, 150, 150)
  S_INACT = (125, 75, 50)
  B_INACT = (35, 23, 23)
  """
  BKG_WIN = (0x09, 0x09, 0x09)
  BKG     = (0x03, 0x3E, 0x6B)
  BKG_PLT = (0x03+20, 0x3E+20, 0x6B+20) #(0x25, 0x56, 0x7B)
  STD     = (0xFF, 0xFF, 0xFF)
  STD_LOW = (0x66, 0xA3, 0xD2)
  HIGH    = (0xFF, 0x92, 0x00)
  H_INACT = (0xA6, 0x5F, 0x00)
  S_INACT = (0x3F, 0x92, 0xD2)
  B_INACT = (0x03//2, 0x3E//2, 0x6B//2) #(0x25, 0x56, 0x7B)

  PLOT_BL = (150, 150, 250) #(100, 100, 200)
  PLOT_YE = (200, 150, 50)
  PLOT_RE = (200, 50, 50)
  PLOT_GR = (50, 200, 50)
  PLOT_OR = (250, 100, 50)

  WARN1   = (0xBF, 0x82, 0x30) #(100, 50, 10)
  WARN2   = (0xA6, 0x5F, 0x00) #(200, 100, 20)
  DANGER1 = (150, 60, 60)
  DANGER2 = (250, 75, 75)
  GOOD1   = (0x00, 0x72, 0x41) #(10, 100, 30)
  GOOD2   = (0x21, 0x83, 0x59) #(20, 200, 60)

# =====================================================================
# Window class for widgets
#
# ---------------------------------------------------------------------
class Window(object):

  def __init__(self, pos, size, title="", logo=""):
    """ Initiate pygame and generate a window
    """
    pygame.init()

    # Get fonts
    w = pygame.display.Info().current_w
    self._fontSm = pygame.font.SysFont(WG_FONT, WG_FONT_SIZE1)
    self._fontLg = pygame.font.SysFont(WG_FONT, WG_FONT_SIZE2)

    # Set title and icon, if any
    self.title = title
    pygame.display.set_caption(self.title)
    """
    if len(logo) > 0:
      self.logo = pygame.image.load(logo)
      pygame.display.set_icon(self.logo)
    """

    # Calculate size in standard widget sizes and create window
    self._size = [0]*2
    self._size[0] = int((WG_STATUS_WIDTH +WG_DX_SPACE) *size[0])
    self._size[1] = int((WG_STATUS_HEIGHT +WG_DY_SPACE) *size[1])
    self._surf = pygame.display.set_mode(self._size)
    #pygame.display.set_mode(flags=pygame.NOFRAME)
    self._surf.fill(Color.BKG_WIN)

  def clear(self):
    """ Clear window
    """
    self._surf.fill(Color.BKG_WIN)

  def update(self):
    """ Update the window content
    """
    pygame.display.flip()

  def close(self):
    """ Close window and quit pygame
    """
    pygame.quit()

  @property
  def lgFont(self):
    return self._fontLg

  @property
  def smFont(self):
    return self._fontSm

  @property
  def surface(self):
    return self._surf

  def doQuit(self):
    """ Checks if user wants to quit program
    """
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        return True
      elif event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
        return True
    return False

# =====================================================================
# Widget Base Class
#
# ---------------------------------------------------------------------
class Widget(object):

  def __init__(self, win, pos, size, dims=(1,1)):
    """ Initialize widget
    """
    self._win = win
    self._surf = win.surface
    self._isActive = True
    self.pos = pos
    self.size = size
    self.dyTxtSm = self.getTextSize("Ag", self._win.smFont)[1]
    self.dyTxtLg = self.getTextSize("Ag", self._win.lgFont)[1]
    self.txtHeader = "n/a"
    self.txtID = "n/a"
    self.txtInfo = "n/a"
    self.dims = dims
    self.colStd = Color.STD
    self.colHigh = Color.HIGH
    self.colBkg = Color.BKG

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def line(self, rect, col, width=WG_FR_LN_THICK, dash=0):
    if dash == 0:
      pygame.draw.line(self._surf, col, rect[0:2], rect[2:4], width)
    else:
      x0 = rect[0]
      y0 = rect[1]
      x3 = rect[2]
      y3 = rect[3]
      dx = x3 -x0
      dy = y3 -y0
      ln = np.sqrt(dx**2 + dy**2)
      sx = dx /ln
      sy = dy /ln
      for i in range(0, int(ln/dash), 2):
        x1 = x0 +(sx *i *dash)
        y1 = y0 +(sy *i *dash)
        x2 = x0 +(sx *(i +1) *dash)
        y2 = y0 +(sy *(i +1) *dash)
        pygame.draw.line(self._surf, col, (x1,y1), (x2,y2), width)

  def rect(self, rect, col, isFilled=False):
    thickn = 0 if isFilled else WG_FR_LN_THICK
    pygame.draw.rect(self._surf, col, pygame.Rect(rect), thickn)

  def circle(self, xy, r, col, isFilled=False, width=WG_FR_LN_THICK):
    thickn = 0 if isFilled else width
    r1 = r if r > thickn else thickn+1
    pygame.draw.circle(self._surf, col, xy, r1, thickn)

  def arc(self, xy, r, ang1_deg, ang2_deg, col, width=WG_FR_LN_THICK):
    """ Zero degrees to the right
    """
    a1_r = np.deg2rad(ang1_deg)
    a2_r = np.deg2rad(ang2_deg)
    rect = pygame.Rect(xy[0] -r, xy[1] -r, 2*r, 2*r)
    pygame.draw.arc(self._surf, col, rect, a1_r, a2_r, width)

  def polygon(self, points, col, isClosed=True, isFilled=False):
    pnts = np.array(points, 'int32')
    if len(pnts) > 2:
      if not isFilled:
        pygame.draw.lines(self._surf, col, isClosed, pnts, WG_PLT_LN_THICK)
      else:
        pygame.gfxdraw.filled_polygon(self._surf, pnts, col)

  def getTextSize(self, txt, font):
    return font.size(txt)

  def putText(self, txt, pos, font, col):
    img = font.render(txt, WG_ANTIALIAS_TXT, col)
    self._surf.blit(img, pos)

  def putTextPair(self, label, txt, pos, font, col1, col2):
    if len(label) > 0:
      label = label +" :"
    if self.dims[0] > 1:
      x2 = int(pos[0] +WG_STATUS_WIDTH *self.dims[0] /2)
    else:
      x2 = int(pos[0] +WG_STATUS_WIDTH/3)
    x3 = x2 -self.getTextSize(label, font)[0] -5
    self.putText(label, (x3, pos[1]), font, col1)
    self.putText(txt, (x2, pos[1]), font, col2)

  def calcXY (self, _angle, _r, _px, _py):
    return ((int(_px +np.cos(_angle) *_r), int(_py +np.sin(_angle) *_r)))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @property
  def width(self):
    return self.size[0]

  @property
  def height(self):
    return self.size[1]

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setLabels(self, sHeader, sID, sInfo):
    """ Set basic text labels
    """
    self.txtHeader = sHeader
    self.txtID = sID
    self.txtInfo = sInfo

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @property
  def isActive(self):
    return self._isActive

  @isActive.setter
  def isActive(self, value):
    self._isActive = value
    if value:
      self.colStd = Color.STD
      self.colHigh = Color.HIGH
      self.colBkg = Color.BKG
    else:
      self.colStd = Color.S_INACT
      self.colHigh = Color.H_INACT
      self.colBkg = Color.B_INACT
      self.update()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def draw(self):
    """ Draw widget
    """
    xy1 = (self.pos[0] +WG_FR_BD_X, self.pos[1] +WG_FR_BD_Y)
    r1  = [xy1[0], xy1[1], self.size[0] -WG_FR_BD_X, self.size[1] -WG_FR_BD_Y]
    self.rect(r1, self.colBkg, isFilled=True)
    return xy1, r1

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def update(self):
    """ Update fields and redraw
    """
    self.draw()

# =====================================================================
# Text Info Widget Class
#
# ---------------------------------------------------------------------
class WidgetInfo(Widget):

  def __init__(self, win, pos, dims=(1,1)):
    """ Initialize widget
    """
    self.dims = dims
    width  = int(dims[1] *WG_STATUS_WIDTH)
    height = int(dims[0] *WG_STATUS_HEIGHT)
    super(WidgetInfo, self).__init__(win, pos, (width, height), dims)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setLabels(self, sHeader, sID, sInfoLabels):
    """ Set basic text labels
    """
    super(WidgetInfo, self).setLabels(sHeader, sID, "")
    self.InfoLabels = sInfoLabels
    self.Infos = ["n/a"] *len(sInfoLabels)
    self.Colors = [self.colStd] *len(sInfoLabels)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def update(self, sInfoLines, cols=[]):
    """ Update info line(s) and redraw
    """
    self.Infos = sInfoLines
    if len(cols) == 0:
      self.Colors = [self.colStd] *len(sInfoLines)
    else:
      self.Colors = cols
    self.draw()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def draw(self):
    """ Draw widget
    """
    xy1, r1 = super(WidgetInfo, self).draw()

    # Print header and ID
    x1 = xy1[0] +WG_DX_SPACE
    y1 = xy1[1] +WG_DY_SPACE
    self.putText(self.txtHeader, (x1, y1), self._win.smFont, self.colStd)
    y1 += self.dyTxtSm +WG_DY_SPACE
    self.putText(self.txtID, (x1, y1), self._win.lgFont, self.colHigh)

    for iLine, label in enumerate(self.InfoLabels):
      y1 += self.dyTxtSm +WG_DY_SPACE
      txt = self.Infos[iLine] if iLine < len(self.Infos) else "-"
      txt = txt.split("\n")
      for iTxt, txt1 in enumerate(txt):
        self.putTextPair(label if iTxt == 0 else "", txt1, (x1, y1),
                         self._win.smFont, self.colStd, self.Colors[iLine])
        if len(txt) > 1:
          y1 += self.dyTxtSm +WG_DY_SPACE

# =====================================================================
# Status Widget Base Class
#
# ---------------------------------------------------------------------
class WidgetStatus(Widget):

  def __init__(self, img, pos):
    """ Initialize widget
    """
    width  = WG_STATUS_WIDTH
    height = WG_STATUS_HEIGHT
    super(WidgetStatus, self).__init__(img, pos, (width, height))
    self.clear()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def clear(self):
    self.vals = []
    self.dxMaxLabel = 0

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setLabels(self, sHeader, sID, sInfo, sValFormat, barValIndex):
    """ Set basic text labels
    """
    super(WidgetStatus, self).setLabels(sHeader, sID, sInfo)
    self.sValFormat = sValFormat
    self.barValTxt  = "n/a"
    self.barValInd  = barValIndex

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def addValProperties(self, label, unit, minmax, tresh, f):
    """ Add a value and its properties to the list
    """
    d = dict()
    d["val"] = minmax[0]
    d["min"] = minmax[0]
    d["max"] = minmax[1]
    d["warn"] = tresh[0]
    d["danger"] = tresh[1]
    d["unit"] = unit
    d["label"] = label
    d["cmpFunc"] = f
    self.vals.append(d)
    txt = "{0} [{1}]".format(label, unit)
    dxTxt = self.getTextSize(txt, self._win.smFont)[0]
    if WG_ADAPT_PLT_LBL:
      self.dxMaxLabel = max(self.dxMaxLabel, dxTxt)
    else:
      self.dxMaxLabel = WG_PLT_LBL_WIDTH

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getValDic(self, iVal):
    if (iVal >= 0) and (iVal < len(self.vals)):
      return self.vals[iVal]
    else:
      return {}

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getFraction(self, iVal):
    val = self.getValDic(iVal)
    if val == {}:
      return 0.0
    fract = val["val"] /(val["max"] -val["min"])
    if fract < 0.0:
      return 0.0
    if fract > 1.0:
      return 1.0
    else:
      return float(fract)

# =====================================================================
# Status Bar Widget Class
#
# ---------------------------------------------------------------------
class WidgetStatusBar(WidgetStatus):

  def __init__(self, img, pos):
    """ Initialize widget
    """
    super(WidgetStatusBar, self).__init__(img, pos)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def draw(self):
    """ Draw widget
    """
    xy1, r1 = super(WidgetStatus, self).draw()

    # Print header, ID and info text
    x1 = xy1[0] +WG_DX_SPACE
    y1 = xy1[1] +WG_DY_SPACE
    self.putText(self.txtHeader, (x1, y1), self._win.smFont, self.colStd)
    y1 += self.dyTxtSm +WG_DY_SPACE
    self.putText(self.txtID, (x1, y1), self._win.lgFont, self.colHigh)
    y1 += self.dyTxtSm +WG_DY_SPACE
    self.putText(self.txtInfo, (x1, y1), self._win.smFont, self.colStd)
    y1 += self.dyTxtSm +WG_DY_SPACE +6

    val = self.getValDic(self.barValInd)
    if val == {}:
      # Value indicated by _iVal does not exist
      return

    # Draw bar and print value text
    col1 = Color.GOOD1
    col2 = Color.GOOD2
    res = val["cmpFunc"](val["val"], val["warn"], val["danger"])
    if res == IS_WARN:
      col1 = Color.WARN1
      col2 = Color.WARN2
    elif res == IS_DANGER:
      col1 = Color.DANGER1
      col2 = Color.DANGER2

    xof = 10
    r2 = [r1[0]+WG_DX_SPACE, y1-WG_DY_SPACE*2.5,
          r1[2]-WG_DX_SPACE*2, self.dyTxtLg*1.5]
    self.rect(r2, col1, isFilled=True)

    dx = r2[2]
    fract = self.getFraction(self.barValInd)
    r2[2] = int(fract *dx)
    self.rect(r2, col2, isFilled=True)

    self.putText(self.barValTxt, (x1 +xof, y1), self._win.lgFont, self.colHigh)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def update(self, vals=None):
    """ Update fields and redraw
    """
    if not vals is None:
      for iVal, val in enumerate(self.vals):
        if iVal < len(vals):
          self.vals[iVal]["val"] = vals[iVal]
      self.barValTxt = self.sValFormat.format(*vals)
    self.draw()

# =====================================================================
# Compass Widget Class
#
# ---------------------------------------------------------------------
class WidgetCompass(WidgetStatus):

  def __init__(self, img, pos):
    """ Initialize widget
    """
    self.head = 0
    self.roll = 0
    self.ptch = 0
    self.errC = 0
    self.isFirst = True
    self.setProperties()
    super(WidgetCompass, self).__init__(img, pos)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setLabels(self, _sHeader, sID):
    """ Set basic text labels
    """
    super(WidgetStatus, self).setLabels(_sHeader, sID, "")

  def setProperties(self, maxAnglePR=20):
    """ Set maximal absolute tilt angle (`maxAnglePR`) that is still
        indicated as o.k.
    """
    self.maxAnglePR = maxAnglePR

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def draw(self):
    """ Draw widget
    """
    xy1, r1 = super(WidgetCompass, self).draw()

    # Print header, ID and info text
    x1 = xy1[0] +WG_DX_SPACE
    y1 = xy1[1] +WG_DY_SPACE
    self.putText(self.txtHeader, (x1, y1), self._win.smFont, self.colStd)
    y1 += self.dyTxtSm +WG_DY_SPACE
    self.putText(self.txtID, (x1, y1), self._win.lgFont, self.colHigh)
    y1 += self.dyTxtLg +WG_DY_SPACE

    x1 += int(WG_STATUS_WIDTH *0.5)
    txt = "{0:.0f}°".format(self.head)
    self.putTextPair("heading", txt if self.head >= 0 else "n/a", (x1, y1),
                      self._win.smFont, self.colStd, self.colStd)
    y1 += self.dyTxtSm +WG_DY_SPACE
    txt = "{0:.0f}°".format(self.roll)
    self.putTextPair("roll", txt, (x1, y1),
                      self._win.smFont, self.colStd, self.colStd)
    y1 += self.dyTxtSm +WG_DY_SPACE
    txt = "{0:.0f}°".format(self.ptch)
    self.putTextPair("pitch", txt, (x1, y1),
                      self._win.smFont, self.colStd, self.colStd)

    if self.isFirst:
      # Calculate some parameters for compass display
      r = int(WG_STATUS_HEIGHT *0.44)
      self.xyo = (int(xy1[0] +WG_STATUS_WIDTH *0.45),
                  int(xy1[1] +WG_STATUS_HEIGHT *0.5) -WG_DY_SPACE*2)
      self.ln1 = (self.xyo[0] -10, self.xyo[1], self.xyo[0] +10, self.xyo[1])
      self.ln2 = (self.xyo[0], self.xyo[1] -10, self.xyo[0], self.xyo[1] +10)
      self.r = r
      size = self.getTextSize("N", self._win.smFont)
      self.txOff = int(size[0] /2)
      self.tyOff = int(size[1] /2)
      self.isFirst = False

    # Draw compass
    self.circle(self.xyo, self.r, Color.BKG_PLT, width=1)
    self.line(self.ln1, Color.BKG_PLT)
    self.line(self.ln2, Color.BKG_PLT)
    xy = (self.xyo[0] -self.txOff, self.xyo[1] -self.r +1)
    self.putText("N", xy, self._win.smFont, Color.STD)

    ang = (-self.head +90 +360) % 360
    self.arc(self.xyo, self.r-2, ang-3, ang+3, Color.HIGH, width=6)
    xc = int(self.xyo[0] +self.roll /180 *self.r)
    yc = int(self.xyo[1] -self.ptch /180 *self.r)
    ok = abs(self.roll) < self.maxAnglePR and abs(self.ptch) < self.maxAnglePR
    self.circle((xc, yc), 11, Color.GOOD2 if ok else Color.DANGER2, width=1)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def update(self, hpr=None):
    """ Update legend and redraw
    """
    if not hpr is None:
      self.head = hpr[0]
      self.roll = hpr[1]
      self.ptch = hpr[2]
    self.draw()

# =====================================================================
# Camera sensor Widget Class
#
# ---------------------------------------------------------------------
class WidgetCamera(WidgetStatus):

  def __init__(self, img, pos, rotation=90):
    """ Initialize widget
    """
    self.img = None
    self.imgData = None
    self.isFirst = True
    self.rot = rotation
    self.setValProperties("n/a", "[-]", (0,255))
    width = WG_STATUS_WIDTH
    height = WG_STATUS_HEIGHT *2
    super(WidgetStatus, self).__init__(img, pos, (width, height))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setLabels(self, _sHeader, sID):
    """ Set basic text labels
    """
    super(WidgetStatus, self).setLabels(_sHeader, sID, "")

  def setValProperties(self, label, unit, minmax, pix_size=(1,1), smooth=True):
    """ Set properties, including pixel size
    """
    d = dict()
    d["unit"] = unit
    d["label"] = label
    d["min"] = minmax[0]
    d["max"] = minmax[1]
    d["imgSize"] = None
    d["pixelSize"] = pix_size
    d["smooth"] = smooth
    d["blobList"] = []
    self.vals = [d]

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def draw(self):
    """ Draw widget
    """
    xy1, r1 = super(WidgetCamera, self).draw()

    # Print header, ID and info text
    #
    x1 = xy1[0] +WG_DX_SPACE
    y1 = xy1[1] +WG_DY_SPACE
    self.putText(self.txtHeader, (x1, y1), self._win.smFont, self.colStd)
    y1 += self.dyTxtSm +WG_DY_SPACE
    self.putText(self.txtID, (x1, y1), self._win.lgFont, self.colHigh)
    y1 += self.dyTxtLg +WG_DY_SPACE

    if self.isFirst:
      # Retrieve a color palette from matplotlib.pyplot and convert it into
      # a pygame palette
      cmap = plt.cm.get_cmap(WG_IRCAM_PALETTE)
      self.pal = []
      for i in range(256):
        rgba = cmap(i/256.)
        self.pal.append((rgba[0]*255, rgba[1]*255, rgba[2]*255))

      # ... and a color bar
      cb = np.array([v for v in range(256)], dtype=np.uint8)
      self.cbar = pygame.image.frombuffer(cb, (1, 256), "P")
      self.cbar_dxy = (16, int(r1[3]/2))
      self.cbar = pygame.transform.scale(self.cbar, self.cbar_dxy)
      self.cbar.set_palette(self.pal)
      self.isFirst = False

    # If image data available, show camera image
    if not self.img is None:
      # Define image position and scaling
      idx, idy = self.img.shape
      pdx, pdy = self.vals[0]["pixelSize"]
      imin = self.vals[0]["min"]
      imax = self.vals[0]["max"]
      ix0 = xy1[0] +int((WG_STATUS_WIDTH -idx*pdx)/2)
      iy0 = y1 +WG_DY_SPACE*4

      # Clip image range and then rescale it to 0..255
      self.img = np.clip(self.img, imin, imax)
      self.img -= imin
      self.img /= imax -imin +1
      self.img *= 255

      # Convert to bytes and create a pygame surface
      self.img = np.array(self.img, dtype=np.uint8)
      image = pygame.image.frombuffer(self.img, (idx, idy), "P")
      if self.rot != 0:
        image = pygame.transform.rotate(image, self.rot)

      # Scale surface (image), apply color palette and bit to widget
      image.set_palette(self.pal)
      if self.vals[0]["smooth"]:
        image = image.convert()
        image = pygame.transform.smoothscale(image, (idx*pdx, idx*pdy))
      else:
        image = pygame.transform.scale(image, (idx*pdx, idx*pdy))
      self._surf.blit(image, [ix0, iy0])

      # Draw blobs, if any
      for iB, blob in enumerate(self.vals[0]["blobList"]):
        if self.rot == 90:
          xb = int(blob[3]*pdx +ix0)
          yb = int((idy-blob[4])*pdy +iy0)
        else:
          xb = int(blob[4]*pdx +ix0)
          yb = int(blob[3]*pdy +iy0)

        rb = int(np.sqrt(blob[0]*pdx/np.pi)) *2
        #print(blob)
        if iB == 0:
          self.circle((xb, yb), rb, self.colStd, width=1)
        else:
          self.circle((xb, yb), rb, Color.WARN2, width=1)

      # Display color bar and label it
      self._surf.blit(self.cbar, [ix0 +idx*pdx +WG_DX_SPACE*2, iy0])
      x1 = ix0 +idx*pdx +WG_DX_SPACE*4 +self.cbar_dxy[0]
      y1 = iy0 -self.dyTxtSm//2
      tx = "{0}".format(imin)
      self.putText(tx, (x1, y1), self._win.smFont, self.colStd)
      y1 += self.cbar_dxy[1]
      tx = "{0}".format(imax)
      self.putText(tx, (x1, y1), self._win.smFont, self.colStd)
      y1 -= self.cbar_dxy[1]//2
      tx = "{0} [{1}]".format(self.vals[0]["label"], self.vals[0]["unit"])
      self.putText(tx, (x1, y1), self._win.smFont, self.colStd)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def update(self, data=None, size=(0,0), blobs=[]):
    """ Update legend and redraw
    """
    if not data is None:
      self.vals[0]["imgSize"] = size
      self.vals[0]["blobList"] = blobs
      self.img = np.resize(np.array(data, dtype=np.float), size)
    else:
      self.img = None
    self.draw()

# =====================================================================
# Distance sensor array Widget Class
#
# ---------------------------------------------------------------------
class WidgetDistanceArray(WidgetStatus):

  def __init__(self, img, pos):
    """ Initialize widget
    """
    self.distData = []
    self.isFirst = True
    self.setValProperties("n/a", "[-]", [0,1], [0,1], None, [], 0)
    width = WG_STATUS_WIDTH
    height = WG_STATUS_HEIGHT *2
    super(WidgetStatus, self).__init__(img, pos, (width, height))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setLabels(self, _sHeader, sID):
    """ Set basic text labels
    """
    super(WidgetStatus, self).setLabels(_sHeader, sID, "")

  def setValProperties(self, label, unit, minmax, tresh, f, pos_deg, cone_deg):
    """ Set properties, including scan angle (`pos_deg`) and scan cone width
        (`cone_deg`)
    """
    d = dict()
    d["val"] = minmax[0]
    d["min"] = minmax[0]
    d["max"] = minmax[1]
    d["warn"] = tresh[0]
    d["danger"] = tresh[1]
    d["unit"] = unit
    d["label"] = label
    d["cmpFunc"] = f
    d["pos_deg"] = pos_deg
    d["cone_deg"] = cone_deg
    self.vals = [d]

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def draw(self):
    """ Draw widget
    """
    xy1, r1 = super(WidgetDistanceArray, self).draw()

    # Print header, ID and info text
    #
    x1 = xy1[0] +WG_DX_SPACE
    y1 = xy1[1] +WG_DY_SPACE
    self.putText(self.txtHeader, (x1, y1), self._win.smFont, self.colStd)
    y1 += self.dyTxtSm +WG_DY_SPACE
    self.putText(self.txtID, (x1, y1), self._win.lgFont, self.colHigh)
    y1 += self.dyTxtLg +WG_DY_SPACE

    if self.isFirst:
      # Calculate some parameters for distance array display
      r = int(WG_STATUS_HEIGHT *0.65)
      self.xyo = (int(xy1[0] +WG_STATUS_WIDTH *0.45),
                  int(xy1[1] +WG_STATUS_HEIGHT) -WG_DY_SPACE*2)
      self.r = r
      self.isFirst = False

    nDist = len(self.distData)
    if nDist > 0:
      # Draw IR distance sensors
      #
      _d = self.vals[0]
      dw = np.radians(_d["cone_deg"] /2)
      dx = 18
      px = int(xy1[0] +self.size[0]/2)
      py = int(xy1[1] +self.size[1]*5/6)
      self.circle([px,py], 15, Color.BKG_PLT, width=1) #STD_LOW
      yTx = y1

      for iDist, Dist_cm in enumerate(self.distData):
        pts = []
        a   = np.radians( _d["pos_deg"][iDist] -90)
        dst = min(Dist_cm *1.5, self.size[1] *2/3)
        pts.append(self.calcXY(a-dw, dx +3, px, py))
        ddw = dw*2 /5.
        for j in range(6):
          pts.append(self.calcXY(a-dw +ddw*j, dx +3 +dst, px, py))
          if j == 1:
            xTx, _ = self.calcXY(a-dw +ddw*j, dx +3 +dst, px, py)
        pts.append(self.calcXY(a+dw, dx +3, px, py))
        if Dist_cm < _d["warn"]:
          cPoly = Color.DANGER2
          cTx   = Color.HIGH
        elif Dist_cm > _d["danger"]:
          cPoly = Color.WARN2
          cTx   = Color.HIGH
        else:
          cPoly = Color.GOOD2
          cTx   = Color.HIGH
        self.polygon(pts, cPoly, isClosed=False, isFilled=True)
        sTxt = "{0} {1}".format(Dist_cm, "" if iDist < nDist-1 else "cm")
        self.putText(sTxt, (xTx, yTx), self._win.smFont, cTx)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def update(self, distData=None):
    """ Update legend and redraw
    """
    if not distData is None:
      self.distData = distData
    self.draw()

# =====================================================================
# Plot Widget Class
#
# ---------------------------------------------------------------------
class WidgetPlot(WidgetStatus):

  def __init__(self, img, pos, rowsCols=(1,1)):
    """ Initialize widget
    """
    width = int(rowsCols[1] *WG_STATUS_WIDTH)
    height = WG_STATUS_HEIGHT*2
    self.rows = rowsCols[0]
    self.cols = rowsCols[1]
    if self.rows > 1:
      height += int(self.cols/2. *WG_STATUS_HEIGHT)
    super(WidgetStatus, self).__init__(img, pos, (width, height))
    self.clear()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setLabels(self, _sHeader, sID):
    """ Set basic text labels
    """
    super(WidgetStatus, self).setLabels(_sHeader, sID, "")

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def addValProperties(self, label, unit, minmax, tr, f, col,
                       rowCol=(0,0), txtFormat=""):
    """ Add a value and its properties to the list
    """
    super(WidgetPlot, self).addValProperties(label, unit, minmax, tr, f)
    self.vals[len(self.vals)-1].update({"rowCol": rowCol})
    self.vals[len(self.vals)-1].update({"color": col})
    self.vals[len(self.vals)-1].update({"format": txtFormat})
    self.vals[len(self.vals)-1].update({"xAxis": -1})
    self.vals[len(self.vals)-1].update({"enabled": True})

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setXYValPair(self, yLabel, xLabel):
    """ Define value pair that will be plotted a y=f(x)
    """
    vLabels = [val["label"] for val in self.vals]
    try:
      iXVal = vLabels.index(xLabel)
      iYVal = vLabels.index(yLabel)
      self.vals[iYVal].update({"xAxis": iXVal})
      self.vals[iXVal].update({"enabled": False})
    except KeyError:
      pass

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def plot (self, rect, _data, lims, col, txt, yTxt, doClear,
            txtFormat="", _dataX=None, limsX=[-1., 1.]):
    """ Plots `data` in a subwindow
    """
    x1 = rect[0]
    y1 = rect[1]
    dx = rect[2]
    dy = rect[3]
    data = _data
    dxBar = dx /float(len(_data))
    vMin = lims[0]
    vMax = lims[1]
    y0 = y1+dy
    if not (_dataX is None):
      dataX = _dataX
      vXMin = limsX[0]
      vXMax = limsX[1]

    if doClear:
      self.rect(rect, Color.BKG_PLT, isFilled=True)

    pts = []
    for iVal, val in enumerate(data):
      val1 = min(max(val, vMin), vMax)
      pVal = int((val1 -vMin)/(vMax -vMin) *dy)
      if not(_dataX is None):
        pX = int((dataX[iVal] -vXMin)/(vXMax -vXMin) *dx)
      else:
        pX = int(iVal *dxBar)
      pX += x1 +2
      pts.append((pX, y0-pVal))

    xTx = x1 +WG_DX_SPACE*3 +dx
    yTx = y1 +WG_DY_SPACE*2 +yTxt
    self.putText(txt, (xTx, yTx), self._win.smFont, col)

    pY = dy -int((0 -vMin)/(vMax -vMin) *dy)
    self.line([x1, y1 +pY, x1 +dx -1, y1 +pY], Color.BKG_WIN) #, dash=5)

    if len(pts) > 0:
      self.polygon(pts, col, isClosed=False)
      if len(txtFormat) > 0:
        if not(_dataX is None):
          vTx = txtFormat.format(val) +", " +txtFormat.format(dataX[iVal])
        else:
          vTx = txtFormat.format(val)
        dxyTx = self.getTextSize(vTx, self._win.smFont)
        dxTx  = dxyTx[0] +WG_DX_SPACE*3
        yTx  = pts[iVal-1][1] -WG_DY_SPACE
        yTx  = min(dy +y1 -dxyTx[1], yTx)
        self.putText(vTx, (xTx -dxTx, yTx), self._win.smFont, col)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def draw(self):
    """ Draw widget
    """
    xy1, r1 = super(WidgetPlot, self).draw()

    # Print header, ID and info text
    #
    x1 = xy1[0] +WG_DX_SPACE
    y1 = xy1[1] +WG_DY_SPACE
    self.putText(self.txtHeader, (x1, y1), self._win.smFont, self.colStd)
    y1 += self.dyTxtSm +WG_DY_SPACE
    self.putText(self.txtID, (x1, y1), self._win.lgFont, self.colHigh)
    y1 += self.dyTxtLg +WG_DY_SPACE

    # Calculate plot rectangle(s)
    #
    dxB = int((r1[2] -WG_DX_SPACE *2) /self.cols)
    dxP = int(dxB -self.dxMaxLabel -WG_DX_SPACE *5)
    dyB = int((r1[3] -(y1 -xy1[1]) -WG_DY_SPACE *8) /self.rows)
    dyP = dyB -WG_DY_SPACE
    dyTx = np.zeros((self.rows, self.cols), dtype=np.int32)
    for iC in range(self.cols):
      for iR in range(self.rows):
        x11 = r1[0] +WG_DX_SPACE +iC*dxB
        y11 = y1 +WG_DY_SPACE*3 +dyB*iR
        r2 = [x11, y11, dxP, dyP]

        for i, val in enumerate(self.vals):
          try:
            if not(val["enabled"]):
              continue
            if (val["rowCol"][0] == iR) and (val["rowCol"][1] == iC):
              data = val["data"]
              txt = "{0} [{1}]".format(val["label"], val["unit"])
              lim = [val["min"], val["max"]]
              dataX = None
              limX  = [-1., 1.]
              if val["xAxis"] >= 0:
                valX = self.vals[val["xAxis"]]
                dataX = valX["data"]
                limX = [valX["min"], valX["max"]]
              self.plot(r2, data, lim, val["color"], txt, dyTx[iR][iC],
                        True if dyTx[iR][iC]==0 else False,
                        txtFormat=val["format"],
                        _dataX=dataX, limsX=limX)
              dyTx[iR][iC] += self.dyTxtSm +WG_DY_SPACE
          except KeyError:
            pass

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def update(self, valArrays=None):
    """ Update fields and redraw
    """
    if not valArrays is None:
      for iVal, val in enumerate(valArrays):
        if iVal < len(valArrays):
          self.vals[iVal]["data"] = valArrays[iVal]
    self.draw()

# =====================================================================
# Graphical Hexapod Widget Class
#
# ---------------------------------------------------------------------
'''
class WidgetHexapod(Widget):

  def __init__(self, _img, _pos):
    """ Initialize widget
    """
    super(WidgetHexapod, self).__init__(_img, _pos,
                                       (WG_STATUS_WIDTH, WG_STATUS_HEIGHT*4))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def __calcXY (self, _angle, _r, _px, _py):
    return ((int(_px +np.cos(_angle) *_r), int(_py +np.sin(_angle) *_r)))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def draw(self, _d):
    """ Draw widget
    """
    xy1, r1 = super(WidgetHexapod, self).draw()

    # Print header, ID and info text
    #
    xTx    = xy1[0] +WG_DX_SPACE
    yTx    = xy1[1] +self.dyTxtSm +WG_DY_SPACE
    self.putText(self.txtHeader, (xTx, yTx), WG_FONT_SIZE1, self.colStd)
    yTx    += self.dyTxtLg +WG_DY_SPACE
    self.putText(self.txtID, (xTx, yTx), WG_FONT_SIZE2, self.colHigh)
    yTx    += self.dyTxtLg +WG_DY_SPACE
    self.putTextPair("updated", "{0:3.1f} ms ago"
                     .format(_d["tIRDistUpdate_ms"]),
                     (xTx, yTx), WG_FONT_SIZE1, self.colStd, self.colHigh)
    yTx    += int((self.dyTxtSm +WG_DY_SPACE)*3.5)
    self.putTextPair("distance", "", (xTx, yTx), WG_FONT_SIZE1,
                     self.colStd, self.colHigh)

    # Draw depth image (DI)
    #
    px      = int(xy1[0] +self.size[0]*2/3 -28)
    py      = int(xy1[1] +self.dyTxtSm*7)
    nxHalf  = _d["DI_dx"]/2
    nyHalf  = _d["DI_dy"]/2
    dx      = 12
    dy      = 9
    for ix in range(_d["DI_dx"]):
      for iy in range(_d["DI_dy"]):
        x   = px -(ix -nxHalf)*dx
        y   = py -(iy -nyHalf)*dy
        if _d["DI_cm"][iy][ix] < 0:
          c = (10,10,0)
        else:
          rat = _d["IRDIST_MAX_CM"] -_d["DI_cm"][iy][ix]
          d   = max(0, 255 *rat /_d["IRDIST_MAX_CM"])
          c   = (d, d, 0)
        self.rect([x, y, x+dx-2, y+dy-2], c, isFilled=True)

    # Draw compass
    #
    dx      = 25
    dy      = 100
    px      = int(xy1[0] +self.size[0]*2/3 -22)
    py      = int(xy1[1] +self.size[1]*2/3 +self.dyTxtSm)
    dw      = 0.2
    a       = np.radians(_d["Dir_deg"])
    pts     = [(px,py)]
    pts.append(self.__calcXY(a-dw, dx/2, px, py))
    pts.append(self.__calcXY(a, dx, px, py))
    pts.append(self.__calcXY(a+dw, dx/2, px, py))
    self.circle((px,py), dx, self.colStd)
    self.polygon([pts],self.colStd, isFilled=True)
    if _d["GGN_tarAngle_deg"] >= 0:
      a     = np.radians(_d["GGN_tarAngle_deg"])
      xy    = self.__calcXY(a, dx, px, py)
      self.circle(xy, 3, Color.HIGH, isFilled=True)

    # Draw IR distance sensors
    #
    nDist   = len(_d["IRDist"])
    da      = np.radians(45 /nDist)
    a       = -1.5*da -np.radians(90)
    dw      = 0.1
    dxTx    = 25
    xTx     = int(px -dxTx*2.25)
    nDist   = len(_d["IRDist"])
    for iDist, Dist_cm in enumerate(_d["IRDist"]):
      pts   = []
      pts.append(self.__calcXY(a-dw, dx +3, px, py))
      pts.append(self.__calcXY(a-dw, dx +3 +Dist_cm, px, py))
      pts.append(self.__calcXY(a+dw, dx +3 +Dist_cm, px, py))
      pts.append(self.__calcXY(a+dw, dx +3, px, py))
      if Dist_cm < _d["IRDist_danger"]:
        cPoly  = Color.DANGER2
        cTx    = cPoly
      elif Dist_cm < _d["IRDist_warn"]:
        cPoly  = Color.WARN2
        cTx    = cPoly
      else:
        cPoly  = Color.STD
        cTx    = Color.HIGH
      self.polygon([pts], cPoly, isFilled=True)
      sTxt     = "{0} {1}".format(Dist_cm, "" if iDist < nDist-1 else "cm")
      self.putText(sTxt, (xTx, yTx), WG_FONT_SIZE1, cTx)
      self.polygon([pts], Color.BKG, isFilled=False)
      a    += da
      xTx  += dxTx

    # Draw "legs"
    #
    da      = np.radians(40)
    a       = np.radians(-40)
    dw      = 0.15
    lMax    = 125.0
    for leg in range(6):
      if leg == 3:
        a   = np.radians(140)
      pts   = []
      pts.append(self.__calcXY(a-dw,   dx+ 4, px, py))
      pts.append(self.__calcXY(a-dw/2, dx+24, px, py))
      pts.append(self.__calcXY(a+dw/2, dx+24, px, py))
      pts.append(self.__calcXY(a+dw,   dx+ 4, px, py))
      l1    = (lMax -_d["LoadSens"][leg])/lMax*128.0
      l2    = _d["LoadSens"][leg]/lMax*255.0
      cPoly = (0, l1, l2)
      self.polygon([pts], cPoly, isFilled=True)
      l1    = (lMax -_d["LoadSens"][leg+6])/lMax*128.0
      l2    = _d["LoadSens"][leg+6]/lMax*255.0
      cPoly = (0, l1, l2)
      xy    = self.__calcXY(a, dx+32, px, py)
      self.circle(xy, 8, cPoly, isFilled=True)
      a    += da

    # More text info
    #
    xTx     = xy1[0] +WG_DX_SPACE
    yTx    += (self.dyTxtSm +WG_DY_SPACE) *15
    self.putTextPair("bodyRot", "x={0}, y={1}"
                     .format(_d["GGN_bodyRotX"], _d["GGN_bodyRotY"]),
                     (xTx, yTx), WG_FONT_SIZE1, self.colStd,self.colHigh)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def update(self, _d):
    """ Update and redraw
    """
    self.draw(_d)
'''
# ---------------------------------------------------------------------
