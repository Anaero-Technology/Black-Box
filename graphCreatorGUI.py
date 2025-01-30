import tkinter
import tkinter.ttk as Ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from tkinter import filedialog
from tkinter import messagebox
import readSetup
import readSeparators

class MainWindow(tkinter.Frame):
    '''Class to contain all of the menus'''
    def __init__(self, parent, *args, **kwargs) -> None:
        #Setup parent configuration
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        #Grid dimensions for main window
        self.numberRows = 15
        self.numberColumns = 7

        self.loading = False

        for row in range(0, self.numberRows):
            self.grid_rowconfigure(row, weight = 1)
        for col in range(0, self.numberColumns):
            self.grid_columnconfigure(col, weight = 1)

        self.column, self.decimal = readSeparators.read()

        #Frame to hold the graph and toolbar
        self.graphFrame = tkinter.Frame(self)
        self.graphFrame.grid(row=1, column=0, rowspan=13, columnspan=5, sticky="NESW")

        #Progress bar (removed initially)
        self.progress = Ttk.Progressbar(self, orient=tkinter.HORIZONTAL, mode="determinate", maximum=10000.0)
        self.progress.grid(row=14, column=0, columnspan=7, sticky="NESW")
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

        self.loadedType = -1

        #Load buttons and label
        self.loadEventButton = tkinter.Button(self, text="Load Event Log", command=lambda: self.loadFile(0))
        self.loadHourButton = tkinter.Button(self, text="Load Hour Log", command=lambda: self.loadFile(1))
        self.loadDayButton = tkinter.Button(self, text="Load Day Log", command=lambda: self.loadFile(1))
        self.loadGasButton = tkinter.Button(self, text="Load Gas Log", command=lambda: self.loadFile(2))
        self.loadPhRedoxButton = tkinter.Button(self, text="Load pH/Redox Log", command=lambda: self.loadFile(2))
        self.loadEventButton.grid(row=0, column=0, sticky="NESW")
        self.loadHourButton.grid(row=0, column=1, sticky="NESW")
        self.loadDayButton.grid(row=0, column=2, sticky="NESW")
        self.loadGasButton.grid(row=0, column=3, sticky="NESW")
        self.loadPhRedoxButton.grid(row=0, column=4, sticky="NESW")
        self.loadedFileLabel = tkinter.Label(self, text="No file loaded")
        self.loadedFileLabel.grid(row=0, column=5, columnspan=2, sticky="NESW")

        #Mode drop down - select what type of graph is wanted
        self.graphMode = tkinter.StringVar()
        self.graphMode.set("Single Plot")
        self.modeIndex = 0
        self.graphMode.trace("w", self.updateMode)
        self.selectMode = tkinter.OptionMenu(self, self.graphMode, "Single Plot", "Compare Channels", "All One Channel")
        self.selectMode.configure(state="disabled")
        self.selectMode.grid(row=1, column=5, columnspan=2, sticky="NESW")

        #Channel drop down - select which channel you want a graph from
        self.selectedChannel = tkinter.StringVar()
        self.selectedChannel.set("Channel 1")
        self.selectedChannel.trace("w", self.updateChannel)
        self.channelList = ["Channel 1", "Channel 2", "Channel 3", "Channel 4", "Channel 5", "Channel 6", "Channel 7", "Channel 8", "Channel 9", "Channel 10", "Channel 11", "Channel 12", "Channel 13", "Channel 14", "Channel 15"]
        self.channelIndex = 0
        self.channelChoice = tkinter.OptionMenu(self, self.selectedChannel, *self.channelList)
        self.channelChoice.configure(state="disabled")
        self.channelChoice.grid(row=2, column=5, columnspan=2, sticky="NESW")

        #Second channel drop down - used to compare two channels
        self.secondSelectedChannel = tkinter.StringVar()
        self.secondSelectedChannel.set("Channel 1")
        self.secondSelectedChannel.trace("w", self.updateSecondChannel)
        self.secondChannelIndex = 0
        self.secondChannelChoice = tkinter.OptionMenu(self, self.secondSelectedChannel, *self.channelList)
        self.secondChannelChoice.grid(row=3, column=5, columnspan=2, sticky="NESW")
        self.secondChannelChoice.configure(state="disabled")

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
        self.selectType.grid(row=6, column=5, columnspan=2, sticky="NESW")

        #Checkbox to toggle display of grid
        self.gridEnabled = tkinter.IntVar()
        self.gridEnabled.set(1)
        self.gridEnabled.trace("w", self.updateCheckBox)
        self.gridCheckBox = tkinter.Checkbutton(self, text="Grid", variable=self.gridEnabled, onvalue=1, offvalue=0)
        self.gridCheckBox.configure(state="disabled")
        self.gridCheckBox.grid(row=7, column=5, columnspan=2, sticky="NESW")

        #Checkbox to toggle legend if necessary
        self.showLegend = tkinter.IntVar()
        self.showLegend.set(1)
        self.showLegend.trace("w", self.updateCheckBox)
        self.legendCheckBox = tkinter.Checkbutton(self, text="Legend", variable=self.showLegend, onvalue=1, offvalue=0)
        self.legendCheckBox.configure(state="disabled")
        self.legendCheckBox.grid(row=8, column=5, columnspan=2, sticky="NESW")

        #Allowed file types and extensions
        self.fileTypes = [("CSV Files", "*.csv")]

        #Colours for labels
        self.red = "#DD0000"
        self.green = "#00DD00"
        self.black = "#000000"

        #Arrays to hold the information once loaded
        self.loadedData = None
        self.information = []
        self.channelInfo = []

        #If the data has been loaded and the controls enabled
        self.ready = False

    def loadFile(self, loadType) -> None:
        '''Load a file of data into the arrays'''
        self.loading = True
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
            if allData != [] and len(allData) > 0 and len(allData[0]) > 0:
                #Convert data into two dimensional array
                self.loadedData = readSetup.formatData(allData)
                types = [" Event ", " Hour ", " Day ", " Gas "]
                #Set the label
                self.loadedFileLabel.configure(text=fileName + types[loadType] + "Data Loaded", fg=self.green)
                self.loadedType = loadType
                #Move the data into hour, day, and setup parts
                error = self.arrangeData()
                if error == None:
                    #Change the name labels for the channels to match the data
                    self.updateType()
                    self.changeChannelNames()
                    self.changeFieldOptions()
                    #Redraw the plot
                    self.updatePlot()
                    #If the buttons aren't enabled yet - enable them
                    if not self.ready:
                        self.ready = True
                        self.enableControls()
                else:
                    messagebox.showinfo(title="Error", message=error)
                    self.loadedFileLabel.configure(text="An error occurred, please try again.", fg=self.red)
                    self.disableGraphs()
            else:
                #Display error message
                self.loadedFileLabel.configure(text="File could not be read", fg=self.red)
        
        self.loading = False
    
    def arrangeData(self) -> None:
        '''Move the loaded data into arrays for hours, days and setup'''
        #Reset data arrays
        self.information = []
        self.channelInfo = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
        self.typeList = []
        self.typeToListPos = []

        if len(self.loadedData) < 1 or len(self.loadedData[0]) < 1:
            return "Data not found, please check separators and file format are correct."

        for c in range(0, len(self.loadedData[0])):
            #Select only valid output columns based on the file type
            self.information.append([])
            if self.loadedType == 1 and c > 6:
                self.typeList.append(self.loadedData[0][c])
                self.typeToListPos.append(c)
            elif self.loadedType == 0 and c > 8:
                self.typeList.append(self.loadedData[0][c])
                self.typeToListPos.append(c)
            elif self.loadedType == 2 and c > 5:
                self.typeList.append(self.loadedData[0][c])
                self.typeToListPos.append(c)

        #Iterate through the data
        for row in self.loadedData[1:]:
            #If there is some information in the row
            if len(row) > 0:
                
                for col in range(0, len(row)):
                    #Attempt to convert to a float
                    try:
                        floatData = float(row[col].replace(self.decimal, "."))
                        self.information[col].append(floatData)
                    except:
                        self.information[col].append(row[col].replace(self.decimal, "."))
                    
                    #if self.loadedType == 1 or self.loadedType == 2:
                    if self.loadedType == 1:
                        try:
                            channelNumber = int(row[0])
                            channelName = row[1]
                            if self.channelInfo[channelNumber - 1] == "":
                                self.channelInfo[channelNumber - 1] = channelName
                        except:
                            pass
                    elif self.loadedType == 2:
                        #Gas / pH/Redox
                        try:
                            channelNumber = int(row[2])
                            channelName = ""
                            if self.channelInfo[channelNumber - 1] == "":
                                self.channelInfo[channelNumber - 1] = channelName
                        except:
                            pass
                    elif self.loadedType == 0:
                        try:
                            channelNumber = int(row[0])
                            channelName = row[1]
                            if self.channelInfo[channelNumber - 1] == "":
                                self.channelInfo[channelNumber - 1] = channelName
                        except:
                            pass
        
        if len(self.typeList) < 1:
            return "File format incorrect, please check and try again."
        else:
            self.graphType.set(self.typeList[0])
                          

    def enableControls(self) -> None:
        '''Enable the controls for the first time'''
        self.selectMode.configure(state="normal")
        self.channelChoice.configure(state="normal")
        self.selectType.configure(state="normal")
        self.gridCheckBox.configure(state="normal")

    def disableGraphs(self) -> None:
        self.disableControls()
        self.ready = False
        self.figure.clf()
        self.subPlot = self.figure.add_subplot(111)
        self.graphCanvas.draw()

    def disableControls(self) -> None:
        self.selectMode.configure(state="disabled")
        self.channelChoice.configure(state="disabled")
        self.selectType.configure(state="disabled")
        self.gridCheckBox.configure(state="disabled")

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
        for channelId in range(0, len(self.channelInfo)):
            #Get the name
            if self.channelInfo[channelId] != "":
                name = self.channelInfo[channelId]
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

    def changeFieldOptions(self) -> None:
        menu = self.selectType["menu"]
        menu.delete(0, tkinter.END)

        for option in self.typeList:
            menu.add_command(label=option, command=lambda v=self.graphType, l=option: v.set(l))
        
        self.graphType.set(self.typeList[0])

    def updatePlot(self) -> None:
        '''Update the graph to show the currently selected data'''
        #Single plot
        if self.modeIndex == 0:
            #If the selected channel is valid (within the available range)
            if self.channelIndex > -1 and self.channelIndex < 15 and self.channelInfo[self.channelIndex] != "":
                channelIds = self.information[0]
                times = self.information[2]
                #Get the data from the list (for hour)
                data = self.information[self.typeToListPos[self.typeIndex]]
                xData = []
                yData = []
                #Iterate through rows
                for index in range(0, len(data)):
                    if self.channelIndex == channelIds[index] - 1:
                        if self.loadedType != 2 or float(data[index]) >= 0:
                            #Add the time point
                            xData.append(float(times[index]))
                            #Add the information
                            yData.append(float(data[index]))
                
                #Remove the old graph and create the new one
                self.subPlot.clear()
                self.subPlot.plot(xData, yData)
                #Set x axis label and title accordingly
                self.subPlot.set_xlabel("Time")
                self.subPlot.set_title(self.channelInfo[self.channelIndex] + " " + self.typeList[self.typeIndex])
                
                #Set y axis label to data
                self.subPlot.set_ylabel(self.typeList[self.typeIndex])
                #Show the grid if enabled
                self.subPlot.grid(self.gridEnabled.get() == 1)
                #Draw the new graph
                self.graphCanvas.draw()

        #Compare channels
        elif self.modeIndex == 1:
            #If the channels selected are available
            if self.channelIndex > -1 and self.channelIndex < 15 and self.secondChannelIndex > -1 and self.secondChannelIndex < 15:
                #Clear the old graph
                self.subPlot.clear()
                #Iterate for each channel
                data = self.information[self.typeToListPos[self.typeIndex]]
                channelIds = self.information[0]
                times = self.information[2]
                for channelIndex in [self.channelIndex, self.secondChannelIndex]:
                    #Lists to hold x and y axis data points
                    xData = []
                    yData = []
                    #Iterate through rows
                    for rowIndex in range(0, len(data)):
                        if channelIds[rowIndex] - 1 == channelIndex:
                            if self.loadedType != 2 or float(data[rowIndex]) >= 0:
                                #Add the time
                                xData.append(float(times[rowIndex]))
                                #Add the data
                                yData.append(float(data[rowIndex]))
                    #If there was data to plot
                    if len(xData) > 0:
                        #Add the data to the plot with a label for the channel
                        self.subPlot.plot(xData, yData, "-", label=self.channelInfo[channelIndex])
                #Set the x axis label and plot title according to data
                self.subPlot.set_xlabel("Time")
                self.subPlot.set_title("Channel Comparison Of " + self.typeList[self.typeIndex])
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
            if self.channelIndex > -1 and self.channelIndex < 15:

                #Delete the old graph
                self.subPlot.clear()

                channelIds = self.information[0]
                times = self.information[2]

                #For each of the types of data
                for dataTypeIndex in range(0, len(self.typeToListPos)):
                    dataType = self.typeToListPos[dataTypeIndex]
                    #Get the name of the type
                    name = self.typeList[dataTypeIndex]
                    data = self.information[dataType]
                    
                    #Lists to hold the x and y axis data points
                    xData = []
                    yData = []
                    #Iterate through the rows
                    for rowIndex in range(0, len(data)):
                        if channelIds[rowIndex] -1 == self.channelIndex:
                            if self.loadedType != 2 or float(data[rowIndex]) >= 0:
                                #Add the time
                                xData.append(times[rowIndex])
                                #Add the data from the array
                                yData.append(float(data[rowIndex]))
                    
                    #Plot the new data with the correct label
                    self.subPlot.plot(xData, yData, label=name)
                
                #Set the x label and plot title accordingly
                self.subPlot.set_xlabel("Time")
                self.subPlot.set_title("All " + self.channelInfo[self.channelIndex] + " Data")
                
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
        if not self.loading:
            self.updatePlot()

    def updateChannel(self, *args) -> None:
        '''When the channel value is changed'''
        #Get the index of the channel
        self.channelIndex = self.channelList.index(self.selectedChannel.get())
        #Update the graph to show the correct plot
        if not self.loading:
            self.updatePlot()

    def updateSecondChannel(self, *args) -> None:
        '''When the second channel value is changed'''
        #Get the index of the second channel
        self.secondChannelIndex = self.channelList.index(self.secondSelectedChannel.get())
        #If the second channel is currently in use
        if self.secondChannelChoice["state"] == "normal":
            #Update the graph to show the correct plot
            if not self.loading:
                self.updatePlot()

    def updateType(self, *args) -> None:
        '''When the type of graph (data type) is changed'''
        #Get the index of the type
        self.typeIndex = self.typeList.index(self.graphType.get())
        if self.typeIndex == -1 or self.typeIndex > len(self.typeList):
            self.typeIndex = 0
            self.graphType.set(0)
        #If the type option is currently enabled
        if self.selectType["state"] == "normal":
            #Update the graph to show the correct plot
            if not self.loading:
                self.updatePlot()
    
    def updateCheckBox(self, *args):
        '''When a check box is changed, update the plot ignoring the exta parameters'''
        self.updatePlot()


#Only run if this is the main module being run
if __name__ == "__main__":
    #Create root window for tkinter
    root = tkinter.Tk()
    #Set the shape of the window
    root.geometry("850x575")
    root.minsize(850, 575)
    #Allow for expanding sizes
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    #Set the title text of the window
    root.title("GFM Graph Creator")
    #Add the editor to the root windows
    MainWindow(root).grid(row = 0, column=0, sticky="NESW")
    #Start running the root
    root.mainloop()