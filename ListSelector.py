# ListSelector.py
#
# Created by Alan Aufderheide, February 2013
#
# Updated to Python 3 using latest adafruit display lib by kladderadatsch, December 2021
#
# Given a list of items in the passed list,
# allow quick access by picking letters progressively.
# Uses up/down to go up and down where cursor is.
# Move left/right to further filter to quickly get to item.
# Still need to do case insensitive, and sort.
from time import sleep
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd

class ListSelector:
    def __init__(self, theList, theLcd):
        self.list = []
        for item in theList:
            if isinstance(item, basestring):
                self.list.append(item)
            else:
                self.list.append(item[0])
        self.lcd = theLcd

    def Pick(self):
        sleep(0.5)
        curitem = 0
        curlen = 1
        self.lcd.clear()
        self.lcd.message = 'self.list[curitem])'
        self.lcd.home()
        self.lcd.blink = True
        self.lcd.cursor_position(0,0)
        while 1:
            if self.lcd.select_button:
                sleep(0.5)
                break
            if self.lcd.up_button:
                tempitem = curitem
                prevstr = self.list[tempitem][:curlen]
                while tempitem > 0 and self.list[tempitem-1][:curlen-1] == self.list[curitem][:curlen-1] and self.list[tempitem][:curlen] >= prevstr:
                    tempitem -= 1
                curitem = tempitem
                # overwrite message, uses spaces to clear previous entries
                self.lcd.home()
                self.lcd.message = 'self.list[curitem]+'                ''
                self.lcd.cursor_position(curlen-1,0)
                sleep(0.5)
            if self.lcd.down_button:
                nextstr = self.list[curitem][:curlen-1]+chr(ord(self.list[curitem][curlen-1])+1)
                tempitem = curitem
                while tempitem+1 < len(self.list) and self.list[tempitem+1][:curlen-1] == self.list[curitem][:curlen-1] and self.list[tempitem] < nextstr:
                    tempitem += 1
                if tempitem < len(self.list):
                    curitem = tempitem
                # overwrite message, uses spaces to clear previous entries
                self.lcd.home()
                self.lcd.message = 'self.list[curitem]+'                ''
                self.lcd.cursor_position(curlen-1,0)
                sleep(0.5)
            if self.lcd.right_button:
                if curlen < len(self.list[curitem]):
                    curlen += 1
                self.lcd.cursor_position(curlen-1,0)
                self.lcd.blink = True
                sleep(0.5)
            if self.lcd.left_button:
                if curlen > 1:
                    curlen -= 1
                else:
                    sleep(0.5)
                    curitem = -1
                    break
                self.lcd.cursor_position(curlen-1,0)
                self.lcd.blink = True
                sleep(0.5)

        self.lcd.cursor_position(0,0)
        self.lcd.blink = False
        return curitem

