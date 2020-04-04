#!/usr/bin/env python3
import socket
import requests
from subprocess import Popen, PIPE
import json
##Match Rule
##Match the start of swipe
MATCHER1 = 'Received Configuration report: Parameter=9'
##Match the end of swipe
MATCHER2 = 'Received Configuration report: Parameter=10'
##Match which button is used on the wallmote quad
MATCHER3 = 'Received: 0x01, 0x07'

def extract_value(line):
  value = line.split('=')[-1].strip()
  return int(value)

# variable
event = 'script.dimmer'

##HA information
URI = 'https://hass-vansteen.duckdns.org/api/services/script/turn_on'
TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiI0NjRhZWRhMmI4NDA0NzU1OGFiMTViYmY4ZTc1ZWZmZCIsImlhdCI6MTU1OTc3MzU0MiwiZXhwIjoxODc1MTMzNTQyfQ.WAGGNmg7FEUjU2MwLI6E16kx3DH7EtlnBOdhOgRfyT8'
OZW_LOG = '/home/homeassistant/.homeassistant/OZW_Log.txt'

debug = False

##Open the tail of our OZW_Log and scan for new lines;
log = Popen(('/usr/bin/tail', '-F', '-n', '0', OZW_LOG), stdout=PIPE)
while True:

  ##Get most recent line and massage it;
  line = log.stdout.readline()
  if not line:
    break
  line = line.strip().decode('utf-8')

  ##Fast match
  if MATCHER1 not in line:
    if MATCHER2 not in line:
      if MATCHER3 not in line:
        continue

  if MATCHER1 in line:
    nodeID = line.split(',')[1].strip().lower()
    if "node002" in nodeID:
      node = "Livingroom"
    if "node016" in nodeID:
      node = "Kitchen"
    
    value9 = extract_value(line)
    if __debug__:
      print(value9)
    continue

  elif MATCHER2 in line:
    value10 = extract_value(line)
    if __debug__:
      print(value10)
    #continue

  elif MATCHER3 in line:
    button = line.split(',')[-5].replace(' 0x0','').strip()
    if __debug__:
      print(button)
    continue

  if __debug__:
    print("Marker")

  if value9 < value10:
    action = 'swipe_up'
  else:
    action = 'swipe_down'
    if __debug__:
      print(action)

  if node is not None:
    if "Livingroom" in node:
      if "1" in button:
        light_id = "light.woonkamer"
      if "2" in button:
        light_id = "light.woonkamer"
      if "3" in button:
        light_id = "light.eetkamer"
      if "4" in button:
        light_id = "light.woonkamer"
    elif "Kitchen" in node:
      if "1" in button:
        light_id = "light.eetkamer"
      if "2" in button:
        light_id = "light.keuken"
      if "3" in button:
        light_id = "light.woonkamer"
      if "4" in button:
        light_id = "light.terras"

  if __debug__:
      print(URI)
  if __debug__:
      print(event)

  if event:
      data = {"entity_id": "{0}".format(event), "variables":{"light_id": light_id, "swipe_action": action}}
      if __debug__:
          print(data)

      if TOKEN:
          resp = requests.post(URI, data=json.dumps(data), headers={'Authorization': 'Bearer {0}'.format(TOKEN), 'content-type': 'application/json'})
      else:
          resp = requests.post(URI, data=json.dumps(data), headers={'content-type': 'application/json'})

      if __debug__:
          print(resp)
