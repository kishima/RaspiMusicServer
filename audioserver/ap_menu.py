#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import subprocess
import re

MENU_IDLE    = 0
MENU_PLAYING = 1
MENU_ONMENU  = 2

class ApMenu:
	
	def __init__(self,ledobj,slide_barobj):
		self.loop1 = 0
		self.led = ledobj
		self.volume = slide_barobj
		self.mpdstat = "" #mpd status
		self.menu_stat = MENU_PLAYING
		self.stat_chage = True

		self.menu_item = ["PLAY","STOP","CANCEL"]
		self.station_list = []
		self.menu_cursor = 0
		self.current_station = 0
		self.get_playlist()
		return

	def get_playlist(self):
		s = self.proc_cmd("mpc playlist")
		list = s.split('\n')
		for music in list:
			if music != "":
				self.station_list.append(music)
				print(music)
				
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
		return stdout_data
	
	def update(self,cnt,x,y,button):
		if self.menu_stat == MENU_IDLE:
			self.mode_idle(cnt,x,y,button)
		elif self.menu_stat == MENU_PLAYING:
			self.mode_playing(cnt,x,y,button)
		elif self.menu_stat == MENU_ONMENU:
			self.mode_onmenu(cnt,x,y,button)
		return
		
	def mode_idle(self,cnt,x,y,button):
		return

	def mode_playing(self,cnt,x,y,button):
		if x!=0 or y!=0 or button != 0:
			self.menu_stat = MENU_ONMENU
			self.stat_chage = True
			return

		if 0 == cnt % 40 :
			self.mpdstat = self.check_mpd_status("mpc")
			self.mpdstat = self.pickup_first_line(self.mpdstat)
			self.mpdstat = self.mpdstat.replace('\n','')
			#logging.debug(stat)
			
		if 0 == cnt % 10:
			if self.loop1 > len(self.mpdstat) :
				self.loop1=0
			#led.setText(stat[loop1:])
			#logging.debug(len(stat)-loop1 )
			if len(self.mpdstat)-self.loop1 < 32:
				t=self.mpdstat[self.loop1:]+" / "+self.mpdstat
				#logging.debug(t)
				self.led.setText_norefresh(t)
			else:
				self.led.setText_norefresh(self.mpdstat[self.loop1:])
			
			self.loop1+=1
		return

	def mode_onmenu(self,cnt,x,y,button):
		if y != 0:
			x = 0
		condition_update = False

		if self.stat_chage:
			#状態変化直後は画面更新周期に関わらず画面を更新
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
			#print("MENU=",self.menu_item[self.menu_cursor])
			#print("Station=",self.station_list[self.current_station])
			volume = self.volume.get_current_volset()
			output  = " ["+self.menu_item[self.menu_cursor]+"]"+"  V:"+str(volume)+"\n"
			output += self.station_list[self.current_station]
			self.led.setText_norefresh(output)

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
		
		return

	
