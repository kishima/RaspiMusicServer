#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging

class MusicServerConfig(object):
	_instance = None
	_conf = None
	_conf_file_path = "./conf.json"

	#singleton
	def __new__(cls, *args, **kwargs):
		if cls._instance is None:
			cls._instance = object.__new__(cls, *args, **kwargs)
		return cls._instance

	def __init__(self):
		if self._conf == None:
			conf_file = open(self._conf_file_path, 'r')
			logging.debug("open %s" % self._conf_file_path)
			self._conf = json.load(conf_file)
			conf_file.close()
	
	def get_conf(self):
		return self._conf