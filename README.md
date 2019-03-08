# SyF Broker
#sigfox #python #sensordata 

Broker to load data from the sigfox backend and prepare those data for further processing

Further information will follow.



Preperation:
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