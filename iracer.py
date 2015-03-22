import os
import sys
import bluetooth
import time
import pygame

# This program controls an iRacer bluetooth controlled car. It is based on a
# makey-makey controller, which can be found using the following url:
# http://conoroneill.net/makey-makey-raspberry-pi-iracer-bluetooth-cheese-controlled-car-ccc/
# Instructions on how to install the joystick drivers can be found at
# PS3 Dual Shock Controller and Pygame
# https://docs.google.com/document/d/1zMlKfshKOKyTrip_NqSnS24qzly-iuWKy2LsFhi3xTM/edit?pli=1
#
# Note: Remember to disable sixad's bluetooth drivers, they conflict with Bluez being used here
# i.e. sixad -r

DEBUG_ON = False

# Set up the Bluetooth Socket
bd_addr = "00:12:05:11:97:90"
port = 1
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

# try:
#   sock.connect((bd_addr, port))
# except bluetooth.btcommon.BluetoothError, value :
#   print "Unable to establish a Bluetooth socket, code:", value
#   sys.exit()

# Outputs debug info to the console when DEBUG flag is True
def logToConsole(message):
  if DEBUG_ON:
    print message

# The iRacer class sends speed and direction commands to the car
class iRacer(object):

  def __init__(self, speed, direction):
    self.carSpeed = speed
    self.carDirection = direction

  # Sends direction and speed character to the iRacer using 
  # the established bluetooth socket
  def sendToRacer(self):
    logToConsole(hex(self.carDirection|self.carSpeed))
    # sock.send(chr(self.carDirection|self.carSpeed))

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

    #an ambitious 3-point turn
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

# This KeyboardHandler class periodically polls the user keyboard for key events, as
# well as displaying user instructions to the screen
class KeyboardHandler:

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
    print "      'h' = Redisplay this help page"
    print ""
    print ""
    print ""
    print ""
    print ""
    print ""
    print ""


  def start(self):

    global DEBUG_ON 
    
    gameRunning = True

    # go right x = 1, go left x = -1 
    x = 0
    # go forward x = 1, go backward x = -1 
    y = 0

    # the main event loop
    while gameRunning:

      # Check the keys periodically
      time.sleep(0.15)

      for event in pygame.event.get():
        # Does the user want to quit?
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
          gameRunning = False

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

      #go faster
      if key[pygame.K_f]:
        (x, y) = (3, 3)

      #go slower
      if key[pygame.K_s]:
        (x, y) = (4, 4)

      # do set manouvre
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

      # stop
      if key[pygame.K_SPACE]:
        (x, y) = (2, 2)

      # default case, i.e. no inputs
      self.adaptor.sendCommand(x, y)
      (x, y) = (0, 0)

# The JoystickHandler class periodically polls a Sony Dual Shock Controller analogue
# sticks and button events
class JoystickHandler:

  def __init__(self, adaptor):
    self.adaptor = adaptor
    pygame.joystick.init()

    if pygame.joystick.get_count() < 1:
        print("Unable to detect joystick. Exiting.")
        sys.exit()
        
    self.joystick = pygame.joystick.Joystick(0)
    self.joystick.init()


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
    print "      Use left analogue stick for direction"
    print "      Use right analogue stick for speed"
    print "      'X' = STOP"
    print "      'esc' = QUIT"
    print ""
    print ""
    print ""
    print ""
    print ""
    print ""
    print ""
    print ""

  def start(self):

    global DEBUG_ON 
    
    leftRightTxt = ""
    upDownTxt = ""
    fasterSlowerTxt = ""
    stopButtonTxt = "" 

    gameRunning = True

    # go right x = 1, go left x = -1 
    x = 0
    # go forward x = 1, go backward x = -1 
    y = 0

    # the main event loop
    while gameRunning:

      # Check the keys periodically
      time.sleep(0.15)

      for event in pygame.event.get():
        # Does the user want to quit?
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
          gameRunning = False

      # test joystick axes
      leftRightTxt = "----"
      upDownTxt = "----"
      fasterSlowerTxt = "----"
      stopButtonTxt = "----"
      
      # read inputs
      leftRightAxis = self.joystick.get_axis(0)
      upDownAxis = self.joystick.get_axis(1)
      fasterSlowerAxis = self.joystick.get_axis(3)
      debugButtonValue = self.joystick.get_button(12)
      stopButtonValue = self.joystick.get_button(14)
      
      # the input checks use a tolerance value so that the user
      # doesn't have to be *extremely* precise.
      if (leftRightAxis < -0.3):
        x = -1
        leftRightTxt = "Left"
      else:
        if (leftRightAxis > 0.3):
          x = 1
          leftRightTxt = "Right"

      if (upDownAxis < -0.3):
        y = 1
        upDownTxt = "Up"
      else:
        if (upDownAxis > 0.3):
          y = -1
          upDownTxt = "Down"

      if (fasterSlowerAxis < 0):
        (x, y) = (3, 3)
        fasterSlowerTxt = "IncreaseSpeed"
      else:
        if (fasterSlowerAxis > 0):
          (x, y) = (4, 4)
          fasterSlowerTxt = "DecreaseSpeed"

      if (stopButtonValue == 1):
        (x, y) = (2, 2)
        stopButtonTxt = "Stop"

      if (debugButtonValue == 1):
        DEBUG_ON = not DEBUG_ON
        if DEBUG_ON:
          print "Debug Mode On"
        else:
          print "Debug Mode Off"

      self.adaptor.sendCommand(x, y)
      (x, y) = (0, 0)

      logToConsole(leftRightTxt + "|" + upDownTxt + "|" + fasterSlowerTxt + "|" + stopButtonTxt)

def main():

  # Check command line inputs before starting for real
  if (len(sys.argv) < 2):
    print 'Please specify controller type (joystick/keyboard)'
    print 'e.g. python iracer.py keyboard'
    sys.exit()

  pygame.init()
  # get controller type from the command line
  controllerType = sys.argv[1]

  gameDisplay = pygame.display.set_mode((400, 200))
  pygame.display.set_caption('iRacer Controller')

  # to spam the pygame.KEYDOWN event every 100ms while key being pressed
  pygame.key.set_repeat(100, 100)

  # Let's initialise our devices
  iracer = iRacer(0x06, 0x10)
  adaptor = InputAdaptor(iracer)

  if (controllerType == 'keyboard'):
    kbHandler = KeyboardHandler(adaptor)
    kbHandler.displayHelp()
    kbHandler.start()
  else:
    if (controllerType == 'joystick'):
      joystickHandler = JoystickHandler(adaptor)
      joystickHandler.displayHelp()
      joystickHandler.start()
    else:
      print 'Please specify controller Type (joystick/keyboard)'

  # We're finished, so let's tidy up
  # sock.close()
  pygame.quit()
  quit()


if __name__ == "__main__":
  main()

