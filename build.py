#####################################################
#               NUITKA BUILD SCRIPT                 #
#####################################################
# Author: Matic Kukovec
# Date: April 2018

import os
import platform
import shutil


NUITKA = "C:/Python38/Scripts/nuitka3-script.py"  # Path where my nuitka3-script.py is
CWD = os.getcwd().replace("\\", "/")
# Requires VB tools to be installed
MSVC = "C:/Program Files (x86)/Microsoft Visual Studio/2017/Community/VC/Auxiliary/Build/vcvars64.bat"
PYTHON_VERSION = "3.8"
PYTHON_EXE_PATH= "C:/Python38/python.exe"
NUMBER_OF_CORES_FOR_COMPILATION = 4 # 1 is the safest choice, but you can try more

# Generate command

command = '"{}" amd64 &'.format(MSVC)
command += "{} ".format(PYTHON_EXE_PATH)
command += "{} ".format(NUITKA)
command += "--verbose "
command += "--jobs={} ".format(NUMBER_OF_CORES_FOR_COMPILATION)
command += "--show-scons "
command += "--follow-imports "

command += "--experimental=use_pefile "
command += "--include-package=selenium "

command += "--recurse-all "
command += "--show-progress "
command += "--show-modules "
command += "--remove-output "
command += "--output-dir={}/app ".format(CWD)
command += "{}/src/LoginCti.py ".format(CWD)

os.system(command)

MyLocation = os.path.dirname(os.path.realpath(__file__))

src = os.path.join(MyLocation, "src", "exe")
dest = os.path.join(MyLocation, "app", "exe")
copy = shutil.copytree(src, dest)

src = os.path.join(MyLocation, "src", "log")
dest = os.path.join(MyLocation, "app", "log")
copy = shutil.copytree(src, dest)

src = os.path.join(MyLocation, "src", "tmp")
dest = os.path.join(MyLocation, "app", "tmp")
copy = shutil.copytree(src, dest)

src = os.path.join(MyLocation, "src", "selenium")
dest = os.path.join(MyLocation, "app", "selenium")
copy = shutil.copytree(src, dest)

print("END")