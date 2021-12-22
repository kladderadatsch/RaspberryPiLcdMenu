#!/usr/bin/python
#
# Created by Alan Aufderheide, February 2013
#
# Updated to Python 3 using latest adafruit display lib by kladderadatsch, December 2021
#
# This provides a menu driven application using the LCD Plates
# from Adafruit Electronics.

import subprocess
import os
#import split
import string 
from time import sleep, strftime, localtime
from datetime import datetime, timedelta
from xml.dom.minidom import *
import board
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd
from ListSelector import ListSelector

import smbus2

# set DEBUG=1 for print debug statements
DEBUG = 0
DISPLAY_ROWS = 2
DISPLAY_COLS = 16
SLEEP_TIME = 0.01

# set to 0 if you want the LCD to stay on, 1 to turn off and on auto
AUTO_OFF_LCD = 0

configfile = 'lcdmenu.xml'

# Initialise I2C bus.
i2c = board.I2C()  # uses board.SCL and board.SDA

# Initialise the LCD class
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, DISPLAY_COLS, DISPLAY_ROWS)

lcd.clear()


# commands
def DoQuit():
    lcd.clear()
    lcd.message = 'Are you sure?\nPress Sel for Y'
    while 1:
        if lcd.left_button:
            break
        if lcd.select_button:
            lcd.clear()
            lcd.color = [0, 0, 0]
            quit()
        sleep(SLEEP_TIME)

def DoShutdown():
    lcd.clear()
    lcd.message = 'Are you sure?\nPress Sel for Y'
    while 1:
        if lcd.left_button:
            break
        if lcd.select_button:
            lcd.clear()
            lcd.color = [0, 0, 0]
            subprocess.check_output('sudo shutdown -h now')
            quit()
        sleep(SLEEP_TIME)

def DoReboot():
    lcd.clear()
    lcd.message = 'Are you sure?\nPress Sel for Y'
    while 1:
        if lcd.left_button:
            break
        if lcd.select_button:
            lcd.clear()
            lcd.color = [0, 0, 0]
            subprocess.check_output('sudo reboot')
            quit()
        sleep(SLEEP_TIME)

def LcdOff():
    global currentLcd
    lcd.display = False
    currentLcd = lcd

def LcdOn():
    global currentLcd
    lcd.display = True
    currentLcd = lcd

def LcdRed():
    global currentLcd
    lcd.color = [100,0,0]
    currentLcd = lcd

def LcdGreen():
    global currentLcd
    lcd.color = [0,100,0]
    currentLcd = lcd

def LcdBlue():
    global currentLcd
    lcd.color = [0,0,100]
    currentLcd = lcd

def LcdYellow():
    global currentLcd
    lcd.color = [100,100,0]
    currentLcd = lcd

def LcdTeal():
    global currentLcd
    lcd.color = [50,50,50]
    currentLcd = lcd

def LcdViolet():
    global currentLcd
    lcd.color = [50,50,100]
    currentLcd = lcd

def ShowDateTime():
    if DEBUG:
        print('in ShowDateTime')
    lcd.clear()
    while not(lcd.left_button):
        sleep(SLEEP_TIME)
        lcd.home()
        lcd.message = strftime('%a %b %d %Y\n%I:%M:%S %p', localtime())
    
def ValidateDateDigit(current, curval):
    # do validation/wrapping
    if current == 0: # Mm
        if curval < 1:
            curval = 12
        elif curval > 12:
            curval = 1
    elif current == 1: #Dd
        if curval < 1:
            curval = 31
        elif curval > 31:
            curval = 1
    elif current == 2: #Yy
        if curval < 1950:
            curval = 2050
        elif curval > 2050:
            curval = 1950
    elif current == 3: #Hh
        if curval < 0:
            curval = 23
        elif curval > 23:
            curval = 0
    elif current == 4: #Mm
        if curval < 0:
            curval = 59
        elif curval > 59:
            curval = 0
    elif current == 5: #Ss
        if curval < 0:
            curval = 59
        elif curval > 59:
            curval = 0
    return curval

