import tkinter
import tkinter.ttk as Ttk
from tkinter.ttk import Style
from tkinter import filedialog
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
        self.numberColumns = 6

        #Whether files are being loaded, processed or saved so the action cannot be repeated
        self.loading = False
        self.processing = False
        self.saving = False

        self.fonts = {"medium":("", 16), "mediumBold":("", 16), "mediumSmall":("", 14)}

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
        self.black = "#000000"

        #Used to store data once it has been processed
        self.eventLog = None
        self.hourLog = None
        self.dayLog = None
        self.continuousLog = None

        #Middle of the screen so a new window can be opened there
        self.screenCentre = [self.parent.winfo_screenwidth() / 2, self.parent.winfo_screenheight() / 2]

        #Allowed file types and extensions
        self.fileTypes = [("CSV Files", "*.csv")]

        self.usingDilution = False
        self.dilutionType = "none"
        self.volumeConfigOpen = False
        self.hoseLength = [-1.0, -1.0]

        self.gfmInternal = 112.2
        self.reactorTotal = 964.0
        self.hoseVolumePerMeter = 12.56
        self.sampleDensity = 1.028

        self.givenInternalVolumes = [0.0] * 15

        self.crossImage = tkinter.PhotoImage(file=self.pathTo("images/cancel.png"))

        #Create first tab - the one to get the setup file
        self.tabSetupFile = tkinter.Label(self, text="Select Setup File", relief="raised")
        #Store colours for tab backgrounds
        self.onColour = self.tabSetupFile.cget("bg")
        self.offColour = "#999999"
        self.selectedColour = "#6666BB"
        self.tabSetupFile.configure(bg=self.selectedColour)
        #Create all the other tabs
        self.tabEventFile = tkinter.Label(self, text="Select Event File", relief="sunken", bg=self.offColour)
        self.tabGasFiles = tkinter.Label(self, text="Select Gas Files", relief="sunken", bg=self.offColour)
        self.tabProcessing = tkinter.Label(self, text="Processing Data...", relief="sunken", bg=self.offColour)
        self.tabPreview = tkinter.Label(self, text="Preview Results", relief="sunken", bg=self.offColour)
        self.tabDownload = tkinter.Label(self, text="Save Results", relief="sunken", bg=self.offColour)
        #Add tabs to grid
        self.tabSetupFile.grid(row=0, column=0, sticky="NESW")
        self.tabEventFile.grid(row=0, column=1, sticky="NESW")
        self.tabGasFiles.grid(row=0, column=2, sticky="NESW")
        self.tabProcessing.grid(row=0, column=3, sticky="NESW")
        self.tabPreview.grid(row=0, column=4, sticky="NESW")
        self.tabDownload.grid(row=0, column=5, sticky="NESW")

        #Frame used to hold each of the different pages so they are displayed in the same place
        self.viewWindow = tkinter.Frame(self)
        self.viewWindow.grid(row=1, column=0, rowspan=15, columnspan=6, sticky="NESW")

        self.viewWindow.grid_rowconfigure(0, weight=1)
        self.viewWindow.grid_columnconfigure(0, weight=1)

        #Create each window, in reverse order so the setup one appears on top at the end
        self.downloadWindow = tkinter.Frame(self.viewWindow)
        self.downloadWindow.grid(row=0, column=0, sticky="NESW")

        self.previewWindow = tkinter.Frame(self.viewWindow)
        self.previewWindow.grid(row=0, column=0, sticky="NESW")

        self.processingWindow = tkinter.Frame(self.viewWindow)
        self.processingWindow.grid(row=0, column=0, sticky="NESW")

        self.gasWindow = tkinter.Frame(self.viewWindow)
        self.gasWindow.grid(row=0, column=0, sticky="NESW")

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
        self.loadSetupFileButton = tkinter.Button(self.setupWindow, text="Load Setup File", command=self.loadSetupFile, font=self.fonts["medium"])
        self.loadSetupFileButton.grid(row=1, column=0)
        #Information about the loaded file
        self.setupFileLabel = tkinter.Label(self.setupWindow, text="No Setup File Loaded", fg=self.red)
        self.setupFileLabel.grid(row=2, column=0)
        #Button to open window to make new setup file
        self.createSetupFileButton = tkinter.Button(self.setupWindow, text="Create New Setup File", command=self.openSetupFileCreator, font=self.fonts["medium"])
        self.createSetupFileButton.grid(row=4, column=0)
        #Extra information for the user
        self.createSetupExtraText = tkinter.Label(self.setupWindow, text="Once you have created and saved a setup file you can load it above.")
        self.createSetupExtraText.grid(row=5, column=0)
        #Next button frame
        self.setupButtonsFrame = tkinter.Frame(self.setupWindow)
        self.setupButtonsFrame.grid(row=6, column=0, sticky="NESW")
        self.setupNextButton = tkinter.Button(self.setupButtonsFrame, text="Next", font=self.fonts["medium"], command=self.nextPressedSetup, state="disabled")
        self.setupNextButton.pack(side="right", anchor="s")
        #Object to hold the reference to the setup creator window so it can be closed if needed
        self.setupCreateWindow = None

        #Setup internal grid for event window
        rowWeights = [4, 2, 1, 1, 3, 4]
        for row in range(0, 5):
            self.eventWindow.grid_rowconfigure(row, weight=rowWeights[row])
        self.eventWindow.grid_columnconfigure(0, weight=1)

        #Load file button
        self.loadEventFileButton = tkinter.Button(self.eventWindow, text="Load Event File", command=self.loadEventFile, font=self.fonts["medium"])
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
        self.eventBackButton = tkinter.Button(self.eventButtonsFrame, text="Back", font=self.fonts["medium"], command=self.backPressedEvent)
        self.eventNextButton = tkinter.Button(self.eventButtonsFrame, text="Next", font=self.fonts["medium"], command=self.nextPressedEvent, state="disabled")
        self.eventBackButton.pack(side="left", anchor="s")
        self.eventNextButton.pack(side="right", anchor="s")

        #Setup internal grid for gas window        
        for row in range(0, 3):
            self.gasWindow.grid_rowconfigure(row, weight=1)
        self.gasWindow.grid_columnconfigure(0, weight=1)

        #Frame to load the gas file into
        self.gasFileFrame = tkinter.Frame(self.gasWindow)
        self.gasFileFrame.grid(row=0, column=0, sticky="NESW")
        #Frame to setup the dilution
        self.gasDilutionFrame = tkinter.Frame(self.gasWindow)
        self.gasDilutionFrame.grid(row=1, column=0, sticky="NESW")

        #Label for gas file
        self.gasFileTitle = tkinter.Label(self.gasFileFrame, text="Gas Event File", font=self.fonts["mediumBold"])
        self.gasFileTitle.pack(side="top", anchor="center", fill="x", expand=True)
        #Button to load the gas file
        self.loadGasFileButton = tkinter.Button(self.gasFileFrame, text="Load Gas File", command=self.loadGasFile, font=self.fonts["medium"])
        self.loadGasFileButton.pack(side="top", anchor="center", expand=True)
        #File information label
        self.gasFileLabel = tkinter.Label(self.gasFileFrame, text="No Gas File Loaded", fg=self.red)
        self.gasFileLabel.pack(side="top", anchor="center", expand=True)
        #Label for dilution
        self.gasDilutionTitle = tkinter.Label(self.gasDilutionFrame, text="Dilution Adjustment", font=self.fonts["mediumBold"])
        self.gasDilutionTitle.pack(side="top", anchor="center", fill="x", expand=True)
        #Frame to hold different types of dilution controls
        self.dilutionTypeFrame = tkinter.Frame(self.gasDilutionFrame)
        self.dilutionTypeFrame.pack(side="top", anchor="center", fill="x", expand=True, padx=10, pady=2)
        #Buttons for automatic, manual or no dilution
        self.dilutionAutomaticButton = tkinter.Button(self.dilutionTypeFrame, text="Automatic BMP", bg="red", font=self.fonts["medium"], command=self.automaticDilutionPressed, state="disabled")
        self.dilutionAutomaticButton.pack(side="left", expand=True, padx=(150, 0), pady=2)
        self.dilutionManualButton = tkinter.Button(self.dilutionTypeFrame, text="Manual", bg="red", font=self.fonts["medium"], command=self.manualDilutionPressed, state="disabled")
        self.dilutionManualButton.pack(side="left", expand=True, padx=(25, 25), pady=2)
        self.noDilutionButton = tkinter.Button(self.dilutionTypeFrame, text="No Dilutuion", bg="lightgreen", font=self.fonts["medium"], command=self.noDilutionPressed)
        self.noDilutionButton.pack(side="left", expand=True, padx=(0, 150), pady=2)
        #Frame to hold different sections for each type of dilution
        self.dilutionInputFrame = tkinter.Frame(self.gasDilutionFrame)
        self.dilutionInputFrame.pack(side="top", anchor="center", fill="x", expand=True, padx=10, pady=2)
        self.dilutionInputFrame.grid_rowconfigure(0, weight=1)
        self.dilutionInputFrame.grid_columnconfigure(0, weight=1)
        #Frame to hold manual dilution controls
        self.dilutionManualFrame = tkinter.Frame(self.dilutionInputFrame)
        self.dilutionManualFrame.grid(row=0, column=0, sticky="NESW")
        #Label for manual information
        self.manualDilutionLabel = tkinter.Label(self.dilutionManualFrame, text="Using manual internal volumes from setup file.", font=self.fonts["medium"])
        self.manualDilutionLabel.pack(side="top", anchor="center", expand=True, pady=2, padx=10)
        #Frame to hold automatic dilution controls
        self.dilutionAutomaticFrame = tkinter.Frame(self.dilutionInputFrame)
        self.dilutionAutomaticFrame.grid(row=0, column=0, sticky="NESW")
        #Frames to hold the hose length inputs centered
        self.hoseLength1Frame = tkinter.Frame(self.dilutionAutomaticFrame)
        self.hoseLength1Frame.pack(side="top", anchor="center", expand=True, pady=5)
        self.hoseLength2Frame = tkinter.Frame(self.dilutionAutomaticFrame)
        self.hoseLength2Frame.pack(side="top", anchor="center", expand=True, pady=5)
        #Labels and entries to let the user enter the two hose lengths        
        self.hoseLength1Label = tkinter.Label(self.hoseLength1Frame, text="Hose length to flow meter (m):", font=self.fonts["medium"])
        self.hoseLength1Label.pack(side="left")
        self.hoseLength1Entry = tkinter.Entry(self.hoseLength1Frame, width=8, font=self.fonts["medium"], justify="center")
        self.hoseLength1Entry.pack(side="left")
        self.hoseLength2Label = tkinter.Label(self.hoseLength2Frame, text="Hose length to chimera (m):", font=self.fonts["medium"])
        self.hoseLength2Label.pack(side="left")
        self.hoseLength2Entry = tkinter.Entry(self.hoseLength2Frame, width=8, font=self.fonts["medium"], justify="center")
        self.hoseLength2Entry.pack(side="left")
        #Frame for no dilution used
        self.noDilutionFrame = tkinter.Frame(self.dilutionInputFrame)
        self.noDilutionFrame.grid(row=0, column=0, sticky="NESW")
        #Info label for user to indicate which values are being used
        self.noDilutionLabel = tkinter.Label(self.noDilutionFrame, text="Dilution will not be used, only original sensor values will be included.", font=self.fonts["medium"])
        self.noDilutionLabel.pack(side="top", anchor="center", expand=True, fill="x", pady=2, padx=10)
        #Frame and buttons for next and back controls
        self.gasButtonsFrame = tkinter.Frame(self.gasWindow)
        self.gasButtonsFrame.grid(row=2, column=0, sticky="NESW")
        self.gasBackButton = tkinter.Button(self.gasButtonsFrame, text="Back", font=self.fonts["medium"], command=self.backPressedGas)
        self.gasNextButton = tkinter.Button(self.gasButtonsFrame, text="Next", font=self.fonts["medium"], command=self.nextPressedGas)
        self.gasBackButton.pack(side="left", anchor="s")
        self.gasNextButton.pack(side="right", anchor="s")

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
        self.processingBackButton = tkinter.Button(self.processingButtonsFrame, text="Back", font=self.fonts["medium"], command=self.backPressedProcessing, state="disabled")
        self.processingNextButton = tkinter.Button(self.processingButtonsFrame, text="Next", font=self.fonts["medium"], command=self.nextPressedProcessing, state="disabled")
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
        self.previewBackButton = tkinter.Button(self.previewButtonsFrame, text="Back", font=self.fonts["medium"], command=self.backPressedPreview)
        self.previewNextButton = tkinter.Button(self.previewButtonsFrame, text="Next", font=self.fonts["medium"], command=self.nextPressedPreview)
        self.previewBackButton.pack(side="left", anchor="s")
        self.previewNextButton.pack(side="right", anchor="s")
        
        #Setup grid for download
        rowWeights = [4, 1, 1, 1, 1, 1, 1, 1, 1, 4]
        for row in range(0, len(rowWeights)):
            self.downloadWindow.grid_rowconfigure(row, weight=rowWeights[row])
        self.downloadWindow.grid_columnconfigure(0, weight=1)
        #Save event log button
        self.eventLogSaveButton = tkinter.Button(self.downloadWindow, text="Save Event Log", command=self.saveEventLog, font=self.fonts["medium"])
        self.eventLogSaveButton.grid(row=1, column=0)
        #Event log info label
        self.eventLogInfo = tkinter.Label(self.downloadWindow, text="Complete log of every event in order. Contains total volumes and net volumes per gram of volatile solids.\nColumns: Channel Number, Name, Timestamp, Days, Hours, Minutes, Tumbler Volume (ml), Temperature (C), Pressure (hPA),\nCumulative Total Tips, Volume This Tip (STP), Total Volume (STP), Tips This Day, Volume This Day (STP), Tips This Hour, Volume This Hour (STP),\n Cumulative Net Volume Per Gram (ml/g) or (ml/gVS)")
        self.eventLogInfo.grid(row=2, column=0)
        #Save hour log button
        self.hourLogSaveButton = tkinter.Button(self.downloadWindow, text="Save Hour Log", command=self.saveHourLog, font=self.fonts["medium"])
        self.hourLogSaveButton.grid(row=3, column=0)
        #Hour log info label
        self.hourLogInfo = tkinter.Label(self.downloadWindow, text="Version of the event log grouped by hour.\nColumns: Channel Number, Name, Timestamp, Days, Hours, Minutes, In Service,\nTips This Hour, Volume This Hour at STP (ml), Net Volume This Hour (ml/g), Cumulative Net Vol (ml/g),Cumulative Volume at STP (ml)")
        self.hourLogInfo.grid(row=4, column=0)
        #Save day log button
        self.dayLogSaveButton = tkinter.Button(self.downloadWindow, text="Save Day Log", command=self.saveDayLog, font=self.fonts["medium"])
        self.dayLogSaveButton.grid(row=5, column=0)
        #Day log info label
        self.dayLogInfo = tkinter.Label(self.downloadWindow, text="Version of the event log grouped by day.\nColumns: Channel Number, Name, Timestamp, Days, Hours, Minutes, In Service,\nTips This Day, Volume This Day at STP (ml), Net Volume This Day (ml/g), Cumulative Net Vol (ml/g), Cumulative Volume at STP (ml)")
        self.dayLogInfo.grid(row=6, column=0)
        #Save continuous log button
        self.continuousLogSaveButton = tkinter.Button(self.downloadWindow, text="Save Continuous Log", command=self.saveContinuousLog, font=self.fonts["medium"])
        self.continuousLogSaveButton.grid(row=7, column=0)
        #Continuous log info label
        self.eventLogInfo = tkinter.Label(self.downloadWindow, text="Version of the event log with no adjustments for inoculum applied.\nColumns: Channel Number, Name, Timestamp, Days, Hours, Minutes,\nVolume This Tip (STP), Total Volume (STP), Volume This Day (STP), Volume This Hour (STP)")
        self.eventLogInfo.grid(row=8, column=0)
        #Back button frame
        self.downloadButtonsFrame = tkinter.Frame(self.downloadWindow)
        self.downloadButtonsFrame.grid(row=9, column=0, columnspan=12, sticky="NESW")
        self.downloadBackButton = tkinter.Button(self.downloadButtonsFrame, text="Back", font=self.fonts["medium"], command=self.backPressedDownload)
        self.downloadBackButton.pack(side="left", anchor="s")

        #Currently loaded setup and event data
        self.setupData = None
        self.eventData = None
        self.gasData = None
    
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
            self.gasWindow.tkraise()
        if stage == 3:
            self.processingWindow.tkraise()
        if stage == 4:
            self.previewWindow.tkraise()
        if stage == 5:
            self.downloadWindow.tkraise()
        
        #Change the tab colours to reflect current one and which ones have not been reached yet
        self.tabSetupFile.configure(bg=self.onColour)
        if stage > 0:
            self.tabEventFile.configure(bg=self.onColour, relief="raised")
        else:
            self.tabEventFile.configure(bg=self.offColour, relief="sunken")
        if stage > 1:
            self.tabGasFiles.configure(bg=self.onColour, relief="raised")
        else:
            self.tabGasFiles.configure(bg=self.offColour, relief="sunken")
        if stage > 2:
            self.tabProcessing.configure(bg=self.onColour, relief="raised")
        else:
            self.tabProcessing.configure(bg=self.offColour, relief="sunken")
        if stage > 3:
            self.tabPreview.configure(bg=self.onColour, relief="raised")
        else:
            self.tabPreview.configure(bg=self.offColour, relief="sunken")
        if stage > 4:
            self.tabDownload.configure(bg=self.onColour, relief="raised")
        else:
            self.tabDownload.configure(bg=self.offColour, relief="sunken")
        
        if stage == 0:
            self.tabSetupFile.configure(bg=self.selectedColour)
        elif stage == 1:
            self.tabEventFile.configure(bg=self.selectedColour)
        elif stage == 2:
            self.tabGasFiles.configure(bg=self.selectedColour)
        elif stage == 3:
            self.tabProcessing.configure(bg=self.selectedColour)
        elif stage == 4:
            self.tabPreview.configure(bg=self.selectedColour)
        elif stage == 5:
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
                    if len(self.setupData[0]) > 6:
                        self.loadGasFileButton.configure(state="normal")
                        self.gasFileLabel.configure(text="No Gas File Loaded", fg=self.black)
                    else:
                        self.loadGasFileButton.configure(state="disabled")
                        self.gasFileLabel.configure(text="Gas file not available, must be configured in setup file.", fg=self.black)
                    if len(self.setupData[0]) > 7:
                        self.dilutionAutomaticButton.configure(state="normal")
                    else:
                        self.dilutionAutomaticButton.configure(state="disabled")
                    if len(self.setupData[0]) > 10:
                        self.dilutionManualButton.configure(state="normal")
                    else:
                        self.dilutionManualButton.configure(state="disabled")
                else:
                    #Display error
                    self.setupLabel.config(text="File invalid or could not be read.", fg=self.red)
                    self.setupData = None
            else:
                #If cancelled and there was already valid data loaded, allow the user to progress
                if self.setupData != None and len(self.setupData) > 0:
                    self.setupNextButton.configure(state="normal")
            
            self.noDilutionPressed()
            self.gasData = None
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
            self.setupCreateWindow.geometry("900x610+{0}+{1}".format(int(self.screenCentre[0] - 300), int(self.screenCentre[1] - 305)))
            self.setupCreateWindow.minsize(900, 610)
            self.setupCreateWindow.title("Create Setup File")
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
            #Move to the gas window
            self.moveWindows(2)

    def backPressedEvent(self) -> None:
        '''Move back to the setup screen from the event screen'''
        self.moveWindows(0)

    def loadGasFile(self) -> list:
        if not self.loading:
            #Get the path to the file from the user
            filePath = filedialog.askopenfilename(title="Select gas log csv file", filetypes=self.fileTypes)
            #Split the file into parts
            pathParts = filePath.split("/")
            #If there i sa file present
            if filePath != "" and filePath != None and len(pathParts) > 0:
                #Attempt to read the file data
                fileData = readSetup.getFile(filePath)
                fileName = fileName = pathParts[-1]
                #If there was data present
                if fileData != []:
                    #Format the data as an array and store it
                    self.gasData = readSetup.formatData(fileData)
                    self.gasFileLabel.config(text=fileName + " loaded correctly.", fg=self.green)
                else:
                    #Display an error message
                    self.gasFileLabel.config(text="Invalid file or could not be read.", fg=self.red)
                    self.gasData = None
                    
        self.loading = False
    
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
    
    def backPressedGas(self) -> None:
        '''Move back to the event screen from the gas screen'''
        if not self.loading:
            self.moveWindows(1)

    def nextPressedGas(self) -> None:
        '''Check the values in the gas info and progress to the processing screen'''
        #If a file is not being loaded
        if not self.loading:
            #Reset hose lengths
            self.hoseLength = [-1.0, -1.0]
            #If using the automatic values
            if self.dilutionType == "automatic":
                #Attempt to read the values entered as floats - report an error if it failed
                try:
                    self.hoseLength[0] = float(self.hoseLength1Entry.get())
                    self.hoseLength[1] = float(self.hoseLength2Entry.get())
                    #Report error if negative values are entered
                    if self.hoseLength[0] < 0 or self.hoseLength[1] < 0:
                        self.sendNotification("Invalid hose lengths", "Please enter positive hose lengths for automatic dilution calculations")
                except:
                    self.sendNotification("Invalid hose lengths", "Please enter hose lengths for automatic dilution calculations")
            #If there was no gas data or using no or manual dilution or in automatic mode and valid hose lengths have been entered
            if self.gasData == None or (self.dilutionType == "none" or self.dilutionType == "manual" or (self.dilutionType == "automatic" and self.hoseLength[0] >= 0 and self.hoseLength[1] >= 0)):
                #If there is setup and event data
                if self.setupData != None and len(self.setupData) > 0 and self.eventData != None and len(self.eventData) > 0:
                    #Setup progress bar, so it looks correct when window changes
                    self.styles.configure("ProgressbarLabeled", text="Processing: 0%", background="lightgreen")
                    #Do not allow user to move
                    self.processingNextButton.configure(state="disabled")
                    self.processingBackButton.configure(state="disabled")
                    self.progressBar["value"] = 0
                    #Reset progress values
                    self.progress = [0, len(self.eventData), "Processing: {0}%"]
                    self.moveWindows(3)
                    #Wait a moment to start the data processing, this allows the window to change before anything else needs to happen
                    self.after(250, self.startProcessing)

    def automaticDilutionPressed(self) -> None:
        '''Switch to automatic dilution mode'''
        #If a file is not being loaded
        if not self.loading:
            #If this is a change
            if self.dilutionType != "automatic":
                #Change the type, colours of the buttons and raise the correct window
                self.dilutionType = "automatic"
                self.dilutionAutomaticFrame.tkraise()
                self.dilutionManualButton.configure(bg="red")
                self.dilutionAutomaticButton.configure(bg="lightgreen")
                self.noDilutionButton.configure(bg="red")

    def manualDilutionPressed(self) -> None:
        '''Switch to manual dilution mode'''
        #If a file is not being loaded
        if not self.loading:
            #If this is a change
            if self.dilutionType != "manual":
                #Change the type, colours of the buttons and raise the correct window
                self.dilutionType = "manual"
                self.dilutionManualFrame.tkraise()
                self.dilutionManualButton.configure(bg="lightgreen")
                self.dilutionAutomaticButton.configure(bg="red")
                self.noDilutionButton.configure(bg="red")
    
    def noDilutionPressed(self) -> None:
        '''Switch to manual dilution mode'''
        #If a file is nor being loaded
        if not self.loading:
            #If this is a change
            if self.dilutionType != "none":
                #Change the type, colours of the buttons and raise the correct window
                self.dilutionType = "none"
                self.noDilutionFrame.tkraise()
                self.dilutionManualButton.configure(bg="red")
                self.dilutionAutomaticButton.configure(bg="red")
                self.noDilutionButton.configure(bg="lightgreen")
    
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
            gasReady = True
            dilutionReady = True
            #If there is gas data
            if self.gasData != None and len(self.gasData) > 0:
                #If there is enough information in the setup file to process gas
                if len(self.setupData[0]) > 6:
                    #If in manual dilution mode
                    if self.dilutionType == "manual":
                        #Check that there are values for each of the manual volumes
                        try:
                            for index in range(1, 16):
                                test = self.setupData[index][10]
                        except:
                            #Not enough values entered into setup file
                            dilutionReady = False
                    #If in automatic mode
                    elif self.dilutionType == "automatic":
                        #If there are enough values to perform the automatic calculation
                        if len(self.setupData[0]) > 7:
                            #Iterate through channels
                            for index in range(1, 16):
                                #Add any extra values that are needed but not present
                                for i in range(len(self.setupData[index]), 10):
                                    self.setupData[index].append("0.0".replace(".", self.decimal))
                            try:
                                #Calculate the hose volumes from the entered lengths
                                hoseVolume1 = self.hoseVolumePerMeter * self.hoseLength[0]
                                hoseVolume2 = self.hoseVolumePerMeter * self.hoseLength[1]
                                #Iterate reactor channels
                                for i in range(0, 15):
                                    #Calculate the volume of the sample from approximade density
                                    sampleVolume = float(self.setupData[index][7]) / self.sampleDensity
                                    #Find remaining reactor volume
                                    reactorInternal = self.reactorTotal - sampleVolume
                                    #Add reactor and hose volume
                                    self.setupData[i + 1][9] = str(reactorInternal  + hoseVolume1).replace(".", self.decimal)
                                    #Add gfm bucket and hose volume
                                    self.setupData[i + 1][10] = str(self.gfmInternal + hoseVolume2).replace(".", self.decimal)
                            except:
                                #Invalid entry for volumes
                                dilutionReady = False
                        else:
                            #Not enough values in setup file
                            dilutionReady = False
                else:
                    #Not enough information in setup file
                    gasReady = False
            
            #If gas is being used and nothing went wrong with the dilution calculations
            if gasReady:
                if dilutionReady:
                    #Call for the calculations and receive the results and any errors   
                    error, events, hours, days, setup = newCalculations.performGeneralCalculations(self.setupData, self.eventData, self.gasData, self.progress)
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
                        self.styles.configure("ProgressbarLabeled", text="Processing: Failed", background=self.red)
                        self.sendNotification("Error", error)

                else:
                    #Display the error if it occurred and update the bar to show it failed
                    self.styles.configure("ProgressbarLabeled", text="Processing: Failed", background=self.red)
                    self.sendNotification("Error", "Invalid dilution volume, please check all values were entered correctly.")
            else:
                #Display the error if it occurred and update the bar to show it failed
                    self.styles.configure("ProgressbarLabeled", text="Processing: Failed", background=self.red)
                    self.sendNotification("Error", "Invalid gas configuration, please check all setup values were entered correctly.")
        else:
            #Display error that files need to be loaded (should not generally occur but in case)
            self.styles.configure("ProgressbarLabeled", text="Processing: Failed", background=self.red)
            self.sendNotification("Error", "Please select a setup and event log file first.")
        
        #No longer processing data, allow user to go back again
        self.processing = False
        self.processingBackButton.configure(state="normal")


    def nextPressedProcessing(self) -> None:
        '''Move to the preview window from the processing window'''
        #Check not still processing and there is data
        if not self.processing:
            if self.eventLog != None and self.hourLog != None and self.dayLog != None and self.continuousLog != None and len(self.eventLog) > 0:
                self.moveWindows(4)

    def backPressedProcessing(self) -> None:
        '''Return to the event window from the processing window'''
        if not self.processing:
            self.moveWindows(2)
    
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

    def saveFile(self, data : list, prompt : str) -> None:
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
                        self.sendNotification("Saved Successfully", "The file has been successfully saved.")
                    else:
                        #Display message to indicate file was not saved
                        self.sendNotification("Error", "File could not be saved, please check location and file name.")
        self.saving = False

    def backPressedDownload(self) -> None:
        '''Return to the preview window from the download window'''
        self.moveWindows(4)

    def backPressedPreview(self) -> None:
        '''Return to the event window from the preview window (skips the processing window)'''
        self.moveWindows(3)
    
    def nextPressedPreview(self) -> None:
        '''Move to the download window from the preview window'''
        self.moveWindows(5)

    def onGasFrameConfigure(self, _event) -> None:
        '''Event called when gas canvas frame resized'''
        #Update canvas bounding box
        self.gasFilesCanvas.configure(scrollregion=self.gasFilesCanvas.bbox("all"))

    def gasFrameWidth(self, _event) -> None:
        '''Event called when gas canvas resized'''
        canvasWidth = self.gasFilesCanvas.winfo_width()
        #Update size of window on canvas
        self.gasFilesCanvas.itemconfig(self.gasCanvasWindow, width=canvasWidth - 1)

    def gasBindMouseWheel(self, _event) -> None:
        '''Add mouse wheel binding to canvas'''
        if self.gasFilesCanvas != None:
            self.gasFilesCanvas.bind_all("<MouseWheel>", self.gasMouseWheelMove)

    def gasUnbindMouseWheel(self, _event) -> None:
        '''Remove mouse wheel binding from canvas'''
        if self.gasFilesCanvas != None:
            self.gasFilesCanvas.unbind_all("<MouseWheel>")

    def gasMouseWheelMove(self, event) -> None:
        '''Change y scroll position when mouse wheel moved'''
        if self.gasFilesCanvas != None:
            self.gasFilesCanvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def sendNotification(self, title : str, message : str) -> None:
        '''Send user a popup notification with the current title and message'''
        notification = notifypy.Notify()
        notification.title = title
        notification.message = message
        notification.icon = self.pathTo("images/icon.png")
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
    root.title("Analyse Data")
    #Add the editor to the root windows
    window = MainWindow(root)
    window.grid(row = 0, column=0, sticky="NESW")
    ico = Image.open(window.pathTo("images/icon.png"))
    photo = ImageTk.PhotoImage(ico)
    root.wm_iconphoto(True, photo)
    #Start running the root
    root.mainloop()