#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import ap_slide_bar
import ap_led
import ap_joystick
import ap_button
import ap_menu

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s (%(threadName)-10s) %(message)s',)


slide_bar = ap_slide_bar.ApSlideBar(barPin=2,ledPin=17)
joystick  = ap_joystick.ApJoystick(pinX=1,pinY=0)
button    = ap_button.ApButton(pin=6)
led       = ap_led.ApLed()
led.setRGB(0,50,0)
led.start()
menu = ap_menu.ApMenu(led,slide_bar)

cnt = 0

while True:
	try:
		button_stat=0
		x=0
		y=0
		
		if 0 == cnt % 4 :
			slide_bar.volume_act()

		if 0 == cnt % 4:
			button_stat = button.get_button_stat()

		if 0 == cnt % 4 :
			x,y = joystick.get_axis()

		menu.update(cnt,x,y,button_stat)
		
		cnt+=1
		if cnt>30000 :
			cnt = 0

		time.sleep(0.05)

	except IOError:
		logging.debug ("Error")
