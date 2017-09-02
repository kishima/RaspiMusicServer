#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import ap_volume
import ap_lcd
import ap_joystick
import ap_button
import ap_menu

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s (%(threadName)-10s) %(message)s',)


lcd = ap_lcd.ApLcd()
lcd.set_bg_rgb(0,50,0)
lcd.start()
joystick  = ap_joystick.ApJoystick(pinX=1,pinY=0)
button    = ap_button.ApButton(pin=6)
volume    = ap_volume.ApVolume(barPin=2,ledPin=17,display_obj=lcd)
menu = ap_menu.ApMenu(lcd,volume)

cnt = 0

while True:
	try:
		button_stat=0
		x=0
		y=0
		
		if 0 == cnt % 4 :
			volume.volume_check()

		if 0 == cnt % 4:
			button_stat = button.get_button_stat()

		if 0 == cnt % 4 :
			x,y = joystick.get_axis()

		volume.led_update(cnt)
		menu.update(cnt,x,y,button_stat)
		
		cnt+=1
		if cnt>30000 :
			cnt = 0

		time.sleep(0.05)

	except IOError:
		logging.debug ("Error")
