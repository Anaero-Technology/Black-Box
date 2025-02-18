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

class MainWindow(tkinter.Frame):
    '''Class to contain all of the menus'''
    def __init__(self, parent, *args, **kwargs) -> None:
        #Setup parent configuration
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        #Grid dimensions for main window
        self.numberRows = 16
        self.numberColumns = 5

        self.loading = False
        self.processing = False
        self.saving = False

        for row in range(0, self.numberRows):
            self.grid_rowconfigure(row, weight=1)
        for col in range(0, self.numberColumns):
            self.grid_columnconfigure(col, weight=1, uniform="cols")

        self.thisPath = os.path.abspath(".")
        try:
            self.thisPath = sys._MEIPASS
        except:
            pass

        self.column, self.decimal = readSeparators.read()

        self.red = "#DD0000"
        self.green = "#00DD00"

        self.eventLog = None
        self.hourLog = None
        self.dayLog = None
        self.continuousLog = None

        self.screenCentre = [self.parent.winfo_screenwidth() / 2, self.parent.winfo_screenheight() / 2]

        #Allowed file types and extensions
        self.fileTypes = [("CSV Files", "*.csv")]

        self.tabSetupFile = tkinter.Label(self, text="Select Setup File", relief="raised")
        self.onColour = self.tabSetupFile.cget("bg")
        self.offColour = "#999999"
        self.tabEventFile = tkinter.Label(self, text="Select Event File", relief="sunken", bg=self.offColour)
        self.tabProcessing = tkinter.Label(self, text="Processing Data...", relief="sunken", bg=self.offColour)
        self.tabPreview = tkinter.Label(self, text="Preview Results", relief="sunken", bg=self.offColour)
        self.tabDownload = tkinter.Label(self, text="Save Results", relief="sunken", bg=self.offColour)

        self.tabSetupFile.grid(row=0, column=0, sticky="NESW")
        self.tabEventFile.grid(row=0, column=1, sticky="NESW")
        self.tabProcessing.grid(row=0, column=2, sticky="NESW")
        self.tabPreview.grid(row=0, column=3, sticky="NESW")
        self.tabDownload.grid(row=0, column=4, sticky="NESW")

        self.viewWindow = tkinter.Frame(self)
        self.viewWindow.grid(row=1, column=0, rowspan=15, columnspan=5, sticky="NESW")

        self.viewWindow.grid_rowconfigure(0, weight=1)
        self.viewWindow.grid_columnconfigure(0, weight=1)

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
    
        
        rowWeights = [4, 2, 1, 1, 2, 1, 4]
        for row in range(0, 7):
            self.setupWindow.grid_rowconfigure(row, weight=rowWeights[row])
        self.setupWindow.grid_columnconfigure(0, weight=1)

        self.loadSetupFileButton = tkinter.Button(self.setupWindow, text="Load Setup File", command=self.loadSetupFile, font=("", 16))
        self.loadSetupFileButton.grid(row=1, column=0)

        self.setupFileLabel = tkinter.Label(self.setupWindow, text="No Setup File Loaded", fg=self.red)
        self.setupFileLabel.grid(row=2, column=0)

        self.createSetupFileButton = tkinter.Button(self.setupWindow, text="Create New Setup File", command=self.openSetupFileCreator, font=("", 16))
        self.createSetupFileButton.grid(row=4, column=0)

        self.createSetupExtraText = tkinter.Label(self.setupWindow, text="Once you have created and saved a setup file you can load it above.")
        self.createSetupExtraText.grid(row=5, column=0)

        self.setupButtonsFrame = tkinter.Frame(self.setupWindow)
        self.setupButtonsFrame.grid(row=6, column=0, sticky="NESW")
        self.setupNextButton = tkinter.Button(self.setupButtonsFrame, text="Next", font=("", 16), command=self.nextPressedSetup, state="disabled")
        self.setupNextButton.pack(side="right", anchor="s")

        self.setupCreateWindow = None

        rowWeights = [4, 2, 1, 4, 4]
        for row in range(0, 5):
            self.eventWindow.grid_rowconfigure(row, weight=rowWeights[row])
        self.eventWindow.grid_columnconfigure(0, weight=1)

        self.loadEventFileButton = tkinter.Button(self.eventWindow, text="Load Event File", command=self.loadEventFile, font=("", 16))
        self.loadEventFileButton.grid(row=1, column=0)

        self.eventFileLabel = tkinter.Label(self.eventWindow, text="No Event File Loaded", fg=self.red)
        self.eventFileLabel.grid(row=2, column=0)

        self.eventButtonsFrame = tkinter.Frame(self.eventWindow)
        self.eventButtonsFrame.grid(row=4, column=0, sticky="NESW")
        self.eventBackButton = tkinter.Button(self.eventButtonsFrame, text="Back", font=("", 16), command=self.backPressedEvent)
        self.eventNextButton = tkinter.Button(self.eventButtonsFrame, text="Next", font=("", 16), command=self.nextPressedEvent, state="disabled")
        self.eventBackButton.pack(side="left", anchor="s")
        self.eventNextButton.pack(side="right", anchor="s")

        rowWeights = [4, 1, 1, 1, 2, 4]
        for row in range(0, len(rowWeights)):
            self.processingWindow.grid_rowconfigure(row, weight=rowWeights[row])
        for col in range(0, 12):
            self.processingWindow.grid_columnconfigure(col, weight=1)

        self.progress = [0, 100, "Processing data..."]
        self.needToUpdateDisplay = False

        #Get the style object for the parent window
        self.styles = Style(self.parent)
        #Create layout for progress bar with a label
        self.styles.layout("ProgressbarLabeled", [("ProgressbarLabeled.trough", {"children": [("ProgressbarLabeled.pbar", {"side": "left", "sticky": "NS"}), ("ProgressbarLabeled.label", {"sticky": ""})], "sticky": "NESW"})])
        #Set the bar colour of the progress bar
        self.styles.configure("ProgressbarLabeled", background="lightgreen", text="Processing: 0%")

        #Create a progress bar
        self.progressBar = Ttk.Progressbar(self.processingWindow, orient="horizontal", mode="determinate", maximum=100.0, style="ProgressbarLabeled")
        self.progressBar.grid(row=1, column=1, columnspan=10, sticky="EW")

        self.processingLabel = tkinter.Label(self.processingWindow, text="Processing event data with setup file. This may take some time depending on the experiment duration.")
        self.processingLabel.grid(row=2, column=1, columnspan=10)

        self.processingButtonsFrame = tkinter.Frame(self.processingWindow)
        self.processingButtonsFrame.grid(row=5, column=0, columnspan=12, sticky="NESW")
        self.processingBackButton = tkinter.Button(self.processingButtonsFrame, text="Back", font=("", 16), command=self.backPressedProcessing, state="disabled")
        self.processingNextButton = tkinter.Button(self.processingButtonsFrame, text="Next", font=("", 16), command=self.nextPressedProcessing, state="disabled")
        self.processingBackButton.pack(side="left", anchor="s")
        self.processingNextButton.pack(side="right", anchor="s")

        rowWeights=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4]
        for row in range(0, len(rowWeights)):
            self.previewWindow.grid_rowconfigure(row, weight=rowWeights[row])
        for col in range(0, 4):
            self.previewWindow.grid_columnconfigure(col, weight=1)

        titles = ["Channel", "Total Tips", "Total Volume (ml)", "Net Volume (ml/gVs)"]
        self.headLabels = []
        for head in range(0, len(titles)):
            l = tkinter.Label(self.previewWindow, text=titles[head], bg="lightblue")
            l.grid(row=0, column=head, sticky="NESW")
            self.headLabels.append(l)
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

        self.previewButtonsFrame = tkinter.Frame(self.previewWindow)
        self.previewButtonsFrame.grid(row=17, column=0, columnspan=12, sticky="NESW")
        self.previewBackButton = tkinter.Button(self.previewButtonsFrame, text="Back", font=("", 16), command=self.backPressedPreview)
        self.previewNextButton = tkinter.Button(self.previewButtonsFrame, text="Next", font=("", 16), command=self.nextPressedPreview)
        self.previewBackButton.pack(side="left", anchor="s")
        self.previewNextButton.pack(side="right", anchor="s")
        
        rowWeights = [4, 1, 1, 1, 1, 1, 1, 1, 1, 4]
        for row in range(0, len(rowWeights)):
            self.downloadWindow.grid_rowconfigure(row, weight=rowWeights[row])
        self.downloadWindow.grid_columnconfigure(0, weight=1)

        self.eventLogSaveButton = tkinter.Button(self.downloadWindow, text="Save Event Log", command=self.saveEventLog, font=("", 16))
        self.eventLogSaveButton.grid(row=1, column=0)

        self.eventLogInfo = tkinter.Label(self.downloadWindow, text="Complete log of every event in order. Contains total volumes and net volumes per gram of volatile solids.")
        self.eventLogInfo.grid(row=2, column=0)

        self.hourLogSaveButton = tkinter.Button(self.downloadWindow, text="Save Hour Log", command=self.saveHourLog, font=("", 16))
        self.hourLogSaveButton.grid(row=3, column=0)

        self.hourLogInfo = tkinter.Label(self.downloadWindow, text="Version of the event log grouped by hour.")
        self.hourLogInfo.grid(row=4, column=0)

        self.dayLogSaveButton = tkinter.Button(self.downloadWindow, text="Save Day Log", command=self.saveDayLog, font=("", 16))
        self.dayLogSaveButton.grid(row=5, column=0)

        self.dayLogInfo = tkinter.Label(self.downloadWindow, text="Version of the event log grouped by day.")
        self.dayLogInfo.grid(row=6, column=0)

        self.continuousLogSaveButton = tkinter.Button(self.downloadWindow, text="Save Continuous Log", command=self.saveContinuousLog, font=("", 16))
        self.continuousLogSaveButton.grid(row=7, column=0)

        self.eventLogInfo = tkinter.Label(self.downloadWindow, text="Version of the event log with no adjustments for inoculum applied.")
        self.eventLogInfo.grid(row=8, column=0)

        self.downloadButtonsFrame = tkinter.Frame(self.downloadWindow)
        self.downloadButtonsFrame.grid(row=9, column=0, columnspan=12, sticky="NESW")
        self.downloadBackButton = tkinter.Button(self.downloadButtonsFrame, text="Back", font=("", 16), command=self.backPressedDownload)
        self.downloadBackButton.pack(side="left", anchor="s")

        #Currently loaded setup and event data
        self.setupData = None
        self.eventData = None
    
    def pathTo(self, path):
        return os.path.join(self.thisPath, path)

    def moveWindows(self, stage : int):
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

    def loadSetupFile(self) -> None:
        '''Load a setup file for processing'''
        if not self.loading:
            self.loading = True
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
                if self.setupData != None and len(self.setupData) > 0:
                    self.setupNextButton.configure(state="normal")
            self.loading = False
    
    def openSetupFileCreator(self) -> None:
        try:
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
        try:
            self.setupCreateWindow.destroy()
            self.setupCreateWindow.update()
        except:
            pass
        self.setupCreateWindow = None

    def nextPressedSetup(self) -> None:
        self.closeSetupFileCreator()
        if self.setupData != None and len(self.setupData) > 0:
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
                if self.eventData != None and len(self.eventData) > 0:
                    self.eventNextButton.configure(state="normal")
        self.loading = False

    def nextPressedEvent(self) -> None:
        if self.setupData != None and len(self.setupData) > 0 and self.eventData != None and len(self.eventData) > 0:
            self.styles.configure("ProgressbarLabeled", text="Processing: 0%", background="lightgreen")
            self.processingNextButton.configure(state="disabled")
            self.processingBackButton.configure(state="disabled")
            self.moveWindows(2)
            self.startProcessing()

    def backPressedEvent(self) -> None:
        self.moveWindows(0)
    
    def updateProgressBar(self) -> None:
        '''Update the progress bar'''
        value = 0
        limit = 100
        message = "Processing: 0%"
        #Repeat until processing ends
        while self.processing:
            #If the maximum value has changed
            if self.progress[1] != limit:
                limit = self.progress[1]
                self.progressBar.configure(maximum=limit)
                self.progressBar["value"] = 0
                value = 0
            #If the value has changed
            if self.progress[0] != value:
                value = self.progress[0]
                self.progressBar["value"] = value
                self.progress[2] = "Processing: {0}%".format(int(value/limit))
            #If the text has changed
            if self.progress[2] != message:
                message = self.progress[2]
                self.styles.configure("ProgressbarLabeled", text=message)
    
    def startProcessing(self) -> None:
        if not self.processing:
            self.progressBar["value"] = 0
            self.progress = [0, 100, "Processing: 0%"]
            self.progressBar.grid()
            self.processing = True
            processThread = Thread(target=self.processInformation, daemon=True)
            processThread.start()
            progressThread = Thread(target=self.updateProgressBar, daemon=True)
            progressThread.start()

    def processInformation(self) -> None:
        '''Perform a data processing pass'''
        #If there is data to be processed
        if self.setupData != None and self.eventData != None:
            #Disable the export buttons until the process is complete
            #self.exportGasButton.configure(state="disabled")
            self.progressBar.configure(maximum=len(self.eventData))
            #Call for the calculations and receive the results and any errors   
            error, events, hours, days, setup = newCalculations.performGeneralCalculations(self.setupData, self.eventData, self.progress)
            #If there are no errors
            if error == None:
                #Iterate through the setup data and labels
                for setupNum in range(0, len(setup[0])):
                    #Message to display - the name of the tube
                    msg = setup[0][setupNum]
                    #Update drop down labels
                    #self.channelLabels[setupNum] = "Channel " + str(setupNum + 1) + " (" + setup[0][setupNum] + ")"
                    #If the tube is in use
                    if setup[1][setupNum]:
                        #IF it is an innoculum only tube
                        if setup[2][setupNum]:
                            #Add the innoculum only message
                            msg = msg + "  (Innoculum Only)"
                        #Add the innoculum mass
                        msg = msg + "  Innoculum:" + str(round(setup[3][setupNum], 3)) + "g"
                        #If this is not innoculum only
                        if not setup[2][setupNum]:
                            #Add the sample mass
                            msg = msg + "  Sample:" + str(round(setup[4][setupNum], 3)) + "g"
                        #Add the tumbler volume
                        msg = msg + "  Volume:" + str(round(setup[5][setupNum], 3)) + "ml"
                    else:
                        #Otherwise add not in use message
                        msg = msg + "  (Not in use)"
                    #Add the text to the label
                    #self.setupTexts.append(msg)

                #Lists of each of the data arrays for hours
                hourDataList = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]

                #Iterate through the lists of hour data
                for hour in range(1, len(hours)):
                    #Get the data for this hour
                    thisHourData = [str(int(hours[hour][4]) + (int(hours[hour][3]) * 24)), hours[hour][8], hours[hour][11], hours[hour][10]]
                    hourDataList[int(hours[hour][0]) - 1].append(thisHourData)

                #Set the display data
                #self.displayData[0] = hourDataList
                
                #Lists for each of the channels for day data
                dayDataList = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]

                #Iterate through lists of day data
                for day in range(1, len(days)):
                    #Get the data for this day
                    thisDayData = [days[day][3], days[day][8], days[day][11], days[day][10]]
                    dayDataList[int(days[day][0]) - 1].append(thisDayData)
                
                #Set the display data
                #self.displayData[1] = dayDataList
                
                #Store each of the logs
                self.eventLog = events
                self.hourLog = hours
                self.dayLog = days
                self.continuousLog = []

                #Iterate through events
                for e in self.eventLog:
                    record = []
                    #Get setup data, time stamp and stp volumes
                    for i in [0, 1, 2, 3, 4, 5, 10, 11, 13, 15]:
                        #Add to the row
                        record.append(e[i])
                    #Add the row to the array
                    self.continuousLog.append(record)

                #An update to the display is needed
                self.needToUpdateDisplay = True

                self.processingNextButton.configure(state="normal")
                self.styles.configure("ProgressbarLabeled", text="Processing: Complete", background="lightgreen")
                
            else:
                #Display the error if it occurred
                self.styles.configure("ProgressbarLabeled", text="Processing: Failed", background="#DD2222")
                messagebox.showinfo(title="Error", message=error)

        else:
            #Display error that files need to be loaded (should not generally occur but in case)
            self.styles.configure("ProgressbarLabeled", text="Processing: Failed", background="#DD2222", )
            messagebox.showinfo(title="Error", message="Please select a setup and event log file first.")
        
        self.processing = False
        self.processingBackButton.configure(state="normal")


    def nextPressedProcessing(self) -> None:
        if not self.processing:
            #Also need to check for valid data...
            self.moveWindows(3)

    def backPressedProcessing(self) -> None:
        if not self.processing:
            self.moveWindows(1)
    
    def saveEventLog(self) -> None:
        self.saveFile(self.eventLog, "Save event log to csv file")

    def saveHourLog(self) -> None:
        self.saveFile(self.hourLog, "Save hour log to csv file")

    def saveDayLog(self) -> None:
        self.saveFile(self.dayLog, "Save day log to csv file")
    
    def saveContinuousLog(self) -> None:
        self.saveFile(self.continuousLog, "Save continuous log to csv file")

    def saveFile(self, data, prompt) -> None:
        if not self.saving:
            self.saving = True
            if data != None and len(data) > 0:
                dataToSave = createSetup.convertArrayToString(data)
                path = filedialog.asksaveasfilename(title="Save hour log to csv file", filetypes=self.fileTypes, defaultextension=self.fileTypes)
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
        self.moveWindows(3)

    def backPressedPreview(self) -> None:
        self.moveWindows(1)
    
    def nextPressedPreview(self) -> None:
        self.moveWindows(4)

    def onFrameConfigure(self, event) -> None:
        '''Event called when canvas frame resized'''
        #Update canvas bounding box
        self.itemCanvas.configure(scrollregion=self.itemCanvas.bbox("all"))

    def frameWidth(self, event) -> None:
        '''Event called when canvas resized'''
        #canvasWidth = event.width
        canvasWidth = self.itemCanvas.winfo_width()
        #Update size of window on canvas
        self.itemCanvas.itemconfig(self.itemCanvasWindow, width=canvasWidth - 1)
    
    def bindMouseWheel(self, event) -> None:
        '''Add mouse wheel binding to canvas'''
        if self.itemCanvas != None:
            self.itemCanvas.bind_all("<MouseWheel>", self.mouseWheelMove)

    def unbindMouseWheel(self, event) -> None:
        '''Remove mouse wheel binding from canvas'''
        if self.itemCanvas != None:
            self.itemCanvas.unbind_all("<MouseWheel>")

    def mouseWheelMove(self, event) -> None:
        '''Change y scroll position when mouse wheel moved'''
        if self.itemCanvas != None:
            self.itemCanvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


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
    root.title("GFM Graph Creator")
    #Add the editor to the root windows
    MainWindow(root).grid(row = 0, column=0, sticky="NESW")
    #Start running the root
    root.mainloop()