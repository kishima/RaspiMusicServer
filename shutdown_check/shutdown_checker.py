#!/usr/bin/python

import RPi.GPIO as gpio
import time
import os

gpio.setmode(gpio.BCM)
gpio.setup(25 ,gpio.IN, pull_up_down=gpio.PUD_UP)
#gpio.setup(25 ,gpio.IN)

gpio.setup(24, gpio.OUT)

gpio.output(24,0)

count=0
while True:
	shutdown_stat = gpio.input(25)
	#print(shutdown_stat)
	time.sleep(.1)

	if shutdown_stat ==0 :
		print(count)
		count+=1
	if shutdown_stat ==1 :
		count=0
	if count>10 :
		os.system("sudo shutdown -h now")

