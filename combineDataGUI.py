import datetime
from email import message
import tkinter
from tkinter import messagebox, filedialog
from threading import Thread
import readSetup
import createSetup
import readSeparators
import dataCombination
import tkinter.ttk as Ttk
from tkinter.ttk import Style

class MainWindow(tkinter.Frame):
    '''Class for the combine window toplevel'''
    def __init__ (self, parent, *args, **kwargs):
        #Initialise parent class
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        #Grid rows and columns
        self.rowCount = 5
        self.columnCount = 3
        for row in range(0, self.rowCount):
            if row != self.rowCount - 1:
                self.grid_rowconfigure(row, weight = 10)
            else:
                self.grid_rowconfigure(row, weight = 1)
        for col in range(0, self.columnCount):
            self.grid_columnconfigure(col, weight = 1)

        #Not currently processing data
        self.processing = False
        #Not currently adding a file to the list
        self.addingFile = False
        #Valid input file types
        self.fileTypes = [("CSV Files", "*.csv")]
        #Event log data array
        self.eventData = None
        #List of file input data
        self.inputData = []
        #Colours
        self.red = "#DD0000"
        self.green = "#00DD00"
        self.black = "#000000"

        #Data that has been processed and ready to export
        self.dataToExportPhRedox = None
        self.dataToExportGas = None

        #Get delimeters from settings
        self.column, self.decimal = readSeparators.read()

        #File images
        self.presentImage = tkinter.PhotoImage(file="filePresent.png")
        self.notPresentImage = tkinter.PhotoImage(file="fileNotPresent.png")

        #Button to import event log file
        self.eventLogButton = tkinter.Button(self, image=self.notPresentImage, compound="top", text="Event Log File", command=self.askForEventFile)
        self.eventLogButton.grid(row=0, column=0)       

        #List of file input objects
        self.inputBoxes = []

        #Frames to hold process and export buttons
        self.processFrame = tkinter.Frame(self)
        self.processFrame.grid(row=0, column=1, sticky="NESW")
        self.exportFrame = tkinter.Frame(self)
        self.exportFrame.grid(row=0, column=2, sticky="NESW")

        #Setup grid in frames
        for row in range(0, 4):
            self.processFrame.grid_rowconfigure(row, weight=1)
            self.exportFrame.grid_rowconfigure(row, weight=1)
        for column in range(0, 4):
            self.processFrame.grid_columnconfigure(column, weight=1)
            self.exportFrame.grid_columnconfigure(column, weight=1)

        #Add buttons to process and export data
        self.processButton = tkinter.Button(self.processFrame, text="Process", command=self.processPressed, state="disabled")
        self.processButton.grid(row=1, column=1, rowspan=2, columnspan=2, sticky="NESW")
        self.exportPhRedoxButton = tkinter.Button(self.exportFrame, text="Export pH/Redox", command=self.exportPhRedoxPressed, state="disabled")
        self.exportPhRedoxButton.grid(row=1, column=1, columnspan=2, sticky="NESW")
        self.exportGasButton = tkinter.Button(self.exportFrame, text="Export Gas", command=self.exportGasPressed, state="disabled")
        self.exportGasButton.grid(row=2, column=1, columnspan=2, sticky="NESW")

        #Create scroll holding frame
        self.itemFrame = tkinter.Frame(self)
        self.itemFrame.grid(row=1, column=0, rowspan=4, columnspan=3, sticky="NESW")

        #Create canvas and scroll bar
        self.itemCanvas = tkinter.Canvas(self.itemFrame)
        self.itemScroll = tkinter.Scrollbar(self.itemFrame, orient="vertical", command=self.itemCanvas.yview)

        self.itemScroll.pack(side="right", fill="y")
        self.itemCanvas.pack(side="left", expand=True, fill="both")

        #Create frame that holds scrolling contents
        self.internalItemFrame = tkinter.Frame(self.itemCanvas)
        self.internalItemFrame.grid_columnconfigure(0, weight=1)
        self.internalItemFrame.grid_rowconfigure(0, minsize=120)

        #Create frame containing add buttons
        self.addFileFrame = tkinter.Frame(self.internalItemFrame)
        for i in range(0, 6):
            self.addFileFrame.grid_rowconfigure(i, weight=1)
            self.addFileFrame.grid_columnconfigure(i, weight=1)
        #Add buttons to add files
        self.addPhRedoxFileButton = tkinter.Button(self.addFileFrame, text="+ Add pH and Redox File", command=self.addPhRedoxFilePressed, fg=self.green, relief="ridge", bg="#FFFFFF")
        self.addGasFileButton = tkinter.Button(self.addFileFrame, text="+ Add Gas File", command=self.addGasFilePressed, fg=self.green, relief="ridge", bg="#FFFFFF")
        #Add to grid
        self.addPhRedoxFileButton.grid(row=2, column=1, rowspan=2, columnspan=2, sticky="NESW")
        self.addGasFileButton.grid(row=2, column=3, rowspan=2, columnspan=2, sticky="NESW")
        self.addFileFrame.grid(row=0, column=0, sticky="NESW")

        #Create scrolling canvas window
        self.itemCanvasWindow = self.itemCanvas.create_window(0, 0, window=self.internalItemFrame, anchor="nw")

        #Setup the resizing commands on the canvas and frame
        self.internalItemFrame.bind("<Configure>", self.onFrameConfigure)
        self.itemCanvas.bind("<Configure>", self.frameWidth)
        self.frameWidth(None)

        #Update the initial size on the canvas (so it looks correct on first load)
        self.itemCanvas.update_idletasks()

        #Add enter and leave mousewheel binding so it can be scrolled
        self.internalItemFrame.bind("<Enter>", self.bindMouseWheel)
        self.internalItemFrame.bind("<Leave>", self.unbindMouseWheel)
        
        #Setup bounding box and scroll region so the scrolling works correctly
        self.itemCanvas.configure(scrollregion=self.itemCanvas.bbox("all"), yscrollcommand=self.itemScroll.set)
        
        #Get the style object for the parent window
        self.styles = Style(self.parent)
        #Create layout for progress bar with a label
        self.styles.layout("ProgressbarLabeled", [("ProgressbarLabeled.trough", {"children": [("ProgressbarLabeled.pbar", {"side": "left", "sticky": "NS"}), ("ProgressbarLabeled.label", {"sticky": ""})], "sticky": "NESW"})])
        #Set the bar colour of the progress bar
        self.styles.configure("ProgressbarLabeled", background="lightgreen")

        #Create a progress bar
        self.progressBar = Ttk.Progressbar(self, orient="horizontal", mode="determinate", maximum=100.0, style="ProgressbarLabeled")
        #Set the text
        self.styles.configure("ProgressbarLabeled", text = "Processing pH and Redox data...")
        self.progressBar.grid(row=4, column=0, columnspan=4, sticky="NESW")
        self.progressBar.grid_remove()

        #Current values for progress bar - so they can be compared with new values
        self.progressCurrentValue = 0
        self.progressCurrentMax = 100
        self.progressCurrentText = "Processing pH and Redox data..."
        #New values for progress bar - updated so it knows to change the value
        self.newProgressValue = 0
        self.newProgressMax = 100
        self.newProgressText = "Processing pH and Redox data..."
        #If the progress bar is done
        self.progressDone = False
        
        #If the data processing is complete
        self.processingDone = False

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
        
    def addPhRedoxFilePressed(self) -> None:
        '''WHen add pH Redox file is pressed'''
        self.addFilePressed(True)
    
    def addGasFilePressed(self):
        '''When add Gas file is pressed'''
        self.addFilePressed(False)

    def addFilePressed(self, phRedox):
        '''Handles request for a file'''
        #If data is not being processed and a file is not being added
        if not self.processing and not self.addingFile:
            #Prevent extra actions while adding the file
            self.addingFile = True
            #Ask the user for the correct type of file
            if phRedox:
                self.askForPhRedoxFile()
            else:
                self.askForGasFile()
            #Allow other actions again
            self.addingFile = False

    def displayProgressBar(self, maxValue : int) -> None:
        '''Enable the progress bar and configure it'''
        #Set the maximum value
        self.progressBar.configure(maximum=maxValue)
        #Set value to 0
        self.progressBar["value"] = 0
        self.progressCurrentValue = 0
        self.newProgressValue = 0
        #Update maximum value
        self.progressCurrentMax = maxValue
        self.newProgressMax = maxValue
        #Change the text
        self.styles.configure("ProgressbarLabeled", text="Processing pH and Redox data...")
        self.progressCurrentText = "Processing pH and Redox data..."
        self.newProgressText = "Processing pH and Redox data..."
        #Show the bar
        self.progressBar.grid()
        #Create thread to handle the progress bar updates
        progressThread = Thread(target=self.updateProgressBar, daemon=True)
        progressThread.start()
    
    def updateProgressBar(self) -> None:
        '''Upadte the progress bar state'''
        #If it has not finished
        if not self.progressDone:
            #Check for changes to maximum, value and text and change them if needed
            if self.newProgressMax != self.progressCurrentMax:
                self.progressBar.configure(maximum=self.newProgressMax)
                self.progressCurrentMax = self.newProgressMax
            if self.newProgressValue != self.progressCurrentValue:
                self.progressBar["value"] = self.newProgressValue
                self.progressCurrentValue = self.newProgressValue
            if self.newProgressText != self.progressCurrentText:
                self.styles.configure("ProgressBarLabeled", text=self.newProgressText)
                self.progressCurrentText = self.newProgressText
            #Call for a repeat of this check
            self.after(10, self.updateProgressBar)
        else:
            #Disable the progress bar once done
            self.hideProgressBar()

    def hideProgressBar(self):
        '''Hide the progress bar'''
        #Remove from the grid - hides
        self.progressBar.grid_remove()
        #Reset values
        self.progressBar["value"] = 0
        self.styles.configure("ProgressbarLabeled", text="Processing pH and Redox data...")
    
    def askForEventFile(self):
        '''Load an event log file'''
        #If not currently processing data or adding a file
        if not self.processing and not self.addingFile:
            #Get the path to the file from the user
            filePath = filedialog.askopenfilename(title="Select event log csv file", filetypes=self.fileTypes)
            #Split the file into parts
            pathParts = filePath.split("/")
            fileName = ""
            #If there is a file present
            if filePath != "" and len(pathParts) > 0:
                #Reset the setup data
                self.eventData = None
                #Get the file's name from the end of the path
                fileName = pathParts[-1]
                #Attempt to read the file
                allFileData = readSetup.getFile(filePath)
                if allFileData != []:
                    #If there was data to be read
                    fileEventData = readSetup.formatData(allFileData)
                    #Format the data into an array
                    results = self.convertEventData(fileEventData)
                    self.eventData = results
                
                if self.eventData != None:
                    #Set the text of the label
                    self.eventLogButton.config(text=fileName, fg=self.green, image=self.presentImage)
                else:
                    #Display error
                    self.eventLogButton.config(text="Invalid Event File", fg=self.red, image=self.notPresentImage)

            #Perform a check to see if the data can be processed
            self.checkReady()

    def askForPhRedoxFile(self) -> None:
        '''When the add phRedox file button is pressed'''
        self.askForDataFile(True)
    
    def askForGasFile(self) -> None:
        '''When the add gas file button is pressed'''
        self.askForDataFile(False)
    
    def askForDataFile(self, phRedox : bool) -> None:
        '''Load a pH and Redox data file'''
        #If not currently processing data
        if not self.processing:
            resultFileData = None
            #Get the path to the file from the user
            filePath = filedialog.askopenfilename(title="Select pH/redox csv file", filetypes=self.fileTypes)
            #Split the file into parts
            pathParts = filePath.split("/")
            fileName = ""
            #If there is a file present
            if filePath != "" and len(pathParts) > 0:
                #Get the file's name from the end of the path
                fileName = pathParts[-1]
                #Attempt to read the file
                allFileData = readSetup.getFile(filePath)
                if allFileData != []:
                    #If there was data to be read
                    #Format the data into an array
                    fileEventData = readSetup.formatData(allFileData)
                    #If it is a pH and Redox file
                    if phRedox:
                        #Attempt to interpret as pH and Redox data
                        results = self.convertPhRedoxData(fileEventData)
                        resultFileData = results
                    else:
                        #Attempt to interpret as Gas data
                        results = self.convertGasData(fileEventData)
                        resultFileData = results
                
                #If there was valid data
                if resultFileData != None:
                    #Add to data array
                    self.inputData.append(resultFileData)
                    #Set the text of the label
                    self.inputBoxes.append(DataSource(self.internalItemFrame, phRedox, len(self.inputBoxes), fileName, self))
                    #Need to grid it in
                    self.adjustInputGrid()
                else:
                    #Correct error message dependent on expected file type
                    message = "File not correctly formatted for pH and redox data. Please check the file is correct and try again."
                    if not phRedox:
                        message = "File not correctly formatted for gas data. Please check the file is correct and try again."
                    #Display error
                    messagebox.showerror(title="Invalid File", message=message)
            #Perform a check to see if the data can be processed
            self.checkReady()


    def deletePressed(self, index : int) -> None:
        '''Remove the input data at the given index'''
        #If that index is within the held data
        if index < len(self.inputData) and index < len(self.inputBoxes):
            #Delete data from input data list
            del self.inputData[index]
            #Remove the object from the UI
            self.inputBoxes[index].grid_remove()
            #Delete the reference to the object
            del self.inputBoxes[index]
            #Re-grid the inputs so they are correctly displayed
            self.adjustInputGrid()

    def adjustInputGrid(self) -> None:
        '''Re add all the input boxes to the frame'''
        #Remove the add file frame
        self.addFileFrame.grid_remove()
        #Iterate through boxes
        for inputBox in self.inputBoxes:
            #Remove from the grid
            inputBox.grid_remove()
        #Iterate for the input count + 1 (for the add as well)
        for i in range(0, len(self.inputBoxes) + 1):
            #Add a row to hold the input
            self.internalItemFrame.grid_rowconfigure(i, minsize=120)
        #Iterate through the boxes
        for i in range(0, len(self.inputBoxes)):
            #Add the input back to the grid
            self.inputBoxes[i].grid(row=i, column=0, sticky="NESW")
            #Update the object's position data
            self.inputBoxes[i].dataPosition = i
        #Add the add file frame back
        self.addFileFrame.grid(row=len(self.inputBoxes), column=0, sticky="NESW")
        #Update the canvas and move the scroll to the bottom
        self.itemCanvas.update_idletasks()
        self.itemCanvas.yview_moveto(1)


    def toUnix(self, timestamp : str) -> int:
        '''Convert the timestamp (yyyy.MM.dd.hh.mm.ss) to the time since the epoch'''
        try:
            #Split into parts
            parts = timestamp.split(self.decimal)
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            hour = int(parts[3])
            minute = int(parts[4])
            second = int(parts[5])
            #Construct datetime from data
            date = datetime.datetime(year, month, day, hour, minute, second)
            #Return the seconds since the unix epoch
            return int(date.timestamp())
        except:
            #If something went wrong give -1 instead
            return -1

    
    def convertEventData(self, data : list) -> list:
        '''Rearrange event log data to just have headers'''
        results = []
        try:
            #Iterate through the events
            for event in data:
                #Get the time
                time = self.toUnix(event[1])
                #If it was an invalid time - stop
                if time == -1:
                    return None
                #Get the channel as an integer
                channel = int(event[3])
                #Get the tip index as an integer
                tipNumber = int(event[0])
                #Add the event to the list of events
                results.append([tipNumber, time, channel])
            
            #Return the collected data
            return results
        except:
            return None
    
    def convertPhRedoxData(self, data : list) -> list:
        '''Convert phRedox file array into formatted data'''
        results = [[], [[], [], [], []], [[], [], [], []]]

        try:
            #Iterate throw rows of the data
            for rowNumber in range(1, len(data)):
                dataRow = data[rowNumber]
                #Get the date and time
                date = dataRow[0]
                time = dataRow[1]
                #date = date.split("-")
                date = date.split("/")
                time = time.split(":")
                #Convert to unix time
                timestamp = date[2] + self.decimal + date[1] + self.decimal + date[0] + self.decimal + time[0] + self.decimal + time[1] + self.decimal + time[2]
                dataTime = self.toUnix(timestamp)
                #Stop if data not formatted correctly
                if dataTime == -1:
                    return None

                ph = []
                #Populate list of pH values
                ph.append(float(dataRow[2]))
                ph.append(float(dataRow[3]))
                ph.append(float(dataRow[4]))
                ph.append(float(dataRow[5]))
                redox = []
                #Populate list of Redox values
                redox.append(float(dataRow[6]))
                redox.append(float(dataRow[7]))
                redox.append(float(dataRow[8]))
                redox.append(float(dataRow[9]))

                #Add the time
                results[0].append(dataTime)
                #Add values from pH and Redox data to results list
                for i in range(0, 4):
                    results[1][i].append(ph[i])
                    results[2][i].append(redox[i])
            
            #Return the complete data
            return results
        except:
            #If something went wrong - return nothing
            return None

    def convertGasData(self, data : list) -> list:
        '''Convert gas data file list to arranged data'''
        #Input format: [[Channel (ReactorN), date, time, CO2 val, CH4 val, CO2 percent, CH4 percent], ...]
        movedData = []
        for row in data:
            movedRow = [row[1], row[2], 0, row[5], row[6]]
            try:
                channelText = row[0]
                channelText = channelText.replace("Reactor", "")
                channelNum = int(channelText)
                movedRow[2] = channelNum
            except:
                pass

            if movedRow[2] != 0:
                movedData.append(movedRow)
        
        #Moved Data format: [[date, time, channel, CO2, CH4], ...]

        results = [[], [], [], []]
        try:
            #Iterate through the rows
            for row in movedData:
                #Get the date and time
                date = row[0]
                time = row[1]
                date = date.split("-")
                time = time.split(":")
                #Convert to unix time
                timestamp = date[0] + self.decimal + date[1] + self.decimal + date[2] + self.decimal + time[0] + self.decimal + time[1] + self.decimal + time[2]
                dataTime = self.toUnix(timestamp)

                #If the time is not formatted correctly then stop
                if dataTime == -1:
                    return None

                #Get the values for the channel, co2 and ch4
                channel = int(row[2])
                co2 = float(row[3])
                ch4 = float(row[4])

                #Add data to results
                results[0].append(dataTime)
                results[1].append(channel)
                results[2].append(co2)
                results[3].append(ch4)
            
            #Return the arranged data
            return results
        except:
            #If something went wrong - return nothing
            return None
    
    def createAssociation(self) -> dict:
        '''Create pH/Redox and Gas channel association dictionaries'''
        phRedoxAssoc = {}
        gasAssoc = {}

        #Iterate through input objects
        for dataNumber in range(0, len(self.inputData)):
            #Check if this is ph/redox data or not
            isPhRedox = self.inputBoxes[dataNumber].phRedox
            #pH Redox: [[ph1, ph2, ph3, ph4], [redox1, redox2, redox3, redox4]]
            #Gas: [gas1, gas2, gas3 ... gas15]
            inputSpins = self.inputBoxes[dataNumber].inputValues
            if isPhRedox:
                #pH and Redox data
                #Iterate for four rows each
                for index in range(0, 4):
                    #Get the value given for ph and redox
                    phChannelGiven = inputSpins[0][index].get()
                    redoxChannelGiven = inputSpins[1][index].get()
                    #If the channel linked has not been linked yet
                    if phChannelGiven not in phRedoxAssoc:
                        #Add ph link
                        phRedoxAssoc[phChannelGiven] = [[dataNumber, index], [-1, -1]]
                    else:
                        #If the ph value has not been set yet
                        if phRedoxAssoc[phChannelGiven][0][0] == -1:
                            #Set the ph link
                            phRedoxAssoc[phChannelGiven][0] = [dataNumber, index]
                    #If the channel linked has not been linked yet
                    if redoxChannelGiven not in phRedoxAssoc:
                        #Add redox link
                        phRedoxAssoc[redoxChannelGiven] = [[-1, -1], [dataNumber, index]]
                    else:
                        #If the redox value has not been set
                        if phRedoxAssoc[redoxChannelGiven][1][0] == -1:
                            #Set the redox link
                            phRedoxAssoc[redoxChannelGiven][1] = [dataNumber, index]
            else:
                #Gas data
                #Iterate through the channels
                for index in range(0, 16):
                    #Get which channel has been set
                    channelGiven = inputSpins[index].get()
                    #If that channel has not been linked already
                    if channelGiven not in gasAssoc:
                        #Set the gas link for that channel
                        gasAssoc[channelGiven] = [dataNumber, index]
        
        #Return the associations
        return phRedoxAssoc, gasAssoc

    def checkReady(self) -> None:
        '''Test if ready to process data and enable process button if needed'''
        ready = True
        #If there is no event data or no input data
        if self.eventData == None or len(self.inputData) < 1:
            #Not ready
            ready = False
        else:
            #Create the associations
            pRassoc, gAssoc = self.createAssociation()
            #If there are no associations
            if len(pRassoc) == 0 and len(gAssoc) == 0:
                #Not ready
                ready = False
        
        #Toggle button state to match ready state
        if ready:
            self.processButton.configure(state="normal")
        else:
            self.processButton.configure(state="disabled")

    def processPressed(self) -> None:
        '''When the process button is pressed'''
        #If not already processing the data and not adding a file
        if not self.processing and not self.addingFile:
            #Processing started
            self.processing = True
            self.processingDone = False
            self.progressDone = False
            #Disable export buttons
            self.exportGasButton.configure(state="disabled")
            self.exportPhRedoxButton.configure(state="disabled")
            #Create linked association for files
            phRedoxAssoc, gasAssoc = self.createAssociation()
            
            #Create a thread to do the processing
            processingThread = Thread(target=self.performCalculations, daemon=True, args=(phRedoxAssoc, gasAssoc))
            #Setup the progress bar
            self.displayProgressBar(len(self.eventData))
            #Start processing
            processingThread.start()
            #Start checks for completed processing
            self.after(100, self.checkDoneProcessing)

    def checkDoneProcessing(self) -> None:
        '''Test if processing is complete'''
        #If finished
        if self.processingDone:
            #Trigger end of processing
            self.processingFinished()
        else:
            #Repeat check
            self.after(100, self.checkDoneProcessing)
    
    def processingFinished(self):
        '''Complete processing and set back to normal state'''
        #Enable export buttons if there is data
        if self.dataToExportPhRedox != None:
            self.exportPhRedoxButton.configure(state="normal")
        if self.dataToExportGas != None:
            self.exportGasButton.configure(state="normal")
        #Finished processing - allow other actions
        self.processing = False
        self.progressDone = True

    def performCalculations(self, phRedoxAssoc : dict, gasAssoc : dict) -> None:
        '''Take the input data and associations to produce output data'''
        #If there are ph/redox associations
        if len(phRedoxAssoc) > 0:
            #Create the results array
            phRedoxResults = dataCombination.mergeDataPhRedox(self.eventData, self.inputData, phRedoxAssoc, self)
            self.dataToExportPhRedox = phRedoxResults
        else:
            self.dataToExportPhRedox = None
        #If there are gas associations
        if len(gasAssoc) > 0:
            #Configure progress bar
            self.newProgressMax = len(self.eventData)
            self.newProgressValue = 0
            self.newProgressText = "Processing Gas data..."
            #Create the results array
            gasResults = dataCombination.mergeDataGas(self.eventData, self.inputData, gasAssoc, self)
            self.dataToExportGas = gasResults
        else:
            self.dataToExportGas = None
        
        #Finished processing
        self.processingDone = True
        self.progressDone = True
            
    def exportPhRedoxPressed(self) -> None:
        '''When the export ph/redox button is pressed'''
        self.exportPressed(True)
    
    def exportGasPressed(self) -> None:
        '''When the export gas button is pressed'''
        self.exportPressed(False)

    def exportPressed(self, phRedox : bool) -> None:
        '''Export the file, either phredox or gas'''
        #If not currently processing or adding a file
        if not self.processing and not self.addingFile:
            data = None
            saveTitle = "Save csv file"
            #Add correct headers and store correct information dependant on export type
            if phRedox:
                data = self.dataToExportPhRedox
                data.insert(0, ["Tip Number", "Time", "Channel", "pH", "Redox"])
                saveTitle = "Save pH and Redox data csv file"
            else:
                data = self.dataToExportGas
                data.insert(0, ["Tip Number", "Time", "Channel", "Carbon Dioxide", "Methane"])
                saveTitle = "Save Gas data csv file"
            
            #If there is data to export
            if data != None:
                #Convert to a string
                dataToSave = createSetup.convertArrayToString(data)
                #Ask the user to give a save location
                path = filedialog.asksaveasfilename(title=saveTitle, filetypes=self.fileTypes, defaultextension=self.fileTypes)
                #Only save the file if a path was selected
                if path != "" and path != None:
                    #Try to save the data (success is a bool storing true if the file saved successfully)
                    success = createSetup.saveAsFile(path, dataToSave)
                    #Display appropriate message for if the file saved or not
                    if success:
                        messagebox.showinfo("Save Successful", "The file was saved successfully.")
                    else:
                        messagebox.showinfo("Save Failed", "The file could not be saved, please check location and file name.")
    

