import tkinter
import tkinter.ttk as Ttk
from tkinter.ttk import Style
from tkinter import filedialog
from tkinter import messagebox
import readSetup
import readSeparators
import os, sys
import setupGUI
from threading import Thread
import newCalculations
import createSetup
from PIL import Image, ImageTk
import notifypy

class MainWindow(tkinter.Frame):
    '''Class to contain all of the menus'''
    def __init__(self, parent, *args, **kwargs) -> None:
        #Setup parent configuration
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        #Grid dimensions for main window
        self.numberRows = 16
        self.numberColumns = 5

        #Whether files are being loaded, processed or saved so the action cannot be repeated
        self.loading = False
        self.processing = False
        self.saving = False

        #Create internal grid
        for row in range(0, self.numberRows):
            self.grid_rowconfigure(row, weight=1)
        for col in range(0, self.numberColumns):
            self.grid_columnconfigure(col, weight=1, uniform="cols")

        #Setup pathing for files stored within one executable or in directory
        self.thisPath = os.path.abspath(".")
        try:
            self.thisPath = sys._MEIPASS
        except:
            pass
        
        #Get the separators from the settings file
        self.column, self.decimal = readSeparators.read()

        self.red = "#DD0000"
        self.green = "#00DD00"

        #Used to store data once it has been processed
        self.eventLog = None
        self.hourLog = None
        self.dayLog = None
        self.continuousLog = None

        #Middle of the screen so a new window can be opened there
        self.screenCentre = [self.parent.winfo_screenwidth() / 2, self.parent.winfo_screenheight() / 2]

        #Allowed file types and extensions
        self.fileTypes = [("CSV Files", "*.csv")]

        #Create first tab - the one to get the setup file
        self.tabSetupFile = tkinter.Label(self, text="Select Setup File", relief="raised")
        #Store colours for tab backgrounds
        self.onColour = self.tabSetupFile.cget("bg")
        self.offColour = "#999999"
        self.selectedColour = "#6666BB"
        self.tabSetupFile.configure(bg=self.selectedColour)
        #Create all the other tabs
        self.tabEventFile = tkinter.Label(self, text="Select Event File", relief="sunken", bg=self.offColour)
        self.tabProcessing = tkinter.Label(self, text="Processing Data...", relief="sunken", bg=self.offColour)
        self.tabPreview = tkinter.Label(self, text="Preview Results", relief="sunken", bg=self.offColour)
        self.tabDownload = tkinter.Label(self, text="Save Results", relief="sunken", bg=self.offColour)
        #Add tabs to grid
        self.tabSetupFile.grid(row=0, column=0, sticky="NESW")
        self.tabEventFile.grid(row=0, column=1, sticky="NESW")
        self.tabProcessing.grid(row=0, column=2, sticky="NESW")
        self.tabPreview.grid(row=0, column=3, sticky="NESW")
        self.tabDownload.grid(row=0, column=4, sticky="NESW")

        #Frame used to hold each of the different pages so they are displayed in the same place
        self.viewWindow = tkinter.Frame(self)
        self.viewWindow.grid(row=1, column=0, rowspan=15, columnspan=5, sticky="NESW")

        self.viewWindow.grid_rowconfigure(0, weight=1)
        self.viewWindow.grid_columnconfigure(0, weight=1)

        #Create each window, in reverse order so the setup one appears on top at the end
        self.downloadWindow = tkinter.Frame(self.viewWindow)
        self.downloadWindow.grid(row=0, column=0, sticky="NESW")

        self.previewWindow = tkinter.Frame(self.viewWindow)
        self.previewWindow.grid(row=0, column=0, sticky="NESW")

        self.processingWindow = tkinter.Frame(self.viewWindow)
        self.processingWindow.grid(row=0, column=0, sticky="NESW")

        self.eventWindow = tkinter.Frame(self.viewWindow)
        self.eventWindow.grid(row=0, column=0, sticky="NESW")

        self.setupWindow = tkinter.Frame(self.viewWindow)
        self.setupWindow.grid(row=0, column=0, sticky="NESW")
    
        #Create grid for setup
        rowWeights = [4, 2, 1, 1, 2, 1, 4]
        for row in range(0, 7):
            self.setupWindow.grid_rowconfigure(row, weight=rowWeights[row])
        self.setupWindow.grid_columnconfigure(0, weight=1)

        #Loading button
        self.loadSetupFileButton = tkinter.Button(self.setupWindow, text="Load Setup File", command=self.loadSetupFile, font=("", 16))
        self.loadSetupFileButton.grid(row=1, column=0)
        #Information about the loaded file
        self.setupFileLabel = tkinter.Label(self.setupWindow, text="No Setup File Loaded", fg=self.red)
        self.setupFileLabel.grid(row=2, column=0)
        #Button to open window to make new setup file
        self.createSetupFileButton = tkinter.Button(self.setupWindow, text="Create New Setup File", command=self.openSetupFileCreator, font=("", 16))
        self.createSetupFileButton.grid(row=4, column=0)
        #Extra information for the user
        self.createSetupExtraText = tkinter.Label(self.setupWindow, text="Once you have created and saved a setup file you can load it above.")
        self.createSetupExtraText.grid(row=5, column=0)
        #Next button frame
        self.setupButtonsFrame = tkinter.Frame(self.setupWindow)
        self.setupButtonsFrame.grid(row=6, column=0, sticky="NESW")
        self.setupNextButton = tkinter.Button(self.setupButtonsFrame, text="Next", font=("", 16), command=self.nextPressedSetup, state="disabled")
        self.setupNextButton.pack(side="right", anchor="s")
        #Object to hold the reference to the setup creator window so it can be closed if needed
        self.setupCreateWindow = None

        #Setup internal grid for event window
        rowWeights = [4, 2, 1, 1, 3, 4]
        for row in range(0, 5):
            self.eventWindow.grid_rowconfigure(row, weight=rowWeights[row])
        self.eventWindow.grid_columnconfigure(0, weight=1)

        #Load file button
        self.loadEventFileButton = tkinter.Button(self.eventWindow, text="Load Event File", command=self.loadEventFile, font=("", 16))
        self.loadEventFileButton.grid(row=1, column=0)
        #File information label
        self.eventFileLabel = tkinter.Label(self.eventWindow, text="No Event File Loaded", fg=self.red)
        self.eventFileLabel.grid(row=2, column=0)
        #User information label
        self.eventFileInfo = tkinter.Label(self.eventWindow, text="This is the file that should have been downloaded directly from the logger.")
        self.eventFileInfo.grid(row=3, column=0)
        #Next and back buttons frame
        self.eventButtonsFrame = tkinter.Frame(self.eventWindow)
        self.eventButtonsFrame.grid(row=5, column=0, sticky="NESW")
        self.eventBackButton = tkinter.Button(self.eventButtonsFrame, text="Back", font=("", 16), command=self.backPressedEvent)
        self.eventNextButton = tkinter.Button(self.eventButtonsFrame, text="Next", font=("", 16), command=self.nextPressedEvent, state="disabled")
        self.eventBackButton.pack(side="left", anchor="s")
        self.eventNextButton.pack(side="right", anchor="s")

        #Setup grid for processing
        rowWeights = [4, 1, 1, 1, 2, 4]
        for row in range(0, len(rowWeights)):
            self.processingWindow.grid_rowconfigure(row, weight=rowWeights[row])
        for col in range(0, 12):
            self.processingWindow.grid_columnconfigure(col, weight=1)

        #Default progress bar info
        self.progress = [0, 100, "Processing: {0}%"]

        #Get the style object for the parent window
        self.styles = Style(self.parent)
        #Create layout for progress bar with a label
        self.styles.layout("ProgressbarLabeled", [("ProgressbarLabeled.trough", {"children": [("ProgressbarLabeled.pbar", {"side": "left", "sticky": "NS"}), ("ProgressbarLabeled.label", {"sticky": ""})], "sticky": "NESW"})])
        #Set the bar colour of the progress bar
        self.styles.configure("ProgressbarLabeled", background="lightgreen", text="Processing: 0%")

        #Create a progress bar
        self.progressBar = Ttk.Progressbar(self.processingWindow, orient="horizontal", mode="determinate", maximum=100.0, style="ProgressbarLabeled")
        self.progressBar.grid(row=1, column=1, columnspan=10, sticky="EW")
        #Add label for user information
        self.processingLabel = tkinter.Label(self.processingWindow, text="Processing event data with setup file. This may take some time depending on the experiment duration.")
        self.processingLabel.grid(row=2, column=1, columnspan=10)
        #Next and back button frame
        self.processingButtonsFrame = tkinter.Frame(self.processingWindow)
        self.processingButtonsFrame.grid(row=5, column=0, columnspan=12, sticky="NESW")
        self.processingBackButton = tkinter.Button(self.processingButtonsFrame, text="Back", font=("", 16), command=self.backPressedProcessing, state="disabled")
        self.processingNextButton = tkinter.Button(self.processingButtonsFrame, text="Next", font=("", 16), command=self.nextPressedProcessing, state="disabled")
        self.processingBackButton.pack(side="left", anchor="s")
        self.processingNextButton.pack(side="right", anchor="s")

        #Setup preview window grid
        rowWeights=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4]
        for row in range(0, len(rowWeights)):
            self.previewWindow.grid_rowconfigure(row, weight=rowWeights[row])
        for col in range(0, 4):
            self.previewWindow.grid_columnconfigure(col, weight=1)

        #Setup header labels
        titles = ["Channel", "Total Tips", "Total Volume (ml)", "Net Volume (ml/gVs)"]
        self.headLabels = []
        for head in range(0, len(titles)):
            l = tkinter.Label(self.previewWindow, text=titles[head], bg="lightblue")
            l.grid(row=0, column=head, sticky="NESW")
            self.headLabels.append(l)
        #Create each label to be used to preview the data and store in 2d array
        self.previewLabels = [[], [], [], []]
        for channel in range(0, 15):
            channelNameLabel = tkinter.Label(self.previewWindow, text="Channel {0}".format(channel + 1), bg="lightgreen")
            channelTipLabel = tkinter.Label(self.previewWindow, text="0")
            channelVolumeLabel = tkinter.Label(self.previewWindow, text="0")
            channelNetVolumeLabel = tkinter.Label(self.previewWindow, text="0")
            channelNameLabel.grid(row=channel + 1, column=0, sticky="NESW")
            channelTipLabel.grid(row=channel + 1, column=1, sticky="NESW")
            channelVolumeLabel.grid(row=channel + 1, column=2, sticky="NESW")
            channelNetVolumeLabel.grid(row=channel + 1, column=3, sticky="NESW")
            self.previewLabels[0].append(channelNameLabel)
            self.previewLabels[1].append(channelTipLabel)
            self.previewLabels[2].append(channelVolumeLabel)
            self.previewLabels[3].append(channelNetVolumeLabel)
        #Next and back buttons
        self.previewButtonsFrame = tkinter.Frame(self.previewWindow)
        self.previewButtonsFrame.grid(row=17, column=0, columnspan=12, sticky="NESW")
        self.previewBackButton = tkinter.Button(self.previewButtonsFrame, text="Back", font=("", 16), command=self.backPressedPreview)
        self.previewNextButton = tkinter.Button(self.previewButtonsFrame, text="Next", font=("", 16), command=self.nextPressedPreview)
        self.previewBackButton.pack(side="left", anchor="s")
        self.previewNextButton.pack(side="right", anchor="s")
        
        #Setup grid for download
        rowWeights = [4, 1, 1, 1, 1, 1, 1, 1, 1, 4]
        for row in range(0, len(rowWeights)):
            self.downloadWindow.grid_rowconfigure(row, weight=rowWeights[row])
        self.downloadWindow.grid_columnconfigure(0, weight=1)
        #Save event log button
        self.eventLogSaveButton = tkinter.Button(self.downloadWindow, text="Save Event Log", command=self.saveEventLog, font=("", 16))
        self.eventLogSaveButton.grid(row=1, column=0)
        #Event log info label
        self.eventLogInfo = tkinter.Label(self.downloadWindow, text="Complete log of every event in order. Contains total volumes and net volumes per gram of volatile solids.\nColumns: Channel Number, Name, Timestamp, Days, Hours, Minutes, Tumbler Volume (ml), Temperature (C), Pressure (hPA),\nCumulative Total Tips, Volume This Tip (STP), Total Volume (STP), Tips This Day, Volume This Day (STP), Tips This Hour, Volume This Hour (STP),\n Cumulative Net Volume Per Gram (ml/g) or (ml/gVS)")
        self.eventLogInfo.grid(row=2, column=0)
        #Save hour log button
        self.hourLogSaveButton = tkinter.Button(self.downloadWindow, text="Save Hour Log", command=self.saveHourLog, font=("", 16))
        self.hourLogSaveButton.grid(row=3, column=0)
        #Hour log info label
        self.hourLogInfo = tkinter.Label(self.downloadWindow, text="Version of the event log grouped by hour.\nColumns: Channel Number, Name, Timestamp, Days, Hours, Minutes, In Service,\nTips This Hour, Volume This Hour at STP (ml), Net Volume This Hour (ml/g), Cumulative Net Vol (ml/g),Cumulative Volume at STP (ml)")
        self.hourLogInfo.grid(row=4, column=0)
        #Save day log button
        self.dayLogSaveButton = tkinter.Button(self.downloadWindow, text="Save Day Log", command=self.saveDayLog, font=("", 16))
        self.dayLogSaveButton.grid(row=5, column=0)
        #Day log info label
        self.dayLogInfo = tkinter.Label(self.downloadWindow, text="Version of the event log grouped by day.\nColumns: Channel Number, Name, Timestamp, Days, Hours, Minutes, In Service,\nTips This Day, Volume This Day at STP (ml), Net Volume This Day (ml/g), Cumulative Net Vol (ml/g), Cumulative Volume at STP (ml)")
        self.dayLogInfo.grid(row=6, column=0)
        #Save continuous log button
        self.continuousLogSaveButton = tkinter.Button(self.downloadWindow, text="Save Continuous Log", command=self.saveContinuousLog, font=("", 16))
        self.continuousLogSaveButton.grid(row=7, column=0)
        #Continuous log info label
        self.eventLogInfo = tkinter.Label(self.downloadWindow, text="Version of the event log with no adjustments for inoculum applied.\nColumns: Channel Number, Name, Timestamp, Days, Hours, Minutes,\nVolume This Tip (STP), Total Volume (STP), Volume This Day (STP), Volume This Hour (STP)")
        self.eventLogInfo.grid(row=8, column=0)
        #Back button frame
        self.downloadButtonsFrame = tkinter.Frame(self.downloadWindow)
        self.downloadButtonsFrame.grid(row=9, column=0, columnspan=12, sticky="NESW")
        self.downloadBackButton = tkinter.Button(self.downloadButtonsFrame, text="Back", font=("", 16), command=self.backPressedDownload)
        self.downloadBackButton.pack(side="left", anchor="s")

        #Currently loaded setup and event data
        self.setupData = None
        self.eventData = None
    
    def pathTo(self, path : str) -> str:
        '''Convert local path to find file'''
        return os.path.join(self.thisPath, path)

    def moveWindows(self, stage : int) -> None:
        '''Switch to the selected window'''
        #Raise the correct window
        if stage == 0:
            self.setupWindow.tkraise()
        if stage == 1:
            self.eventWindow.tkraise()
        if stage == 2:
            self.processingWindow.tkraise()
        if stage == 3:
            self.previewWindow.tkraise()
        if stage == 4:
            self.downloadWindow.tkraise()
        
        #Change the tab colours to reflect current one and which ones have not been reached yet
        self.tabSetupFile.configure(bg=self.onColour)
        if stage > 0:
            self.tabEventFile.configure(bg=self.onColour, relief="raised")
        else:
            self.tabEventFile.configure(bg=self.offColour, relief="sunken")
        if stage > 1:
            self.tabProcessing.configure(bg=self.onColour, relief="raised")
        else:
            self.tabProcessing.configure(bg=self.offColour, relief="sunken")
        if stage > 2:
            self.tabPreview.configure(bg=self.onColour, relief="raised")
        else:
            self.tabPreview.configure(bg=self.offColour, relief="sunken")
        if stage > 3:
            self.tabDownload.configure(bg=self.onColour, relief="raised")
        else:
            self.tabDownload.configure(bg=self.offColour, relief="sunken")
        
        if stage == 0:
            self.tabSetupFile.configure(bg=self.selectedColour)
        elif stage == 1:
            self.tabEventFile.configure(bg=self.selectedColour)
        elif stage == 2:
            self.tabProcessing.configure(bg=self.selectedColour)
        elif stage == 3:
            self.tabPreview.configure(bg=self.selectedColour)
        elif stage == 4:
            self.tabDownload.configure(bg=self.selectedColour)

    def loadSetupFile(self) -> None:
        '''Load a setup file for processing'''
        #If there is not already a file being loaded
        if not self.loading:
            self.loading = True
            #Cannot move forward yet
            self.setupNextButton.configure(state="disabled")
            #Get the path to the file from the user
            filePath = filedialog.askopenfilename(title="Select setup csv file", filetypes=self.fileTypes)
            #Split the file into parts
            pathParts = filePath.split("/")
            fileName = ""
            #If there is a file present
            if filePath != "" and filePath != None and len(pathParts) > 0:
                #Reset the setup data
                self.setupData = None
                #Get the file's name from the end of the path
                fileName = pathParts[-1]
                #Attempt to read the file
                allFileData = readSetup.getFile(filePath)
                if allFileData != [] and len(allFileData) > 0 and len(allFileData[0]) > 0:
                    #If there was data to be read
                    #Format the data into an array
                    self.setupData = readSetup.formatData(allFileData)
                    #Set the text of the label
                    self.setupFileLabel.config(text=fileName + " loaded correctly.", fg=self.green)
                    self.setupNextButton.configure(state="normal")
                else:
                    #Display error
                    self.setupLabel.config(text="File invalid or could not be read.", fg=self.red)
                    self.setupData = None
            else:
                #If cancelled and there was already valid data loaded, allow the user to progress
                if self.setupData != None and len(self.setupData) > 0:
                    self.setupNextButton.configure(state="normal")
            #Not loading a file any more
            self.loading = False
    
    def openSetupFileCreator(self) -> None:
        '''Open the setup file creation window'''
        try:
            #Attempt to raise the window to focus should it exist
            self.setupCreateWindow.lift()
            self.setupCreateWindow.focus()
        except:
            #If unable to do so, create a new setup window
            self.setupCreateWindow = tkinter.Toplevel(self.parent)
            self.setupCreateWindow.transient(self.parent)
            self.setupCreateWindow.geometry("600x610+{0}+{1}".format(int(self.screenCentre[0] - 300), int(self.screenCentre[1] - 305)))
            self.setupCreateWindow.minsize(550, 400)
            self.setupCreateWindow.title("Setup GFM")
            self.setupCreateWindow.grid_rowconfigure(0, weight=1)
            self.setupCreateWindow.grid_columnconfigure(0, weight=1)
            setupGUI.MainWindow(self.setupCreateWindow).grid(row=0, column=0, sticky="NESW")
            self.setupCreateWindow.focus()
    
    def closeSetupFileCreator(self) -> None:
        '''Close the extra setup window, should it exist'''
        try:
            #Attempt to close
            self.setupCreateWindow.destroy()
            self.setupCreateWindow.update()
        except:
            #The window did not exist
            pass
        #Reset object
        self.setupCreateWindow = None

    def nextPressedSetup(self) -> None:
        '''Move to next screen from setup if possible'''
        #Close extra window
        self.closeSetupFileCreator()
        #If the setup data has been loaded
        if self.setupData != None and len(self.setupData) > 0:
            #Move to event window
            self.moveWindows(1)

    def loadEventFile(self) -> None:
        '''Load an event log file'''
        #If not currently processing data
        if not self.loading:
            self.loading = True
            self.eventNextButton.config(state="disabled")
            #Get the path to the file from the user
            filePath = filedialog.askopenfilename(title="Select event log csv file", filetypes=self.fileTypes)
            #Split the file into parts
            pathParts = filePath.split("/")
            fileName = ""
            #If there i sa file present
            if filePath != "" and filePath != None and len(pathParts) > 0:
                #Reset the event data
                self.eventData = None
                #Get the file's name from the end of the path
                fileName = pathParts[-1]
                #Attempt to read the file data
                allFileData = readSetup.getFile(filePath)
                #If there was data present
                if allFileData != []:
                    #Format the data as an array and store it
                    self.eventData = readSetup.formatData(allFileData)
                    #Set the text of the display label
                    self.eventFileLabel.config(text=fileName + " loaded correctly.", fg=self.green)
                    self.eventNextButton.config(state="normal")
                else:
                    #Display an error message
                    self.eventFileLabel.config(text="Invalid file or could not be read.", fg=self.red)
                    self.eventData = None
            else:
                #If canceled and valid data was already loaded, allow the user to progress
                if self.eventData != None and len(self.eventData) > 0:
                    self.eventNextButton.configure(state="normal")
        self.loading = False

    def nextPressedEvent(self) -> None:
        '''Move to the next screen from event'''
        #If valid data was loaded
        if self.setupData != None and len(self.setupData) > 0 and self.eventData != None and len(self.eventData) > 0:
            #Setup progress bar, so it looks correct when window changes
            self.styles.configure("ProgressbarLabeled", text="Processing: 0%", background="lightgreen")
            #Do not allow user to move
            self.processingNextButton.configure(state="disabled")
            self.processingBackButton.configure(state="disabled")
            self.progressBar["value"] = 0
            #Reset progress values
            self.progress = [0, len(self.eventData), "Processing: {0}%"]
            #Move to the processing window
            self.moveWindows(2)
            #Wait a moment to start the data processing, this allows the window to change before anything else needs to happen
            self.after(250, self.startProcessing)

    def backPressedEvent(self) -> None:
        '''Move back to the setup screen from the event screen'''
        self.moveWindows(0)
    
    def updateProgressBar(self) -> None:
        '''Update the progress bar's value and text'''
        #Get the initial values
        value = self.progress[0]
        limit = self.progress[1]
        #Set bar states
        self.progressBar["value"] = value
        self.styles.configure("ProgressbarLabeled", text=self.progress[2].format(int((value/limit) * 100)))

        changing = False
        #Repeat until processing ends
        while self.processing:
            #If the limit has been changed
            if limit != self.progress[1]:
                #Store new limit
                limit = self.progress[1]
                changing = True
            #If the value has changed or the limit has
            if self.progress[0] != value or changing:
                #Get the updated value
                value = self.progress[0]
                #Convert to percentage
                percent = int((value/limit) * 100)
                #Change bar text and value
                self.progressBar["value"] = percent
                self.styles.configure("ProgressbarLabeled", text=self.progress[2].format(percent))
                changing = False
    
    def startProcessing(self) -> None:
        '''Begin the threads that perform the calculations and update the progress'''
        #If not already started
        if not self.processing:
            #Set the values of the bar to defaults
            self.progressBar["value"] = 0
            self.progress = [0, len(self.eventData), "Processing: {0}%"]
            self.processing = True
            #Thread to handle the actual data processing and storage
            processThread = Thread(target=self.processInformation, daemon=True)
            processThread.start()
            #Thread to handle the progress bar being changed
            progressThread = Thread(target=self.updateProgressBar, daemon=True)
            progressThread.start()

    def processInformation(self) -> None:
        '''Perform a data processing pass'''
        #If there is data to be processed
        if self.setupData != None and self.eventData != None:
            #Call for the calculations and receive the results and any errors   
            error, events, hours, days, setup = newCalculations.performGeneralCalculations(self.setupData, self.eventData, self.progress)
            #If there are no errors
            if error == None:

                #Lists of each of the data arrays for hours
                hourDataList = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]

                #Iterate through the lists of hour data
                for hour in range(1, len(hours)):
                    #Get the data for this hour
                    thisHourData = [str(int(hours[hour][4]) + (int(hours[hour][3]) * 24)), hours[hour][8], hours[hour][11], hours[hour][10]]
                    hourDataList[int(hours[hour][0]) - 1].append(thisHourData)
                
                #Lists for each of the channels for day data
                dayDataList = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]

                #Iterate through lists of day data
                for day in range(1, len(days)):
                    #Get the data for this day
                    thisDayData = [days[day][3], days[day][8], days[day][11], days[day][10]]
                    dayDataList[int(days[day][0]) - 1].append(thisDayData)
                
                #Store each of the logs
                self.eventLog = events
                self.hourLog = hours
                self.dayLog = days
                self.continuousLog = []

                #Change progress mode to data preparation - the bar will change to reflect this
                self.progress[0] = 0
                self.progress[1] = 30 + len(events)
                self.progress[2] = "Preparing Data: {0}%"

                #Values stored to be displayed in the preview
                maxTips = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                maxVolumes = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                finalNetVolume = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                channelNames = []
                #Go through the setup data
                for i in range(1, 16):
                    try:
                        #Store channel name if possible
                        channelNames.append(setup[0][i - 1])
                    except:
                        #Default to numbered channel
                        channelNames.append("Channel {0}".format(i))
                    #Increment progress counter
                    self.progress[0] = self.progress[0] + 1

                #Iterate through events
                for e in self.eventLog:
                    record = []
                    #Get setup data, time stamp and stp volumes
                    for i in [0, 1, 2, 3, 4, 5, 10, 11, 13, 15]:
                        #Add to the row
                        record.append(e[i])
                    #Add the row to the array
                    self.continuousLog.append(record)
                    #If possible get the channel number and store the tips, volume at stp and net volume from this entry
                    try:
                        channel = int(e[0]) - 1
                        try:
                            maxTips[channel] = int(e[9])
                        except:
                            pass
                        try:
                            maxVolumes[channel] = round(float(e[11]), 2)
                        except:
                            pass
                        try:
                            finalNetVolume[channel] = round(float(e[16]), 2)
                        except:
                            pass
                    except:
                        pass
                    
                    #Increment progress on this step
                    self.progress[0] = self.progress[0] + 1

                #Iterate through channels and add data to preview array
                for i in range(0, 15):
                    self.previewLabels[0][i].configure(text=channelNames[i])
                    self.previewLabels[1][i].configure(text=maxTips[i])
                    self.previewLabels[2][i].configure(text=maxVolumes[i])
                    self.previewLabels[3][i].configure(text=finalNetVolume[i])
                    self.progress[0] = self.progress[0] + 1
                
                #No longer processing, this is here to stop the bar overwriting the changes afterwards
                self.processing = False

                #Allow user to progress forward
                self.processingNextButton.configure(state="normal")
                #Set bar to complete
                self.styles.configure("ProgressbarLabeled", text="Processing: Complete", background="lightgreen")
                self.progressBar["value"] = 100.0
                
            else:
                #Display the error if it occurred and update the bar to show it failed
                self.styles.configure("ProgressbarLabeled", text="Processing: Failed", background="#DD2222")
                messagebox.showinfo(title="Error", message=error)

        else:
            #Display error that files need to be loaded (should not generally occur but in case)
            self.styles.configure("ProgressbarLabeled", text="Processing: Failed", background="#DD2222", )
            messagebox.showinfo(title="Error", message="Please select a setup and event log file first.")
        
        #No longer processing data, allow user to go back again
        self.processing = False
        self.processingBackButton.configure(state="normal")


    def nextPressedProcessing(self) -> None:
        '''Move to the preview window from the processing window'''
        #Check not still processing and there is data
        if not self.processing:
            if self.eventLog != None and self.hourLog != None and self.dayLog != None and self.continuousLog != None and len(self.eventLog) > 0:
                self.moveWindows(3)

    def backPressedProcessing(self) -> None:
        '''Return to the event window from the processing window'''
        if not self.processing:
            self.moveWindows(1)
    
    def saveEventLog(self) -> None:
        '''Save the event log to a file'''
        self.saveFile(self.eventLog, "Save event log to csv file")

    def saveHourLog(self) -> None:
        '''Save the hour log to a file'''
        self.saveFile(self.hourLog, "Save hour log to csv file")

    def saveDayLog(self) -> None:
        '''Save the day log to a file'''
        self.saveFile(self.dayLog, "Save day log to csv file")
    
    def saveContinuousLog(self) -> None:
        '''Save the continuous log to a file'''
        self.saveFile(self.continuousLog, "Save continuous log to csv file")

    def saveFile(self, data, prompt) -> None:
        '''Save the data given into a user selected file using the given prompt as a title'''
        #If not alrady trying to save a file
        if not self.saving:
            self.saving = True
            #If there was actually some data passed
            if data != None and len(data) > 0:
                #Convert data into a string (using new lines)
                dataToSave = createSetup.convertArrayToString(data)
                #Get the path from the user
                path = filedialog.asksaveasfilename(title=prompt, filetypes=self.fileTypes, defaultextension=self.fileTypes)
                if path != "":
                    #Attempt to save file - store result in success
                    success = createSetup.saveAsFile(path, dataToSave)
                    #If saved successfully
                    if success:
                        #Display message to indicate file has been saved
                        messagebox.showinfo(title="Saved Successfully", message="The file has been successfully saved.")
                    else:
                        #Display message to indicate file was not saved
                        messagebox.showinfo(title="Error", message="File could not be saved, please check location and file name.")
        self.saving = False

    def backPressedDownload(self) -> None:
        '''Return to the preview window from the download window'''
        self.moveWindows(3)

    def backPressedPreview(self) -> None:
        '''Return to the event window from the preview window (skips the processing window)'''
        self.moveWindows(1)
    
    def nextPressedPreview(self) -> None:
        '''Move to the download window from the preview window'''
        self.moveWindows(4)

    def sendNotification(self, title : str, message : str) -> None:
        '''Send user a popup notification with the current title and message'''
        notification = notifypy.Notify()
        notification.title = title
        notification.message = message
        notification.icon = self.pathTo("icon.png")
        notification.send()


#Only run if this is the main module being run
if __name__ == "__main__":
    #Create root window for tkinter
    root = tkinter.Tk()
    #Set the shape of the window
    root.geometry("850x650")
    root.minsize(850, 650)
    #Allow for expanding sizes
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    #Set the title text of the window
    root.title("GFM Data Analysis")
    #Add the editor to the root windows
    window = MainWindow(root)
    window.grid(row = 0, column=0, sticky="NESW")
    ico = Image.open(window.pathTo("icon.png"))
    photo = ImageTk.PhotoImage(ico)
    root.wm_iconphoto(True, photo)
    #Start running the root
    root.mainloop()