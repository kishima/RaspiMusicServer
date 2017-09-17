#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import smbus
import time as timec
import datetime
from datetime import datetime as datetimec
import json
import urllib
import pprint
import sys
import subprocess
import requests
import feedparser

import ap_music_server_conf
import ap_music

class Yukkuri:
	def __init__(self):
		self.conf = ap_music_server_conf.MusicServerConfig().get_conf()
		return

	def send_cmmand(self,cmd):
		p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout_data, stderr_data = p.communicate()
		return stdout_data

	def speech(self,text):
		cmd = self.conf['speech_api'] % text
		logging.debug(cmd)
		self.send_cmmand(cmd)

	def dayofweek_info_speech(self):
		weekday = datetime.datetime.now().weekday()
		for d in self.conf['dayofweek_info']:
			if d == str(weekday):
				self.speech(self.conf['dayofweek_info'][d])

	def wether_speech(self):
		url = 'http://weather.livedoor.com/forecast/webservice/json/v1'
		payload = { 'city' : self.conf['city_id'] }
		data = requests.get(url, params = payload).json()
		
		text=""
		try:
			title = data['title']+u'をお伝えします。'
		
			text = title
			for weather in data["forecasts"]:
				date = weather['date']
				d = date.encode().split("-")
				text += str(int(d[1])) +u"月"+ str(int(d[2]))+ u'日、' + weather['dateLabel'] + u'は' + weather['telop'] + u'です。'

			d = data["forecasts"][0]['date'].encode().split("-")
			max = data["forecasts"][0]['temperature']['max']['celsius']
			text += u'今日、'+str(int(d[1])) +u"月"+ str(int(d[2]))+ u'日、の最高気温は、%s 度です。' % max
			min = data["forecasts"][0]['temperature']['min']['celsius']
			text += u'最低気温は、%s 度です。' % min
		except TypeError:
			print("No temp in data")
		self.speech(text)

	def rss_speech(self,rss_url):
		feed = feedparser.parse(rss_url)
		for e in feed.entries:
			self.speech( e.title )

	def play_welcome_msg(self):
		self.speech(self.conf['welcome_msg'])


class Schedule:
	def __init__(self,motion_obj,timer_obj):
		self.conf = ap_music_server_conf.MusicServerConfig().get_conf()
		envfile = open(self.conf['schedule_file_path'], 'r')
		self.data = json.load(envfile)
		envfile.close()
		
		self.timer = timer_obj
		self.motion = motion_obj
		self.yukkuri = Yukkuri()
		self.music = ap_music.ApMusic()
		
		return

	def check_ex(self,timing):
		if timing.get('excond')=='movement':
			#if movement is active:
			print("excond",self.motion.get_latest_status())
			if self.motion.get_latest_status() > 2:
				return True
			return False
			
		#movement is not set
		return True
		
	def check_power_control(self,entry):
		if entry['status']=='done':
			return
		if entry['action']=='shutdown':
			logging.debug("**************************")
			logging.debug("*** shutdown RasPi now ***")
			logging.debug("**************************")
			self.timer.send_shutdown_request()
			entry['status']='done'
			return
		return

	def check_speech_control(self,entry):
		if entry['action'] == "speech":
			self.yukkuri.speech(entry['content'])
		elif entry['action'] == "speech_weather":
			self.yukkuri.wether_speech()
		return

	def check_music_control(self,entry):
		if entry['action'] == "play":
			self.music.play(entry['content'])
		elif entry['action'] == "stop":
			self.music.stop()
		return

	def check_basic_timer(self,timing,now,target):
		t1 = ArduinoTimer.datetime_to_epoch(now)
		t2 = ArduinoTimer.datetime_to_epoch(target)
		
		if t1 > t2:
			if abs(t1-t2) < 60*1: #allow 60sec diff
				return self.check_ex(timing)
			else:
				if timing.get('excond')=='movement' and abs(t1-t2) < 60*60*3:
					return False
				return "done"
		return False	
	
	def judge_timing(self,timing):
		now = datetime.datetime.now()
		day = now.weekday()
		
		if    (timing['type']=='weekday' and day in {0,1,2,3,4}) \
		   or (timing['type']=='weekend' and day in {5,6}) \
		   or (timing['type']=='everyday'):
			hour,min = timing['value'].split(':')
			target = datetime.datetime(now.year,now.month,now.day,int(hour),int(min),0)
			return self.check_basic_timer(timing,now,target)
		elif timing['type']=='onshot':
			target = datetimec.strptime(timing['value'], '%Y/%m/%d %H:%M:%S')
			print("onshot",target)
			return self.check_basic_timer(timing,now,target)
		return False
		
	def check_entry(self,entry):
		if entry['status'] == 'done':
			return
			
		fire = self.judge_timing(entry['timing'])
		if fire == False:
			return
		elif fire == "done":
			entry['status'] = 'done'
			return

		if entry['type']=='power': #power control
			self.check_power_control(entry)
		elif entry['type']=='speech': #speech control
			self.check_speech_control(entry)
		elif entry['type']=='music': #speech control
			self.check_music_control(entry)
		entry['status'] = 'done'
		
	def update(self):
		for entry in self.data:
			self.check_entry(self.data[entry])
		return
	
	def get_wakeup_timer_request(self):
		requests=[]
		for entry in self.data:
			d = self.data[entry]
			if d['action'] =='wakeup' and d['type']=='power':
				requests.append(d['timing']['value'].split(":"))
		return requests

