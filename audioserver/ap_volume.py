#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import subprocess
import grovepi
from collections import Counter
from collections import deque
import logging

class ApVolume:
	LED_OFF        = 0
	LED_ON         = 1
	LED_BLINK      = 2
	LED_BLINK_NSEC = 3
	
	def __init__(self,barPin,ledPin,display_obj):
		self.slide = barPin
		self.led   = ledPin
		self.lcd   = display_obj
		grovepi.pinMode(self.slide,"INPUT")
		grovepi.pinMode(self.led,"OUTPUT")
		self.last_val = deque([50,50,50])
		value=50
		try:
			self.last_val[0] = self.last_val[1] = self.last_val[2] = self.get_vol()
		except:
			logging.debug("ApSlideBar.get_vol() error")
		self.last_set_vol = -1
		self.init_led()
		self.led_set_blink_nsec(3)
		return
		
	def init_led(self):
		self.led_stat = 0
		self.led_off()
		self.led_mode = self.LED_OFF
		self.led_count = 0
		self.led_count_offset = 0
		return

	def led_on(self):
		grovepi.digitalWrite(self.led,1)
		self.led_stat = 1
		return
	
	def led_off(self):
		grovepi.digitalWrite(self.led,0)
		self_led_stat = 0
		return
	
	def led_update(self,count):
		if self.led_mode == self.LED_OFF and self.led_stat == 1:
			self.led_off()
		elif self.led_mode == self.LED_ON and self.led_stat == 0:
			self.led_on()
		elif self.led_mode == self.LED_BLINK:
			if (count - self.led_count_offset) % 10 < 5:
				self.led_on()
			else:
				self.led_off()
		elif  self.led_mode == self.LED_BLINK_NSEC:
			if self.led_count_offset == -1:
				self.led_count_offset = count #in order to turn on LED immediately when LED_BLINK_NSEC is set.
			if self.led_count > 0:
				if (count - self.led_count_offset) % 4 < 2:
					self.led_on()
				else:
					self.led_off()
			else:
				self.led_count = 0
				self.led_off()
				self.led_mode == self.LED_OFF
				return
			self.led_count -= 1
		return
	
	def led_set_blink_nsec(self, time):
		if self.led_count > int(20 * time):
			return
		self.led_count = int(20 * time)
		self.led_mode = self.LED_BLINK_NSEC
		self.led_count_offset = -1
		return
	
	def get_vol(self):
		value = grovepi.analogRead(self.slide)
		value = int(value / 1023.0 * 100.0)
		value = 100 - value
		if value > 100 :
			value = 100
		if value < 0 :
			value = 0
		return value

	def set_vol(self,value):
		if value < 5:
			value=0
		cmd = "mpc volume "+str(value)
		proc = subprocess.call(cmd, shell=True)
		self.last_set_vol = value
		self.led_set_blink_nsec(0.25)
		self.lcd.put_text("      V="+str(value)+"   ")
		return

	def volume_check(self):
		value = self.get_vol()
		self.last_val.append(value)
		self.last_val.popleft()
		counter = Counter(self.last_val)
		value = counter.most_common() # sometimes get_vol returns strange value. have to avoid it.
		value = value[0][0]
		if abs(self.last_set_vol - value) > 5 :
			self.set_vol(value)
		return
	
	def get_current_volset(self):
		return self.last_set_vol

