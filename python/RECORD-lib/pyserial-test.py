# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 13:03:35 2022

@author: Raquel Ibáñez Alcalá 
"""

import serial
import time

ser = serial.Serial()
ser.baudrate = 9600
ser.port = 'COM4'
ser

ser.open()
ser.is_open

ser.write(b't')
time.sleep(0.5)
print(ser.read_all())

ser.close()