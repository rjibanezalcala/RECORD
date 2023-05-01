# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 13:00:17 2022

@author: Raquel Ibáñez Alcalá

An example script to use as a guide when programming a "Approach-avoid
multi-level decision-making task", a.k.a. "Phase 2" or "P2" task.
"""

## A "phase 2" trial example:
    
from record_lib import RECORD
import time

# For timing Wall time of this script.
wall_start = time.time()

# Generate random numbers for feeder and light level here.


MCU = RECORD()      # Call the initialization method in the RECORD library

session = MCU.createSS()    # Assign a name to the serial session and create an object from it
session.open()      # Open the serial interface

## Inter-trial interval
print("Starting trial with inter-trial interval of 5 seconds...\r\n")
MCU.all_inactive()  # Reset the microcontroller to its idle state, just in case.
time.sleep(5)

## Start trial timer
MCU.timer_start()
# (Optional) Display the microcontroller's response in the console.
print(MCU.fetch_response())

## Indicate start of trial
MCU.indicator_toggle()
time.sleep(0.05)    # Give the microcontroller time to respond.
# (Optional) Display the microcontroller's response in the console.
print(MCU.fetch_response())

## Cue rat to approach feeder 2 with cost level 1
MCU.feeder_light(2,1)
# (Optional) Display the microcontroller's response in the console.
print(MCU.fetch_response())

## Wait for rat to approach feeder, give it 5 seconds to do so...
print("Allowing rat to make a decision (5 seconds)...\r\n")
time.sleep(5)

## React to rat's decision
# THIS PART IS NOT AUTOMATED, IN THIS EXAMPLE. If you have a way to automate
# zone detection with rat tracking, please update this section appropriately.
# Check if the rat is at the feeder...
approach = input("Did the rat approach the offer? [y/n]\r\n")
if approach == "y":
    # Deliver reward if the rat did approach the offer.
    MCU.valve_activate(2)
    # (Optional) Display the microcontroller's response in the console.
    print(MCU.fetch_response())
    # Wait until rat finishes eating (2 seconds)
    print("Waiting for rat to eat (2 seconds)...\r\n")
    time.sleep(2)
else:
    # Do nothing if the rat did not approach the offer.
    pass

## Reset microcontroller to idle state
MCU.all_inactive()
# (Optional) Display the microcontroller's response in the console.
print(MCU.fetch_response())

## Record for 2 seconds...
print("Recording for 2 seconds before ending...\r\n")
time.sleep(2)

## ...then stop the timer and end the trial
MCU.timer_stop()
# (Optional) Display the microcontroller's response in the console.
print(MCU.fetch_response())

## Close the serial session
print("Trial ended, closing serial communications...\r\n")
session.close()

# Calculate execution time
wall_elapsed_time = time.time() - wall_start

print('Human execution time:', time.strftime("%H:%M:%S", time.gmtime(wall_elapsed_time)))