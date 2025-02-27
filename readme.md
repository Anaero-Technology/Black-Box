# GFM Python Data Tools V0.4
This is a collection of tools for creating and processing data files that are associated with a Gas Flow Meter logger.

## Usage
To access the tools either run the executable file from the compiled version or run gfmPythonToolsMain.py a menu will open giving access to all of the different tools.

### Main Screen
The initial view when starting the software will display a list of currently connected gas flow logger devices. If no devices could be found a message will be displayed to show this.
Once a device has been found it will display as a row on the main screen, showing the user the port name that it is connected to, what name the device has been assigned and whether or not it is logging.
There are several buttons associated with each device:
- Start or stop logging, depending on the state of the logger.
- Rename the device, to assign it a new, unique, name. This cannot be done while the device is logging.
- Open the full file view window, allows the user to see the list of files and download or delete any they choose.
- Open the monitor window, this allows the user to see how many tips have occured per hour on each channel
Below this section the analyse data button opens the dialogue window to process downloaded data and the settings gear opens the options menu.
No two windows can be opened at the same time to prevent conflict or confusion so simply close one before opening another.

### File View
Once the files button is pressed on a specific device a new window will open which will automatically connect to and open the files for the device.
At the top of the window you can see the name and port of the device. Below this it shows the current status of the SD card and the percentage usage of the storage.
The button to the right allows the user to start or stop the device logging.
- Starting requires the user to provide a new file name to save the data under after which the device will check it is setup correctly and if not it will prompt the user to try again.
- Stopping simply asks the user for confirmation as once stopped the same file cannot be used again until it has been deleted.
The section bellow shows all of the files in the SD card and their size
- If the device is logging one will have its name displayed in blue to indicate that this is the current working file.
- Clicking on a file will highlight it in green and light up the two buttons at the bottom of the window.
    - Download will ask the user for a location to save the data on their computer then download all of the files data and save it there. This may take some time depending on the experiment duration. This can be done while the logger is running and any tips that are missed during this time will be recovered but may have a small margin for error in their event time.
    - Delete will ask for confirmation and then remove the file from the SD card. This cannot be done while logging to prevent accidental deletion or corruption.
- Closing this winodw can be done at any time as long as an action has not been completed with the logger yet. The connection will be terminated safely.

### Monitor view
Once the monitor button is pressed on a specific device a new window will open which will automatically connect to and display the graphs for the device.
All the data for the hours of the experiment so far will be loaded and any subsequent hours that occur with the display open will be added.
Each of the channels from 1 to 15 will be shown as graphs with a common axis scale, showing just the number of tips that have been recorded per hour.
This is designed as a diagnostic tool, to make sure events are being recorded and provide a quick check for issues. 

### Analyse Data
Once this window opens it will show you a step by step process for converting the data produced by the logger into useful information.
This can be done multiple times with the same data, allowing setup configuration to be adjusted whenever needed. As such it is recommended that the initial file from the logger be kept, even after this processing has been done.
The steps are as follows:
- Select setup file - either select a setup file, exactly the same as our other system, or create a new one. If creating one a window will open to enter or load information and allows the user to save this as a file which can then be opened for usage.
- Select event file - select the file that has been downloaded from the logger
- Wait for process completion - this will take longer if the experiment has been running for a long time
- Preview data - provides basic overview of the results at the end of the experiment: total number of tips, total volume of gas at STP and net volume of gas (ml/gVS) for each channel.
- Download files - Choose which of the resultant files you would like to save. Event log - every event and all information, Hour log - event log grouped by hour, Day log - event log grouped by day, Continuous log - contains no adjustments for inoculum, just gas amounts.

### Settings
This section allows you to choose which file separators you want to use for your CSV files. Allowing two defaults and a custom option should you need it.
It is recommended that you use the separators associated with the region of your computer as it ensures files will be compatible with other software easily.
This only needs to be set once, when you first start the software for the first time and then can be left as your selection will be remembered, even if the software is closed.
Remember to change this when moving to a new computer.