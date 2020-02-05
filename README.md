# autoLogin

Used for autologging into WDE.

Consists of:
--- Python ---
--- Chrome + ChromeDriver ---
--- AutoIt ---

Idea:

1. Mount RamDisk with ImDisk
2. Check if disk is mounted
3. Launch Python script
4. Python launches ChromeDriver + Chrome
5. Once web part is done, AutoIt handles Citrix Windows

Installation:

1. Install ImDisk
3. Compress repository into *.img file and put start.bat in the root folder
2. Install start.bat in Windows Task Scheduler
4. Test and Use.