class DataSource(tkinter.Frame):
    '''Class for a frame containing imported data options'''
    def __init__ (self, parent, phRedox : bool, index : int, fileName : str, window : object, *args, **kwargs):
        #Initialise parent class
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        #Store the parent window
        self.window = window
        self.numRows = 1
        self.numColumns = 3

        #Index in data list
        self.dataPosition = index

        #Grid setup
        for row in range(0, self.numRows):
            self.grid_rowconfigure(row, weight=1)
        for col in range(0, self.numColumns):
            self.grid_columnconfigure(col, weight=1)

        #Images for buttons
        self.presentImage = tkinter.PhotoImage(file="filePresent.png")
        self.notPresentImage = tkinter.PhotoImage(file="fileNotPresent.png")
        self.cancelImage = tkinter.PhotoImage(file="cancel.png")

        #Correct message dependant on type
        iconMessage = "Gas Data\n" + fileName
        if phRedox:
            iconMessage = "pH and Redox Data\n" + fileName

        #Create indicator
        self.fileIndicator = tkinter.Button(self, image=self.presentImage, compound="top", text=iconMessage)
        self.fileIndicator.grid(row=0, column=0)

        #Create input area
        self.inputFrame = tkinter.Frame(self)
        self.inputFrame.grid(row=0, column=1, sticky="NESW")

        self.phRedox = phRedox

        self.inputValues = None
        #Create input spinboxes
        if phRedox:
            self.inputValues = self.setupChannelInputPhRedox(self.inputFrame)
        else:
            self.inputValues = self.setupChannelInputGas(self.inputFrame)
        
        #Create delete button
        self.cancelButton = tkinter.Button(self, image=self.cancelImage, command=self.deletePressed)
        self.cancelButton.grid(row=0, column=2)

    def setupChannelInputPhRedox(self, parentFrame : object) -> list:
        rows = 5
        cols = 16
        #Setup grid of parent frame
        for row in range(0, rows):
            parentFrame.grid_rowconfigure(row, weight=1)
        for col in range(0, cols):
            parentFrame.grid_columnconfigure(col, weight=1)
        
        #Create and add labels
        phLabel = tkinter.Label(parentFrame, text="pH")
        phLabel.grid(row=0, column=0, columnspan=8, sticky="NESW")
        redoxLabel = tkinter.Label(parentFrame, text="Redox")
        redoxLabel.grid(row=0, column=8, columnspan=8)

        phSpins = []
        redoxSpins = []

        #Four of each
        for i in range(1, 5):
            #Create variables
            phValue = tkinter.IntVar()
            phValue.set(0)
            redoxValue = tkinter.IntVar()
            redoxValue.set(0)
            #Create spinboxes
            phSpin = tkinter.Spinbox(parentFrame, from_=0, to=15, state="readonly", wrap="true", textvariable=phValue)
            redoxSpin = tkinter.Spinbox(parentFrame, from_=0, to=15, state="readonly", wrap="true", textvariable=redoxValue)

            #Create and add labels
            phInLabel = tkinter.Label(parentFrame, text="pH " + str(i))
            phInLabel.grid(row=i, column=0, columnspan=5, sticky="NESW")
            redoxInLabel = tkinter.Label(parentFrame, text="ORP " + str(i))
            redoxInLabel.grid(row=i, column=8, columnspan=5, sticky="NESW")

            #Add spinboxes to grid
            phSpin.grid(row=i, column=5, columnspan=3, sticky="NESW")
            redoxSpin.grid(row=i, column=13, columnspan=3, sticky="NESW")

            #Add variables to lists to be returned
            phSpins.append(phValue)
            redoxSpins.append(redoxValue)
        
        return [phSpins, redoxSpins]
    
    def setupChannelInputGas(self, parentFrame : object) -> list:
        rows = 9
        cols = 16
        #Setup grid of parent frame
        for row in range(0, rows):
            parentFrame.grid_rowconfigure(row, weight=1)
        for col in range(0, cols):
            parentFrame.grid_columnconfigure(col, weight=1)
        
        #Create and add label
        gasLabel = tkinter.Label(parentFrame, text="Gas")
        gasLabel.grid(row=0, column=0, columnspan=8, sticky="NESW")

        gasSpins = []

        #For each channel
        for i in range(1, 16):
            #Create variable
            gasValue = tkinter.IntVar()
            gasValue.set(i)
            #Create spinbox
            gasSpin = tkinter.Spinbox(parentFrame, from_=0, to=15, state="readonly", wrap="true", textvariable=gasValue)
            #Create label
            gasInLabel = tkinter.Label(parentFrame, text="Gas " + str(i))
            #Select correct position - two rows of eight (last item missing)
            rowNum = i
            colNum = 0
            if i > 8:
                rowNum = i - 8
                colNum = 8

            #Grid label and spin
            gasInLabel.grid(row=rowNum, column=colNum, columnspan=5, sticky="NESW")
            gasSpin.grid(row=rowNum, column=colNum + 5, columnspan=3, sticky="NESW")

            #Add variable to list to be returned
            gasSpins.append(gasValue)
        
        return gasSpins
    
    def deletePressed(self) -> None:
        '''Send remove signal to parent window'''
        self.window.deletePressed(self.dataPosition)


#Only run if this is the main module being run
if __name__ == "__main__":
    #Create root window for tkinter
    root = tkinter.Tk()
    #Calculate the position of the centre of the screen
    screenMiddle = [root.winfo_screenwidth() / 2, root.winfo_screenheight() / 2]
    #Set the shape of the window and place it in the centre of the screen
    root.geometry("700x500+{0}+{1}".format(int(screenMiddle[0] - 350), int(screenMiddle[1] - 250)))
    root.minsize(700, 500)
    #Allow for expanding sizes
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    #Set the title text of the window
    root.title("Combine Data Sets")
    #Add the editor to the root windows
    MainWindow(root).grid(row = 0, column=0, sticky="NESW")
    #Start running the root
    root.mainloop()