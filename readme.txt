# GFM Python Data Tools V0.2.13
This is a collection of tools for creating and processing data files that are associated with a Gas Flow Meter (GFM).

## Usage
To access the tools just run the mainMenu.pyw file, a menu will open giving access to all of the different tools.

### Connect To GFM
Used to configure the ESP data logging and to download files from the ESP memory.
Once the ESP is connected to the computer, select the correct port from the drop down and press connect.
If the connection is successfull, the disconnect and start buttons should activate; as well as the file system openning.
Start is used to beigin a test and will ask for a unique file name (alphanumeric and fewer than 27 characters) and if you want to use the gas analyser after which the ESP will begin logging data.
Disconnect can be called at any time to terminate the connection (as long as it has power the ESP will continue to log data).
The files will be open at all times and are refreshed whenever a new connection is made or the logging is started / stopped.
Downloads can be performed at any time while deletes must be performed while the ESP is not logging data to prevent memory problems.

### View Connected Devices
Used to view and manage multiple connected devices at the same time. Once opened it will shortly load a list of attached devices that are correctly functional.
For each device the logging may be started or stopped, the device can be renamed (this is the identifier displayed on this screen) and the full connected view may be opened to download the files.
This is most useful when running several machines at once so that the user does not have to go around and plug in to each device separately.
This will not work with wireless connections as this would require a much more complex process which would slow down the performance significantly.

### Experiment Settings
Used to create, edit and export setup configurations for the Gas Flow Meter. Storing information about the different tubes and what they contain.
Data can be entered manually and then exported or can be loaded in from a correctly formatted .csv file for editing and viewing.

### Analyse Data
Used to combine a setup and event log file together to produce the hourly and daily results, volumes and totals.
Setup and Event log files are loaded in using the buttons in the top left.
The 'process data' button can then be pressed. The calculations are then performed, this may cause tkinter to freeze temporarily.
Once complete the information will be displayed in the tables which an be navigated using the channel, hour and day buttons.
Once processed data is present the export data buttons can be pressed to save it into a .csv file, the whole data log, hourly data, daily data or continuous data may be exported.
If there is any gas analysis data within the event log file the gas composition data will also be able to be exported

### Combine pH / Redox or Gas Data
Used to produce data files which contain the pH and redox data or the gas data for each tip from an event log file and any number of continuous logs for pH/redox/gas.
The event file is loaded at the top using the button.
The data files are added one at a time using the 'add pH/redox file' and 'add gas file' buttons.
Once a data file has been loaded the association needs to be set using the boxes that appear, so that the software knows which channels should take data from where.
Each of the channels are numbered 1 to 15 and if multiple associations are found then the first one (highest in the interface) will be used.
Gas and pH/redox may be processed at the same time, using the process button, and two files can be exported using the buttons in the upper right.
If any of the files are not formatted as expected the software will inform the user and the file will not be added.

### Create Graphs
Used to produce a variety of graphs from a processed information file (created by the Perform Calculations section).
Files must be loaded from one of the following: full event log, hour log, day log or the gas log. Press the correct button and choose the file.
Once the file has been loaded several choices can be made as to the type of graph displayed:
Single Plot - shows one set of values for one channel, choose channel from first drop down and which value from the lower drop down.
Compare Channels - show one set of values for two channels on the same axes. Select channels from two drop downs and value from the third.
All One Channel - show all the values for a single channel. Select the channel from the first drop down.
For any of these the view may be switched between hourly data and daily data as well as the grid and legend (if there is one) toggled on or off.
Using the toolbar on the graph it is possible to zoom and manipulate the graph as well as save it as an image.

### Set Date/time
Used to adjust the time and date settings on the ESP device.
Once the ESP is connected to the computer, select the correct port from the drop down and press connect.
Either set the desired time and date manually using the arrows or check the 'System Time' box which will disable the arrows and keep the time up to date with the computer time.
The 'Get Time From Clock' button will read the current time from the ESP clock and enter it into the input fields.
The 'Set Clock Time' button will attempt to write the currently input time to the ESP. A message will be displayed to indicate if this was successful.

### Calibrate Gas Analyser
Used to recalibrate the gas analyser for both methane and carbon dioxide. Requires gas analyser to be connected to gas flow meter.
Once a connection has been made to the gas flow meter it will attempt to connect to the gas analyser. If this is successful the data and state of the analyser will be shown on screen.
By pressing 'Calibrate CO2' or 'Calibrate CH4' the user can begin calibrating the analyser.
Each gas sample should be connected one at a time. After each sample is connected press 'Add point' and type in the percentage of gas in the sample. After 15 seconds the data point will be added.
Repeat for each sample, it is recommended that the percentage should increase each time, until all are added. Then press 'End Calibration' and the calculated line of best fit should appear.
Once both have been calibrated, two lines should appear on the screen and it should say that the analyser is ready for analysis.
The analyser uses the SD card to remember its calibration even if switched off, just make sure you finish a calibration so that it is saved.

### Settings
Used to decide which separators are used for CSV files. This applies to both imported and exported files. It is strongly recommended that you select a separator before you start working and do not change it afterwards.
Both comma and semicolon sepeared modes are available by default but you can also enter your own pair of separators if you wish; they just have to be two different symbols.

## Future ideas or plans
Wireless connection to ESP from laptop.