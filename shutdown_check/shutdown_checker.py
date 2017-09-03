#!/usr/bin/python

import RPi.GPIO as gpio
import time
import os

PIN_SHUTDOWN_REQ=25
PIN_RASPI_STAT=24

gpio.setmode(gpio.BCM)
gpio.setup(PIN_SHUTDOWN_REQ ,gpio.IN, pull_up_down=gpio.PUD_UP)

#set PIN_RASPI_STAT LOW when RasPi wakes up
#if RasPi is shutdown, the pin will be HIGH.
gpio.setup(PIN_RASPI_STAT, gpio.OUT)
gpio.output(PIN_RASPI_STAT,0)

count=0
while True:
	shutdown_stat = gpio.input(PIN_SHUTDOWN_REQ)
	time.sleep(.1)

	if shutdown_stat ==0 :
		print(count)
		count+=1
	if shutdown_stat ==1 :
		count=0
	if count>10 :
		os.system("sudo shutdown -h now")

