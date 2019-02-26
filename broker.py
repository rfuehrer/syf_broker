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
sys.path.insert(0, os.path.abspath('./modules'))

# https://support.sigfox.com/apidocs#operation/getDeviceMessagesListForDevice
sigfox_timeframe_before_now=((60*60)*24)
#sigfox_timeframe_filename="broker.timestamp"
sigfox_timeframe_timestamp=str(int(time.time()))
syf_csv_filename="syf.csv"
syf_sqlite3_filename="syf.db"
#sigfox_api_password_filename="sigfox.password"
sigfox_timeframe_timestamp_lastcheck=0

syf_config_filename = "syf.config"

#sigfox_api_login = '5c5bc0230499f57acb8060cc'
#sigfox_api_password = ''
valid_data_length = 4
max_accepted_version = 5

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
	sigfox_timeframe_timestamp_lastcheck= config.get("api_access","last_timestamp")
	proxy_active = config.get('proxy_access', "active")
	proxy_pass = config.get('proxy_access', "password")
	proxy_user = config.get('proxy_access', "username")
	proxy_server_http = config.get('proxy_access',"server_http")
	proxy_port_http = config.get('proxy_access',"port_http")
	proxy_server_https = config.get('proxy_access',"server_https")
	proxy_port_https = config.get('proxy_access',"port_https")
	print("Timestamp read: %s" % (sigfox_timeframe_timestamp_lastcheck))
except Exception as e :
    print(str(e),' - could not read configuration file')

if proxy_active != "":
    print("Setting proxy... (%s)" % (proxy_server_http))
    proxyDict={ "http":"http://"+proxy_user+":"+proxy_pass+"@"+proxy_server_http+":"+proxy_port_http, "https" : "https://"+proxy_user+":"+proxy_pass+"@"+proxy_server_https+":"+proxy_port_https }
else:
    print("No proxy configured...")
    proxyDict={ "http":"","https":"" }

s = SF.PySigfox(sigfox_api_login, sigfox_api_password,proxyDict)

sql3conn = sqlite3.connect(syf_sqlite3_filename)
sql3c = sql3conn.cursor()
sql3c.execute("CREATE TABLE IF NOT EXISTS messages ('device' TEXT,'timestamp' INT,'date' TEXT, 'time' TEXT, 'message_raw' TEXT,'temperature' REAL,PRIMARY KEY ('device', 'timestamp'))")
sql3conn.commit()

try:
	s.login_test()
	print("API login OK")
except Exception as e:
	print(str(e))
	sys.exit(1)

my_file = Path(syf_csv_filename)
if my_file.is_file():
    # file not exists
	f = open(syf_csv_filename, "a")
	f.close()
else:
    # file exists
	f = open(syf_csv_filename, "w")
	f.close()

count_all_devices = 0
count_all_messages = 0
count_valid_messages = 0
count_affected_messages = 0

print("Getting list of all devices:")
for device_type_id in s.device_types_list():
	for device in s.device_list(device_type_id):
		count_all_devices = ( count_all_devices + 1 )
		valid_messages = 0
		rows_affected = 0
#		pprint(device)
		last_device = device
		
		print("== Read messages for device '%s' (id:%s)..." % (last_device['name'],last_device['id']))
		messages = s.device_messages(last_device['id'], str(sigfox_timeframe_timestamp_lastcheck))
#		pprint(messages)
		for msg in messages:
			count_all_messages = ( count_all_messages +1 )
#			print("msg: " + str(msg['data']))
			if len(msg['data']) == valid_data_length:
#				print("%s  %s  %s" % (str(last_device['id']),str(msg['time']),str(msg['data'])))
				version = int(msg['data'][:2],16)
				if version < max_accepted_version:
					count_valid_messages = ( count_valid_messages +1 )
					temp_dec = ((int(msg['data'][2:],16)-80)/2)
					print("Valid message found (id: %s, v.: %s, data: %s @ %s)" % (last_device['id'],str(version), str(temp_dec), str(time.ctime(int(msg['time'])))))

					sql3c.execute("INSERT OR IGNORE INTO messages VALUES ('%s','%s','%s','%s','%s','%s');" % (str(last_device['id']),str(msg['time']),datetime.utcfromtimestamp(msg['time']).strftime('%Y-%m-%d'),datetime.utcfromtimestamp(msg['time']).strftime('%H:%M:%S'),str(msg['data']),str(temp_dec)))
					sql3conn.commit()
					if int(sql3c.rowcount) > 0:
						count_affected_messages = ( count_affected_messages +1 )
						rows_affected=rows_affected+(int(sql3c.rowcount))
						f = open("syf.csv", "a")
						f.write("\"%s\",%s,\"%s\",\"%s\",\"%s\",%s\n" % (str(last_device['id']),str(msg['time']),datetime.utcfromtimestamp(msg['time']).strftime('%Y-%m-%d'),datetime.utcfromtimestamp(msg['time']).strftime('%H:%M:%S'),str(msg['data']),str(temp_dec)))


					valid_messages = (valid_messages +1)

		print("[%s] Number of messages '%s' (all/valid/inserted): %s/%s/%s" % (last_device['id'],last_device['name'],str(len(messages)),str(valid_messages),str(rows_affected)))
		print("")

sql3conn.commit()
f.close()

print("Writing new timestamp...(%s)" % (sigfox_timeframe_timestamp))
cfgfile = open(syf_config_filename,'w')
config.set("api_access","last_timestamp", str(sigfox_timeframe_timestamp))
config.write(cfgfile)
cfgfile.close()
print("Timestamp was written...")

print("")
print("Summary:")
print("=======================================================================")
print("Last timestamp for check         : %s / %s" % (sigfox_timeframe_timestamp_lastcheck,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(sigfox_timeframe_timestamp_lastcheck)))))
print("New timestamp for check          : %s / %s" % (sigfox_timeframe_timestamp,time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(sigfox_timeframe_timestamp)))))
print("Time difference since last check : %s seconds" % (int(sigfox_timeframe_timestamp)-int(sigfox_timeframe_timestamp_lastcheck)))
print("Number of devices                : %s" % str(count_all_devices))
print("Number of all messages           : %s" % str(count_all_messages))
print("Number of valid messages         : %s" % str(count_valid_messages))
print("Numer of relevant messages       : %s" % str(count_affected_messages))