def SetDateTime():
    if DEBUG:
        print('in SetDateTime')
    # M D Y H:M:S AM/PM
    curtime = localtime()
    month = curtime.tm_mon
    day = curtime.tm_mday
    year = curtime.tm_year
    hour = curtime.tm_hour
    minute = curtime.tm_min
    second = curtime.tm_sec
    ampm = 0
    if hour > 11:
        hour -= 12
        ampm = 1
    curr = [0,0,0,1,1,1]
    curc = [2,5,11,1,4,7]
    curvalues = [month, day, year, hour, minute, second]
    current = 0 # start with month, 0..14

    lcd.clear()
    lcd.message(strftime('%b %d, %Y  \n%I:%M:%S %p  ', curtime))
    lcd.blink = True
    lcd.cursor_position(curc[current], curr[current])
    sleep(0.5)
    while 1:
        curval = curvalues[current]
        if lcd.up_button:
            curval += 1
            curvalues[current] = ValidateDateDigit(current, curval)
            curtime = (curvalues[2], curvalues[0], curvalues[1], curvalues[3], curvalues[4], curvalues[5], 0, 0, 0)
            lcd.home()
            lcd.message = strftime('%b %d, %Y  \n%I:%M:%S %p  ', curtime)
            lcd.cursor_position(curc[current], curr[current])
        if lcd.down_button:
            curval -= 1
            curvalues[current] = ValidateDateDigit(current, curval)
            curtime = (curvalues[2], curvalues[0], curvalues[1], curvalues[3], curvalues[4], curvalues[5], 0, 0, 0)
            lcd.home()
            lcd.message = strftime('%b %d, %Y  \n%I:%M:%S %p  ', curtime)
            lcd.cursor_position(curc[current], curr[current])
        if lcd.right_button:
            current += 1
            if current > 5:
                current = 5
            lcd.cursor_position(curc[current], curr[current])
        if lcd.left_button:
            current -= 1
            if current < 0:
                lcd.blink = False
                return
            lcd.cursor_position(curc[current], curr[current])
        if lcd.select_button:
            # set the date time in the system
            lcd.blink = False
            os.system(strftime("sudo date --set='%d %b %Y %H:%M:%S'", curtime))
            break
        sleep(SLEEP_TIME)

    lcd.blink = False

def ShowIPAddress():
    if DEBUG:
        print('in ShowIPAddress')
    lcd.clear()
    lcd.message = subprocess.check_output('/sbin/ifconfig').split('\n')[1].split()[1][5:]
    while 1:
        if lcd.left_button:
            break
        sleep(SLEEP_TIME)
    
#only use the following if you find useful
def Use10Network():
    'Allows you to switch to a different network for local connection'
    lcd.clear()
    lcd.message = 'Are you sure?\nPress Sel for Y'
    while 1:
        if lcd.left_button:
            break
        if lcd.select_button:
            # uncomment the following once you have a separate network defined
            #subprocess.check_output('sudo cp /etc/network/interfaces.hub.10 /etc/network/interfaces')
            lcd.clear()
            lcd.message = 'Please reboot'
            sleep(1.5)
            break
        sleep(SLEEP_TIME)

#only use the following if you find useful
def UseDHCP():
    'Allows you to switch to a network config that uses DHCP'
    lcd.clear()
    lcd.message = 'Are you sure?\nPress Sel for Y'
    while 1:
        if lcd.left_button:
            break
        if lcd.select_button:
            # uncomment the following once you get an original copy in place
            #subprocess.check_output('sudo cp /etc/network/interfaces.orig /etc/network/interfaces')
            lcd.clear()
            lcd.message = 'Please reboot'
            sleep(1.5)
            break
        sleep(SLEEP_TIME)

def ShowLatLon():
    if DEBUG:
        print('in ShowLatLon')

def SetLatLon():
    if DEBUG:
        print('in SetLatLon')
    
def SetLocation():
    if DEBUG:
        print('in SetLocation')
    global lcd
    list = []
    # coordinates usable by ephem library, lat, lon, elevation (m)
    list.append(['New York', '40.7143528', '-74.0059731', 9.775694])
    list.append(['Paris', '48.8566667', '2.3509871', 35.917042])
    selector = ListSelector(list, lcd)
    item = selector.Pick()
    # do something useful
    if (item >= 0):
        chosen = list[item]

def CompassGyroViewAcc():
    if DEBUG:
        print('in CompassGyroViewAcc')

def CompassGyroViewMag():
    if DEBUG:
        print('in CompassGyroViewMag')

def CompassGyroViewHeading():
    if DEBUG:
        print('in CompassGyroViewHeading')

def CompassGyroViewTemp():
    if DEBUG:
        print('in CompassGyroViewTemp')

def CompassGyroCalibrate():
    if DEBUG:
        print('in CompassGyroCalibrate')
    
def CompassGyroCalibrateClear():
    if DEBUG:
        print('in CompassGyroCalibrateClear')
    
def TempBaroView():
    if DEBUG:
        print('in TempBaroView')

def TempBaroCalibrate():
    if DEBUG:
        print('in TempBaroCalibrate')
    
def AstroViewAll():
    if DEBUG:
        print('in AstroViewAll')

