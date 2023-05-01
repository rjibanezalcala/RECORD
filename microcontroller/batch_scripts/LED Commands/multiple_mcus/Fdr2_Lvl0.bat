echo -------------------------------------- >> "..\..\Log Files\FR2355_output.log" 2>&1
echo %time% >> "..\..\Log Files\FR2355_output.log" 2>&1
echo %date% >> "..\..\Log Files\FR2355_output.log" 2>&1
(
	timeout /t 1 > nul
	echo #F2L0
	exit
) | start /B plink -batch -load "FR2355" >> "..\..\Log Files\FR2355_output.log" 2>&1

echo -------------------------------------- >> "..\..\Log Files\FR2355_2_output.log" 2>&1
echo %time% >> "..\..\Log Files\FR2355_2_output.log" 2>&1
echo %date% >> "..\..\Log Files\FR2355_2_output.log" 2>&1
(
	timeout /t 1 > nul
	echo #F2L0
	exit
) | start /B plink -batch -load "FR2355_2" >> "..\..\Log Files\FR2355_2_output.log" 2>&1

echo -------------------------------------- >> "..\..\Log Files\FR2355_3_output.log" 2>&1
echo %time% >> "..\..\Log Files\FR2355_3_output.log" 2>&1
echo %date% >> "..\..\Log Files\FR2355_3_output.log" 2>&1
(
	timeout /t 1 > nul
	echo #F2L0
	exit
) | start /B plink -batch -load "FR2355_3" >> "..\..\Log Files\FR2355_3_output.log" 2>&1

echo -------------------------------------- >> "..\..\Log Files\FR2355_4_output.log" 2>&1
echo %time% >> "..\..\Log Files\FR2355_4_output.log" 2>&1
echo %date% >> "..\..\Log Files\FR2355_4_output.log" 2>&1
(
	timeout /t 1 > nul
	echo #F2L0
	exit
) | start /B plink -batch -load "FR2355_4" >> "..\..\Log Files\FR2355_4_output.log" 2>&1

EXIT /B