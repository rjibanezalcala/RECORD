function status = AutoCloseSS(process,file,stopMsg)
%Auto-Close Serial Session
%   Closes the latest found putty or plink serial comm. session returned by
%   the GetPID function.

verifyPID = @(x) isnumeric(x) && (x > 4);
PID = GetPID(process,'session','latest');

if verifyPID(PID) 
    log = fopen(file);
    tline = fgetl(log);
    while ~contains(string(tline),stopMsg)
        tline = fgetl(log);
    end
    fclose(log);
    
    syscmd = "taskkill /F /PID "+PID;
    cmdstatus = system(syscmd);

    if cmdstatus
        disp("[AutoCloseSS] The command 'taskkill' returned an error, no task has been terminated.");
        status = 1;
    else
        disp("[AutoCloseSS] Log file must be flushed before automatically" + ...
            " closing a serial communication session next time." + ...
            " Please make sure to clear log files for this device." + ...
            " You may use ClearLogs() to do this.");
        status = 0;
    end
else
disp("[AutoCloseSS] PID provided ("+PID+") is not a valid input to the taskkill command.");
end

end