def AstroViewAltAz():
    if DEBUG:
        print('in AstroViewAltAz')
    
def AstroViewRADecl():
    if DEBUG:
        print('in AstroViewRADecl')

def CameraDetect():
    if DEBUG:
        print('in CameraDetect')
    
def CameraTakePicture():
    if DEBUG:
        print('in CameraTakePicture')

def CameraTimeLapse():
    if DEBUG:
        print('in CameraTimeLapse')

# Get a word from the UI, a character at a time.
# Click select to complete input, or back out to the left to quit.
# Return the entered word, or None if they back out.
def GetWord():
    lcd.clear()
    lcd.blink = True
    sleep(0.75)
    curword = list('A')
    curposition = 0
    while 1:
        if lcd.up_button:
            if (ord(curword[curposition]) < 127):
                curword[curposition] = chr(ord(curword[curposition])+1)
            else:
                curword[curposition] = chr(32)
        if lcd.down_button:
            if (ord(curword[curposition]) > 32):
                curword[curposition] = chr(ord(curword[curposition])-1)
            else:
                curword[curposition] = chr(127)
        if lcd.right_button:
            if curposition < DISPLAY_COLS - 1:
                curword.append('A')
                curposition += 1
                lcd.cursor_position(curposition, 0)
            sleep(0.75)
        if lcd.left_button:
            curposition -= 1
            if curposition <  0:
                lcd.blink = False
                return
            lcd.cursor_position(curposition, 0)
        if lcd.select_button:
            # return the word
            sleep(0.75)
            return ''.join(curword)
        lcd.home()
        lcd.message = ''.join(curword)
        lcd.cursor_position(curposition, 0)
        sleep(SLEEP_TIME)

    lcd.blink = False

# An example of how to get a word input from the UI, and then
# do something with it
def EnterWord():
    if DEBUG:
        print('in EnterWord')
    word = GetWord()
    lcd.clear()
    lcd.home()
    if word is not None:
        lcd.message = '>'+word+'<'
        sleep(5)

class CommandToRun:
    def __init__(self, myName, theCommand):
        self.text = myName
        self.commandToRun = theCommand
    def Run(self):
        self.clist = subprocess.check_output(self.commandToRun).split('\n')
        if len(self.clist) > 0:
            lcd.clear()
            lcd.message = self.clist[0]
            for i in range(1, len(self.clist)):
                while 1:
                    if lcd.down_button:
                        break
                    sleep(SLEEP_TIME)
                lcd.clear()
                lcd.message = self.clist[i-1]+'\n'+self.clist[i]          
                sleep(0.5)
        while 1:
            if lcd.left_button:
                break

class Widget:
    def __init__(self, myName, myFunction):
        self.text = myName
        self.function = myFunction
        
class Folder:
    def __init__(self, myName, myParent):
        self.text = myName
        self.items = []
        self.parent = myParent

def HandleSettings(node):
    global lcd
    if node.getAttribute('lcdColor').lower() == 'red':
        LcdRed()
    elif node.getAttribute('lcdColor').lower() == 'green':
        LcdGreen()
    elif node.getAttribute('lcdColor').lower() == 'blue':
        LcdBlue()
    elif node.getAttribute('lcdColor').lower() == 'yellow':
        LcdYellow()
    elif node.getAttribute('lcdColor').lower() == 'teal':
        LcdTeal()
    elif node.getAttribute('lcdColor').lower() == 'violet':
        LcdViolet()
    elif node.getAttribute('lcdColor').lower() == 'white':
        LcdOn()
    if node.getAttribute('lcdBacklight').lower() == 'on':
        LcdOn()
    elif node.getAttribute('lcdBacklight').lower() == 'off':
        LcdOff()

def ProcessNode(currentNode, currentItem):
    children = currentNode.childNodes

    for child in children:
        if isinstance(child, xml.dom.minidom.Element):
            if child.tagName == 'settings':
                HandleSettings(child)
            elif child.tagName == 'folder':
                thisFolder = Folder(child.getAttribute('text'), currentItem)
                currentItem.items.append(thisFolder)
                ProcessNode(child, thisFolder)
            elif child.tagName == 'widget':
                thisWidget = Widget(child.getAttribute('text'), child.getAttribute('function'))
                currentItem.items.append(thisWidget)
            elif child.tagName == 'run':
                thisCommand = CommandToRun(child.getAttribute('text'), child.firstChild.data)
                currentItem.items.append(thisCommand)

