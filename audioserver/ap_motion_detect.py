import logging
import time
import grovepi
from collections import Counter
from collections import deque
import RPi.GPIO as gpio

class ApMotionDetect:
	def __init__(self,gpio_pin):
		self.pin = gpio_pin
		gpio.setmode(gpio.BCM)
		gpio.setup(self.pin ,gpio.IN)
		self.history = deque([0 for i in range(20)])
		return
	
	def check_status(self):
		stat = gpio.input(self.pin)
		if self.history[len(self.history)-1] == 0 and stat==1:
			logging.debug("motion detected")
		self.history.append(stat)
		self.history.popleft()
		if stat == 0:
			return False
		else:
			return True
	
	def get_latest_status(self):
		return self.history.count(1)