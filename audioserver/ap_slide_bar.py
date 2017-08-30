#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import subprocess
import grovepi
from collections import Counter
from collections import deque
import logging

class ApSlideBar:
		
	def __init__(self,barPin,ledPin):
		self.slide = barPin
		self.led   = ledPin
		grovepi.pinMode(self.slide,"INPUT")
		grovepi.pinMode(self.led,"OUTPUT")
		self.last_val = deque([50,50,50])
		value=50
		try:
			self.last_val[0] = self.last_val[1] = self.last_val[2] = self.get_vol()
		except:
			logging.debug("ApSlideBar.get_vol() error")
		self.last_set_vol = -1
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
		cmd = "mpc volume "+str(value)
		proc = subprocess.call(cmd, shell=True)
		self.last_set_vol = value
		#logging.debug("set OK")
		return

	def volume_act(self):
		value = self.get_vol()
		self.last_val.append(value)
		self.last_val.popleft()
		counter = Counter(self.last_val)
		value = counter.most_common() # sometimes get_vol returns strange value. have to avoid it.
		value = value[0][0]
		if abs(self.last_set_vol - value) > 5 :
			#logging.debug("sensor_value =", value)
			self.set_vol(value)
		return
	
	def get_current_volset(self):
		return self.last_set_vol

