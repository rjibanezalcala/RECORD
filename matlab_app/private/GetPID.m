function pid = GetPID(process,varargin)
%GETPID Retreives the process ID (PID) of one or more Windows processes by 
%       using the 'tasklist' MS-DOS process in a command shell. This
%       function returns a process' PID, or a list or PIDs if more than one
%       process with the same name is running.
%       A temporary comma-separated values (CSV) file is created in the
%       working directory where the command shell output is stored.
%   Inputs to function:
%       * Required: process (string) - Name of process to retreive PID
%                   from. Examples: "plink", "putty"...
%       * Optional: session (numeric array) - List of sessions to that the
%                   function should return, in order of appearance.
%                   Examples: 1, [1,2,3].
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Define default parameters:
defaultSession = 'all';
expectedSession = {'first','all','latest'};

%% Parse required input and optional input:
p = inputParser;
validProcessName = @(x) ischar(x);
%validNumArray = @(x) isnumeric(x) && all(x > 0);
validSession = @(x) any(validatestring(x,expectedSession));
addRequired(p,'process',validProcessName);
addParameter(p,'session',defaultSession,validSession);
parse(p,process,varargin{:});

%% Build the system command and run it:
% Note: Use ">>" when outputing to file via command shell to append instead
% of ">" which overwrites the existing information. Do not output to file
% if you wish to save output to variable.
syscmd = "tasklist /FO csv /FI "+'"IMAGENAME eq '+process+'*" '+"> temp\PID_temp.csv 2>&1";
cmdstatus = system(syscmd);

%% Parse output:
if cmdstatus == 0
    table = readtable("temp\PID_temp.csv");
    if ~isempty(table)
        pid = table.("PID");
        pid = pid(:,1);
        if strcmp(p.Results.session,'latest')
            pid = pid(length(pid),1);
        elseif strcmp(p.Results.session,'first')
            pid = pid(1,1);
        end
    else
        pid = 'NaN';
        disp("[GetPID] No tasks are running which match the specified criteria.");
    end
else
    % Return error message if command returns with error.
    pid = 'NaN';
    disp("[GetPID] The command 'taskid' returned an error, no output has been generated.");
end

%% End function:
end

