#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import smbus
import time as timec
import datetime
import json
import urllib
import pprint
import sys
import subprocess
import requests
import ap_music_server_conf
import feedparser

class Yukkuri:
	def __init__(self):
		self.conf = ap_music_server_conf.MusicServerConfig().get_conf()
		return

	def send_cmmand(self,cmd):
		p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout_data, stderr_data = p.communicate()
		return stdout_data

	def speach(self,text):
		cmd = self.conf['speach_api'] % text
		logging.debug(cmd)
		self.send_cmmand(cmd)

	def dayofweek_info_speach(self):
		weekday = datetime.datetime.now().weekday()
		for d in self.conf['dayofweek_info']:
			if d == str(weekday):
				self.speach(self.conf['dayofweek_info'][d])

	def wether_speach(self):
		url = 'http://weather.livedoor.com/forecast/webservice/json/v1'
		payload = { 'city' : self.conf['city_id'] }
		data = requests.get(url, params = payload).json()
		
		text=""
		try:
			title = data['title']+u'をお伝えします。'
		
			text = title
			for weather in data["forecasts"]:
				text += weather['dateLabel'] + u'は' + weather['telop'] + u'です。'

			max = data["forecasts"][0]['temperature']['max']['celsius']
			text += u'今日の最高気温は、%s 度です。' % max
			min = data["forecasts"][0]['temperature']['min']['celsius']
			text += u'最低気温は、%s 度です。' % min
		except TypeError:
			print("No temp in data")
		self.speach(text)

	def rss_speach(self,rss_url):
		feed = feedparser.parse(rss_url)
		for e in feed.entries:
			self.speach( e.title )


class Schedule:
	def __init__(self):
		envfile = open('schedule/schedule.json', 'r')
		self.data = json.load(envfile)
		envfile.close()
		self.yukkuri = Yukkuri()
		self.read_data()
		return

	def read_data(self):
		#print(self.data['entry'])
		
		return

	def check_ex(self,timing):
		if timing.get('excond')=='movement':
			#if movement is active:
			return False
		return True

	def judge_timing(self,timing):
		print(timing['type'])
		if timing['type']=='weekday' and self.check_ex(timing):
			return True
		elif timing['type']=='weekend':
			return False
		elif timing['type']=='point':
			return True
		return False

	def check_power_control(self,entry):
		if entry['status']=='done':
			return
		fire = self.judge_timing(entry['timing'])
		if fire:
			print(entry)
			print("fire!")
			entry['status'] = 'done'
		return

	def check_speach_control(self,data):
		self.judge_timing(data['timing'])

	def check_entry(self,data):
		if data['type']=='power': #power control
			self.check_power_control(data)
		elif data['type']=='speach': #speach control
			self.check_speach_control(data)
		
	def update(self):
		
		#for en in self.data:
		#	self.check_entry(self.data[en])
		
		#reload
		return

class ArduinoTimer():
	ARDUINO_I2C_ADDR=0x10
	CMD_SET_WAKUP_TIMER01    = 0x11
	CMD_SET_WAKUP_TIMER02    = 0x12
	CMD_CLEAR_TIMER          = 0x40
	CMD_SHUTDOWN_NOW         = 0xFF

	def __init__(self,motion_obj):
		self.conf = ap_music_server_conf.MusicServerConfig().get_conf()
		self.i2c = smbus.SMBus(1)
		self.first_setting = False
		self.event = [];
		self.motion = motion_obj
		self.schedule = Schedule()
		return
		
	def datetime_to_epoch(self,d):
		return int(timec.mktime(d.timetuple()))

	def epoch_to_datetime(self,epoch):
		return datetime(*timec.localtime(epoch)[:6])
	
	def send_i2c_command(self,cmd,data):
		for num in range(1,5):
			try:
				self.i2c.write_block_data(self.ARDUINO_I2C_ADDR,cmd,data)
			except IOError:
				logging.debug("I2C IOerror in timer in Arduino communication > Retry")
				timec.sleep(num)
			else:
				logging.debug("I2C send OK to Arduino")
				return True
		return Flase
	
	def set_timer(self,cmd,time):
		target = self.datetime_to_epoch(time)
		diff = target - int(timec.time())
		data=[0,0,0,0]
		data[0]= 0 #(diff & 0xFF000000)>>24
		data[1]= (diff & 0x00FF0000)>>16
		data[2]= (diff & 0x0000FF00)>>8
		data[3]= diff & 0x000000FF
		
		if diff<0:
			return
		logging.debug("cmd="+str(cmd))
		logging.debug(data)
		self.send_i2c_command(cmd,data)
		return
	
	def send_shutdown_request(self):
		logging.debug('send_shutdown_request')
		self.set_timer(self.CMD_SHUTDOWN_NOW,datetime.datetime.now())
		return

	def send_cleartimer_request(self):
		logging.debug('send_cleartimer_request')
		self.set_timer(self.CMD_CLEAR_TIMER,datetime.datetime.now())
		return

	def get_time(self,hour,min):
		now = datetime.datetime.now()
		tomorrow = now + datetime.timedelta(days=1)
		t = datetime.datetime(now.year,now.month,now.day,hour,min,0)
		if t < now:
			t = datetime.datetime(tomorrow.year,tomorrow.month,tomorrow.day,hour,min,0)
		return t

	def load_schedule_file(self):
		file = open(self.conf['schedule_file_path'],'r')
		json_data = json.load(file)
		
		return
	
	def set_timer_once(self):
		if self.first_setting:
			return
		self.send_cleartimer_request()
		#self.load_schedule_file()
		t1 = self.get_time(7,00)
		self.set_timer(self.CMD_SET_WAKUP_TIMER01,t1)

		self.event.append( self.get_time( 7,05))
		self.event.append( self.get_time( 2,49))
		self.event.append( self.get_time( 8,30))

		self.first_setting = True
		return

	def check_event(self):
		mov_act = self.motion.get_latest_status()
		
		self.schedule.update()
		return

	def send_cmmand(self,cmd):
		p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout_data, stderr_data = p.communicate()
		return stdout_data


