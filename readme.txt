# GFM Python Data Tools
This is a collection of tools for creating and processing data files that are associated with a Gas Flow Meter (GFM).

## Usage
To access the tools just run the mainMenu.pyw file, a menu will open giving access to all of the different tools.

### Configure Setup
Used to create, edit and export setup configurations for the Gas Flow Meter. Storing information about the different tubes and what they contain.
Data can be entered manually and then exported or can be loaded in from a correctly formatted .csv file for editing and viewing.

### Configure Event Log
Used to create event logs for testing purposes (real ones will be produced by the hardware attached to the GFM).
Set the temperature and pressure maximum and minimum value as well as the duration of the experiment and the time between tips, then press generate and the data will be created.
The generated information will be one tip every interval from each bucket in turn with a random temperature and pressure. This is not very realistic but good enough for testing the UI.
The data can then be exported to a .csv file using the export button.

### Perform Calculations
Used to combine a setup and event log file together to produce the hourly and daily results, volumes and totals.
Setup and Event log files are loaded in using the buttons in the top left.
The 'process data' button can then be pressed. The calculations are then performed, this may cause tkinter to freeze temporarily.
Once complete the information will be displayed in the tables which an be navigated using the channel, hour and day buttons.
Once processed data is present the 'export data' button can be pressed to save it into a .csv file.

### Create Graphs
Not currently implemented.
Will allow user to import processed data file and produce a variety of graphs from the information.

## Future ideas or plans
Add graphing section.
Make data validation consistent and more obvious. (As the event log generator will probably dissapear with time this isn't top priority)
Add multithreading to prevent UI freezes while the program is doing something.