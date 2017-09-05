#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import ap_volume
import ap_lcd
import ap_joystick
import ap_button
import ap_menu
import ap_motion_detect
import arduino_timer
import grove_gesture_sensor

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s (%(threadName)-10s) %(message)s',)

lcd = ap_lcd.ApLcd()
lcd.set_bg_rgb(0,50,0)
lcd.start()
gesture   = grove_gesture_sensor.gesture()
gesture.init()
joystick  = ap_joystick.ApJoystick(pinX=1,pinY=0)
button    = ap_button.ApButton(pin=3)
volume    = ap_volume.ApVolume(barPin=2,ledPin=17,display_obj=lcd)
motion    = ap_motion_detect.ApMotionDetect(gpio_pin=23)
timer     = arduino_timer.ArduinoTimer(motion)
timer.set_timer_once()

menu = ap_menu.ApMenu(lcd,volume)

cnt = 0
last_button_stat = 0
last_x = 0
last_y = 0

time.sleep(0.1)

while True:
	try:
		button_stat=0
		x=0
		y=0
		
		if 0 == cnt % 4 : #50ms*4=200ms
			motion.check_status()
			volume.volume_check()

		if 0 == cnt % 2 : #50ms*2=100ms
			gesture.print_gesture()
			
			current_button_stat = button.get_button_stat()
			if last_button_stat == 0 and current_button_stat == 1:
				button_stat = 1
			last_button_stat = current_button_stat
			
			current_x,current_y = joystick.get_axis()
			if last_x == 0 and current_x != 0:
				x = current_x
			if last_y == 0 and current_y != 0:
				y = current_y
			last_x,last_y = current_x,current_y

		volume.led_update(cnt)
		menu.update(cnt,x,y,button_stat)
		
		if 0 == cnt % 20:
			timer.check_event()
		
		cnt+=1
		if cnt>30000 :
			cnt = 0

		time.sleep(0.05)

	except IOError:
		logging.debug ("IOError")
