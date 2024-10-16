function status = McuEvent(deviceID,eventType,varargin)
%RunSysCheck
%   Run batch script containing routine for a microcontroller event on the 
%   indicated device. 6 types of microcontroller event are available, which
%   are indicated by means of the eventType parameter.
%   Argument(s):
%       Required:
%       1. deviceID (string) - The ID for the device to run the evemt on,
%       used as an input argument for the batch script. This ID must be a
%       serial comm. session name saved within the PuTTY graphical user
%       interface.
%       2. eventType (string) - The type of event that you wish to call.
%       Different event have certain parameters associated with them, these
%       parameters must be defined when calling this function and are 
%       discussed below.
%       Accepted values:
%           a. 'valve' - For toggling valves for liquid reward delivery to
%               the RECORD arena. This type of event opens a valve by means
%               of a relay connected to the GPIO of the microcontroller,
%               then automatically closes it after a certain amount of time
%               which is programmed to the microcontroller.
%               Associated parameters: 'valve_id' ('1' through '4').
%           b. 'light' - For turning on feeder lights on the arena at
%               different brightnesses determined by the parameter
%               'light_level'. A light must be specifid with a number from
%               1 through 4.
%               Associated parameters: 'light_id' ('1' through '4')
%                                      'light_level' ('0' through '3')
%           c. 'reset' - Sets the microcontroller to its default state
%               where all light are turned off.
%               Associated parameters: None.
%           d. 'red_light' - Turns on the microcontroller's on-board red
%               LED. This can be used for debugging purposes.
%               Associated parameters: None.
%           e. 'green_light' - Turns on the microcontroller's on-board
%               green LED. This can be used for debugging purposes.
%               Associated parameters: None.
%           e. 'indicator_toggle' - Toggles the indicator LED peripheral on
%               and off. The indicator LED is a light that continuously
%               glows until it is turned off.
%               Associated parameters: None.
%       Optional:
%       3. kill_on_exit (logical) - Indicated whether the serial
%          communication interface process should be stopped as soon as
%          the stop message (stop_msg) is received. This requires polling
%          a log file for the sotp message. Default false.
%       4. stop_msg (string) - The message which triggers the taskkill
%          Windows command to stop the execution of the serial
%          communication interface process. This message is sent by the
%          microcontroller and should be defined as the last message that
%          is received after the system check has run completely. Default
%          is set to whatever command is generated by this function and 
%          sent to the microcontroller.
%
%   Note: TIMEOUT function was changed to the PING function to allow the
%   batch script to execute in the background.
%   "ping -n 3 127.0.0.1 > nul" gives 3s delay and redirect output to NUL.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Define default and expected parameters:
defaultKillOnExit  = true;
defaultStopMsg     = ':';
defaultLogFilePath = "..\..\Log Files\";
expectedEventType  = {'valve','light','reset','red_light','green_light','indicator_toggle'};
expectedLightLevel = {'0','1','2','3'};
expectedLightVlvID = {'1','2','3','4'};

%% Parse inputs:
validStringIn   = @(x) ischar(x);
validTextIn     = @(x) isstring(x);
validEventType = @(x) any(validatestring(x,expectedEventType));
validLightLevel = @(x) any(validatestring(x,expectedLightLevel));
validFdrVlvID = @(x) any(validatestring(x,expectedLightVlvID));
validLogical = @(x) islogical(x);
% Define parameters:
p = inputParser;
addRequired(p,'deviceID',validStringIn);
addRequired(p,'eventType',validEventType);
addParameter(p,'kill_on_exit',defaultKillOnExit,validLogical);
addParameter(p,'stop_msg',defaultStopMsg,validStringIn);
addParameter(p,'light_id','x',validFdrVlvID);
addParameter(p,'valve_id','x',validFdrVlvID);
addParameter(p,'light_level','x',validLightLevel);
addParameter(p,'log_file_path',defaultLogFilePath,validTextIn);

parse(p,deviceID,eventType,varargin{:});

%% Log event active:
% Timestamp event as "IS_ACTIVE".
eventlog = "..\event log\"+p.Results.deviceID+"_eventlog.log";
TSEvent(p.Results.eventType,'IS_ACTIVE',eventlog);

%% Interpret input
mcu_cmd = '';
switch p.Results.eventType
    case 'valve'
        if strcmp(p.Results.valve_id,'1')
            mcu_cmd = 'F';
        elseif strcmp(p.Results.valve_id,'2')
            mcu_cmd = 'G';
        elseif strcmp(p.Results.valve_id,'3')
            mcu_cmd = 'H';
        else
            mcu_cmd = 'J';
        end
%        p.Results.stop_msg = mcu_cmd+':';
    case 'light'
        mcu_cmd = "#F"+p.Results.light_id+"L"+p.Results.light_level;
%        p.Results.stop_msg = '#:';
    case 'reset'
        mcu_cmd = 'R';
%        p.Results.stop_msg = mcu_cmd+':';
    case 'red_light'
        mcu_cmd = 'r';
%        p.Results.stop_msg = mcu_cmd+':';
    case 'green_light'
        mcu_cmd = 'g';
%        p.Results.stop_msg = mcu_cmd+':';
    case 'indicator_toggle'
        mcu_cmd = 'k';
%        p.Results.stop_msg = mcu_cmd+':';
    otherwise
        disp("Invalid input: event_type = "+p.Results.eventType);
end

%% Buid system command string and run:
syscmd = "cmd /c "+'"cd /d ..\..\ && mcu_event '+...
    p.Results.deviceID+' '+mcu_cmd+' '+p.Results.eventType+' &';
status = system(syscmd);

if p.Results.kill_on_exit
    log_file = p.Results.log_file_path+p.Results.deviceID+"_out.out";
    AutoCloseSS('plink',log_file,p.Results.stop_msg);
    ClearLogs(log_file);
else
    disp("[McuEvent] User specified kill_on_exit as false. Please manually"...
        +" close the serial communication interface program before"...
        +" attempting to send any more commands to the microcontroller"...
        +" Please make sure to clear log file with ClearLogs() as well");
end
%% Log event:
% TIMESTAMP EVENT AS IS_INACTIVE
TSEvent(p.Results.eventType,'IS_INACTIVE',eventlog);
end