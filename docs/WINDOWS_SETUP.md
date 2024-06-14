# rc - WINDOWS SETUP
Installing on Windows can be a PITA if your $PATH and folder permissions aren't setup correctly to work with pip.  

This page captures Windows setup issues & solutions ran across to date.

## Issue #1:
* Python is installed to a non-system folder like:
  * C:\Python312
* Python installs scripts to a location like:
  * C:\Python312\Scripts
* Error during install:
  * WARNING: Failed to write executable - trying to use .deleteme logic
  * ERROR: Could not install packages due to an OSError: [WinError 2] The system cannot find the file specified
* Solution:
  * From File Explorer, grant your user "full control" to the C:\Python312 folder

## Issue #2:
* Python is installed to a system folder like:
  * C:\System32\Python312
* Python installs scripts to a location like:
  * %AppData%\Python\Python312\Scripts
* Error after a successful install, like:
  * bash: rc: command not found
* Solution:
  * Update your USER PATH, adding the Scripts folder:
    * %AppData%\Python\Python312\Scripts
