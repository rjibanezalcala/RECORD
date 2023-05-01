echo -------------------------------------- >> "Log Files\%1_output.log" 2>&1
echo System Check >> "Log Files\%1_output.log" 2>&1
echo %time% >> "Log Files\%1_output.log" 2>&1
echo %date% >> "Log Files\%1_output.log" 2>&1
(
	echo R
	
	ping -n 3 127.0.0.1 > nul
	echo #F1L3
	ping -n 3 127.0.0.1 > nul
	echo F
	ping -n 3 127.0.0.1 > nul
	echo F
	ping -n 3 127.0.0.1 > nul
	echo #F1L0
	
	ping -n 3 127.0.0.1 > nul
	echo #F2L3
	ping -n 3 127.0.0.1 > nul
	echo G
	ping -n 3 127.0.0.1 > nul
	echo G
	ping -n 3 127.0.0.1 > nul
	echo #F2L0
	
	ping -n 3 127.0.0.1 > nul
	echo #F3L3
	ping -n 3 127.0.0.1 > nul
	echo H
	ping -n 3 127.0.0.1 > nul
	echo H
	ping -n 3 127.0.0.1 > nul
	echo #F3L0
	
	ping -n 3 127.0.0.1 > nul
	echo #F4L3
	ping -n 3 127.0.0.1 > nul
	echo J
	ping -n 3 127.0.0.1 > nul
	echo J
	ping -n 3 127.0.0.1 > nul
	echo #F4L0
	
) | plink -batch -load %1 >> "Log Files\%1_out.out" 2>&1
EXIT /B