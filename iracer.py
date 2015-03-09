import os
import sys
import bluetooth
import time
import pygame

# Author: Team Squirrel
# Date: 09 Mar 2015
# Version: 0.0.9
#
# Description:
# This program controls an iRacer bluetooth controlled car. It is based on a
# makey-makey controller, which can be found using this following url:
# http://conoroneill.net/makey-makey-raspberry-pi-iracer-bluetooth-cheese-controlled-car-ccc/

DEBUG_ON = False

# Set up the Bluetooth Socket
bd_addr = "00:12:05:11:97:90"
port = 1
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

#try:
#  sock.connect((bd_addr, port))
#except bluetooth.btcommon.BluetoothError, value :
#  print "Unable to establish a Bluetooth socket, code:", value
#  sys.exit()

# Outputs debug info to the console when DEBUG flag is True
def logToConsole(message):
  if DEBUG_ON:
    print message

# The iRacer class controls speed and direction controls
class iRacer(object):

  def __init__(self, speed, direction):
    self.carSpeed = speed
    self.carDirection = direction

  # Sends direction and speed character to the iRacer using 
  # the established bluetooth socket
  def sendToRacer(self):
    logToConsole(hex(self.carDirection|self.carSpeed))
#    sock.send(chr(self.carDirection|self.carSpeed))

  def goForward(self):
    logToConsole('go forward')

    self.carDirection = 0x10
    self.sendToRacer()

  def goForwardRight(self):
    logToConsole('go forward+right')

    self.carDirection = 0x60
    self.sendToRacer()

  def goForwardLeft(self):
    logToConsole('go forward+left')

    self.carDirection = 0x50
    self.sendToRacer()

  def goBackward(self):
    logToConsole('go back')

    self.carDirection = 0x20
    self.sendToRacer()

  def goBackwardRight(self):
    logToConsole('go back+right')

    self.carDirection = 0x80
    self.sendToRacer()

  def goBackwardLeft(self):
    logToConsole('go back+left')

    self.carDirection = 0x70
    self.sendToRacer()

  def goRight(self):
    logToConsole('go right')

    self.carDirection = 0x60
    self.sendToRacer()

  def goLeft(self):
    logToConsole('go left')

    self.carDirection = 0x50
    self.sendToRacer()

  def stopMoving(self):
    logToConsole('stop')

    self.carDirection = 0x00
    self.sendToRacer()

  def setSpeed(self, speed):
    if speed >= 15:
      self.carSpeed = 15
    else:
      if speed <= 3:
        self.carSpeed = 3
      else:
        self.carSpeed = speed


  def increaseSpeed(self):
    self.carSpeed += 1

    # it doesn't go any faster than this
    if self.carSpeed >= 15:
      self.carSpeed = 15

    self.sendToRacer()

  def decreaseSpeed(self):
    self.carSpeed -= 1

    # less than this is probably too slow
    if self.carSpeed <= 3:
      self.carSpeed = 3

    self.sendToRacer()


# This adaptor class (or middleware) contains logic to convert input
# controller signals into iRacer directional and speed commands without
# any specific knowledge of either device.
class InputAdaptor:

  def __init__(self, iracer):
    self.iracer = iracer

  # Checks for single keypresses (up, down, etc) as
  # well as keypress combinations (up+right, down+left, etc)
  def sendCommand(self, x , y):
    if y == 1: 
      if x == 0:
        self.iracer.goForward()
      else:
        if x == 1:
          self.iracer.goForwardRight()
        else:
          if x == -1:
            self.iracer.goForwardLeft()
    if y == -1:
      if x == 0:
        self.iracer.goBackward()
      else:
        if x == 1:
          self.iracer.goBackwardRight()
        else:
          if x == -1:
            self.iracer.goBackwardLeft()

    if y == 0 and x == 1:
      self.iracer.goRight()
    else:
      if y == 0 and x == -1:
        self.iracer.goLeft()

    if (x,y) == (2,2):
      self.iracer.stopMoving()

    if (x,y) == (3,3):
      self.iracer.increaseSpeed()

    if (x,y) == (4,4):
      self.iracer.decreaseSpeed()

    if (x,y) == (5,5):
      #set a fixed speed
      self.iracer.setSpeed(6)
      self.iracer.goForwardRight()
      time.sleep(3)
      self.iracer.goBackwardLeft()
      time.sleep(3)
      self.iracer.goForwardRight()
      time.sleep(0.5)
      self.iracer.goForward()
      time.sleep(1.2)
      self.iracer.stopMoving()

