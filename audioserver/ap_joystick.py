#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
import grovepi

class ApJoystick:
	def __init__(self,pinX,pinY):
		self.xPin = pinX
		self.yPin = pinY
		grovepi.pinMode(self.xPin,"INPUT")
		grovepi.pinMode(self.yPin,"INPUT")
		return
	
	def get_axis(self):
		x = grovepi.analogRead(self.xPin)
		y = grovepi.analogRead(self.yPin)
		c = 510
		m = 150

		Bx = 0
		if x < c-m:
			Bx = -1 
		if x > c+m:
			Bx = 1

		By = 0
		if y < c-m:
			By = -1
		if y > c+m:
			By = 1
		return Bx,By


