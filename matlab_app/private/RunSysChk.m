function status = RunSysChk(deviceID,varargin)
%Run System Check
%   Run batch script containing routine for a system check on the indicated
%   arena.
%   Arguments:
%       Required:
%           1. arena (string) - The arena ID for the arena to run the check
%           on, used as an input argument for the batch script.
%   Optional:
%           2. kill_on_exit (logical) - Indicated whether the serial
%           communication interface process should be stopped as soon as
%           the stop message (stop_msg) is received. This requires polling
%           a log file for the sotp message. Default false.
%           3. stop_msg (string) - The message which triggers the taskkill
%           Windows command to stop the execution of the serial
%           communication interface process. This message is sent by the
%           microcontroller and should be defined as the last message that
%           is received after the system check has run completely. Default
%           'F4L0'.
%
%   Note: TIMEOUT function was changed to the PING function to allow the
%   batch script to execute in the background.
%   "ping -n 3 127.0.0.1 > nul" gives 3s delay and redirect output to NUL.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Define default parameters:
defaultKillOnExit  = false;              % Exit serial communication application automatically after receiving the stop message.
defaultStopMsg     = 'F4L0';             % At least a portion of the last expected message received from the microcontroller.
defaultLogFilePath = "..\..\Log Files\"; % Where the batch script dumps output from serial comm. interface.
sysChkScript       = 'system_check';     % The batch script containing commands for system check.

%% Parse inputs:
validStringIn   = @(x) ischar(x);
validTextIn     = @(x) isstring(x);
% validKillOnExit = @(x) any(validatestring(x,expectedKillOnExit));
validKillOnExit = @(x) islogical(x);
% Define parameters:
p = inputParser;
addRequired(p,'deviceID',validStringIn);
addParameter(p,'kill_on_exit',defaultKillOnExit,validKillOnExit);
addParameter(p,'stop_msg',defaultStopMsg,validStringIn);
addParameter(p,'log_file_path',defaultLogFilePath,validTextIn);

parse(p,deviceID,varargin{:});

%% Buid system command string and run:
syscmd = "cmd /c "+'"cd /d ..\..\ && '+sysChkScript+' '+p.Results.deviceID+' &';
status = system(syscmd);

if status
    disp("[RunSysChk] Batch script "+sysChkScript+" execution returned with status code other than 0."...
        +" Please check that such a script exists within the root folder of the RECORD"...
        +" system scripts or that this script does not contain errors.");
else
    if p.Results.kill_on_exit
        log_file = p.Results.log_file_path+p.Results.deviceID+"_out.out";
        AutoCloseSS('plink',log_file,p.Results.stop_msg);
        ClearLogs(log_file);
    else
        disp("[RunSysChk] User specified kill_on_exit as false. Please manually"...
            +" close the serial communication interface program before"...
            +" attempting to send any more commands to the microcontroller"...
            +" Please make sure to clear log file with ClearLogs() as well.");
    end
end
end