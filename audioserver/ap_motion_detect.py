import logging
import time
import grovepi
from collections import Counter
from collections import deque
import RPi.GPIO as gpio

class ApMotionDetect:
#	def __init__(self,digital_pin):
#		self.pin = digital_pin
#		grovepi.pinMode(self.pin,"INPUT")
	def __init__(self,gpio_pin):
		self.pin = gpio_pin
		gpio.setmode(gpio.BCM)
		gpio.setup(self.pin ,gpio.IN)
		self.history = deque([0 for i in range(20)])
		return
	
	def check_status(self):
		#stat = grovepi.digitalRead(self.pin)
		stat = gpio.input(self.pin)
		self.history.append(stat)
		self.history.popleft()
		if stat == 0:
			return False
		else:
			return True
	
	def get_latest_status(self):
		return self.history.count(1)