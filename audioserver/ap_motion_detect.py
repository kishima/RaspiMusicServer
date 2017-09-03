import logging
import time
import grovepi

class ApMotionDetect:
	def __init__(self,digital_pin):
		self.pin = digital_pin
		grovepi.pinMode(self.pin,"INPUT")
		return
	
	def check_status(self):
		stat = grovepi.digitalRead(self.pin)
		if stat == 1:
			return False
		else:
			return True