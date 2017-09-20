#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import smbus
import RPi.GPIO as GPIO
import logging
import subprocess
import grovepi
from collections import Counter
from collections import deque
import threading
import Queue

		
class ApLcd(threading.Thread):
	TEXT_ADDR = 0x3e

	def __init__(self):
		threading.Thread.__init__(self)
		self.setDaemon(True)
		self.queue = Queue.Queue()
		self.bus = smbus.SMBus(1)
		self.current_text=""
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
		if q[0] == 'put_text_pos':
			self.do_put_text_pos(q[1],q[2],q[3])
		return self.queue.empty()

	def i2c_byte_write(self,addr,type,cmd):
		for num in range(1,5):
			try:
				self.bus.write_byte_data(addr,type,cmd)
			except IOError:
				logging.debug("I2C IOerror in LCD in Arduino communication > Retry")
				time.sleep(num)
			else:
				return True
		logging.debug("I2C IOerror in LCD in Arduino communication > Retry FAILE!")
		return Flase
		
	def send_command(self,cmd):
		self.i2c_byte_write(self.TEXT_ADDR,0x80,cmd)
		return

	def clear_display(self):
		self.queue.put(['clear_display',""])
		return

	def do_clear_display(self):
		self.send_command(0x01) # clear display
		time.sleep(.05)
		return

	def put_temp_text(self,text,time,x,y):
		self.put_text_pos(text,x,y)
		return

	def put_text_pos(self,text,x,y):
		self.queue.put(['put_text_pos',text,x,y])
		return

	def do_put_text_pos(self,text,x,y):
		self.send_command(0x02) # return home
		time.sleep(.05)
		
		for n in range(x):
			self.send_command(0x10) # cursol_shift
			self.send_command(0x04) # move right
		
		return
		
	def put_text(self,text):
		self.queue.put(['put_text',text])
		return
	
	def do_put_text(self,text):
		self.current_text = text
		#cmd=home
		self.send_command(0x02)
		time.sleep(.05)
		#cmd=disp control > cursor off / cmd=function set > 2line
		self.send_command(0x08 | 0x04) 
		self.send_command(0x28) 
		time.sleep(.05)
		count = 0
		row = 0
		for c in text:
			if c == '\n' or count == 16:
				count = 0
				row += 1
				if row == 2:
					break
				#cmd=set c gram addr, set d gram addr
				self.send_command(0xc0)
				if c == '\n':
					continue
			count += 1
			self.i2c_byte_write(self.TEXT_ADDR,0x40,ord(c))

	def update(self,count):
		return
		
	def set_bg_rgb(self,r,g,b):
		self.bus.write_byte_data(0x62,0,0)
		self.bus.write_byte_data(0x62,1,0)
		self.bus.write_byte_data(0x62,0x08,0xaa)
		self.bus.write_byte_data(0x62,4,r)
		self.bus.write_byte_data(0x62,3,g)
		self.bus.write_byte_data(0x62,2,b)
		return
