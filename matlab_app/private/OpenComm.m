function status = OpenComm(process,varargin)
%OPENCOMM Opens a serial communication channel between the PC and a RECORD
%         microcontroller by calling PuTTY or its command line variant,
%         Plink. A channel can be opened by either passing a structure
%         containing session parameters, or a session ID if such a session
%         has already been created and saved within PuTTY. Returns status
%         code of the executable.
%   Inputs to function:
%       Required:
%               * process (string) - Executable to open comm channel with.
%                 Use 'putty' to open a separate command line window, in
%                 the foreground, or use 'plink' to open a command shell
%                 within MATLAB. Default value is "putty".
%       Optional:
%               * session (string or structure) - The session parameters to
%                 load. This can either be a session ID if a session has
%                 been saved within PuTTY, or six arguments describing the
%                 session parameters. If no session information is provided
%                 default parameters will be loaded, but there is no 
%                 guarantee that a session to the correct device will be
%                 created. 
%                 See default parameters at the end of this explanation.
%                 Example 1: A session has been saved to PuTTY with the ID
%                 "FR2355". In this case, the session parameter will simply
%                 be the character string 'FR2355'.
%                 Example 2: There is no saved serial session in PuTTY,
%                 thus a session must be configured. The parameters defined
%                 must be all that are listed in the PuTTY documentation
%                 (https://documentation.help/PuTTY/using-cmdline-sercfg.html#S3.8.3.22).
%                 The array passed have the following elements, in the
%                 correct order, and all must be defined as character strings:
%                 {
%                   com_port:  [a single numeric string, see explanation
%                               below] 
%                   baud_rate: [a numeric string containing the baud rate],
%                   data_bits: [single digit from 5 to 9],
%                   parity:    [a single lower-case letter, either n, o, e,
%                               m, or s],
%                   stop_bits: [a single numeric string, either 1, 1.5, or
%                               2],
%                   flow_ctrl: [a single uppercase letter, either N, X, R,
%                               or D],
%                 }
%               ** com_port - COM port to open a serial communication
%                 session to. This is displayed under "Ports (COM&LPT)" on
%                 the windows device manager.
%               ** Default parameters:
%                   com_port  = '4';
%                   baud_rate = '9600';
%                   data_bits = '8';
%                   parity    = 'n';
%                   stop_bits = '1';
%                   flow_ctrl = 'N';
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Define default parameters:
defaultComPort  = '4';
defaultBaudRate = '9600';
defaultDataBits = '8';
defaultParity   = 'n';
defaultStopBits = '1';
defaultFlowCtrl = 'N';
expectedDataBits = {'5','6','7','8','9'};
expectedParity = {'n','o','e','m','s'};
expectedStopBits = {'1','1.5','2'};
expectedFlowCtrl = {'N','X','R','D'};
useSessionID = false;
defaultDeviceID = 'dne';
expectedProcessName = {'putty','plink'};

%% Parse inputs:
p = inputParser;
validProcessName = @(x) any(validatestring(x,expectedProcessName));
validSessionID   = @(x) ischar(x);
validDataBits = @(x) any(validatestring(x,expectedDataBits));
validParity = @(x) any(validatestring(x,expectedParity));
validStopBits = @(x) any(validatestring(x,expectedStopBits));
validFlowCtrl = @(x) any(validatestring(x,expectedFlowCtrl));
validEntryNumber = @(x) ischar(x) && all(~isletter(x));
% Add required parameter:
addRequired(p,'process',validProcessName);
% Check if second input is a session ID and define it:
if nargin == 2
    addOptional(p,'deviceID',defaultDeviceID,validSessionID);
    useSessionID = true;
% Otherwise define serial session:
else
    addOptional(p,'com_port',defaultComPort,validEntryNumber);
    addParameter(p,'baud_rate',defaultBaudRate,validEntryNumber);
    addParameter(p,'data_bits',defaultDataBits,validDataBits);
    addParameter(p,'parity',defaultParity,validParity);
    addParameter(p,'stop_bits',defaultStopBits,validStopBits);
    addParameter(p,'flow_ctrl',defaultFlowCtrl,validFlowCtrl);
end

parse(p,process,varargin{:});

%% Build command line command and run:
if useSessionID
    cmdstring = p.Results.process+" -load "+p.Results.deviceID;
else
    cmdstring = p.Results.process+" -serial com"+p.Results.com_port+...
        " -sercfg "+p.Results.baud_rate+","+p.Results.data_bits+","+...
        p.Results.parity+","+p.Results.stop_bits+","+p.Results.flow_ctrl;
end
status = system(cmdstring);

%% End function
end