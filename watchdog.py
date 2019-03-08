#!/usr/bin/python

import os
import sys
import time
import json
import sqlite3
import configparser
from datetime import datetime
from pprint import pprint
from pathlib import Path
import PySigfox.PySigfox as SF
import requests
sys.path.insert(0, os.path.abspath('./modules'))

# https://support.sigfox.com/apidocs#operation/getDeviceMessagesListForDevice
sigfox_timeframe_before_now=((60*60)*24)
sigfox_timeframe_timestamp_lastcheck=str(int(time.time()))
syf_csv_filename="syf.csv"
syf_sqlite3_filename="syf.db"
syf_watchdog_recheck_every=15
sigfox_limit_messages=100

syf_config_filename = "syf.config"
max_accepted_version = 5

def send_ifttt(key, event,value1,value2="",value3=""):
	url     = "https://maker.ifttt.com/trigger/%s/with/key/%s" % (event, key)
	payload = {"value1" : value1, "value2" : value2, "value3" : value3} 
	headers = {}
	res = requests.post(url, data=payload, headers=headers)

config = configparser.ConfigParser()
try:
	print("Reading config file... (%s)" % (syf_config_filename))
	config.read(syf_config_filename)
except Exception as e :
	print(str(e))
try:
	print("Reading config values...")
	sigfox_api_login = config.get('api_access',"username")
	sigfox_api_password = config.get('api_access',"password")
	ifttt_key = config.get('ifttt',"key")
	ifttt_event = config.get('ifttt',"event")
	proxy_active = config.get('proxy_access', "active", fallback="no")
	proxy_pass = config.get('proxy_access', "password")
	proxy_user = config.get('proxy_access', "username")
	proxy_server_http = config.get('proxy_access',"server_http")
	proxy_port_http = config.get('proxy_access',"port_http")
	proxy_server_https = config.get('proxy_access',"server_https")
	proxy_port_https = config.get('proxy_access',"port_https")

except Exception as e :
    print(str(e),' - could not read configuration file')

if proxy_active == "yes":
    print("Setting proxy... (%s)" % (proxy_server_http))
    proxyDict={ "http":"http://"+proxy_user+":"+proxy_pass+"@"+proxy_server_http+":"+proxy_port_http, "https" : "https://"+proxy_user+":"+proxy_pass+"@"+proxy_server_https+":"+proxy_port_https }
else:
    print("Proxy deactivated...")
    proxyDict={ "http":"","https":"" }

s = SF.PySigfox(sigfox_api_login, sigfox_api_password,proxyDict)

try:
	s.login_test()
	print("API login OK")
except Exception as e:
	print(str(e))
	sys.exit(1)

count_all_devices = 0
count_all_messages = 0
count_valid_messages = 0
count_affected_messages = 0
count_signaltest_messages = 0
count_alarm_messages = 0

while True:
	count_all_messages=0
	print("Timestamp set to : %s" % str(sigfox_timeframe_timestamp_lastcheck))

	for device_type_id in s.device_types_list():
		for device in s.device_list(device_type_id):
			count_all_devices = ( count_all_devices + 1 )
			valid_messages = 0
			rows_affected = 0
			last_device = device
			
			print("== Read messages for device '%s' (id:%s)..." % (last_device['name'],last_device['id']))
			messages = s.device_messages(last_device['id'], str(sigfox_timeframe_timestamp_lastcheck), "100")
			for msg in messages:
				count_all_messages = ( count_all_messages +1 )
				version = int(msg['data'][:2],16)
				if version < max_accepted_version:
					count_valid_messages = ( count_valid_messages +1 )
					try:
						message_status = msg['data'][4:6]
					except:
						message_status = ""
					
					if message_status.upper() == "FF":
						count_signaltest_messages = ( count_signaltest_messages +1 )
						print("Sending SIGNALTEST")
						send_ifttt(ifttt_key, ifttt_event,"SIGNALTEST")
					elif message_status.upper() == "FE":
						count_alarm_messages = ( count_alarm_messages +1 )
						print("Sending SIGNALTEST OVERRIDE")
						send_ifttt(ifttt_key, ifttt_event,"SIGNALTEST OVERRIDE")
					elif message_status.upper() == "EE":
						count_alarm_messages = ( count_alarm_messages +1 )
						print("Sending ALARM")
						send_ifttt(ifttt_key, ifttt_event,"ALARM")
					else:
						message_status="00"
#						print("Sending NORMAL")

	sigfox_timeframe_timestamp_lastcheck=str(int(time.time()))
	print("New Timestamp set to : %s" % str(sigfox_timeframe_timestamp_lastcheck))
	print("Waiting %s seconds..." % syf_watchdog_recheck_every)
	time.sleep(syf_watchdog_recheck_every)

