import tkinter
import tkinter.ttk as Ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from tkinter import filedialog
import readSetup

class mainWindow(tkinter.Frame):
    '''Class to contain all of the menus'''
    def __init__(self, parent, *args, **kwargs) -> None:
        #Setup parent configuration
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        #Grid dimensions for main window
        self.numberRows = 15
        self.numberColumns = 6

        for row in range(0, self.numberRows):
            self.grid_rowconfigure(row, weight = 1)
        for col in range(0, self.numberColumns):
            self.grid_columnconfigure(col, weight = 1)

        #Frame to hold the graph and toolbar
        self.graphFrame = tkinter.Frame(self)
        self.graphFrame.grid(row=1, column=0, rowspan=13, columnspan=4, sticky="NESW")

        #Progress bar (removed initially)
        self.progress = Ttk.Progressbar(self, orient=tkinter.HORIZONTAL, mode="determinate", maximum=10000.0)
        self.progress.grid(row=14, column=0, columnspan=6, sticky="NESW")
        self.progress.grid_remove()

        #Create the graph and add it to the frame
        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.subPlot = self.figure.add_subplot(111)
        self.graphCanvas = FigureCanvasTkAgg(self.figure, master=self.graphFrame)
        self.graphCanvas.draw()
        self.graphCanvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.graphCanvas, self.graphFrame)
        self.toolbar.update()
        self.graphCanvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        #Load button and label
        self.loadDataButton = tkinter.Button(self, text="Load Processed Data", command=self.loadFile)
        self.loadDataButton.grid(row=0, column=0, sticky="NESW")
        self.loadedFileLabel = tkinter.Label(self, text="No file loaded")
        self.loadedFileLabel.grid(row=0, column=1, columnspan=5, sticky="NESW")

        #Mode drop down - select what type of graph is wanted
        self.graphMode = tkinter.StringVar()
        self.graphMode.set("Single Plot")
        self.modeIndex = 0
        self.graphMode.trace("w", self.updateMode)
        self.selectMode = tkinter.OptionMenu(self, self.graphMode, "Single Plot", "Compare Channels", "All One Channel")
        self.selectMode.configure(state="disabled")
        self.selectMode.grid(row=1, column=4, columnspan=2, sticky="NESW")

        #Channel drop down - select which channel you want a graph from
        self.selectedChannel = tkinter.StringVar()
        self.selectedChannel.set("Channel 1")
        self.selectedChannel.trace("w", self.updateChannel)
        self.channelList = ["Channel 1", "Channel 2", "Channel 3", "Channel 4", "Channel 5", "Channel 6", "Channel 7", "Channel 8", "Channel 9", "Channel 10", "Channel 11", "Channel 12", "Channel 13", "Channel 14", "Channel 15"]
        self.channelIndex = 0
        self.channelChoice = tkinter.OptionMenu(self, self.selectedChannel, *self.channelList)
        self.channelChoice.configure(state="disabled")
        self.channelChoice.grid(row=2, column=4, columnspan=2, sticky="NESW")

        #Second channel drop down - used to compare two channels
        self.secondSelectedChannel = tkinter.StringVar()
        self.secondSelectedChannel.set("Channel 1")
        self.secondSelectedChannel.trace("w", self.updateSecondChannel)
        self.secondChannelIndex = 0
        self.secondChannelChoice = tkinter.OptionMenu(self, self.secondSelectedChannel, *self.channelList)
        self.secondChannelChoice.grid(row=3, column=4, columnspan=2, sticky="NESW")
        self.secondChannelChoice.configure(state="disabled")

        #Hour and day buttons - to toggle between types
        self.hourButton = tkinter.Button(self, text="Hours", state="disabled", command=self.hourPressed)
        self.dayButton = tkinter.Button(self, text="Days", state="disabled", command=self.dayPressed)
        self.hourButton.grid(row=4, column=4, sticky="NESW")
        self.dayButton.grid(row=4, column=5, sticky="NESW")

        self.hour = True

        #Convert index from drop down to column in data
        self.typeToListPos = [0, 1, 2, 5]

        #Graph type drop down - select which data the graph should show
        self.graphType = tkinter.StringVar()
        self.graphType.set("Total Volume")
        self.graphType.trace("w", self.updateType)
        self.typeList = ["Total Volume", "Volume From Sample", "Volume Per Gram", "Total Evolved"]
        self.typeIndex = 0
        self.selectType = tkinter.OptionMenu(self, self.graphType, *self.typeList)
        self.selectType.configure(state="disabled")
        self.selectType.grid(row=5, column=4, columnspan=2, sticky="NESW")

        #Checkbox to toggle display of grid
        self.gridEnabled = tkinter.IntVar()
        self.gridEnabled.set(1)
        self.gridEnabled.trace("w", self.updateCheckBox)
        self.gridCheckBox = tkinter.Checkbutton(self, text="Grid", variable=self.gridEnabled, onvalue=1, offvalue=0)
        self.gridCheckBox.configure(state="disabled")
        self.gridCheckBox.grid(row=6, column=4, columnspan=2, sticky="NESW")

        #Checkbox to toggle legend if necessary
        self.showLegend = tkinter.IntVar()
        self.showLegend.set(1)
        self.showLegend.trace("w", self.updateCheckBox)
        self.legendCheckBox = tkinter.Checkbutton(self, text="Legend", variable=self.showLegend, onvalue=1, offvalue=0)
        self.legendCheckBox.configure(state="disabled")
        self.legendCheckBox.grid(row=7, column=4, columnspan=2, sticky="NESW")

        #Allowed file types and extensions
        self.fileTypes = [("CSV Files", "*.csv")]

        #Colours for labels
        self.red = "#DD0000"
        self.green = "#00DD00"
        self.black = "#000000"

        #Arrays to hold the information once loaded
        self.loadedData = None
        self.hourInformation = []
        self.dayInformation = []
        self.channelInfo = []

        #If the data has been loaded and the controls enabled
        self.ready = False

    def loadFile(self) -> None:
        '''Load a file of data into the arrays'''
        #Get the path
        path = filedialog.askopenfilename(title="Select processed data file", filetypes=self.fileTypes)
        pathParts = path.split("/")
        #If there is a path
        if path != "" and path != None and len(pathParts) > 0:
            #Reset the loaded data
            self.loadedData = None
            #Get the name of the file
            fileName = pathParts[-1]
            #Read all the data as one dimensional array
            allData = readSetup.getFile(path)
            #If some data was read
            if allData != []:
                #Convert data into two dimensional array
                self.loadedData = readSetup.formatData(allData)
                #Set the label
                self.loadedFileLabel.configure(text=fileName + " Loaded Successfully", fg=self.green)
                #Move the data into hour, day, and setup parts
                self.arrangeData()
                #Change the name labels for the channels to match the data
                self.changeChannelNames()
                #Redraw the plot
                self.updatePlot()
                #If the buttons aren't enabled yet - enable them
                if not self.ready:
                    self.ready = True
                    self.enableControls()
            else:
                #Display error message
                self.loadedFileLabel.configure(text="File could not be read", fg=self.red)
    
    def arrangeData(self) -> None:
        '''Move the loaded data into arrays for hours, days and setup'''
        #Reset data arrays
        self.dayInformation = []
        self.hourInformation = []
        self.channelInfo = []
        #If currently reading hour or day information
        currentHour = False
        currentDay = False
        #The current channel being recorded
        currentChannel = -1

        #Iterate through the data
        for row in self.loadedData:
            #If there is some information in the row
            if len(row) > 0:
                
                #The position to start from when adding the data
                start = 0
                
                #If this is an hour marker
                if row[0] == "Hour":
                    #Currently reading hour
                    currentHour = True
                    currentDay = False
                    #Do not include this row
                    start = len(row)
                #If this is a day marker
                elif row[0] == "Day":
                    #Currently reading day
                    currentDay = True
                    currentHour = False
                    #Do not include this row
                    start = len(row)
                else:
                    floatNumber = False
                    #Attempt to convert to a float
                    try:
                        float(row[0])
                        floatNumber = True
                    except:
                        pass
                        #If the first value is not a float (and not Hour or Day)
                    if not floatNumber:
                        #Setup for new channel
                        self.channelInfo.append([])
                        self.dayInformation.append([])
                        self.hourInformation.append([])
                        currentHour = False
                        currentDay = False
                        currentChannel = currentChannel + 1

                #If a new hour row is needed
                if currentHour and start == 0:
                    self.hourInformation[currentChannel].append([])
                #If a new day row is needed
                if currentDay and start == 0:
                    self.dayInformation[currentChannel].append([])

                #Iterate from start position to the end of the row
                for itemIndex in range(start, len(row)):
                    #If there is a channel
                    if currentChannel > -1:
                        #Add data to the correct array (Hour, Day or Setup)
                        if currentHour:
                            self.hourInformation[currentChannel][-1].append(row[itemIndex])
                        elif currentDay:
                            self.dayInformation[currentChannel][-1].append(row[itemIndex])
                        else:
                            self.channelInfo[currentChannel].append(row[itemIndex])

    def enableControls(self) -> None:
        '''Enable the controls for the first time'''
        self.selectMode.configure(state="normal")
        self.channelChoice.configure(state="normal")
        self.dayButton.configure(state="normal")
        self.selectType.configure(state="normal")
        self.gridCheckBox.configure(state="normal")

    def changeChannelNames(self) -> None:
        '''Change the labels for the channels'''
        #Get the menu objects and remove all values
        menu = self.channelChoice["menu"]
        menu.delete(0, tkinter.END)
        menu2 = self.secondChannelChoice["menu"]
        menu2.delete(0, tkinter.END)
        #Reset the channel list
        self.channelList = []
        #Iterate through the channels
        for channel in self.channelInfo:
            #Get the name
            name = channel[0]
            #Add the item to both menus
            menu.add_command(label=name, command=lambda v=self.selectedChannel, l=name: v.set(l))
            menu2.add_command(label=name, command=lambda v=self.secondSelectedChannel, l=name: v.set(l))
            #Add the name to the list of channels
            self.channelList.append(name)
        #Set the selected channels (or default to first if not found)
        if self.channelIndex > -1 and self.channelIndex < len(self.channelList):
            self.selectedChannel.set(self.channelList[self.channelIndex])
        else:
            self.selectedChannel.set(self.channelList[0])
        
        if self.secondChannelIndex > -1 and self.secondChannelIndex < len(self.channelList):
            self.secondSelectedChannel.set(self.channelList[self.secondChannelIndex])
        else:
            self.secondSelectedChannel.set(self.channelList[0])

    def updatePlot(self) -> None:
        '''Update the graph to show the currently selected data'''
        #Single plot
        if self.modeIndex == 0:
            #If the selected channel is valid (within the available range)
            if self.channelIndex > -1 and ((self.hour and self.channelIndex < len(self.hourInformation)) or (not self.hour and self.channelIndex < len(self.dayInformation))):
                #Get the data from the list (for hour)
                data = self.hourInformation[self.channelIndex]
                #If it is in day mode, get the day data instead
                if not self.hour:
                    data = self.dayInformation[self.channelIndex]
                #Get the correct column position for the data
                column = self.typeToListPos[self.typeIndex]
                #If the column is within the data
                if column > -1 and column < len(data[0]):
                    #Lists to hold x and y axis points
                    xData = []
                    yData = []
                    #Iterate through rows
                    for index in range(0, len(data)):
                        #Add the hour/day
                        xData.append(index + 1)
                        #Add the information
                        yData.append(float(data[index][column]))
                    
                    #Remove the old graph and create the new one
                    self.subPlot.clear()
                    self.subPlot.plot(xData, yData)
                    #If this is hours
                    if self.hour:
                        #Set x axis label and title accordingly
                        self.subPlot.set_xlabel("Hour")
                        self.subPlot.set_title(self.channelInfo[self.channelIndex][0] + " " + self.typeList[self.typeIndex] + " Per Hour")
                    else:
                        #Set x axis label and title accordingly
                        self.subPlot.set_xlabel("Day")
                        self.subPlot.set_title(self.channelInfo[self.channelIndex][0] + " " + self.typeList[self.typeIndex] + " Per Day")
                    
                    #Set y axis label to data
                    self.subPlot.set_ylabel(self.typeList[self.typeIndex])
                    #Show the grid if enabled
                    self.subPlot.grid(self.gridEnabled.get() == 1)
                    #Draw the new graph
                    self.graphCanvas.draw()

        #Compare channels
        elif self.modeIndex == 1:
            #Get all the data for hours
            data = self.hourInformation
            #If it is days get the day data instead
            if not self.hour:
                data = self.dayInformation
            #Get the column for the data being displayed
            column = self.typeToListPos[self.typeIndex]
            #If the channels selected are available
            if self.channelIndex > -1 and self.channelIndex < len(data) and self.secondChannelIndex > -1 and self.secondChannelIndex < len(data):
                #Clear the old graph
                self.subPlot.clear()
                #Iterate for each channel
                for index in [self.channelIndex, self.secondChannelIndex]:
                    #If the data is present
                    if index < len(data):
                        #And the column is valid
                        if column < len(data[index][0]):
                            #Lists to hold x and y axis data points
                            xData = []
                            yData = []
                            #Iterate through rows
                            for rowIndex in range(0, len(data[index])):
                                #Add the hour/day number
                                xData.append(rowIndex + 1)
                                #Add the data
                                yData.append(float(data[index][rowIndex][column]))
                            #If there was data to plot
                            if len(xData) > 0:
                                #Add the data to the plot with a label for the channel
                                self.subPlot.plot(xData, yData, "-", label=self.channelInfo[index][0])
                #Set the x axis label and plot title according to hour or day
                if self.hour:
                    self.subPlot.set_xlabel("Hour")
                    self.subPlot.set_title("Channel Comparison Of " + self.typeList[self.typeIndex] + " Per Hour")
                else:
                    self.subPlot.set_xlabel("Day")
                    self.subPlot.set_title("Channel Comparison Of " + self.typeList[self.typeIndex] + " Per Day")
                #Set the y label to the type of data being shown
                self.subPlot.set_ylabel(self.typeList[self.typeIndex])
                #Display the legend if it is on
                if self.showLegend.get() == 1:
                    self.subPlot.legend()
                #Show the grid if enabled
                self.subPlot.grid(self.gridEnabled.get() == 1)
                #Draw the new graph
                self.graphCanvas.draw()

        #All one channel
        elif self.modeIndex == 2:
            #If the channel is valid
            if self.channelIndex > -1 and ((self.hour and self.channelIndex < len(self.hourInformation)) or (not self.hour and self.channelIndex < len(self.dayInformation))):
                #Get the hour data for the channel
                data = self.hourInformation[self.channelIndex]
                #If it is day, get the day information instead
                if not self.hour:
                    data = self.dayInformation[self.channelIndex]

                #Delete the old graph
                self.subPlot.clear()

                #For each of the types of data
                for dataType in range(0, len(self.typeToListPos)):
                    #Get the name of the type
                    name = self.typeList[dataType]
                    #Lists to hold the x and y axis data points
                    xData = []
                    yData = []
                    #Iterate through the rows
                    for rowIndex in range(0, len(data)):
                        #Add the hour/day number
                        xData.append(rowIndex + 1)
                        #Add the data from the array
                        yData.append(float(data[rowIndex][self.typeToListPos[dataType]]))
                    
                    #Plot the new data with the correct label
                    self.subPlot.plot(xData, yData, label=name)
                
                #Set the x label and plot title accordingly
                if self.hour:
                    self.subPlot.set_xlabel("Hour")
                    self.subPlot.set_title("All " + self.channelInfo[self.channelIndex][0] + " Data Per Hour")
                else:
                    self.subPlot.set_xlabel("Day")
                    self.subPlot.set_title("All " + self.channelInfo[self.channelIndex][0] + " Data Per Day")
                
                #Display no y axis label (all different)
                self.subPlot.set_ylabel("")
                #Show the legend if it is on
                if self.showLegend.get() == 1:
                    self.subPlot.legend()
                #Display the grid if enabled
                self.subPlot.grid(self.gridEnabled.get() == 1)
                #Draw the new graph
                self.graphCanvas.draw()

    def updateMode(self, *args) -> None:
        '''Update the value of the mode and redraw the correct graph'''
        #Get the string value of the current mode
        mode = self.graphMode.get()
        if mode == "Single Plot":
            #Prevent second channel being changed
            self.secondChannelChoice.configure(state="disabled")
            #Allow type to be selected
            self.selectType.configure(state="normal")
            #Turn off the legend check box
            self.legendCheckBox.configure(state="disabled")
            #Set index to 0 for single plot
            self.modeIndex = 0
        elif mode == "Compare Channels":
            #Allow second channel to be chosen
            self.secondChannelChoice.configure(state="normal")
            #Allow type to be selected
            self.selectType.configure(state="normal")
            #Turn on the legend check box
            self.legendCheckBox.configure(state="normal")
            #Set index to 1 for compare channels
            self.modeIndex = 1
        elif mode == "All One Channel":
            #Prevent second channel from being changed
            self.secondChannelChoice.configure(state="disabled")
            #Do not allow type to be selected
            self.selectType.configure(state="disabled")
            #Turn on the legend check box
            self.legendCheckBox.configure(state="normal")
            #Set index to 2 for all one channel
            self.modeIndex = 2
        #Update the graph to show the new plot
        self.updatePlot()

    def updateChannel(self, *args) -> None:
        '''When the channel value is changed'''
        #Get the index of the channel
        self.channelIndex = self.channelList.index(self.selectedChannel.get())
        #Update the graph to show the correct plot
        self.updatePlot()

    def updateSecondChannel(self, *args) -> None:
        '''When the second channel value is changed'''
        #Get the index of the second channel
        self.secondChannelIndex = self.channelList.index(self.secondSelectedChannel.get())
        #If the second channel is currently in use
        if self.secondChannelChoice["state"] == "normal":
            #Update the graph to show the correct plot
            self.updatePlot()

    def updateType(self, *args) -> None:
        '''When the type of graph (data type) is changed'''
        #Get the index of the type
        self.typeIndex = self.typeList.index(self.graphType.get())
        #If the type option is currently enabled
        if self.selectType["state"] == "normal":
            #Update the graph to show the correct plot
            self.updatePlot()

    def hourPressed(self) -> None:
        '''When the hour button is pressed'''
        #Switch to hour mode
        self.hour = True
        #Toggle button states so only day may be pressed
        self.hourButton.configure(state="disabled")
        self.dayButton.configure(state="normal")
        #Draw the updated version of the graph
        self.updatePlot()

    def dayPressed(self) -> None:
        '''When the day button is pressed'''
        #Switch to day mode
        self.hour = False
        #Toggle buttons so only hour may be pressed
        self.dayButton.configure(state="disabled")
        self.hourButton.configure(state="normal")
        #Draw the updated version of the graph
        self.updatePlot()
    
    def updateCheckBox(self, *args):
        '''When a check box is changed, update the plot ignoring the exta parameters'''
        self.updatePlot()


#Only run if this is the main module being run
if __name__ == "__main__":
    #Create root window for tkinter
    root = tkinter.Tk()
    #Set the shape of the window
    root.geometry("800x575")
    root.minsize(800, 575)
    #Allow for expanding sizes
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    #Set the title text of the window
    root.title("GFM Graph Creator")
    #Add the editor to the root windows
    mainWindow(root).grid(row = 0, column=0, sticky="NESW")
    #Start running the root
    root.mainloop()