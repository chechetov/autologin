@ECHO OFF

Setlocal EnableDelayedExpansion
set MOUNTED=0
timeout 1 > NUL

GOTO :CHECKING

:LAUNCHING
IF !MOUNTED! == 1 (
	echo "RamDisk mounted. Launching..."
	timeout 1
	python "R:\autologin\app\login_cti.py"
	pause
)
ELSE(
	GOTO :MOUNTING
)


:MOUNTING
echo "Mounting..."
timeout 1 > NUL
imdisk -a -f "A:\ramdisk\image.img" -m R:
timeout 1 > NUL
GOTO :CHECKING


:CHECKING	
IF EXIST "R:\autologin\app\login_cti.py" (
	echo "Mounted"
	SET MOUNTED=1
	echo "Status: " !MOUNTED!
	GOTO :LAUNCHING
) ELSE (
	echo "Not mounted"
	SET MOUNTED=0
	echo "Status: " !MOUNTED!
	GOTO :MOUNTING
)