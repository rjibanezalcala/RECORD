echo -------------------------------------- >> "..\Log Files\%1_output.log" 2>&1
echo %time% >> "..\Log Files\%1_output.log" 2>&1
echo %date% >> "..\Log Files\%1_output.log" 2>&1
(
	timeout /t 1 > nul
	echo G
	exit
) | plink -batch -load "%1" >> "Log Files\%1_out.out" 2>&1
EXIT /B