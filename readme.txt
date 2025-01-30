# GFM Python Data Tools V0.2
This is a collection of tools for creating and processing data files that are associated with a Gas Flow Meter (GFM).

## Usage
To access the tools just run the mainMenu.pyw file, a menu will open giving access to all of the different tools.

### Connect To GFM
Used to configure the ESP data logging and to download files from the ESP memory.
Once the ESP is connected to the computer, select the correct port from the drop down and press connect.
If the connection is successfull, the disconnect and start buttons should activate; as well as the file system openning.
Start is used to beigin a test and will ask for a unique file name (alphanumeric and fewer than 27 characters) after which the ESP will begin logging data.
Disconnect can be called at any time to terminate the connection (as long as it has power the ESP will continue to log data).
The files will be open at all times and are refreshed whenever a new connection is made or the logging is started / stopped.
Downloads can be performed at any time while deletes must be performed while the ESP is not logging data to prevent memory problems.

### Configure Setup
Used to create, edit and export setup configurations for the Gas Flow Meter. Storing information about the different tubes and what they contain.
Data can be entered manually and then exported or can be loaded in from a correctly formatted .csv file for editing and viewing.

### Perform Calculations
Used to combine a setup and event log file together to produce the hourly and daily results, volumes and totals.
Setup and Event log files are loaded in using the buttons in the top left.
The 'process data' button can then be pressed. The calculations are then performed, this may cause tkinter to freeze temporarily.
Once complete the information will be displayed in the tables which an be navigated using the channel, hour and day buttons.
Once processed data is present the 'export data' button can be pressed to save it into a .csv file.

### Create Graphs
Used to produce a variety of graphs from a processed information file (created by the Perform Calculations section).
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

## Future ideas or plans
Wireless connection to ESP from laptop.
Integration for Gas Composition Analysis.