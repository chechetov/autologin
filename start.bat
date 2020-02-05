@ECHO OFF
Setlocal EnableDelayedExpansion
set MOUNTED=0

for /l %%i IN (1,2,3,4,5) do (
echo "Iteration %%i"
timeout 1 > NUL

GOTO :CHECKING
echo "Mounted here: " !MOUNTED!

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
echo "Doing mounting..."
timeout 1 > NUL
imdisk -a -f "A:\ramdisk\image.img" -m R:
timeout 1 > NUL
GOTO :CHECKING


:CHECKING	
IF EXIST "R:\autologin\app\login_cti.py" (
	echo "Looks mounted"
	SET MOUNTED=1
	echo "Mounted is: " !MOUNTED!
	GOTO :LAUNCHING
) ELSE (
	echo "Looks not mounted"
	SET MOUNTED=0
	GOTO :MOUNTING
	echo "Mounted is: " !MOUNTED!
)