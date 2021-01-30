import tkinter
from tkinter import filedialog
import readSetup
import createSetup
import overallCalculations
from tkinter import messagebox


class mainWindow(tkinter.Frame):
    '''Class to contain all of the editor for the csv files'''
    def __init__(self, parent, *args, **kwargs):
        '''Setup the window and initialize all the sections'''
        #Call parent init so it sets up frame correctly
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        #Set width and height and number of rows and columns
        self.width = 1095
        self.height = 610
        self.numRows = 20
        self.numcolumns = 15
        
        #Create grid from rows and columns
        for row in range(0, self.numRows):
            self.grid_rowconfigure(row, minsize=self.height / self.numRows)
        for col in range(0, self.numcolumns):
            self.grid_columnconfigure(col, minsize=self.width / self.numcolumns)

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

        #Create process data button - starts disabled (need to have two files loaded)
        self.processButton = tkinter.Button(self, text="Process Data", bg="#DDEEFF", state="disabled", command=self.processInformation)
        self.processButton.grid(row=0, column=9, rowspan=2, columnspan=3, sticky="NESW")
        #Create export data button - starts disabled (need to have processed data successfully first)
        self.exportButton = tkinter.Button(self, text="Export Data", bg="#DDEEFF", state="disabled", command=self.exportInformation)
        self.exportButton.grid(row=0, column=12, rowspan=2, columnspan=3, sticky="NESW")

        #List to contain buttons for the different channels
        self.channelButtons = []

        #Lists to hold the hour and day frames
        self.channelHourFrames = []
        self.channelDayFrames = []
        #Lists to hold the setup information frames and labels
        self.setupFrames = []
        self.setupLabels = []

        #Setup the font for the headers
        self.headerFont = ("courier", 10, "bold")

        #Create the hours and days buttons
        self.hoursButton = tkinter.Button(self, text="Per Hour", relief="ridge", command=self.changeToHours)
        self.hoursButton.grid(row=3, column=0, sticky="NESW")
        self.daysButton = tkinter.Button(self, text="Per Day", relief="ridge", command=self.changeToDays)
        self.daysButton.grid(row=3, column=1, sticky="NESW")

        #Currently viewing the first channel in hours mode
        self.hours = True
        self.currentScreen = 0

        #Iterate through each channel
        for channelNum in range(1, 16):
            #Create button for the channel and assign switch function (with parameter)
            channelButton = tkinter.Button(self, text="Cha " + str(channelNum), relief="ridge", command=lambda num=channelNum - 1: self.changeChannel(num))
            channelButton.grid(row=2, column=channelNum - 1, sticky="NESW")
            #Create the hour frame
            channelHourFrame = tkinter.Frame(self)
            channelHourFrame.grid(row=4, column=0, rowspan=16, columnspan=15, sticky="NESW")
            #Create the day frame
            channelDayFrame = tkinter.Frame(self)
            channelDayFrame.grid(row=4, column=0, rowspan=16, columnspan=15, sticky="NESW")
            #Create and place the setup frame and label
            channelSetupFrame = tkinter.Frame(self)
            channelSetupLabel = tkinter.Label(channelSetupFrame, font=self.headerFont)
            channelSetupFrame.grid(row=3, column=2, columnspan=12, sticky="NESW")
            channelSetupFrame.grid_rowconfigure(0, minsize=self.height/self.numRows)
            channelSetupFrame.grid_columnconfigure(0, minsize=self.width/self.numcolumns*12)
            channelSetupLabel.grid(row=0, column=0, sticky="NESW")
            #Add all components to the lists so they can be manipulated
            self.channelButtons.append(channelButton)
            self.channelHourFrames.append(channelHourFrame)
            self.channelDayFrames.append(channelDayFrame)
            self.setupFrames.append(channelSetupFrame)
            self.setupLabels.append(channelSetupLabel)
        
        #Get the default button colour and create deselected colour
        self.defaultButtonColour = self.channelButtons[0].cget("bg")
        self.otherButtonColour = "#BBBBBB"
        self.alternateBackground = "#E0E0E0"

        #Switch to channel 0 and hours mode (to ensure it is all set up correctly at the start)
        self.changeChannel(0)
        self.changeToHours()

        #Allowed file types and extensions
        self.fileTypes = [("CSV Files", "*.csv")]

        #Colours for use with mesages for indicator colour
        self.red = "#DD0000"
        self.green = "#00DD00"
        self.black = "#000000"

        #Currently loaded setup and event data
        self.setupData = None
        self.eventData = None

        #Canvases, scrollbars and labels used for each of the displays (None at start as nothing has been processed)
        self.hourCanvases = []
        self.dayCanvases = []
        self.hourScrolls = []
        self.dayScrolls = []
        self.hourLabels = []
        self.dayLabels = []

        #Column headers for hours and days
        self.hourHeaders = ["Hour", "Volume(ml)", "Volume From Sample(ml)", "Volume/Gram(ml/g)", "Innoculum Avg(ml/g)", "Total Evolved(ml)"]
        self.dayHeaders = ["Day", "Volume(ml)", "Volume From Sample(ml)", "Volume/Gram(ml/g)", "Innoculum Avg(ml/g)", "Total Evolved(ml)"]

        #Flag to indicate if a data processing pass is currently underway
        self.processing = False

        self.exportData = []


    def raiseCurrentScreen(self) -> None:
        '''Raise the correct frame'''
        if self.hours:
            #Raise the current hours screen
            self.channelHourFrames[self.currentScreen].tkraise()
        else:
            #Raise the correct days screen
            self.channelDayFrames[self.currentScreen].tkraise()


    def changeChannel(self, channelNumber: int) -> None:
        '''Change the currently selected channel'''
        #Change the channel number
        self.currentScreen = channelNumber
        #Raise the correct frame
        self.raiseCurrentScreen()
        #Iterate through the channel buttons
        for buttonId in range(0, len(self.channelButtons)):
            #If this is the button associated with the current channel
            if buttonId == channelNumber:
                #Set it to selected (default) colour
                self.channelButtons[buttonId].config(bg=self.defaultButtonColour)
            else:
                #Set it to deselected (darkened) colour
                self.channelButtons[buttonId].config(bg=self.otherButtonColour)
        
        #If there is a setup frame present
        if self.currentScreen < len(self.setupFrames):
            #Raise the correct setup frame
            self.setupFrames[self.currentScreen].tkraise()

    
    def changeToHours(self) -> None:
        '''Switch to hours view'''
        self.hours = True
        #Raise the correct frame
        self.raiseCurrentScreen()
        #Switch to the hours highlighted colours
        self.hoursButton.config(bg=self.defaultButtonColour)
        self.daysButton.config(bg=self.otherButtonColour)
    
    def changeToDays(self) -> None:
        '''Switch to days view'''
        self.hours = False
        #Raise the correct frame
        self.raiseCurrentScreen()
        #Switch to the days highlighted colours
        self.hoursButton.config(bg=self.otherButtonColour)
        self.daysButton.config(bg=self.defaultButtonColour)


    def loadSetup(self) -> None:
        '''Load a setup file'''
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

    
    def processInformation(self) -> None:
        '''Perform a data processing pass'''
        self.processing = True
        #TODO Add separate thread and block window to prevent 'not responding'
        #If there is data to be processed
        if self.setupData != None and self.eventData != None:
            #Call for the calculations and receive the results and any errors
            results, error = overallCalculations.performGeneralCalculations(self.setupData, self.eventData)
            #If there are no errors
            if error == None:
                #Disable the export button until the process is complete
                self.exportButton.configure(state="disabled")
                #Reset the export data
                self.exportData = []
                #Split the results into parts
                setup = results[0]
                hourLists = results[1]
                hourListsWOI = results[2]
                hourListsWOIGram = results[3]
                dayLists = results[4]
                dayListsWOI = results[5]
                dayListsWOIGram = results[6]
                hourlyInnoculumAvg = results[8]
                daylyInnoculumAvg = results[9]
                #Cumulative totals
                hourEvolved = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                dayEvolved = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                #Populate the windows to a correct size
                self.populateWindows(len(hourLists[0]), len(dayLists[0]))
                #Iterate through the setup data and labels
                for setupNum in range(0, len(setup[0])):
                    #Add the setup information
                    self.exportData.append([[setup[0][setupNum], setup[1][setupNum], setup[2][setupNum], setup[3][setupNum], setup[4][setupNum], setup[5][setupNum]]])
                    if setupNum < len(self.setupLabels):
                        #Message to display - the name of the tube
                        msg = setup[0][setupNum]
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
                        self.setupLabels[setupNum].configure(text=msg)

                #Iterate through the lists of hour data
                for listNum in range(0, len(hourLists)):
                    #List to hold hour data for export
                    hourDataList = []
                    #Iterate through the hours
                    for hour in range(0, len(hourLists[listNum])):
                        #List to hold the current hour's data
                        thisHourData = []
                        #Calculate the cumulative volume evolved
                        hourEvolved[listNum] = hourEvolved[listNum] + hourListsWOI[listNum][hour]
                        #Calculate each of the values
                        thisHourData.append(round(hourLists[listNum][hour], 3)) #Volume
                        thisHourData.append(round(hourListsWOI[listNum][hour], 3)) #Volume - innoculum average
                        thisHourData.append(round(hourListsWOIGram[listNum][hour], 3)) #Volume produced per gram of sample
                        thisHourData.append(round(hourlyInnoculumAvg[hour], 3)) #Innoculum average volume per gram
                        thisHourData.append(round(hourlyInnoculumAvg[hour] * setup[3][listNum], 3)) #Innoculum average volume for this tube
                        thisHourData.append(round(hourEvolved[listNum], 3)) #Total gas evolved by sample in this tube
                        #Set each of the labels of the hour frame
                        self.hourLabels[listNum][0][hour].config(text=str(thisHourData[0]))
                        self.hourLabels[listNum][1][hour].config(text=str(thisHourData[1]))
                        self.hourLabels[listNum][2][hour].config(text=str(thisHourData[2]))
                        #Show innoculum average per gram for that hour and then the actual ml using the mass of innoculum
                        innoculumMessage = str(thisHourData[3]) + " (" + str(thisHourData[4]) + "ml)"
                        self.hourLabels[listNum][3][hour].config(text=innoculumMessage)
                        self.hourLabels[listNum][4][hour].config(text=str(thisHourData[5]))
                        #Add this hour's information to the overall list
                        hourDataList.append(thisHourData)
                    
                    #If there is a channel to add this to
                    if listNum < len(self.exportData):
                        #Store the hour data so it can be exported
                        self.exportData[listNum].append(hourDataList)

                #Iterate through lists of day data
                for listNum in range(0, len(dayLists)):
                    #List to hold day data for export
                    dayDataList = []
                    #Iterate through the days
                    for day in range(0, len(dayLists[listNum])):
                        #List to hold the current day's data
                        thisDayData = []
                        #Calculate the cumulative volume evolved
                        dayEvolved[listNum] = dayEvolved[listNum] + dayListsWOI[listNum][day]
                        #Calculate each of the values
                        thisDayData.append(round(dayLists[listNum][day], 3))
                        thisDayData.append(round(dayListsWOI[listNum][day], 3))
                        thisDayData.append(round(dayListsWOIGram[listNum][day], 3))
                        thisDayData.append(round(daylyInnoculumAvg[day], 3))
                        thisDayData.append(round(daylyInnoculumAvg[day] * setup[3][listNum], 3))
                        thisDayData.append(round(dayEvolved[listNum], 3))
                        #Set each of the labels of the day frame
                        self.dayLabels[listNum][0][day].config(text=str(thisDayData[0]))
                        self.dayLabels[listNum][1][day].config(text=str(thisDayData[1]))
                        self.dayLabels[listNum][2][day].config(text=str(thisDayData[2]))
                        #Show innoculum average per gram for that day and then the actual ml using the mass of innoculum
                        innoculumMessage = str(thisDayData[3]) + " (" + str(thisDayData[4]) + "ml)"
                        self.dayLabels[listNum][3][day].config(text=innoculumMessage)
                        self.dayLabels[listNum][4][day].config(text=str(thisDayData[5]))
                        #Add this day's information to the overall list
                        dayDataList.append(thisDayData)
                    
                    #If there is a channel to add this to
                    if listNum < len(self.exportData):
                        #Store the day data so it can be exported
                        self.exportData[listNum].append(dayDataList)
                
                #Allow for the export of the information
                self.exportButton.configure(state="normal")
            else:
                #Display the error if it occurred
                messagebox.showinfo(title="Error", message=error)

        else:
            #Display error that files need to be loaded (should not generally occur but in case)
            messagebox.showinfo(title="Error", message="Please select a setup and event log file first.")

        self.processing = False

    
    def exportInformation(self) -> None:
        '''Export all the information in the tables as a csv file'''
        #Export only if not currently processing information and there is data to be exported
        if not self.processing and len(self.exportData) > 0:
            #Group data by tube then hour and day
            exportArray = []
            #Iterate through the different channels
            for tube in self.exportData:
                #Add a new row
                exportArray.append([])
                #Iterate through the setup data
                for item in tube[0]:
                    #If it is a boolean
                    if type(item) == bool:
                        #Convert to integer 1 or 0 for true or false
                        if item:
                            item = 1
                        else:
                            item = 0
                    #Add the item to the row
                    exportArray[-1].append(str(item))
                #Add a new row
                exportArray.append([])
                #Iterate through hour headers
                for header in self.hourHeaders:
                    #Add the header to the row
                    exportArray[-1].append(header)
                #Iterate through the hours
                for row in tube[1]:
                    #Add a new row
                    exportArray.append([])
                    #Iterate through the items for this hour
                    for item in row:
                        #Add the item to the row
                        exportArray[-1].append(str(item))
                #Add a new row
                exportArray.append([])
                #Iterate through the day headers
                for header in self.dayHeaders:
                    #Add the header to the row
                    exportArray[-1].append(header)
                #Iterate through the days
                for row in tube[2]:
                    #Add a new row
                    exportArray.append([])
                    #Iterate through the items for this day
                    for item in row:
                        #Add the items to the row
                        exportArray[-1].append(str(item))
            
            #Convert the data to be saved to a string
            dataToSave = createSetup.convertArrayToString(exportArray)
            #Ask the user to give a save location
            path = filedialog.asksaveasfilename(title="Save processed information to csv file", filetypes=self.fileTypes, defaultextension=self.fileTypes)

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
            #If currently processing data - display error message (Should never happen but will prevent crashes if it occurs)
            messagebox.showinfo(title="Error", message="Currently processing data, please wait and try again.")
    
    
    def unpopulateWindows(self) -> None:
        '''Remove all canvases and scroll bars and delete all references'''
        #Iterate through lists and destroy (children will be destoryed too so labels can be ignored)
        for canvas in self.hourCanvases:
            canvas.destroy()
        for canvas in self.dayCanvases:
            canvas.destroy()
        for scroll in self.hourScrolls:
            scroll.destroy()
        for scroll in self.dayScrolls:
            scroll.destroy()
        
        #Reset canvas, scroll and label lists to remove references to non-existant objects
        self.hourCanvases = []
        self.dayCanvases = []
        self.hourScrolls = []
        self.dayScrolls = []
        self.hourLabels = []
        self.dayLabels = []


    def populateWindows(self, rowsHours: int, rowsDays: int) -> None:
        #Remove all the current window items
        self.unpopulateWindows()

        #Iterate through the different channels' hour frames
        for hFrame in self.channelHourFrames:
            #Create canvas
            hourCanvas = tkinter.Canvas(hFrame)
            #Create scroll bar
            hourScrollBar = tkinter.Scrollbar(hFrame, orient="vertical", command=hourCanvas.yview)

            #Add canvas and scroll bar to hour frame
            hourCanvas.pack(side="left", expand=True, fill="both")
            hourScrollBar.pack(side="right", fill="y")

            #Create a frame to hold the labels in the canvas
            gridFrame = tkinter.Frame(hourCanvas)

            #Iterate through the rows of data and columns and set up grid in frame
            for col in range(0, 6):
                gridFrame.grid_columnconfigure(col, minsize=(self.width - 10) / 6)
            for row in range(0, rowsHours + 1):
                gridFrame.grid_rowconfigure(row, weight=1)

            #List to hold all the labels
            labels = [[], [], [], [], []]
            
            #Iterate through the rows
            for row in range(0, rowsHours + 1):
                for col in range(0, 6):
                    #Create labels
                    label = tkinter.Label(gridFrame, text="")
                    if row % 2 == 0:
                        label.configure(bg=self.alternateBackground)
                    label.grid(row=row, column=col, sticky="NESW")
                    #If is is not a header
                    if row != 0:
                        #If it is not the numbering column
                        if col > 0:
                            #Add to list of labels
                            labels[col - 1].append(label)
                        else:
                            #Add the current hour number
                            label.configure(text=row)
                    else:
                        #Set the text to the header and change the font
                        label.configure(text=self.hourHeaders[col], font=("courier", 10, "bold"))

            #Add the frame to the window of the canvas
            hourCanvas.create_window(0, 0, window=gridFrame, anchor="nw")
            #Call for update of canvas (so that size is correct)
            hourCanvas.update_idletasks()

            #Manually call for calculation of scroll region based on bounding box
            hourCanvas.configure(scrollregion=hourCanvas.bbox("all"), yscrollcommand=hourScrollBar.set)

            #Add hour canvas, scroll and labels to lists
            self.hourCanvases.append(hourCanvas)
            self.hourScrolls.append(hourScrollBar)
            self.hourLabels.append(labels)
        
        #Iterate through the different channels' day frames
        for dFrame in self.channelDayFrames:
            #Create a canvas
            dayCanvas = tkinter.Canvas(dFrame)
            #Create a scroll bar
            dayScrollBar = tkinter.Scrollbar(dFrame, orient="vertical", command=dayCanvas.yview)
            
            #Add the canvas and the scroll bar to the day frame
            dayCanvas.pack(side="left", expand=True, fill="both")
            dayScrollBar.pack(side="right", fill="y")

            #Create frame inside canvas for labels
            gridFrame = tkinter.Frame(dayCanvas)

            #Iterate through columns and rows to create grid
            for col in range(0, 6):
                gridFrame.grid_columnconfigure(col, minsize=(self.width - 10) / 6)
            for row in range(0, rowsDays + 1):
                gridFrame.grid_rowconfigure(row, weight=1)

            #List to hold the created labels
            labels = [[], [], [], [], []]
            
            #Iterate through the rows and columns
            for row in range(0, rowsDays + 1):
                for col in range(0, 6):
                    #Create a labels
                    label = tkinter.Label(gridFrame, text="")
                    if row % 2 == 0:
                        label.configure(bg=self.alternateBackground)
                    label.grid(row=row, column=col, sticky="NESW")
                    #If this is not the header row
                    if row != 0:
                        #If this is not the day number row
                        if col > 0:
                            #Add the label to the list
                            labels[col - 1].append(label)
                        else:
                            #Add the day number to the label
                            label.configure(text=row)
                    else:
                        #Add the header text to the label and change the font
                        label.configure(text=self.dayHeaders[col], font=self.headerFont)

            #Add the frame to the window of the canvas
            dayCanvas.create_window(0, 0, window=gridFrame, anchor="nw")
            #Call for update of canvas - so the size is correct
            dayCanvas.update_idletasks()

            #Manually call for the calculation of the scroll area using the bounding area
            dayCanvas.configure(scrollregion=dayCanvas.bbox("all"), yscrollcommand=dayScrollBar.set)

            #Add all the canvases, scroll bars and labels to the lists
            self.dayCanvases.append(dayCanvas)
            self.dayScrolls.append(dayScrollBar)
            self.dayLabels.append(labels)

#Only run if this is the main module being run
if __name__ == "__main__":
    #Create root window for tkinter
    root = tkinter.Tk()
    #Set the shape of the window
    root.geometry("1095x620")
    #Window cannot be resized
    root.resizable(False, False)
    #Set the title text of the window
    root.title("Process GFM Data")
    #Add the editor to the root windows
    mainWindow(root).grid(row = 0, column=0, sticky="NESW")
    #Start running the root
    root.mainloop()