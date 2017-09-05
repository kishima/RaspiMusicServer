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

class MusicServer:
	
	def __init__(self):
		self.lcd = ap_lcd.ApLcd()
		self.lcd.set_bg_rgb(0,50,0)
		self.lcd.start()
		self.gesture   = grove_gesture_sensor.gesture()
		self.gesture.init()
		self.joystick  = ap_joystick.ApJoystick(pinX=1,pinY=0)
		self.button    = ap_button.ApButton(pin=3)
		self.volume    = ap_volume.ApVolume(barPin=2,ledPin=17,display_obj=self.lcd)
		self.motion    = ap_motion_detect.ApMotionDetect(gpio_pin=23)
		self.timer     = arduino_timer.ArduinoTimer(self.motion)
		self.timer.set_timer_once()

		self.menu = ap_menu.ApMenu(self.lcd,self.volume)
		time.sleep(0.1)

	def main_loop(self):
		cnt = 0
		last_button_stat = 0
		last_x = 0
		last_y = 0
		while True:
			try:
				button_stat=0
				x=0
				y=0
				
				if 0 == cnt % 4 : #50ms*4=200ms
					self.motion.check_status()
					self.volume.volume_check()

				if 0 == cnt % 2 : #50ms*2=100ms
					self.gesture.print_gesture()
					
					current_button_stat = self.button.get_button_stat()
					if last_button_stat == 0 and current_button_stat == 1:
						button_stat = 1
					last_button_stat = current_button_stat
					
					current_x,current_y = self.joystick.get_axis()
					if last_x == 0 and current_x != 0:
						x = current_x
					if last_y == 0 and current_y != 0:
						y = current_y
					last_x,last_y = current_x,current_y
		
				self.volume.led_update(cnt)
				self.menu.update(cnt,x,y,button_stat)
				
				if 0 == cnt % 20:
					self.timer.check_event()
		
				cnt+=1
				if cnt>30000 :
					cnt = 0
		
				time.sleep(0.05)
		
			except IOError:
				logging.debug ("IOError")

music_server = MusicServer()
music_server.main_loop()