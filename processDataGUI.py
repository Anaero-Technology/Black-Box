import tkinter
from tkinter import filedialog
import tkinter.ttk as Ttk
from tkinter.ttk import Style
import readSetup
import createSetup
import overallCalculations
import newCalculations
from tkinter import messagebox
import readSeparators
from threading import Thread


class MainWindow(tkinter.Frame):
    '''Class to contain all of the editor for the csv files'''
    def __init__(self, parent, *args, **kwargs):
        '''Setup the window and initialize all the sections'''
        #Call parent init so it sets up frame correctly
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        #Set the number of rows and columns
        self.numRows = 20
        self.numcolumns = 15
        
        #Create grid from rows and columns
        for row in range(0, self.numRows):
            if row > 4:
                self.grid_rowconfigure(row, weight=3)
            else:
                self.grid_rowconfigure(row, weight=1)
        for col in range(0, self.numcolumns):
            self.grid_columnconfigure(col, weight=1)

        #Create buttons for setup and event log file selects
        self.setupSelectButton = tkinter.Button(self, text="Load Setup", command=self.loadSetup)
        self.setupSelectButton.grid(row=0, column=0, sticky="NESW")
        self.eventSelectButton = tkinter.Button(self, text="Load Events", command=self.loadEvent)
        self.eventSelectButton.grid(row=1, column=0, sticky="NESW")

        #Create labels for loaded setup and event log files
        self.setupLabel = tkinter.Label(self, text="No setup file loaded")
        self.setupLabel.grid(row=0, column=1, columnspan=3, sticky="NESW")
        self.eventLabel = tkinter.Label(self, text="No event file loaded")
        self.eventLabel.grid(row=1, column=1, columnspan=3, sticky="NESW")

        self.column, self.decimal = readSeparators.read()

        #Create process data button - starts disabled (need to have two files loaded)
        self.processButton = tkinter.Button(self, text="Process Data", bg="#DDEEFF", state="disabled", command=self.startProcessing)
        self.processButton.grid(row=0, column=9, rowspan=2, columnspan=3, sticky="NESW")
        
        #Create export data buttons - starts disabled (need to have processed data successfully first)
        self.exportFrame = tkinter.Frame(self)
        self.exportFrame.grid(row=0, column=12, columnspan=3, rowspan=2, sticky="NESW")
        self.exportFrame.grid_rowconfigure(0, weight=1)
        self.exportFrame.grid_rowconfigure(1, weight=1)
        self.exportFrame.grid_columnconfigure(0, weight=1)
        self.exportFrame.grid_columnconfigure(1, weight=1)
        self.exportDataLogButton = tkinter.Button(self.exportFrame, text="Export Data Log", bg="#DDEEFF", state="disabled", command=self.exportEventLog)
        self.exportDataLogButton.grid(row=0, column=0, sticky="NESW")
        self.exportContinuousButton = tkinter.Button(self.exportFrame, text="Export Continuous Log", bg="#DDEEFF", state="disabled", command=self.exportContinuousLog)
        self.exportContinuousButton.grid(row=0, column=1, sticky="NESW")
        self.exportHourButton = tkinter.Button(self.exportFrame, text="Export Hour Log", bg="#DDEEFF", state="disabled", command=self.exportHourLog)
        self.exportDayButton = tkinter.Button(self.exportFrame, text="Export Day Log", bg="#DDEEFF", state="disabled", command=self.exportDayLog)
        self.exportHourButton.grid(row=1, column=0, sticky="NESW")
        self.exportDayButton.grid(row=1, column=1, sticky="NESW")

        #List to contain buttons for the different channels
        self.channelButtons = []

        #Setup the font for the headers
        self.headerFont = ("courier", 10, "bold")

        #Seutp the gas composition export button
        #self.exportGasButton = tkinter.Button(self, text="Export Gas Composition", bg="#DDEEFF", state="disabled", command=self.exportGasLog)
        #self.exportGasButton.grid(row=2, column=11, sticky="NESW")

        #Create the hours and days buttons
        self.hoursButton = tkinter.Button(self, text="Per Hour", relief="ridge", command=self.changeToHours)
        self.hoursButton.grid(row=2, column=13, sticky="NESW")
        self.daysButton = tkinter.Button(self, text="Per Day", relief="ridge", command=self.changeToDays)
        self.daysButton.grid(row=2, column=14, sticky="NESW")

        #Currently viewing the first channel in hours mode
        self.hours = True
        #self.gas = False
        self.currentScreen = 0

        self.channelLabels = []

        #Iterate through each channel
        for channelNum in range(1, 16):
            self.channelLabels.append("Channel " + str(channelNum))

        self.channelChoiceVar = tkinter.StringVar()
        self.channelChoiceVar.set(self.channelLabels[0])
        self.channelChoiceVar.trace("w", self.changeChannel)

        #Create channel drop down
        self.channelChoice = tkinter.OptionMenu(self, self.channelChoiceVar, "Channel 1", "Channel 2", "Channel 3", "Channel 4", "Channel 5", "Channel 6", "Channel 7", "Channel 8", "Channel 9", "Channel 10", "Channel 11", "Channel 12", "Channel 13", "Channel 14", "Channel 15")
        self.channelChoice.grid(row=2, column=0, columnspan=8, sticky="NESW")

        #Create the hour frame
        self.channelHourFrame = tkinter.Frame(self)
        self.channelHourFrame.grid(row=4, column=0, rowspan=16, columnspan=15, sticky="NESW")
        #Create the day frame
        self.channelDayFrame = tkinter.Frame(self)
        self.channelDayFrame.grid(row=4, column=0, rowspan=16, columnspan=15, sticky="NESW")

        #Create and place the setup frame and label
        self.channelSetupFrame = tkinter.Frame(self)
        self.channelSetupLabel = tkinter.Label(self.channelSetupFrame, font=self.headerFont)
        self.channelSetupFrame.grid(row=3, column=0, columnspan=14, sticky="NESW")
        self.channelSetupFrame.grid_rowconfigure(0, weight=1)
        self.channelSetupFrame.grid_columnconfigure(0, weight=1)
        self.channelSetupLabel.grid(row=0, column=0, sticky="NESW")
            
        
        #Get the default button colour and create deselected colour
        self.defaultButtonColour = self.hoursButton.cget("bg")
        self.otherButtonColour = "#BBBBBB"
        self.alternateBackground = "#E0E0E0"

        #Allowed file types and extensions
        self.fileTypes = [("CSV Files", "*.csv")]

        #Colours for use with mesages for indicator colour
        self.red = "#DD0000"
        self.green = "#00DD00"
        self.black = "#000000"

        #Currently loaded setup and event data
        self.setupData = None
        self.eventData = None

        self.eventLog = None
        self.hourLog = None
        self.dayLog = None
        self.gasLog = None

        #Canvases, scrollbars and labels used for each of the displays (None at start as nothing has been processed)
        self.hourCanvas = None
        self.dayCanvas = None
        self.hourScroll = None
        self.dayScroll = None
        self.hourLabels = []
        self.dayLabels = []
        self.setupTexts = []
        self.gridFrameHour = None
        self.gridFrameDay = None

        #Column headers for hours and days
        self.hourHeaders = ["Hour", "Volume(ml)", "Total Evolved(ml)", "Net Evolved(ml/g)"]
        self.dayHeaders = ["Day", "Volume(ml)", "Total Evolved(ml)", "Net Evolved(ml/g)"]

        #Flag to indicate if a data processing pass is currently underway
        self.processing = False

        self.needToUpdateDisplay = False
        
        self.displayData = [[], []]

        #Get the style object for the parent window
        self.styles = Style(self.parent)
        #Create layout for progress bar with a label
        self.styles.layout("ProgressbarLabeled", [("ProgressbarLabeled.trough", {"children": [("ProgressbarLabeled.pbar", {"side": "left", "sticky": "NS"}), ("ProgressbarLabeled.label", {"sticky": ""})], "sticky": "NESW"})])
        #Set the bar colour of the progress bar
        self.styles.configure("ProgressbarLabeled", background="lightgreen")

        #Create a progress bar
        self.progressBar = Ttk.Progressbar(self, orient="horizontal", mode="determinate", maximum=100.0, style="ProgressbarLabeled")
        #Set the text
        self.styles.configure("ProgressbarLabeled", text = "Processing Data ...")
        self.progressBar.grid(row=20, column=0, columnspan=16, sticky="NESW")
        self.progressBar.grid_remove()
        self.progress = [0, 100, "Processing data..."]

        self.populateWindows(48, 2)
        self.unpopulateWindows()

        #Switch to channel 0 and hours mode (to ensure it is all set up correctly at the start)
        self.changeChannel()
        self.changeToHours()


    def changeChannelData(self) -> None:
        '''Populate the grids with the correct information'''
        #Setup information
        if len(self.setupTexts) > self.currentScreen:
            self.channelSetupLabel.config(text=self.setupTexts[self.currentScreen])
        #Add in the hour data
        if len(self.displayData[0]) > self.currentScreen:
            channelHourData = self.displayData[0][self.currentScreen]
            hour = 0
            for thisHourData in channelHourData:
                for index in range(0, 4):
                    self.hourLabels[index][hour].config(text=str(thisHourData[index]))
                hour = hour + 1
        
            #Add in the day data
            channelDayData = self.displayData[1][self.currentScreen]
            day = 0
            for thisDayData in channelDayData:
                for index in range(0, 4):
                    self.dayLabels[index][day].config(text=str(thisDayData[index]))
                day = day + 1


    def changeChannel(self, *args) -> None:
        '''Change the currently selected channel'''
        #Get the channel number from the list
        channelNumber = self.channelLabels.index(self.channelChoiceVar.get())
        #If the channel exists (prevents errors if something went wrong)
        if channelNumber > -1:
            #Change the channel number
            self.currentScreen = channelNumber
            #Raise the correct frame
            self.changeChannelData()
            #Iterate through the channel buttons
            for buttonId in range(0, len(self.channelButtons)):
                #If this is the button associated with the current channel
                if buttonId == channelNumber:
                    #Set it to selected (default) colour
                    self.channelButtons[buttonId].config(bg=self.defaultButtonColour)
                else:
                    #Set it to deselected (darkened) colour
                    self.channelButtons[buttonId].config(bg=self.otherButtonColour)

    
    def changeToHours(self) -> None:
        '''Switch to hours view'''
        self.hours = True
        #Raise the correct frame
        self.channelHourFrame.tkraise()
        #Switch to the hours highlighted colours
        self.hoursButton.config(bg=self.defaultButtonColour)
        self.daysButton.config(bg=self.otherButtonColour)
    
    def changeToDays(self) -> None:
        '''Switch to days view'''
        self.hours = False
        #Raise the correct frame
        self.channelDayFrame.tkraise()
        #Switch to the days highlighted colours
        self.hoursButton.config(bg=self.otherButtonColour)
        self.daysButton.config(bg=self.defaultButtonColour)

    def loadSetup(self) -> None:
        '''Load a setup file'''
        #If not currently processing data
        if not self.processing:
            #Get the path to the file from the user
            filePath = filedialog.askopenfilename(title="Select setup csv file", filetypes=self.fileTypes)
            #Split the file into parts
            pathParts = filePath.split("/")
            fileName = ""
            #If there is a file present
            if filePath != "" and len(pathParts) > 0:
                #Reset the setup data
                self.setupData = None
                #Get the file's name from the end of the path
                fileName = pathParts[-1]
                #Attempt to read the file
                allFileData = readSetup.getFile(filePath)
                if allFileData != []:
                    #If there was data to be read
                    #Format the data into an array
                    self.setupData = readSetup.formatData(allFileData)
                    #Set the text of the label
                    self.setupLabel.config(text=fileName, fg=self.green)
                else:
                    #Display error
                    self.setupLabel.config(text="File could not be read.", fg=self.red)

            #Perform a check to see if the data can be processed
            self.checkReady()


    def loadEvent(self) -> None:
        '''Load an event log file'''
        #If not currently processing data
        if not self.processing:
            #Get the path to the file from the user
            filePath = filedialog.askopenfilename(title="Select event log csv file", filetypes=self.fileTypes)
            #Split the file into parts
            pathParts = filePath.split("/")
            fileName = ""
            #If there i sa file present
            if filePath != "" and len(pathParts) > 0:
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
                    self.eventLabel.config(text=fileName, fg=self.green)
                else:
                    #Display an error message
                    self.eventLabel.config(text="File could not be read.", fg=self.red)
            
            #Perform a check to see if the data can be processed
            self.checkReady()


    def checkReady(self) -> None:
        '''Perform a test to see if there is data to process'''
        #If there is both setup and event log data
        if self.setupData != None and self.eventData != None:
            #Activate process button
            self.processButton.config(state="normal")
        else:
            #Deactivate process button
            self.processButton.config(state="disabled")

    def startProcessing(self) -> None:
        if not self.processing:
            self.progressBar["value"] = 0
            self.progress = [0, 100, "Processing data..."]
            self.progressBar.grid()
            self.processing = True
            processThread = Thread(target=self.processInformation, daemon=True)
            processThread.start()
            progressThread = Thread(target=self.updateProgressBar, daemon=True)
            progressThread.start()
            self.after(100, self.checkDisplay)
    
    def checkDisplay(self) -> None:
        '''Repeatedly check if the display needs to be updated'''
        if self.needToUpdateDisplay:
            #Populate the windows to a correct size
            self.populateWindows(int((len(self.hourLog) - 1) / 15), int(((len(self.dayLog) - 1) / 15)))
            #Update the menu options for the channels
            menu = self.channelChoice["menu"]
            menu.delete(0, tkinter.END)
            for value in self.channelLabels:
                menu.add_command(label=value, command=lambda v=self.channelChoiceVar, l=value: v.set(l))
            
            #Switch to the first channel (this will repopulate the values too)
            self.channelChoiceVar.set(self.channelLabels[0])
            #End processing
            self.processing = False
            self.needToUpdateDisplay = False
            #Hide the progress bar
            self.progressBar.grid_remove()
        else:
            self.after(100, self.checkDisplay)
    
    def updateProgressBar(self) -> None:
        '''Update the progress bar'''
        value = 0
        limit = 100
        message = "Processing data..."
        #Repeat until processing ends
        while self.processing:
            #If the value has changed
            if self.progress[0] != value:
                value = self.progress[0]
                self.progressBar["value"] = value
            #If the maximum value has changed
            if self.progress[1] != limit:
                limit = self.progress[1]
                self.progressBar.configure(maximum=limit)
                self.progressBar["value"] = 0
                value = 0
            #If the text has changed
            if self.progress[2] != message:
                message = self.progress[2]
                self.styles.configure("ProgressbarLabeled", text=message)
    
    def processInformation(self) -> None:
        '''Perform a data processing pass'''
        #If there is data to be processed
        if self.setupData != None and self.eventData != None:
            #Disable the export buttons until the process is complete
            self.exportDataLogButton.configure(state="disabled")
            self.exportContinuousButton.configure(state="disabled")
            self.exportHourButton.configure(state="disabled")
            self.exportDayButton.configure(state="disabled")
            #self.exportGasButton.configure(state="disabled")
            self.progressBar.configure(maximum=len(self.eventData))
            #Call for the calculations and receive the results and any errors
            #error, events, hours, days, gas, setup = overallCalculations.performGeneralCalculations(self.setupData, self.eventData, self.progress)
            #error, events, hours, days, setup = overallCalculations.performGeneralCalculations(self.setupData, self.eventData, self.progress)
            error, events, hours, days, setup = newCalculations.performGeneralCalculations(self.setupData, self.eventData, self.progress)
            #If there are no errors
            if error == None:
                #Iterate through the setup data and labels
                for setupNum in range(0, len(setup[0])):
                    #Message to display - the name of the tube
                    msg = setup[0][setupNum]
                    #Update drop down labels
                    self.channelLabels[setupNum] = "Channel " + str(setupNum + 1) + " (" + setup[0][setupNum] + ")"
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
                    self.setupTexts.append(msg)

                #Lists of each of the data arrays for hours
                hourDataList = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]

                #Iterate through the lists of hour data
                for hour in range(1, len(hours)):
                    #Get the data for this hour
                    thisHourData = [str(int(hours[hour][4]) + (int(hours[hour][3]) * 24)), hours[hour][8], hours[hour][11], hours[hour][10]]
                    hourDataList[int(hours[hour][0]) - 1].append(thisHourData)

                #Set the display data
                self.displayData[0] = hourDataList
                
                #Lists for each of the channels for day data
                dayDataList = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]

                #Iterate through lists of day data
                for day in range(1, len(days)):
                    #Get the data for this day
                    thisDayData = [days[day][3], days[day][8], days[day][11], days[day][10]]
                    dayDataList[int(days[day][0]) - 1].append(thisDayData)
                
                #Set the display data
                self.displayData[1] = dayDataList
                
                #Store each of the logs
                self.eventLog = events
                self.hourLog = hours
                self.dayLog = days
                #self.gasLog = gas
                
                '''anyGas = False
                #Check if there was any gas composition data
                try:
                    rowNumber = 0
                    #Iterate through gas
                    for row in self.gasLog:
                        #If is is not the header
                        if rowNumber != 0:
                            #If there was any data
                            if float(row[6]) >= 0 or float(row[7]) >= 0:
                                #Gas is present
                                anyGas = True
                        #Next row
                        rowNumber = rowNumber + 1
                except:
                    #If the file was not formatted correctly
                    anyGas = False'''
                
                #Allow for the export of the information
                self.exportDataLogButton.configure(state="normal")
                self.exportContinuousButton.configure(state="normal")
                self.exportHourButton.configure(state="normal")
                self.exportDayButton.configure(state="normal")

                '''#Allow for gas export if there was any
                if anyGas:
                    self.exportGasButton.configure(state="normal")'''

                #An update to the display is needed
                self.needToUpdateDisplay = True
                
            else:
                #Display the error if it occurred
                messagebox.showinfo(title="Error", message=error)
                self.processing = False

        else:
            #Display error that files need to be loaded (should not generally occur but in case)
            messagebox.showinfo(title="Error", message="Please select a setup and event log file first.")
    
    
    def exportEventLog(self) -> None:
        '''Export the full event log as a file'''
        if not self.processing:
            if self.eventLog != None:
                dataToSave = createSetup.convertArrayToString(self.eventLog)
                path = filedialog.asksaveasfilename(title="Save event log to csv file", filetypes=self.fileTypes, defaultextension=self.fileTypes)
                #If a path was given (not canceled)
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
        else:
            messagebox.showinfo(title="Please wait", message="Please wait until data processing is complete.")

    def exportContinuousLog(self) -> None:
        '''Export the continuous data as a file'''
        if not self.processing:
            if self.eventLog != None:
                #Array to hold continuous results
                continuousLog = []

                #Iterate through events
                for e in self.eventLog:
                    record = []
                    #Get setup data, time stamp and stp volumes
                    for i in [0, 1, 2, 3, 4, 5, 10, 11, 13, 15]:
                        #Add to the row
                        record.append(e[i])
                    #Add the row to the array
                    continuousLog.append(record)
                
                #Convert data to string
                dataToSave = createSetup.convertArrayToString(continuousLog)
                #Get path to save file
                path = filedialog.asksaveasfilename(title="Save continuous event log to csv file", filetypes=self.fileTypes, defaultextension=self.fileTypes)
                #If a path was given (not canceled)
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
        else:
            messagebox.showinfo(title="Please wait", message="Please wait until data processing is complete.")

    def exportHourLog(self) -> None:
        '''Export the hour log as a file'''
        if not self.processing:
            if self.hourLog != None:
                dataToSave = createSetup.convertArrayToString(self.hourLog)
                path = filedialog.asksaveasfilename(title="Save hour log to csv file", filetypes=self.fileTypes, defaultextension=self.fileTypes)
                #If a path was given (not canceled)
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
        else:
            messagebox.showinfo(title="Please wait", message="Please wait until data processing is complete.")
    
    def exportDayLog(self) -> None:
        '''Export the day log as a file'''
        if not self.processing:
            if self.dayLog != None:
                dataToSave = createSetup.convertArrayToString(self.dayLog)
                path = filedialog.asksaveasfilename(title="Save day log to csv file", filetypes=self.fileTypes, defaultextension=self.fileTypes)
                #If a path was given (not canceled)
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
        else:
            messagebox.showinfo(title="Please wait", message="Please wait until data processing is complete.")
    
    '''def exportGasLog(self) -> None:
        #Export the gas log as a file
        #If not currently processing data
        if not self.processing:
            #If there is gas data
            if self.gasLog != None:

                anyGas = False
                #Attempt (will fail if the file is not formatted correctly)
                try:
                    rowNumber = 0
                    #Iterate through the gas data
                    for row in self.gasLog:
                        #If it is not the header row
                        if rowNumber != 0:
                            #If there is a value that is not negative
                            if float(row[6]) >= 0 or float(row[7]) >= 0:
                                #There is gas data
                                anyGas = True
                        rowNumber = rowNumber + 1
                except:
                    #There is not valid gas data
                    anyGas = False
                
                #If there was a valid file with some data in it
                if anyGas:
                    #Format the data for the file
                    dataToSave = createSetup.convertArrayToString(self.gasLog)
                    #Get the file path
                    path = filedialog.asksaveasfilename(title="Save gas log to csv file", filetypes=self.fileTypes, defaultextension=self.fileTypes)
                    #If a path was given (not canceled)
                    if path != "":
                        #Attempt to save file - store result in success
                        success = createSetup.saveAsFile(path, dataToSave)
                        #If saved successfully
                        if success:
                            #Display message to indicate file has been saved
                            messagebox.showinfo(title="Saved Successfully", message="The file has been successfully saved.")
                        else:
                            #Display message to indicate file was not saved
                            messagebox.showinfo(title="Error", message="File could not be saved, please check location and file name.")'''
                

    def unpopulateWindows(self) -> None:
        '''Remove all canvases and scroll bars and delete all references'''
        #Delete all the created parts
        if self.hourCanvas != None:
            self.hourCanvas.destroy()
        if self.dayCanvas != None:
            self.dayCanvas.destroy()
        if self.hourScroll != None:
            self.hourScroll.destroy()
        if self.dayScroll != None:
            self.dayScroll.destroy()
        
        #Reset canvas, scroll and label objects to remove references to non-existant objects
        self.hourCanvas = None
        self.dayCanvas = None
        self.hourScroll = None
        self.dayScroll = None
        self.hourLabels = []
        self.dayLabels = []


    def populateWindows(self, rowsHours: int, rowsDays: int) -> None:
        #Remove all the current window items
        self.unpopulateWindows()

        #For hours
        #Create canvas
        self.hourCanvas = tkinter.Canvas(self.channelHourFrame)
        #Create scroll bar
        self.hourScroll = tkinter.Scrollbar(self.channelHourFrame, orient="vertical", command=self.hourCanvas.yview)

        #Add canvas and scroll bar to hour frame
        self.hourCanvas.pack(side="left", expand=True, fill="both")
        self.hourScroll.pack(side="right", fill="y")

        #Create a frame to hold the labels in the canvas
        self.gridFrameHour = tkinter.Frame(self.hourCanvas)

        #Iterate through the rows of data and columns and set up grid in frame
        for col in range(0, 4):
            self.gridFrameHour.grid_columnconfigure(col, weight=1)
        for row in range(0, rowsHours + 1):
            self.gridFrameHour.grid_rowconfigure(row, weight=1)

        #List to hold all the labels
        labelsHour = [[], [], [], []]

        self.progress[0] = 0
        self.progress[1] = rowsHours + rowsDays
        self.progress[2] = "Setting up display..."

        #Iterate through the rows
        for row in range(0, rowsHours + 1):
            for col in range(0, 4):
                #Create labels
                label = tkinter.Label(self.gridFrameHour, text="")
                if row % 2 == 0:
                    label.configure(bg=self.alternateBackground)
                label.grid(row=row, column=col, sticky="NESW")
                #If is is not a header
                if row != 0:
                    #Add to list of labels
                    labelsHour[col].append(label)
                else:
                    #Set the text to the header and change the font
                    label.configure(text=self.hourHeaders[col], font=("courier", 10, "bold"))
            
            self.progress[0] = row + 1

        #Add the frame to the window of the canvas
        self.hourCanvasWindow = self.hourCanvas.create_window(0, 0, window=self.gridFrameHour, anchor="nw")

        #Add resize configuration binds
        self.gridFrameHour.bind("<Configure>", self.onFrameConfigureHour)
        self.hourCanvas.bind("<Configure>", self.frameWidthHour)

        #Call for update of canvas (so that size is correct)
        self.hourCanvas.update_idletasks()

        #Manually call for calculation of scroll region based on bounding box
        self.hourCanvas.configure(scrollregion=self.hourCanvas.bbox("all"), yscrollcommand=self.hourScroll.set)

        #Store labels
        self.hourLabels = labelsHour

        #Bind grid to add scroll wheel functionality
        self.gridFrameHour.bind("<Enter>", self.bindMouseWheel)
        self.gridFrameHour.bind("<Leave>", self.unbindMouseWheel)
        
        #For Days
        #Create a canvas
        self.dayCanvas = tkinter.Canvas(self.channelDayFrame)
        #Create a scroll bar
        self.dayScroll = tkinter.Scrollbar(self.channelDayFrame, orient="vertical", command=self.dayCanvas.yview)
        
        #Add the canvas and the scroll bar to the day frame
        self.dayCanvas.pack(side="left", expand=True, fill="both")
        self.dayScroll.pack(side="right", fill="y")

        #Create frame inside canvas for labels
        self.gridFrameDay = tkinter.Frame(self.dayCanvas)

        #Iterate through columns and rows to create grid
        for col in range(0, 4):
            self.gridFrameDay.grid_columnconfigure(col, weight=1)
        for row in range(0, rowsDays + 1):
            self.gridFrameDay.grid_rowconfigure(row, weight=1)

        #List to hold the created labels
        labelsDay = [[], [], [], []]
        
        #Iterate through the rows and columns
        for row in range(0, rowsDays + 1):
            for col in range(0, 4):
                #Create a labels
                label = tkinter.Label(self.gridFrameDay, text="")
                if row % 2 == 0:
                    label.configure(bg=self.alternateBackground)
                label.grid(row=row, column=col, sticky="NESW")
                #If this is not the header row
                if row != 0:
                    #Add the label to the list
                    labelsDay[col].append(label)
                else:
                    #Add the header text to the label and change the font
                    label.configure(text=self.dayHeaders[col], font=self.headerFont)
            
            self.progress[0] = rowsHours + row + 1

        #Add the frame to the window of the canvas
        self.dayCanvasWindow = self.dayCanvas.create_window(0, 0, window=self.gridFrameDay, anchor="nw")

        #Add resize configuration binds
        self.gridFrameDay.bind("<Configure>", self.onFrameConfigureDay)
        self.dayCanvas.bind("<Configure>", self.frameWidthDay)

        #Call for update of canvas - so the size is correct
        self.dayCanvas.update_idletasks()

        #Manually call for the calculation of the scroll area using the bounding area
        self.dayCanvas.configure(scrollregion=self.dayCanvas.bbox("all"), yscrollcommand=self.dayScroll.set)

        #Store labels
        self.dayLabels = labelsDay

        #Bind grid to add scrollwheel functionality
        self.gridFrameDay.bind("<Enter>", self.bindMouseWheel)
        self.gridFrameHour.bind("<Leave>", self.unbindMouseWheel)
    
    def frameWidthHour (self, event) -> None:
        '''Event called when hour canvas resized'''
        canvasWidth = event.width
        #Update size of window on canvas
        self.hourCanvas.itemconfig(self.hourCanvasWindow, width=canvasWidth)

    def onFrameConfigureHour (self, event) -> None:
        '''Event called when hour canvas frame resized'''
        #Update canvas bounding box
        self.hourCanvas.configure(scrollregion=self.hourCanvas.bbox("all"))
    
    def frameWidthDay (self, event) -> None:
        '''Event called when day canvas resized'''
        canvasWidth = event.width
        #Update size of window on canvas
        self.dayCanvas.itemconfig(self.dayCanvasWindow, width=canvasWidth)

    def onFrameConfigureDay (self, event) -> None:
        '''Event called when day canvas frame resized'''
        #Update canvas bounding box
        self.dayCanvas.configure(scrollregion=self.dayCanvas.bbox("all"))

    def bindMouseWheel(self, event) -> None:
        '''Add binding for scrollwheel movement to current canvas'''
        #If hours is the current frame
        if self.hours:
            #If the data has been loaded
            if self.hourCanvas != None:
                #Bind the scrollwheel movement to the hour canvas
                self.hourCanvas.bind_all("<MouseWheel>", self.mouseWheelMove)
        else:
            #If the data has been loaded
            if self.dayCanvas != None:
                #Bind the scrollwheel movement to the day canvas
                self.dayCanvas.bind_all("<MouseWheel>", self.mouseWheelMove)

    def unbindMouseWheel(self, event) -> None:
        '''Remove binding for scrollwheel movement from the current frame'''
        #If hours is the current frame
        if self.hours:
            #If the data has been loaded
            if self.hourCanvas != None:
                #Unbind the scrollwheel movement from the hours frame
                self.hourCanvas.unbind_all("<MouseWheel>")
        else:
            #If the data has been loaded
            if self.dayCanvas != None:
                #Unbind the scrollwheel movement from the days frame
                self.dayCanvas.unbind_all("<MouseWheel>")

    def mouseWheelMove(self, event) -> None:
        '''Change the scroll position of the bound frame when using the scrollwheel'''
        #If it is currently hours
        if self.hours:
            #If data has been loaded
            if self.hourCanvas != None:
                #Update the scroll position of the canvas
                self.hourCanvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            #If the data has been loaded
            if self.dayCanvas != None:
                #Update the scroll position of the canvas
                self.dayCanvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

#Only run if this is the main module being run
if __name__ == "__main__":
    #Create root window for tkinter
    root = tkinter.Tk()
    #Set the shape of the window
    root.geometry("1095x620")
    #Allow for expanding sizes
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    #Set minimum size
    root.minsize(800, 300)
    #Set the title text of the window
    root.title("Process GFM Data")
    #Add the editor to the root windows
    MainWindow(root).grid(row = 0, column=0, sticky="NESW")
    #Start running the root
    root.mainloop()