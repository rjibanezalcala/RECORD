echo -------------------------------------- >> "Log Files\%1_output.log" 2>&1
echo System Cleanup >> "Log Files\%1_output.log" 2>&1
echo %time% >> "Log Files\%1_output.log" 2>&1
echo %date% >> "Log Files\%1_output.log" 2>&1
(
	timeout /t 1 > nul
	echo F
	timeout /t 3 > nul
	echo F
	timeout /t 3 > nul
	echo F
	
	timeout /t 3 > nul
	echo G
	timeout /t 3 > nul
	echo G
	timeout /t 3 > nul
	echo G
	
	timeout /t 3 > nul
	echo H
	timeout /t 3 > nul
	echo H
	timeout /t 3 > nul
	echo H
	
	timeout /t 3 > nul
	echo J
	timeout /t 3 > nul
	echo J
	timeout /t 3 > nul
	echo J
	
) | plink -batch -load "%1" >> "Log Files\%1_output.log" 2>&1
EXIT /B