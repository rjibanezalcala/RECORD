# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 14:39:16 2022

@author: Raquel
"""

from record_lib import RECORD
import time

# Initialize the RECORD class, we'll use this to call methods that will
# control the microcontroller in some way. We'll call this object "MCU".
MCU = RECORD()

# Define and initialize a serial communications session so we can start talking 
# to the microcontroller. We don't need to do anything before opening the
# communication channel to the microcontroller so we'll open it right away.
print("Opening serial port. Interrupt execution of all trials with keyboard interrupt (Ctrl + C)")
session = MCU.createSS()
session.open()      # Open the serial interface

MCU.send_cmd('K', enforce_delay=False)

response = ""
eol = "\r\n\n"
now = time.time()
byte = b''
while not eol in response:
    if (time.time() - now >= 1):
        print("[Error]: No bytes found in the serial buffer after the specified timeout.")
        break
    # Reading all bytes available bytes till EOL
    byte = session.read()
    response += byte.decode()

print(response)
session.flushOutput()

print("Closing serial port.")
session.close()