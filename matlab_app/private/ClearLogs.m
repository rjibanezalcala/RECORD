function ClearLogs(filename)
%% Clear contents of log file...
pause(1.0);
disp("[ClearLogs] Flushing log file...");
f = fopen(filename,'w');
disp("[ClearLogs] Log file '"+filename+"' flushed.");
fclose(f);
end