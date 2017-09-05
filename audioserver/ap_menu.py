#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import subprocess
import re
from pykakasi import kakasi
from arduino_timer import Yukkuri
import grove_gesture_sensor

MENU_IDLE    = 0
MENU_PLAYING = 1
MENU_ONMENU  = 2

class ApMenu:
	MENU_TIMEOUT_SET = 20*5
	
	def __init__(self,ledobj,volumebj):
		self.loop1 = 0
		self.led = ledobj
		self.volume = volumebj
		self.mpdstat = "" #mpd status
		self.menu_stat = MENU_ONMENU
		self.stat_chage = True

		self.menu_item = ["PLAY","STOP","CANCEL","WEATHER","NEWS"]
		self.station_list = []
		self.menu_cursor = 0
		self.current_station = 0
		self.get_playlist()
		self.menu_timeout = 0
		
		self.kakasi = kakasi()
		self.kakasi.setMode('H', 'a')
		self.kakasi.setMode('K', 'a')
		self.kakasi.setMode('J', 'a')
		self.conv = self.kakasi.getConverter()
		
		self.yukkuri = Yukkuri()
		return

	def get_playlist(self):
		s = self.proc_cmd("mpc playlist")
		list = s.split('\n')
		for music in list:
			if music != "":
				self.station_list.append(music)
				#print(music)
				
	def pickup_first_line(self,string):
		regex=re.compile('.*\n')
		m = regex.match(string)
		if m:
			position = m.span()
			return string[position[0]:position[1]]
		return string

	def proc_cmd(self,cmd):
		logging.debug(cmd)
		p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout_data, stderr_data = p.communicate()
		return stdout_data
	
	def check_mpd_status(self,cmd):
		p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout_data, stderr_data = p.communicate()
		return self.conv.do(stdout_data.decode('utf-8'))
	
	def update(self,cnt,x,y,button,ges):
		if self.menu_stat == MENU_IDLE:
			self.mode_idle(cnt,x,y,button,ges)
		elif self.menu_stat == MENU_PLAYING:
			self.mode_playing(cnt,x,y,button,ges)
		elif self.menu_stat == MENU_ONMENU:
			self.mode_onmenu(cnt,x,y,button,ges)
		return
		
	def mode_idle(self,cnt,x,y,button,ges):
		return

	def mode_playing(self,cnt,x,y,button,ges):
		if x!=0 or y!=0 or button != 0 or ges == grove_gesture_sensor.gesture.FORWARD:
			self.menu_stat = MENU_ONMENU
			self.stat_chage = True
			self.menu_timeout = 20*5
			return

		if 0 == cnt % 40 :
			self.mpdstat = self.check_mpd_status("mpc")
			self.mpdstat = self.pickup_first_line(self.mpdstat)
			self.mpdstat = self.mpdstat.replace('\n','')
			
		if 0 == cnt % 10:
			if self.loop1 > len(self.mpdstat) :
				self.loop1=0
			if len(self.mpdstat)-self.loop1 < 32:
				t=self.mpdstat[self.loop1:]+" / "+self.mpdstat
				self.led.put_text(t)
			else:
				self.led.put_text(self.mpdstat[self.loop1:])
			
			self.loop1+=1
			
		if ges == grove_gesture_sensor.gesture.CLOCKWISE:
			play_stat = self.check_mpc_status()
			if play_stat:
				self.proc_cmd("mpc stop")
			self.yukkuri.wether_speach()
			if play_stat:
				self.proc_cmd("mpc play")

		return

	def check_mpc_status(self):
		ret = self.proc_cmd("mpc")
		match = '[playing]' in ret
		return match

	def mode_onmenu(self,cnt,x,y,button,ges):
		if y != 0:
			x = 0
		condition_update = False

		if x!=0 or y!=0 or button != 0 or ges != 0:
			self.menu_timeout = self.MENU_TIMEOUT_SET

		self.menu_timeout -= 1
		if self.menu_timeout <= 0:
			self.menu_stat = MENU_PLAYING

		if ges == grove_gesture_sensor.gesture.FORWARD:
			button = 1

		if ges == grove_gesture_sensor.gesture.UP:
			y = -1
		if ges == grove_gesture_sensor.gesture.DOWN:
			y = 1
		if ges == grove_gesture_sensor.gesture.RIGHT:
			x = 1
		if ges == grove_gesture_sensor.gesture.LEFT:
			x = -1


		if self.stat_chage:
			#menu will be updated when state is changed
			condition_update = True
			self.stat_chage=False

		if y == 1:
			self.menu_cursor+=1
			condition_update = True
			if self.menu_cursor>=len(self.menu_item):
				self.menu_cursor=0
		
		if y == -1:
			self.menu_cursor-=1
			condition_update = True
			if self.menu_cursor<0:
				self.menu_cursor=len(self.menu_item)-1

		if x == 1:
			self.current_station+=1
			condition_update = True
			if self.current_station>=len(self.station_list):
				self.current_station=0
		
		if x == -1:
			self.current_station-=1
			condition_update = True
			if self.current_station<0:
				self.current_station=len(self.station_list)-1
		
		if condition_update:
			self.led.clear_display()
			volume = self.volume.get_current_volset()
			output  = "["+self.menu_item[self.menu_cursor]+"]"+"  V:"+str(volume)+"\n"
			output += self.station_list[self.current_station]
			self.led.put_text(output)

		if button==1:
			print("button press")
			if self.menu_item[self.menu_cursor] == "PLAY":
				r = self.proc_cmd("mpc play "+str(self.current_station+1))
				logging.debug(r)
			elif self.menu_item[self.menu_cursor] == "STOP":
				r = self.proc_cmd("mpc stop")
				logging.debug(r)
			elif self.menu_item[self.menu_cursor] == "NEXT":
				r = self.proc_cmd("mpc next")
				logging.debug(r)
			elif self.menu_item[self.menu_cursor] == "CANCEL":
				self.menu_stat = MENU_PLAYING
				self.stat_chage = True
			elif self.menu_item[self.menu_cursor] == "WEATHER":
				play_stat = self.check_mpc_status()
				if play_stat:
					self.proc_cmd("mpc stop")
				#self.yukkuri.wether_speach()
				self.yukkuri.dayofweek_info_speach()
				if play_stat:
					self.proc_cmd("mpc play")
			elif self.menu_item[self.menu_cursor] == "NEWS":
				play_stat = self.check_mpc_status()
				if play_stat:
					self.proc_cmd("mpc stop")
				self.yukkuri.rss_speach("http://www.inoreader.com/stream/user/1006435756/tag/%E8%89%A6%E3%81%93%E3%82%8C")
				self.yukkuri.rss_speach("https://news.google.com/news?hl=ja&ned=us&ie=UTF-8&oe=UTF-8&output=rss&topic=po")
				self.yukkuri.rss_speach("https://news.google.com/news?hl=ja&ned=us&ie=UTF-8&oe=UTF-8&output=rss&topic=w")
				if play_stat:
					self.proc_cmd("mpc play")
		
		return

	