# This class periodically polls the user keyboard for input, as
# well as displaying user instructions to the screen
class KeyboardHandler:

  # Controller variables
  gameRunning = True

  def __init__(self, adaptor):
    self.adaptor = adaptor

  def displayHelp(self):
    print ""
    print ""
    print ""
    print ""
    print ""
    print ""
    print "                Welcome to Team Squirrel iRacer controller"
    print ""
    print ""
    print ""
    print "      Use the arrow keys for direction"
    print "      'f' = FASTER"
    print "      's' = SLOWER"
    print "      'space' = STOP"
    print "      'esc' = QUIT"
    print "      'h' = To redisplay this help page"
    print ""
    print ""
    print ""
    print ""
    print ""
    print ""
    print ""


  def start(self):

    global DEBUG_ON 
    
    # go right x = 1, go left x = -1 
    x = 0
    # go forward x = 1, go backward x = -1 
    y = 0

    # the main event loop
    while self.gameRunning:

      # Check the keys periodically
      time.sleep(0.15)

      for event in pygame.event.get():
        # Does the user want to quit?
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
          self.gameRunning = False

      # key.get_pressed can handle simultaneous key presses
      key = pygame.key.get_pressed()
      if key[pygame.K_UP]:
        y = 1

      if key[pygame.K_DOWN]:
        y = -1

      if key[pygame.K_LEFT]:
        x = -1

      if key[pygame.K_RIGHT]:
        x = 1

      if key[pygame.K_f]:
        (x, y) = (3, 3)

      if key[pygame.K_s]:
        (x, y) = (4, 4)

      if key[pygame.K_1]:
        (x, y) = (5, 5)

      if key[pygame.K_h]:
        self.displayHelp()

      if key[pygame.K_d]:
        DEBUG_ON = not DEBUG_ON
        if DEBUG_ON:
          print "Debug Mode On"
        else:
          print "Debug Mode Off"

      if key[pygame.K_SPACE]:
        (x, y) = (2, 2)

      self.adaptor.sendCommand(x, y)
      (x, y) = (0, 0)

# This class periodically polls a Sony Dual Shock Controller for input
class JoystickHandler:

  # Controller variables
  gameRunning = True
  leftRightTxt = ""
  upDownTxt = ""
  fasterSlowerTxt = ""
  stopButtonTxt = "" 
  joystick = 0

  def __init__(self, adaptor):
    self.adaptor = adaptor
    pygame.joystick.init()
    self.joystick = pygame.joystick.Joystick(0)
    self.joystick.init()

  def start(self):

    global DEBUG_ON 
    
    # go right x = 1, go left x = -1 
    x = 0
    # go forward x = 1, go backward x = -1 
    y = 0

    # the main event loop
    while self.gameRunning:

      # Check the keys periodically
      time.sleep(0.15)

      for event in pygame.event.get():
        # Does the user want to quit?
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
          self.gameRunning = False

      # test joystick axes
      self.leftRightTxt = "----"
      self.upDownTxt = "----"
      self.fasterSlowerTxt = "----"
      self.stopButtonTxt = "----"
      
      #stop joystick debug messages
      sys.stdout = os.devnull
      sys.stderr = os.devnull
      
      leftRightAxis = self.joystick.get_axis(0)
      upDownAxis = self.joystick.get_axis(1)
      fasterSlowerAxis = self.joystick.get_axis(3)
      stopButtonValue = self.joystick.get_button(14)
      
      #restart joystick debug messages
      sys.stdout = sys.__stdout__
      sys.stderr = sys.__stderr__

      if (leftRightAxis < -0.3):
        self.leftRightTxt = "Left"
      else:
        if (leftRightAxis > 0.3):
          self.leftRightTxt = "Right"

      if (upDownAxis < -0.3):
        self.upDownTxt = "Up"
      else:
        if (upDownAxis > 0.3):
          self.upDownTxt = "Down"

      if (fasterSlowerAxis < 0):
        self.fasterSlowerTxt = "IncreaseSpeed"
      else:
        if (fasterSlowerAxis > 0):
          self.fasterSlowerTxt = "DecreaseSpeed"

      if (stopButtonValue == 1):
        self.stopButtonTxt = "Stop"


      print self.leftRightTxt + "|" + self.upDownTxt + "|" + self.fasterSlowerTxt + "|" + self.stopButtonTxt

def main():
  # Set up Keyboard Inputs
  pygame.init()

  gameDisplay = pygame.display.set_mode((400, 200))
  pygame.display.set_caption('Keyboard Input')

  # to spam the pygame.KEYDOWN event every 100ms while key being pressed
  pygame.key.set_repeat(100, 100)

  # Let's initialise our devices
  iracer = iRacer(0x06, 0x10)
  adaptor = InputAdaptor(iracer)
  joystickHandler = JoystickHandler(adaptor)
# kbHandler = KeyboardHandler(adaptor)

  joystickHandler.start()
#  kbHandler.displayHelp()
#  kbHandler.start()

  # We're finished, so let's tidy up
#  sock.close()
  pygame.quit()
  quit()


if __name__ == "__main__":
  main()

