#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time,sys
import logging
import subprocess
import grovepi
from collections import Counter
from collections import deque
import threading
import Queue

DISPLAY_RGB_ADDR = 0x62
DISPLAY_TEXT_ADDR = 0x3e
		
class ApLed(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.setDaemon(True)
		self.queue = Queue.Queue()
		if sys.platform == 'uwp':
			import winrt_smbus as smbus
			self.bus = smbus.SMBus(1)
		else:
			import smbus
			import RPi.GPIO as GPIO
			rev = GPIO.RPI_REVISION
			if rev == 2 or rev == 3:
				self.bus = smbus.SMBus(1)
			else:
				self.bus = smbus.SMBus(0)
		return

	def run(self):
		logging.debug("start:run")
		while True:
			self.check_queue()
		return

	def check_queue(self):
		q = self.queue.get()
		if q[0] == 'setText':
			self.doSetText_norefresh(q[1])
		if q[0] == 'clear_display':
			self.do_clear_display()
		return self.queue.empty()

	def textCommand(self,cmd):
		self.bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)
		return

	def clear_display(self):
		self.queue.put(['clear_display',""])
		return

	def do_clear_display(self):
		self.textCommand(0x01) # clear display
		time.sleep(.05)
		return

	def setText_norefresh(self,text):
		#logging.debug("setText_norefresh:put queue")
		self.queue.put(['setText',text])
		return
	
	def doSetText_norefresh(self,text):
		#logging.debug(text)
		#return
		self.textCommand(0x02) # return home
		time.sleep(.05)
		
		self.textCommand(0x08 | 0x04) # display on, no cursor
		self.textCommand(0x28) # 2 lines
		time.sleep(.05)
		count = 0
		row = 0
		for c in text:
			if c == '\n' or count == 16:
				count = 0
				row += 1
				if row == 2:
					break
				self.textCommand(0xc0)
				if c == '\n':
					continue
			count += 1
			self.bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))
		
	def put_temp_string(self,line,string):
		logging.debug("put_temp_string")
		return
		
	def setRGB(self,r,g,b):
		self.bus.write_byte_data(DISPLAY_RGB_ADDR,0,0)
		self.bus.write_byte_data(DISPLAY_RGB_ADDR,1,0)
		self.bus.write_byte_data(DISPLAY_RGB_ADDR,0x08,0xaa)
		self.bus.write_byte_data(DISPLAY_RGB_ADDR,4,r)
		self.bus.write_byte_data(DISPLAY_RGB_ADDR,3,g)
		self.bus.write_byte_data(DISPLAY_RGB_ADDR,2,b)
		return