class Display:
    def __init__(self, folder):
        self.curFolder = folder
        self.curTopItem = 0
        self.curSelectedItem = 0
    def display(self):
        if self.curTopItem > len(self.curFolder.items) - DISPLAY_ROWS:
            self.curTopItem = len(self.curFolder.items) - DISPLAY_ROWS
        if self.curTopItem < 0:
            self.curTopItem = 0
        if DEBUG:
            print('------------------')
        str = ''
        for row in range(self.curTopItem, self.curTopItem+DISPLAY_ROWS):
            if row > self.curTopItem:
                str += '\n'
            if row < len(self.curFolder.items):
                if row == self.curSelectedItem:
                    cmd = '-'+self.curFolder.items[row].text
                    if len(cmd) < DISPLAY_COLS:
                        for row in range(len(cmd), DISPLAY_COLS):
                            cmd += ' '
                    if DEBUG:
                        print('|'+cmd+'|')
                    str += cmd
                else:
                    cmd = ' '+self.curFolder.items[row].text
                    if len(cmd) < DISPLAY_COLS:
                        for row in range(len(cmd), DISPLAY_COLS):
                            cmd += ' '
                    if DEBUG:
                        print('|'+cmd+'|')
                    str += cmd
        if DEBUG:
            print('------------------')
        lcd.home()
        lcd.message = str

    def update(self, command):
        global currentLcd
        global lcdstart
        lcd.color = currentLcd.color
        lcdstart = datetime.now()
        if DEBUG:
            print('do',command)
        if command == 'u':
            self.up()
        elif command == 'd':
            self.down()
        elif command == 'r':
            self.right()
        elif command == 'l':
            self.left()
        elif command == 's':
            self.select()
    def up(self):
        if self.curSelectedItem == 0:
            return
        elif self.curSelectedItem > self.curTopItem:
            self.curSelectedItem -= 1
        else:
            self.curTopItem -= 1
            self.curSelectedItem -= 1
    def down(self):
        if self.curSelectedItem+1 == len(self.curFolder.items):
            return
        elif self.curSelectedItem < self.curTopItem+DISPLAY_ROWS-1:
            self.curSelectedItem += 1
        else:
            self.curTopItem += 1
            self.curSelectedItem += 1
    def left(self):
        if isinstance(self.curFolder.parent, Folder):
            # find the current in the parent
            itemno = 0
            index = 0
            for item in self.curFolder.parent.items:
                if self.curFolder == item:
                    if DEBUG:
                        print('foundit')
                    index = itemno
                else:
                    itemno += 1
            if index < len(self.curFolder.parent.items):
                self.curFolder = self.curFolder.parent
                self.curTopItem = index
                self.curSelectedItem = index
            else:
                self.curFolder = self.curFolder.parent
                self.curTopItem = 0
                self.curSelectedItem = 0
    def right(self):
        if isinstance(self.curFolder.items[self.curSelectedItem], Folder):
            self.curFolder = self.curFolder.items[self.curSelectedItem]
            self.curTopItem = 0
            self.curSelectedItem = 0
        elif isinstance(self.curFolder.items[self.curSelectedItem], Widget):
            if DEBUG:
                print('eval', self.curFolder.items[self.curSelectedItem].function)
            eval(self.curFolder.items[self.curSelectedItem].function+'()')
        elif isinstance(self.curFolder.items[self.curSelectedItem], CommandToRun):
            self.curFolder.items[self.curSelectedItem].Run()

    def select(self):
        if DEBUG:
            print('check widget')
        if isinstance(self.curFolder.items[self.curSelectedItem], Widget):
            if DEBUG:
                print('eval', self.curFolder.items[self.curSelectedItem].function)
            eval(self.curFolder.items[self.curSelectedItem].function+'()')

# now start things up
uiItems = Folder('root','')

dom = parse(configfile) # parse an XML file by name

top = dom.documentElement

lcd.display = True
lcd.color = [0, 100, 0]
currentLcd = lcd
LcdGreen()
ProcessNode(top, uiItems)

display = Display(uiItems)
display.display()

if DEBUG:
    print('start while')

lcdstart = datetime.now()
while 1:
    if (lcd.left_button):
        display.update('l')
        display.display()
        sleep(SLEEP_TIME)

    if (lcd.up_button):
        display.update('u')
        display.display()
        sleep(SLEEP_TIME)

    if (lcd.down_button):
        display.update('d')
        display.display()
        sleep(SLEEP_TIME)

    if (lcd.right_button):
        display.update('r')
        display.display()
        sleep(SLEEP_TIME)

    if (lcd.select_button):
        display.update('s')
        display.display()
        sleep(SLEEP_TIME)

    if AUTO_OFF_LCD:
        lcdtmp = lcdstart + timedelta(seconds=5)
        if (datetime.now() > lcdtmp):
            lcd.color = [0, 0, 0]

