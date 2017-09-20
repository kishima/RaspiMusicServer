#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
import subprocess
import re

class ApMusic:
	def __init__(self):
		pass
	
	def proc_cmd(self,cmd):
		logging.debug(cmd)
		p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout_data, stderr_data = p.communicate()
		return stdout_data
		
	def check_mpd_status(self):
		cmd="mpc"
		p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout_data, stderr_data = p.communicate()
		return stdout_data.decode('utf-8')

	def play(self):
		self.proc_cmd("mpc play")

	def play_item(self,item):
		self.proc_cmd("mpc play "+item)

	def stop(self):
		self.proc_cmd("mpc stop")

	def next(self):
		self.proc_cmd("mpc next")

	def get_playlist(self):
		s = self.proc_cmd("mpc playlist")
		list = s.split('\n')
		return list
				
	def pickup_first_line(self,string):
		regex=re.compile('.*\n')
		m = regex.match(string)
		if m:
			position = m.span()
			return string[position[0]:position[1]]
		return string

	def check_mpc_status(self):
		ret = self.proc_cmd("mpc")
		match = '[playing]' in ret
		return match

	def mute_play_action(self,action):
		play_stat = self.check_mpc_status()
		if play_stat:
			self.stop()
		action()
		if play_stat:
			self.play()