class ArduinoTimer():
	ARDUINO_I2C_ADDR=0x10
	CMD_SET_WAKUP_TIMER01A    = 0x11
	CMD_SET_WAKUP_TIMER01B    = 0x12
	CMD_SET_WAKUP_TIMER02A    = 0x21
	CMD_SET_WAKUP_TIMER02B    = 0x22
	CMD_CLEAR_TIMER          = 0x40
	CMD_SHUTDOWN_NOW         = 0xFF

	def __init__(self,motion_obj):
		self.conf = ap_music_server_conf.MusicServerConfig().get_conf()
		self.i2c = smbus.SMBus(1)
		self.first_setting = False
		self.motion = motion_obj
		self.schedule = Schedule(self.motion,self)
		return
		
	@classmethod
	def datetime_to_epoch(self,d):
		return int(timec.mktime(d.timetuple()))

	@classmethod
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
	
	def set_timer(self,time):
		target = self.datetime_to_epoch(time)
		diff = target - int(timec.time())
		data1=[0,0]
		data2=[0,0]
		data1[0] = int((diff & 0xFF000000)>>24)
		data1[1] = (diff & 0x00FF0000)>>16
		data2[0] = (diff & 0x0000FF00)>>8
		data2[1] =  diff & 0x000000FF
		
		if diff<0:
			return
		cmd = self.CMD_SET_WAKUP_TIMER01A
		logging.debug("cmd="+str(cmd)+"  diff="+str(diff))
		logging.debug(data1)
		self.send_i2c_command(cmd,data1)
		timec.sleep(0.05)
		cmd = self.CMD_SET_WAKUP_TIMER01B
		logging.debug("cmd="+str(cmd)+"  diff="+str(diff))
		logging.debug(data2)
		self.send_i2c_command(cmd,data2)
		return

	def set_cmd(self,cmd,time):
		data=[0,0]
		logging.debug("cmd="+str(cmd))
		self.send_i2c_command(cmd,data)
		return
	
	def send_shutdown_request(self):
		logging.debug('send_shutdown_request')
		self.set_cmd(self.CMD_SHUTDOWN_NOW,datetime.datetime.now())
		return

	def send_cleartimer_request(self):
		logging.debug('send_cleartimer_request')
		self.set_cmd(self.CMD_CLEAR_TIMER,datetime.datetime.now())
		return

	def get_time(self,hour,min):
		now = datetime.datetime.now()
		tomorrow = now + datetime.timedelta(days=1)
		t = datetime.datetime(now.year,now.month,now.day,hour,min,0)
		if t < now:
			t = datetime.datetime(tomorrow.year,tomorrow.month,tomorrow.day,hour,min,0)
		return t
	
	def set_timer_once(self):
		if self.first_setting:
			return
		self.send_cleartimer_request()
		logging.debug("set wake up timer")
		requests = self.schedule.get_wakeup_timer_request()
		for req in requests:
			t1 = self.get_time(int(req[0]),int(req[1]))
			logging.debug(t1)
			self.set_timer(t1)

		self.first_setting = True
		return

	def check_event(self):
		mov_act = self.motion.get_latest_status()
		
		self.schedule.update()
		return

	def reload_schedule(self):
		logging.debug("reload_schedule")
		self.schedule = Schedule(self.motion,self)
		self.first_setting=False
		self.set_timer_once()

	def p(self):
		print("testestet")