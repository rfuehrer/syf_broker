# SyF Broker

# Disclaimer

This repository will not be developed further. But I will keep it public for future reference. If you have any questions, I'll be happy to answer them, but I won't maintain the code and the repository any further. The original purpose was achieved in the context of a hackathon, an active use of this code is no longer given. 

This solution is not suitable for productive use!

## Purpose

Broker to load data from the sigfox backend and prepare those data for further processing. 

## Preperation:
- create file "syf.config" with following fields

[api_access]\
username = `sigfox api access username>`\
password = `sigfox api access username`\
last_timestamp = `value is updated by script / last timestamp of update`\

[ifttt]\
key = `ifttt webhook magic key`\
event = `ifttt event name`\

[proxy_access]\
active = `proxy on/off: "yes"=proxy on`\
username = `proxy access username`\
password = `proxy access password`\
server_http = `http proxy server name`\
port_http = `http proxy server port`\
server_https = `https proxy server name`\
port_https = `https proxy server port`\

## Installation

1. Clone repo
2. create and fill syf.config (see above)
3. run `python server.py`to initialize server mode
4. run `python broker.py`to receive data from sigfox backend
5. run `python watchdog.py`to send notifications if alarms are detected
