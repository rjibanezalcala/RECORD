# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 13:43:13 2022
Last updated Tue Feb 17 2023
v0.5.0

RECORD-lib
@author: Raquel Ibáñez Alcalá
"""

import serial
import time
import datetime

class RECORD:
    def __init__(self):
        pass
    
    def createSS(self, **kwargs):
        # Create a serial session tailored to the MSP430-FR2355 microcontroller
        # running the RECORD firmware and return the session object to open
        # and close the session later.
        
        # Initialize serial session details.
        # Default values will be set up if a parameter is not defined.
        # Default values are based on microcontroller settings defined in
        # firmware.
        
        # Serial comms information
        # com_port    = kwargs.get("com_port",'COM4')
        # baud_rate   = kwargs.get("baud_rate",9600)
        # data_bits   = kwargs.get("data_bits",8)
        # parity      = kwargs.get("parity",'N')
        # stop_bits   = kwargs.get("stop_bits",1)
        # flow_ctrl   = kwargs.get("flow_ctrl",0)
        # Microcontroller information
        self.ttlin_state = "Unknown"
        
        # Make the serial session object and introduce the parameters given by
        # kwargs or introduce default values.
        self.session = serial.Serial()
        
        self.session.baudrate = kwargs.get("baud_rate",9600)
        self.session.port     = kwargs.get("com_port",'COM4')
        self.session.bytesize = kwargs.get("data_bits",8)
        self.session.parity   = kwargs.get("parity",'N')
        self.session.stopbits = kwargs.get("stop_bits",1)
        self.session.xonxoff  = kwargs.get("flow_ctrl",0)
        self.session.timeout  = kwargs.get("timeout", 1)
        
        return self.session
    
    def feeder_light(self,fdr,lvl,
                     ttl_length=0.1,
                     enforce_delay=True):
        # Builds a string that the microcontroller can interpret as a command
        # and sends it over an existing open serial interface.
        # Arguments:
        #    - fdr: The feeder to be activated. Must be an integer from 1
        #      through 4.
        #    - lvl: The brightness level at which to turn the light on. Must be
        #      an integer from 0 through 3.
        #    - ttl_length: The length of the TTL signal sent by the
        #      microcontroller. This can be checked by sending it a '?'. 0.1 is
        #      set as a default.
        #    - enforce_delay: Enforces a delay after sending the command to the
        #      microcontroller. This delay is long enough to execute the
        #      command, send a TTL, and communicate the microcontroller's 
        #      timestamp.
        # Returns 0 and the time when the command was sent if no exceptions
        # occur, otherwise returns -1.
        
        command = '#F'+str(fdr)+'L'+str(lvl)
        command = bytes(command, 'utf-8')
        
        try:
            self.session.write(command)
            ts = datetime.datetime.now()
            if enforce_delay:
                # Wait for TTL signal and for the microcontroller to execute command.
                time.sleep(ttl_length + 0.13)
            
            return 0, ts
        except:
            return -1, ts
        
    def valve_activate(self,vlv,
                       ttl_length=0.1,
                       rly_length=0.5,
                       enforce_delay=True):
        # Builds a string that the microcontroller can interpret as a command
        # and sends it over an existing open serial interface.
        # Arguments:
        #    - vlv: The valve to be activated. Must be an integer from 1
        #      through 4.
        #    - ttl_length: The length of the TTL signal sent by the
        #      microcontroller. This can be checked by sending it a '?'. 0.1 is
        #      set as a default.
        #    - rly_length: The length of the signal which activates the
        #      microcontroller's relays, which activate the valve. 0.5 is set
        #      as default.
        #    - enforce_delay: Enforces a delay after sending the command to the
        #      microcontroller. This delay is long enough to execute the
        #      command, send a TTL, activate a relay, and communicate the
        #      microcontroller's timestamp.
        # Returns 0 and the time when the command was sent if no exceptions
        # occur, otherwise returns -1.
        
        switch = {
            1:b'F',
            2:b'G',
            3:b'H',
            4:b'J'}
        command = switch.get(vlv,b' ')
        
        try:
            self.session.write(command)
            ts = datetime.datetime.now()
            if enforce_delay:
                # Wait for TTL signal and for the microcontroller to execute command.
                time.sleep(ttl_length + rly_length + 0.12)
            
            return 0, ts
        except:
            return -1, ts
    
    def all_inactive(self,
                     ttl_length=0.1,
                     enforce_delay=True):
        # Sends the "reset" command to the microcontroller to turn off all
        # lights, and TTL signals. Keep in mind that this does not mean that
        # the microcontroller will reboot, rather, it will be reset to an idle
        # state where all lights and relays are inactive.
        # Arguments:
        #    - enforce_delay: Enforces a delay after sending the command to the
        #      microcontroller. This delay is long enough to execute the
        #      command, send a TTL, and communicate the microcontroller's 
        #      timestamp.
        # Returns 0 and the time when the command was sent if no exceptions
        # occur, otherwise returns -1.
        
        try:
            self.session.write(b'R')
            ts = datetime.datetime.now()
            if enforce_delay:
                # Wait for TTL signal and for the microcontroller to execute command.
                time.sleep(ttl_length + 0.12)
                
            return 0, ts
        except:
            return -1, ts
    
    def all_active(self,
                   ttl_length=0.1,
                   enforce_delay=True):
        # Sends the "all on" command to turn all cost lights on at level 3 
        # then send a TTL. This will NOT activate any relays, the reason for
        # this is to avoid overloading any power supplies and preventing leaks
        # if the relays are connected to valves delivering liquid reward. The
        # "all on" command is intended for diagnostics and debugging purposes,
        # thus no timestamp is communicated.
        # Arguments:
        #    - ttl_length: The length of the TTL signal sent by the
        #      microcontroller. This can be checked by sending it a '?'. 0.1 is
        #      set as a default.
        #    - enforce_delay: Enforces a delay after sending the command to the
        #      microcontroller. This delay is long enough to execute the
        #      command and send a TTL.
        # Returns 0 and the time when the command was sent if no exceptions
        # occur, otherwise returns -1.
        
        try:
            self.session.write(b'A')
            ts = datetime.datetime.now()
            if enforce_delay:
                # Wait for TTL signal and for the microcontroller to execute command.
                time.sleep(ttl_length + 0.02)
                
            return 0, ts
        except:
            return -1, ts
    
    def indicator_toggle(self,
                         ttl_length=0.1,
                         enforce_delay=True):
        # Sends the "k" command to toggle the indicator light. This
        # can be used to indicate that a trial is running or some other
        # event. The light is static and will turn on at a set brightness,
        # then the microcontroller will send a TTL and give a timestamp.
        # Arguments:
        #    - ttl_length: The length of the TTL signal sent by the
        #      microcontroller. This can be checked by sending it a '?'. 0.1 is
        #      set as a default.
        #    - enforce_delay: Enforces a delay after sending the command to the
        #      microcontroller. This delay is long enough to execute the
        #      command and send a TTL.
        # Returns 0 and the time when the command was sent if no exceptions
        # occur, otherwise returns -1.
        
        try:
            self.session.write(b'K')
            ts = datetime.datetime.now()
            if enforce_delay:
                # Wait for TTL signal and for the microcontroller to execute command.
                time.sleep(ttl_length + 0.1)
                
            return 0, ts
        except:
            return -1, ts
    
    def timer_start(self,
                    ttl_length=0.1,
                    enforce_delay=True):
        # Sends the "Q" command to start the microcontrolelr timer. After
        # starting the timer, the microcontroller will send a TTL to confirm
        # the command execution. It will also communicate that it started the
        # timer, thus some time must be given to the microcontroller to do
        # this. The timer is not affected by a reset event.
        # Arguments:
        #    - ttl_length: The length of the TTL signal sent by the
        #      microcontroller. This can be checked by sending it a '?'. 0.1 is
        #      set as a default.
        #    - enforce_delay: Enforces a delay after sending the command to the
        #      microcontroller. This delay is long enough to execute the
        #      command and send a TTL.
        # Returns 0 and the time when the command was sent if no exceptions
        # occur, otherwise returns -1.
        
        try:
            self.session.write(b'Q')
            ts = datetime.datetime.now()
            if enforce_delay:
                # Wait for TTL signal and for the microcontroller to execute command.
                time.sleep(ttl_length+0.1)
                
            return 0, ts
        except:
            return -1, ts
    
    def timer_fetch(self,
                    ttl_length=0.1,
                    enforce_delay=True):
        # Sends the "W" command to request a timestamp. After
        # responding, the microcontroller will send a TTL to confirm
        # the command execution. It will also communicate the timestamp, thus 
        # some time must be given to the microcontroller to do so.
        # Arguments:
        #    - ttl_length: The length of the TTL signal sent by the
        #      microcontroller. This can be checked by sending it a '?'. 0.1 is
        #      set as a default.
        #    - enforce_delay: Enforces a delay after sending the command to the
        #      microcontroller. This delay is long enough to execute the
        #      command and send a TTL.
        # Returns 0 and the time when the command was sent if no exceptions
        # occur, otherwise returns -1.
        
        try:
            self.session.write(b'W')
            ts = datetime.datetime.now()
            if enforce_delay:
                # Wait for TTL signal and for the microcontroller to execute command.
                time.sleep(ttl_length)
                
            return 0, ts
        except:
            return -1, ts
    
    def timer_stop(self,
                   ttl_length=0.1,
                   enforce_delay=True):
        # Sends the "E" command to stop the timer. After stopping the timer,
        # the microcontroller will send a TTL to confirm the command execution.
        # It will also communicate the last value the timer had before stopping 
        # thus some time must be given to the microcontroller to do so.
        # Arguments:
        #    - ttl_length: The length of the TTL signal sent by the
        #      microcontroller. This can be checked by sending it a '?'. 0.1 is
        #      set as a default.
        #    - enforce_delay: Enforces a delay after sending the command to the
        #      microcontroller. This delay is long enough to execute the
        #      command and send a TTL.
        # Returns 0 and the time when the command was sent if no exceptions
        # occur, otherwise returns -1.
        
        try:
            self.session.write(b'E')
            ts = datetime.datetime.now()
            if enforce_delay:
                # Wait for TTL signal and for the microcontroller to execute command.
                time.sleep(ttl_length+0.12)
                
            return 0, ts
        except:
            return -1, ts
    
    def output_ttl(self,
                   ttl_length=0.1,
                   enforce_delay=True):
        # Sends the 'T' command to the microcontroller to send out an
        # independent TTL for synchronization with external hardware.
        # Arguments:
        #    - ttl_length: The length of the TTL signal sent by the
        #      microcontroller. This can be checked by sending it a '?'. 0.1 is
        #      set as a default.
        #    - enforce_delay: Enforces a delay after sending the command to the
        #      microcontroller. This delay is long enough to execute the
        #      command and send a TTL.
        # Returns 0 and the time when the command was sent if no exceptions
        # occur, otherwise returns -1.
        
        try:
            self.session.write(b'T')
            ts = datetime.datetime.now()
            if enforce_delay:
                # Wait for TTL signal and for the microcontroller to execute command.
                time.sleep(ttl_length)
                
            return 0, ts
        except:
            return -1, ts
        
    def toggle_ttlin(self,
                     ttl_length=0.1,
                     enforce_delay=True):
        # Sends the 'Y' command to the microcontroller to toggle incoming ttl
        # servicing on the microcontroller. Incoming TTLs are turned off by
        # default, so the first call to this method will always allow incoming
        # TTLs after the micrcontroller is booted up the first time. This
        # command is acknowledged with the ACK signal.
        # Arguments:
        #    - ttl_length: The length of the TTL signal sent by the
        #      microcontroller. This can be checked by sending it a '?'. 0.1 is
        #      set as a default.
        #    - enforce_delay: Enforces a delay after sending the command to the
        #      microcontroller. This delay is long enough to execute the
        #      command and send a TTL.
        # Returns 0 and the time when the command was sent if no exceptions
        # occur, otherwise returns -1.
        
        try:
            self.session.write(b'Y')
            ts = datetime.datetime.now()
            time.sleep(ttl_length+0.12)
            resp = self.fetch_response()
            print(resp)
            if "on" in resp:
                self.ttlin_state = True
            elif "off" in resp:
                self.ttlin_state = False
            
            if enforce_delay:
                # Wait for TTL signal and for the microcontroller to execute command.
                time.sleep(ttl_length)
                
            return self.ttlin_state, ts
        except:
            return -1, ts
    
    def send_cmd(self,cmd,
                 ttl_length=0.1,
                 enforce_delay=True):
        # Sends a command to the microcontroller. It is very likely that a TTL
        # will be sent after executing the command, in which case it is
        # recommended that a delay is implemented after sending the command.
        # This can be done by setting enforce_delay to True.
        # Arguments:
        #    - cmd: The command to be sent. Please make sure to check the
        #      RECORD documentation to know what can be interpreted as a
        #      command and what cannot.
        #    - ttl_length: The length of the TTL signal sent by the
        #      microcontroller. This can be checked by sending it a '?'. 0.1 is
        #      set as a default.
        #    - enforce_delay: Enforces a delay after sending the command to the
        #      microcontroller. This delay is long enough to execute the
        #      command and send a TTL.
        # Returns 0 and the time when the command was sent if no exceptions
        # occur, otherwise returns -1.
        
        cmd = bytes(cmd, 'utf-8')
        
        try:
            self.session.write(cmd)
            ts = datetime.datetime.now()
            if enforce_delay:
                # Wait for TTL signal and for the microcontroller to execute command.
                time.sleep(ttl_length)
                
            return 0, ts
        except:
            return -1, ts
    
    # Utility methods:
    def fetch_response(self, timeout=1, cleanup=True, eol="\r\n\n"):
        # Returns any bytes available in the serial I/O pipe. This is useful
        # for retreiving microcontroller responses and using them later. It is
        # possible that, when a command is issued to the microcontroller and 
        # no response is retreivd by this method, not enough time has been
        # given to the microcontroller to respond with a full message. Consider
        # using delays in-between commands.
        # Also returns the time at which either bytes were found in the buffer
        # or when the method timed out.
        # Parameters:
        #    1. timeout: The seconds to wait for bytes to be available in the
        #       buffer. If no bytes are avaiable after timeout, the method will
        #       return "No response message available...".
        
        # Start with an empty response message and byte to not confuse our
        # while loop.
        response = ""
        byte = b''
        
        # Take the time when you started this function, will be useful for
        # implementing a timeout
        start = time.time()
        
        # While the end-of-line string (eol) is not contained in the response
        # keep reading bytes one by one, decoding them, and adding them to the
        # response message. If the timeout elapses, break the loop and let the
        # user know there was nothing in the buffer.
        while not eol in response:
            if (time.time() - start >= timeout):
                print("[Error]: No bytes found in the serial buffer after the specified timeout.")
                response = "No response message available..."
                ts = datetime.datetime.now()
                break
            byte = self.session.read(1)
            # Receiving the ':' character indicates the closest time at which
            # the micrcontroller executed the command, so save this time.
            if byte == b':':
                ts = datetime.datetime.now()
            response += byte.decode()
        
        if cleanup:
            response = response.replace('\n', '')
            response = response.replace('\r', '')
        # Precautionary measure to clear the buffer from any stray characters
        # possibly left from the process above.
        self.session.flushOutput()
        
        return response, ts
    
    def feeder_reconfig(self,fdr,lvl,val,
                        test_new=True,
                        firm_version="2.1.1+"):
        # A scripted reconfiguration of any one particular feeder light at some
        # indicated level. This can be useful for reconfiguring things quickly
        # without the need to manually connect to the serial interface.
        # Arguments:
        #   - fdr: The feeder to be reconfigured (1, 2, 3, or 4).
        #   - lvl: The level to modify (1, 2, or 3).
        #   - val: The new CCR value to be written to memory, consult the
        #     RECORD documentation for more information on CCR values (whole
        #     number between 0 and 8000).
        #   - test_new: Whether or not all the cost lights should turn on using
        #     the new configured value (True or False)
        
        # Preprocess and validate inputs.
        if fdr in range(1, 4, 1):
            fdr = str(fdr)
        else:
            print("'fdr' must be either 1, 2, 3, or 4.")
            return 1
        
        if lvl in range(1, 3, 1):
            lvl = str(lvl)
        else:
            print("'lvl' must be either 1, 2, or 3.")
            return 1
        
        if val in range(-1, 8001, 1):
            val = str(val)+'\r'
        else:
            print("'val' must be a whole number between 0 and 8000.")
            return 1
        
        # How to script reconfiguration of feeders:        
        self.send_cmd('$',enforce_delay=False)
        time.sleep(0.5)
        if firm_version == "2.1.1+":
            # Firmware v2.1.1 introduced configuration of relay active time and
            # ttl length, this modified the microcontroller's configuration
            # mode to have a menu at the time it is called, thus we select the
            # correct item here.
            self.send_cmd('A',enforce_delay=False)
            time.sleep(0.15)
        self.send_cmd(lvl,enforce_delay=False)
        time.sleep(0.15)
        self.send_cmd(fdr,enforce_delay=False)
        time.sleep(0.3)
        self.send_cmd(val,enforce_delay=False)
        time.sleep(0.15)
        
        if test_new:
            self.send_cmd('y',enforce_delay=False)
        else:
            self.send_cmd('n',enforce_delay=False)
        time.sleep(0.15)
        #print(self.fetch_response())
        
        return 0
    
    def valve_reconfig(self,val):
        # A scripted reconfiguration of all valves connected to the system.
        # This can be useful for reconfiguring things quickly without the need
        # to manually connect to the serial interface. This method will not
        # work for RECORD microcontrollers running firmware versions prior to
        # v2.1.1.
        # Arguments:
        #   - val: The new value to be written to memory, corresponds to the
        #     amount of milliseconds to keep a valve open to deliver food.
        #     Maximum of 9999 milliseconds (9.999 seconds).
        
        # Preprocess and validate inputs.
        if val in range(-1, 10000, 1):
            val = str(val)+'\r'
        else:
            print("'val' must not exceed 9999 milliseconds.")
            return 1
        
        # How to script reconfiguration of feeders:        
        self.send_cmd('$',enforce_delay=False)
        time.sleep(0.5)
        self.send_cmd('B',enforce_delay=False)
        time.sleep(0.15)
        self.send_cmd(val,enforce_delay=False)
        time.sleep(0.15)
        #print(self.fetch_response())
        
        return 0
    
    def ttl_length_reconfig(self,val):
        # A scripted reconfiguration of all ttls coming in and out of the
        # system.
        # This can be useful for reconfiguring things quickly without the need
        # to manually connect to the serial interface. This method will not
        # work for RECORD microcontrollers running firmware versions prior to
        # v2.1.1.
        # Arguments:
        #   - val: The new value to be written to memory, corresponds to the
        #     amount of milliseconds to keep a ttl signal on.
        #     Maximum of 9999 milliseconds (9.999 seconds).
        
        # Preprocess and validate inputs.
        if val in range(-1, 10000, 1):
            val = str(val)+'\r'
        else:
            print("'val' must not exceed 9999 milliseconds.")
            return 1
        
        # How to script reconfiguration of feeders:        
        self.send_cmd('$',enforce_delay=False)
        time.sleep(0.5)
        self.send_cmd('C',enforce_delay=False)
        time.sleep(0.15)
        self.send_cmd(val,enforce_delay=False)
        time.sleep(0.15)
        #print(self.fetch_response())
        
        return 0
    
    def ttl_mode_reconfig(self,mode):
        # A scripted reconfiguration of the operation mode of outgoing TTLs.
        # This can be useful for reconfiguring things quickly without the need
        # to manually connect to the serial interface. This method will not
        # work for RECORD microcontrollers running firmware versions prior to
        # v2.2.
        # Arguments:
        #   - mode: A numerical representation of the TTL operating mode...
        #        1: TOGGLE mode, upon request TTL will stay on until next
        #           request.
        #        2: PULSE mode, upon request TTL will pulse on for the length
        #           indicated by TTL_LENGTH.
        #        3: OFF mode, outgoing TTL requests are not serviced.
        
        # Preprocess and validate inputs.
        if mode in range(0, 4):
            mode = str(mode)+'\r'
        else:
            print("'mode' must be 1, 2, or 3.")
            return 1
        
        # How to script reconfiguration of feeders:        
        self.send_cmd('$',enforce_delay=False)
        time.sleep(0.5)
        self.send_cmd('D',enforce_delay=False)
        time.sleep(0.15)
        self.send_cmd(mode,enforce_delay=False)
        time.sleep(0.15)
        #print(self.fetch_response())
        
        return 0
    
    def request_ttl_state(self):
        # Requests the TTL state by sending the 't' command. Response is then
        # parsed and the state is reported either True for HIGH or False for 
        # LOW.
        try:
            self.session.write(b't')
            ts = datetime.datetime.now()
            resp, _ = self.fetch_response()
            # Precautionary measure to clear the buffer from any stray characters
            self.session.flushOutput()
            if resp.split('is ',1)[1] == 'HIGH':
                return True, ts
            elif resp.split('is ',1)[1] == 'LOW':
                return False, ts
            else:
                return None, ts
            
        except Exception as e:
            print(e)
            return -1, ts
