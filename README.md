# Auto Login harness to log in to Workspace automatically

## Built on

###Python
###Selenium WebDriver
###ChromeDriver
###Chrome
###AutoIt
###Node.js + NodeWebKit

Main idea:
1. Mount RamDisk with ImDisk (to cope with slow HDD speed at startup)
2. Check if disk is mounted
3. Launch Python script
4. Python launches Chrome through Selenium WebDriver + ChromeDriver
5. Web browser handles web part, node.js handles google authenticator part
6. Once web part is done, AutoIt handles Citrix Windows

Installation:
1. Install ImDisk
2. Compress repository into *.img file and put start.bat in the root folder
3. Install start.bat in Windows Task Scheduler
4. Intall required Python dependencies with PIP + Visual Basic tools
5. Use and go back to step 4 in case something is missing.



