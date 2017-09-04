import logging
import time
import grovepi
from collections import Counter
from collections import deque

class ApMotionDetect:
	def __init__(self,digital_pin):
		self.pin = digital_pin
		grovepi.pinMode(self.pin,"INPUT")
		self.history = deque([1 for i in range(20)])
		return
	
	def check_status(self):
		stat = grovepi.digitalRead(self.pin)
		self.history.append(stat)
		self.history.popleft()
		if stat == 1:
			return False
		else:
			return True
	
	def get_latest_status(self):
		return self.history.count(0)