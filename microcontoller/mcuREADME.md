# Welcome to RECORD/microcontroller!
The code in this repository was written for the [MSP430-FR2355 microcontroller development kit](https://www.ti.com/tool/MSP-EXP430FR2355) in [Texas Instrument's Code Composer Studio 11.1.0](https://www.ti.com/tool/download/CCSTUDIO/11.1.0.00011).

# Files
This repository contains 3 files:

 1. 'main.c' file: The microcontroller firmware. This code is essential for the functionality of the microcontroller system and will call the other two files. It contains setup and initialisation, the command servicing routine, interrupt servicing routines, and main variable definitions.
 2. 'RECORD.h' file: A header file containing essential variables and functions necessary for functionality.
 3. 'mcucfg.h' file: A header file referenced by the 'RECORD.h' file that defines default parametres loaded by the microcontroller at startup.
	 - This file contains variables essential to the brightness of the cost lights, as they will control the pulse width-modulated signal that turns on the cost lights.  **Make sure these values are calibrated to your setup's specific needs!**
 
 These three files must be flashed to the microcontroller in order for the RECORD system to work. The 'mcucfg.h' file may be named something else and multiple copies can be made for a setup using multiple RECORD arenas, however, make sure that the 'RECORD.h' file references the correct 'cfg' file when flashing.

# Updates
A rundown of the current version's most recent changes will be shown here!

## Current version v2.2.0 (17/February/2022) 
### Firmware:
 1. Added the capability to switch TTL operation modes by configuring in configuration mode
	 - TOGGLE will turn the TTL on and keep it on until it is toggled again
	 -  PULSE is the legacy mode, only stays on for as long as TTL_LENGTH
	   indicates, then turns back off. 
	 - OFF is off, duh!
 2. TTL OUT command ‘T’ will now check for the TTL operation mode and act accordingly.
 3. Information mode ('?' command):
	- Will now report the operation mode of the output TTL immediately before reporting CCR values.
	- Will now prompt the user to either enter H to display the help section, or Enter to exit info mode. Any character sent will also exit info mode.
 4. Added command ‘t’ to report the state of the output TTL in text. This is to make sure the state can be reported to serial comm-based systems that are oblivious to I/O signals.
 5. Removed TTL_OUT and ACK from ‘R’ command, so the state of these signals is not altered when doing resets.


> Written with [StackEdit](https://stackedit.io/).
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTU4MTc2NDIxOF19
-->