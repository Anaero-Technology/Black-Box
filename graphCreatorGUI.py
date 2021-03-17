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

        self.numberRows = 15
        self.numberColumns = 6

        for row in range(0, self.numberRows):
            self.grid_rowconfigure(row, weight = 1)
        for col in range(0, self.numberColumns):
            self.grid_columnconfigure(col, weight = 1)

        self.graphFrame = tkinter.Frame(self)
        self.graphFrame.grid(row=1, column=0, rowspan=13, columnspan=4, sticky="NESW")

        self.progress = Ttk.Progressbar(self, orient=tkinter.HORIZONTAL, mode="determinate", maximum=10000.0)
        self.progress.grid(row=14, column=0, columnspan=6, sticky="NESW")
        #self.progress.grid_remove()

        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.subPlot = self.figure.add_subplot(111)
        self.subPlot.plot([1,2,3,4], [1,2,1,3])
        self.graphCanvas = FigureCanvasTkAgg(self.figure, master=self.graphFrame)
        self.graphCanvas.draw()
        self.graphCanvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.graphCanvas, self.graphFrame)
        self.toolbar.update()
        self.graphCanvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        self.loadDataButton = tkinter.Button(self, text="Load Processed Data", command=self.loadFile)
        self.loadDataButton.grid(row=0, column=0, sticky="NESW")
        self.loadedFileLabel = tkinter.Label(self, text="No file loaded")
        self.loadedFileLabel.grid(row=0, column=1, columnspan=5, sticky="NESW")
        
        self.graphMode = tkinter.StringVar()
        self.graphMode.set("Single Plot")
        self.modeIndex = 0
        self.graphMode.trace("w", self.updateMode)
        self.selectMode = tkinter.OptionMenu(self, self.graphMode, "Single Plot", "Compare Channels", "All One Channel")
        self.selectMode.grid(row=1, column=4, columnspan=2, sticky="NESW")

        self.selectedChannel = tkinter.StringVar()
        self.selectedChannel.set("Channel 1")
        self.selectedChannel.trace("w", self.updateChannel)
        self.channelList = ["Channel 1", "Channel 2", "Channel 3", "Channel 4", "Channel 5", "Channel 6", "Channel 7", "Channel 8", "Channel 9", "Channel 10", "Channel 11", "Channel 12", "Channel 13", "Channel 14", "Channel 15"]
        self.channelIndex = 0
        self.channelChoice = tkinter.OptionMenu(self, self.selectedChannel, *self.channelList)
        self.channelChoice.grid(row=2, column=4, columnspan=2, sticky="NESW")

        self.secondSelectedChannel = tkinter.StringVar()
        self.secondSelectedChannel.set("Channel 1")
        self.secondSelectedChannel.trace("w", self.updateSecondChannel)
        self.secondChannelList = ["Channel 1", "Channel 2", "Channel 3", "Channel 4", "Channel 5", "Channel 6", "Channel 7", "Channel 8", "Channel 9", "Channel 10", "Channel 11", "Channel 12", "Channel 13", "Channel 14", "Channel 15"]
        self.secondChannelIndex = 0
        self.secondChannelChoice = tkinter.OptionMenu(self, self.secondSelectedChannel, *self.secondChannelList)
        self.secondChannelChoice.grid(row=3, column=4, columnspan=2, sticky="NESW")
        self.secondChannelChoice.configure(state="disabled")

        self.hourButton = tkinter.Button(self, text="Hours", state="disabled", command=self.hourPressed)
        self.dayButton = tkinter.Button(self, text="Days", command=self.dayPressed)
        self.hourButton.grid(row=4, column=4, sticky="NESW")
        self.dayButton.grid(row=4, column=5, sticky="NESW")

        self.hour = True

        self.typeToListPos = [0, 1, 2, 4]
        
        self.graphType = tkinter.StringVar()
        self.graphType.set("Total Volume")
        self.graphType.trace("w", self.updateType)
        self.typeList = ["Total Volume", "Volume From Sample", "Volume Per Gram", "Total Evolved"]
        self.typeIndex = 0
        self.selectType = tkinter.OptionMenu(self, self.graphType, *self.typeList)
        self.selectType.grid(row=5, column=4, columnspan=2, sticky="NESW")

        #Allowed file types and extensions
        self.fileTypes = [("CSV Files", "*.csv")]

        self.red = "#DD0000"
        self.green = "#00DD00"
        self.black = "#000000"

        self.loadedData = None
        self.hourInformation = []
        self.dayInformation = []
        self.channelInfo = []

    def loadFile(self):
        path = filedialog.askopenfilename(title="Select processed data file", filetypes=self.fileTypes)
        pathParts = path.split("/")
        if path != "" and path != None and len(pathParts) > 0:
            self.loadedData = None
            fileName = pathParts[-1]
            allData = readSetup.getFile(path)
            if allData != []:
                self.loadedData = readSetup.formatData(allData)
                self.loadedFileLabel.configure(text=fileName + " Loaded Successfully", fg=self.green)
                self.arrangeData()
                self.changeChannelNames()
                self.updatePlot()
            else:
                self.loadedFileLabel.configure(text="File could not be read", fg=self.red)
    
    def arrangeData(self):
        self.dayInformation = []
        self.hourInformation = []
        self.channelInfo = []
        currentHour = False
        currentDay = False
        currentChannel = -1

        for row in self.loadedData:
            if len(row) > 0:
                
                start = 0

                if row[0] == "Hour":
                    currentHour = True
                    currentDay = False
                    start = len(row)
                elif row[0] == "Day":
                    currentDay = True
                    currentHour = False
                    start = len(row)
                else:
                    floatNumber = False
                    try:
                        float(row[0])
                        floatNumber = True
                    except:
                        pass
                    if not floatNumber:
                        self.channelInfo.append([])
                        self.dayInformation.append([])
                        self.hourInformation.append([])
                        currentHour = False
                        currentDay = False
                        currentChannel = currentChannel + 1

                if currentHour and start == 0:
                    self.hourInformation[currentChannel].append([])
                if currentDay and start == 0:
                    self.dayInformation[currentChannel].append([])

                for itemIndex in range(start, len(row)):
                    if currentChannel > -1:
                        if currentHour:
                            self.hourInformation[currentChannel][-1].append(row[itemIndex])
                        elif currentDay:
                            self.dayInformation[currentChannel][-1].append(row[itemIndex])
                        else:
                            self.channelInfo[currentChannel].append(row[itemIndex])
                    
    def changeChannelNames(self):
        menu = self.channelChoice["menu"]
        menu.delete(0, tkinter.END)
        menu2 = self.secondChannelChoice["menu"]
        menu2.delete(0, tkinter.END)
        self.channelList = []
        self.secondChannelList = []
        for channel in self.channelInfo:
            name = channel[0]
            menu.add_command(label=name, command=lambda v=self.selectedChannel, l=name: v.set(l))
            menu2.add_command(label=name, command=lambda v=self.secondSelectedChannel, l=name: v.set(l))
            self.channelList.append(name)
            self.secondChannelList.append(name)
        self.selectedChannel.set(self.channelList[self.channelIndex])
        self.secondSelectedChannel.set(self.secondChannelList[self.secondChannelIndex])

    def updatePlot(self):
        if self.modeIndex == 0:
            if self.channelIndex > -1 and ((self.hour and self.channelIndex < len(self.hourInformation)) or (not self.hour and self.channelIndex < len(self.dayInformation))):
                data = self.hourInformation[self.channelIndex]
                if not self.hour:
                    data = self.dayInformation[self.channelIndex]
                column = self.typeToListPos[self.typeIndex]
                if column > -1 and column < len(data[0]):
                    xData = []
                    yData = []
                    for index in range(0, len(data)):
                        xData.append(index + 1)
                        yData.append(float(data[index][column]))
                    self.subPlot.clear()
                    self.subPlot.plot(xData, yData)
                    if self.hour:
                        self.subPlot.set_xlabel("Hour")
                        self.subPlot.set_title(self.channelInfo[self.channelIndex][0] + " " + self.typeList[self.typeIndex] + " Per Hour")
                    else:
                        self.subPlot.set_xlabel("Day")
                        self.subPlot.set_title(self.channelInfo[self.channelIndex][0] + " " + self.typeList[self.typeIndex] + " Per Day")
                    self.subPlot.set_ylabel(self.typeList[self.typeIndex])
                    self.graphCanvas.draw()
        elif self.modeIndex == 1:
            data = self.hourInformation
            if not self.hour:
                data = self.dayInformation
            column = self.typeToListPos[self.typeIndex]
            if self.channelIndex > -1 and self.channelIndex < len(data) and self.secondChannelIndex > -1 and self.secondChannelIndex < len(data):
                self.subPlot.clear()
                for index in [self.channelIndex, self.secondChannelIndex]:
                    if index < len(data):
                        if column < len(data[index][0]):
                            xData = []
                            yData = []
                            for rowIndex in range(0, len(data[index])):
                                xData.append(rowIndex + 1)
                                yData.append(float(data[index][rowIndex][column]))
                            if len(xData) > 0:
                                self.subPlot.plot(xData, yData, "-", label=self.channelInfo[index][0])
                if self.hour:
                    self.subPlot.set_xlabel("Hour")
                    self.subPlot.set_title("Channel Comparison Of " + self.typeList[self.typeIndex] + " Per Hour")
                else:
                    self.subPlot.set_xlabel("Day")
                    self.subPlot.set_title("Channel Comparison Of " + self.typeList[self.typeIndex] + " Per Day")
                self.subPlot.set_ylabel(self.typeList[self.typeIndex])
                self.subPlot.legend()
                self.graphCanvas.draw()

        elif self.modeIndex == 2:
            pass

    def updateMode(self, *args):
        mode = self.graphMode.get()
        if mode == "Single Plot":
            self.secondChannelChoice.configure(state="disabled")
            self.selectType.configure(state="normal")
            self.modeIndex = 0
        elif mode == "Compare Channels":
            self.secondChannelChoice.configure(state="normal")
            self.selectType.configure(state="normal")
            self.modeIndex = 1
        elif mode == "All One Channel":
            self.secondChannelChoice.configure(state="disabled")
            self.selectType.configure(state="disabled")
            self.modeIndex = 2
        self.updatePlot()

    def updateChannel(self, *args):
        self.channelIndex = self.channelList.index(self.selectedChannel.get())
        self.updatePlot()

    def updateSecondChannel(self, *args):
        self.secondChannelIndex = self.secondChannelList.index(self.secondSelectedChannel.get())
        if self.secondChannelChoice["state"] == "normal":
            self.updatePlot()

    def updateType(self, *args):
        self.typeIndex = self.typeList.index(self.graphType.get())
        if self.selectType["state"] == "normal":
            self.updatePlot()

    def hourPressed(self):
        self.hour = True
        self.hourButton.configure(state="disabled")
        self.dayButton.configure(state="normal")
        self.updatePlot()

    def dayPressed(self):
        self.hour = False
        self.dayButton.configure(state="disabled")
        self.hourButton.configure(state="normal")
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