@ECHO OFF

Setlocal EnableDelayedExpansion
set MOUNTED=0
timeout 1 > NUL

GOTO :CHECKING

:LAUNCHING
IF !MOUNTED! == 1 (
	echo "RamDisk mounted. Launching..."
	timeout 1
	R:\autologin\app\LoginCti.exe
	pause
)
ELSE IF !MOUNTED! !=1 (
	GOTO :MOUNTING
)


:MOUNTING
echo "Mounting..."
timeout 1 > NUL
imdisk -a -f "A:\ramdisk\512m.img" -m R:
timeout 1 > NUL
GOTO :CHECKING


:CHECKING	
IF EXIST "R:\autologin\app\LoginCti.exe" (
	echo "Mounted"
	SET MOUNTED=1
	echo "Status: " !MOUNTED!
	GOTO :LAUNCHING
) ELSE IF NOT EXIST "R:\autologin\app\LoginCti.exe" (
	echo "Not mounted"
	SET MOUNTED=0
	echo "Status: " !MOUNTED!
	GOTO :MOUNTING
)