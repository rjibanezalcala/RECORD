echo %time% - SENDING COMMAND "%2" TO DEVICE: "%1" >> "GUI\event log\%1_eventlog.log" 2>&1
(
	timeout /t 1 > nul
	echo %2
	exit
) | plink -batch -load %1 >> "Log Files\%1_out.out" 2>&1
echo %time% - EVENT OF TYPE "%3" , "%2" TERMINATED BY APPLICATION >> "GUI\event log\%1_eventlog.log" 2>&1
EXIT /B