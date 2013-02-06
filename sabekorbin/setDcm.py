#!/usr/bin/env python

import subprocess, shlex, os

def SetDcmIp(ip):
  with open("/home/steelj99/Projects/DCM_IP", 'w') as f:
    print("Set DCM IP to %s" % ip)
    f.write(ip)
    f.write(os.linesep)

p = subprocess.Popen(shlex.split("lisa.py get_available_devices DCM exclude_available steelj99"), stdout=subprocess.PIPE)
reservedDevices = p.communicate()[0].split()
reservedDevices = list(map(lambda x: str(x, 'utf-8'), reservedDevices))
if len(reservedDevices) == 0:
  SetDcmIp("")
if len(reservedDevices) == 1:
  SetDcmIp(reservedDevices[0])
if len(reservedDevices) > 1:
  userInput = 0
  while userInput < 1 or userInput > len(reservedDevices):
    print("Which DCM do you want to use?")
    for i in range(len(reservedDevices)):
      p = subprocess.Popen(shlex.split("lisa.py get_device_config %s" % reservedDevices[i]), stdout=subprocess.PIPE)
      print("%d. %s (%s)" % (i + 1, reservedDevices[i], str(p.communicate()[0], 'utf-8').strip()))
    rinput = input()
    try:
      userInput = int(rinput)
    except:
      pass
  SetDcmIp(reservedDevices[userInput - 1])
 

