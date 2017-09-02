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
		
class ApLcd(threading.Thread):

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
		if q[0] == 'put_text':
			self.do_put_text(q[1])
		if q[0] == 'clear_display':
			self.do_clear_display()
		return self.queue.empty()

	def send_command(self,cmd):
		self.bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)
		return

	def clear_display(self):
		self.queue.put(['clear_display',""])
		return

	def do_clear_display(self):
		self.send_command(0x01) # clear display
		time.sleep(.05)
		return

	def put_text(self,text):
		self.queue.put(['put_text',text])
		return
	
	def do_put_text(self,text):
		self.send_command(0x02) # return home
		time.sleep(.05)
		
		self.send_command(0x08 | 0x04) # display on, no cursor
		self.send_command(0x28) # 2 lines
		time.sleep(.05)
		count = 0
		row = 0
		for c in text:
			if c == '\n' or count == 16:
				count = 0
				row += 1
				if row == 2:
					break
				self.send_command(0xc0)
				if c == '\n':
					continue
			count += 1
			self.bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))
		
	def put_temp_string(self,line,string):
		logging.debug("put_temp_string")
		return
		
	def set_bg_rgb(self,r,g,b):
		self.bus.write_byte_data(DISPLAY_RGB_ADDR,0,0)
		self.bus.write_byte_data(DISPLAY_RGB_ADDR,1,0)
		self.bus.write_byte_data(DISPLAY_RGB_ADDR,0x08,0xaa)
		self.bus.write_byte_data(DISPLAY_RGB_ADDR,4,r)
		self.bus.write_byte_data(DISPLAY_RGB_ADDR,3,g)
		self.bus.write_byte_data(DISPLAY_RGB_ADDR,2,b)
		return
