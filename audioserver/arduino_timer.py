#!/usr/bin/python
# -*- coding: utf-8 -*-

import smbus
import time as timec
import datetime

class ArduinoTimer():
	ARDUINO_I2C_ADDR=0x10
	CMD_SET_WAKUP_TIMER01    = 0x11
	CMD_SET_WAKUP_TIMER02    = 0x12
	CMD_CLEAR_TIMER          = 0x40
	CMD_SHUTDOWN_NOW         = 0xFF

	def __init__(self):
		self.i2c = smbus.SMBus(1)
		return
		
	def datetime_to_epoch(self,d):
		return int(timec.mktime(d.timetuple()))

	def epoch_to_datetime(self,epoch):
		return datetime(*timec.localtime(epoch)[:6])
	
	def set_wakeup_timer(self,time):
		target = self.datetime_to_epoch(time)
		diff = target - int(timec.time())
		data=[0,0,0,0]
		data[0]= 0 #(diff & 0xFF000000)>>24
		data[1]= (diff & 0x00FF0000)>>16
		data[2]= (diff & 0x0000FF00)>>8
		data[3]= diff & 0x000000FF
		
		if diff<0:
			return
		print(diff)

		print(data)
		self.send_command(self.CMD_SET_WAKUP_TIMER01,data)
		self.send_command(self.CMD_SHUTDOWN_NOW,data)
		
		return
	
	def send_command(self,cmd,data):
		self.i2c.write_block_data(self.ARDUINO_I2C_ADDR,cmd,data)
		return

	def get_time(self,hour,min):
		now = datetime.datetime.now()
		tomorrow = now + datetime.timedelta(days=1)
		t = datetime.datetime(now.year,now.month,now.day,hour,min,0)
		if t < now:
			t = datetime.datetime(tomorrow.year,tomorrow.month,tomorrow.day,hour,min,0)
		return t

	def set_timer_once():
		return

#--------------------------

c = ArduinoTimer()
print(c.get_time(12,10))
#c.set_wakeup_timer(t2)
