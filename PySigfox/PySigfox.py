#!/usr/bin/python

import os
import sys
import json
import requests
import configparser 
from pprint import pprint

class PySigfox:
    def __init__(self, login, password, proxyDict):
        if not login or not password:
            print("Please define login and password when initiating PySigfox class!")
            sys.exit(1)
        self.login    = login
        self.password = password
        self.api_url  = 'https://backend.sigfox.com/api/'
        if type(proxyDict) is dict:
            self.proxyDict = proxyDict 

    def login_test(self):
        """Try to login into the  Sigfox backend API - if unauthorized or any other issue raise Exception
        """
        url = self.api_url + 'devicetypes'
        r = requests.get(url, auth=requests.auth.HTTPBasicAuth(self.login, self.password), proxies=self.proxyDict)
        if r.status_code != 200:
            raise Exception("Unable to login to Sigfox API: " + str(r.status_code))

    def device_types_list(self):
        """Return list of device types IDs
        """
        out = []
        url = self.api_url + 'devicetypes'
        r = requests.get(url, auth=requests.auth.HTTPBasicAuth(self.login, self.password), proxies=self.proxyDict)
        for device in json.loads(r.text)['data']:
            out.append(device['id'])
        return out

    def device_list(self, device_type_id = 0):
        """Return array of dictionaries - one array item per device.
        If device_type_id is not set devices of all device types are returned!
        """
        device_type_ids = []
        out = []
        if device_type_id != 0:
            device_type_ids.append(device_type_id)
        else:
            device_type_ids = self.device_types_list()

        for device_type_id in device_type_ids:
            # print("Getting data for device type id " + device_type_id)
            url = self.api_url + 'devicetypes/' + device_type_id + '/devices'
            r = requests.get(url, auth=requests.auth.HTTPBasicAuth(self.login, self.password), proxies=self.proxyDict)
            out.extend(json.loads(r.text)['data'])
        return out

    def device_messages(self, device_id, after=""):
        """Return array of messages from device with ID defined in device_id.
           Limit of 100 is the maximum Sigfox API will accept.
        """
        out = []

        url = self.api_url + 'devices/' + device_id + '/messages?limit=100'
        if after != "":
            url = url + "&since=%s" % (after)

        r = requests.get(url, auth=requests.auth.HTTPBasicAuth(self.login, self.password), proxies=self.proxyDict)
        if 'next' in r.text:
            pprint(json.loads(r.text)['paging']['next'])
#        else:
#            print("--------> element nicht gefunden")

        try:
            out.extend(json.loads(r.text)['data'])
            pass
        except Exception as e:
            raise

        try:
            if 'next' in r.text:
                json.loads(r.text)['paging']['next']
#                print("Loading next page...")
                out.extend(self.device_messages_page(json.loads(r.text)['paging']['next']))
#            else:
#                print("--------> element nicht gefunden")
        except Exception as e:
             # print("No paging")
             raise

        return out

    def device_messages_page(self, url):
        """Return array of message from paging URL.
        """
        out = []
        r = requests.get(url, auth=requests.auth.HTTPBasicAuth(self.login, self.password), proxies=self.proxyDict)
        out.extend(json.loads(r.text)['data'])
        try:
            json.loads(r.text)['paging']['next']
            out.extend(self.device_messages_page(json.loads(r.text)['paging']['next']))
        except Exception as e:
            # no more pages
            pass

        return out
