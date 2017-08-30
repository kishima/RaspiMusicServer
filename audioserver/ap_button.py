#!/usr/bin/env python
# -*- coding: utf-8 -*-

import grovepi

class ApButton:
	def __init__(self,pin):
		self.pin = pin
		return
	
	def get_button_stat(self):
		b = grovepi.digitalRead(self.pin)
		return b
