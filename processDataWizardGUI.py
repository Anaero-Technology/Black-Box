import tkinter
import tkinter.ttk as Ttk
from tkinter import filedialog
from tkinter import messagebox
import readSetup
import readSeparators
import os, sys
import setupGUI

class MainWindow(tkinter.Frame):
    '''Class to contain all of the menus'''
    def __init__(self, parent, *args, **kwargs) -> None:
        #Setup parent configuration
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        #Grid dimensions for main window
        self.numberRows = 11
        self.numberColumns = 4

        self.loading = False

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

        self.screenCentre = [self.parent.winfo_screenwidth() / 2, self.parent.winfo_screenheight() / 2]

        self.tabSetupFile = tkinter.Label(self, text="Select Setup File", relief="raised")
        self.onColour = self.tabSetupFile.cget("bg")
        self.offColour = "#999999"
        self.tabEventFile = tkinter.Label(self, text="Select Event File", relief="sunken", bg=self.offColour)
        self.tabProcessing = tkinter.Label(self, text="Processing Data...", relief="sunken", bg=self.offColour)
        self.tabDownload = tkinter.Label(self, text="Save Results", relief="sunken", bg=self.offColour)

        self.tabSetupFile.grid(row=0, column=0, sticky="NESW")
        self.tabEventFile.grid(row=0, column=1, sticky="NESW")
        self.tabProcessing.grid(row=0, column=2, sticky="NESW")
        self.tabDownload.grid(row=0, column=3, sticky="NESW")

        self.viewWindow = tkinter.Frame(self)
        self.viewWindow.grid(row=1, column=0, rowspan=10, columnspan=4, sticky="NESW")

        self.viewWindow.grid_rowconfigure(0, weight=1)
        self.viewWindow.grid_columnconfigure(0, weight=1)

        self.downloadWindow = tkinter.Frame(self.viewWindow)
        self.downloadWindow.grid(row=0, column=0, sticky="NESW")

        self.processingWindow = tkinter.Frame(self.viewWindow)
        self.processingWindow.grid(row=0, column=0, sticky="NESW")

        self.eventWindow = tkinter.Frame(self.viewWindow)
        self.eventWindow.grid(row=0, column=0, sticky="NESW")

        self.setupWindow = tkinter.Frame(self.viewWindow)
        self.setupWindow.grid(row=0, column=0, sticky="NESW")
        
        self.columns = []
        self.data = []
        self.channelColumn = -1
        self.channelList = []
        
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
        self.eventBackButton = tkinter.Button(self.eventButtonsFrame, text="Back", font=("", 16), command=self.nextPressedSetup, state="disabled")
        self.eventNextButton = tkinter.Button(self.eventButtonsFrame, text="Next", font=("", 16), command=self.nextPressedSetup, state="disabled")
        self.eventBackButton.pack(side="left", anchor="s")
        self.eventNextButton.pack(side="right", anchor="s")

        self.processingWindow.grid_rowconfigure(0, weight=1)
        self.processingWindow.grid_rowconfigure(1, weight=10)
        self.processingWindow.grid_rowconfigure(2, weight=1)
        self.processingWindow.grid_columnconfigure(0, weight=1)

        self.linesInstruction = tkinter.Label(self.processingWindow, text="Add lines to be plotted on the graph", font=("", 16))
        self.linesInstruction.grid(row=0, column=0, sticky="NESW")


        self.itemFrame = tkinter.Frame(self.processingWindow)
        self.itemFrame.grid(row=1, column=0, sticky="NESW")

        #Create canvas and scroll bar
        self.itemCanvas = tkinter.Canvas(self.itemFrame)
        self.itemScroll = tkinter.Scrollbar(self.itemFrame, orient="vertical", command=self.itemCanvas.yview)

        self.itemScroll.pack(side="right", fill="y")
        self.itemCanvas.pack(side="left", expand=True, fill="both")

        #Create frame that holds scrolling contents
        self.internalItemFrame = tkinter.Frame(self.itemCanvas)
        self.internalItemFrame.grid_columnconfigure(0, weight=1)
        self.internalItemFrame.grid_rowconfigure(0, minsize=100)

        #Create frame containing add buttons
        self.addLineFrame = tkinter.Frame(self.internalItemFrame)
        for i in range(0, 4):
            self.addLineFrame.grid_rowconfigure(i, weight=1)
            self.addLineFrame.grid_columnconfigure(i, weight=1)
        #Add buttons to add files
        self.addLineButton = tkinter.Button(self.addLineFrame, text="+ Add Line", command=self.addLine, fg="#00DD00", relief="ridge", bg="#FFFFFF", font=("", 16))
        #Add to grid
        self.addLineButton.grid(row=1, column=1, rowspan=2, columnspan=2, sticky="NESW")
        self.addLineFrame.grid(row=0, column=0, sticky="NESW")

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
        


        self.linesButtons = tkinter.Frame(self.processingWindow)
        self.linesButtons.grid(row=2, column=0, sticky="NESW")

        self.linesBackButton = tkinter.Button(self.linesButtons, text="Back", font=("", 16), command=lambda x = 1: self.moveWindows(x))
        self.linesBackButton.pack(side="left", anchor="s")

        self.linesNextButton = tkinter.Button(self.linesButtons, text="Next", font=("", 16), command=self.showGraph)
        self.linesNextButton.pack(side="right", anchor="s")

        #Allowed file types and extensions
        self.fileTypes = [("CSV Files", "*.csv")]

        self.lines = {}

        self.addingLine = True
        self.currentLineName = ""

        self.lineEditWindow = tkinter.Toplevel(self)
        self.lineEditWindow.minsize(500, 400)
        self.lineEditWindow.maxsize(500, 400)
        self.lineEditWindow.resizable(False, False)
        self.lineEditWindow.title("Line Customisation Options")
        self.lineEditWindow.protocol("WM_DELETE_WINDOW", self.lineCancelPressed)
        self.lineEditWindow.transient(self.parent)

        self.lineEditNameFrame = tkinter.Frame(self.lineEditWindow)
        self.lineEditNameLabel = tkinter.Label(self.lineEditNameFrame, text="Line Name:", font=("", 16))
        self.nameInputVar = tkinter.StringVar()
        self.lineEditNameInput = tkinter.Entry(self.lineEditNameFrame, textvariable=self.nameInputVar, font=("", 16))
        self.lineEditNameLabel.pack(side="left")
        self.lineEditNameInput.pack(side="left")
        self.lineEditNameFrame.pack(expand="true")

        self.currentColour = "#FF0000"

        self.lineEditColourFrame = tkinter.Frame(self.lineEditWindow)
        self.lineEditColourButton = tkinter.Button(self.lineEditColourFrame, text="Choose Line Colour", command="", font=("", 16))
        self.lineEditColourDisplay = tkinter.Button(self.lineEditColourFrame, bg=self.currentColour, relief="sunken", state="disabled", text="      ", font=("", 16))
        self.lineEditColourButton.pack(side="left")
        self.lineEditColourDisplay.pack(side="left")
        self.lineEditColourFrame.pack(expand="true")

        self.lineEditXAxisFrame = tkinter.Frame(self.lineEditWindow)
        self.lineEditXAxisLabel = tkinter.Label(self.lineEditXAxisFrame, text="X Axis Column:", font=("", 16))
        self.xAxisVar = tkinter.StringVar()
        self.lineEditXAxisMenu = tkinter.OptionMenu(self.lineEditXAxisFrame, self.xAxisVar, "None")
        self.lineEditXAxisMenu.configure(font=("", 16))
        self.lineEditXAxisLabel.pack(side="left")
        self.lineEditXAxisMenu.pack(side="left")
        self.lineEditXAxisFrame.pack(expand="true")

        self.lineEditYAxisFrame = tkinter.Frame(self.lineEditWindow)
        self.lineEditYAxisLabel = tkinter.Label(self.lineEditYAxisFrame, text="Y Axis Column:", font=("", 16))
        self.yAxisVar = tkinter.StringVar()
        self.lineEditYAxisMenu = tkinter.OptionMenu(self.lineEditYAxisFrame, self.yAxisVar, "None")
        self.lineEditYAxisMenu.configure(font=("", 16))
        self.lineEditYAxisLabel.pack(side="left")
        self.lineEditYAxisMenu.pack(side="left")
        self.lineEditYAxisFrame.pack(expand="true")

        self.lineEditChannelFrame = tkinter.Frame(self.lineEditWindow)
        self.lineEditChannelLabel = tkinter.Label(self.lineEditChannelFrame, text="Channel filter:", font=("", 16))
        self.lineChannelVar = tkinter.StringVar()
        self.lineEditChannelMenu = tkinter.OptionMenu(self.lineEditChannelFrame, self.lineChannelVar, "None")
        self.lineEditChannelMenu.configure(font=("", 16))
        self.lineEditChannelLabel.pack(side="left")
        self.lineEditChannelMenu.pack(side="left")
        self.lineEditChannelFrame.pack(expand="true")

        self.lineEditCumulativeFrame = tkinter.Frame(self.lineEditWindow)
        self.lineCumulativeVar = tkinter.IntVar()
        self.lineEditCumulativeCheck = tkinter.Checkbutton(self.lineEditCumulativeFrame, text="Cumulative", variable=self.lineCumulativeVar, onvalue=1, offvalue=0, font=("", 16))
        self.lineEditCumulativeCheck.pack(side="left")
        self.lineEditCumulativeFrame.pack(expand="true")

        self.lineEditControlsFrame = tkinter.Frame(self.lineEditWindow)
        self.lineEditCancelButton = tkinter.Button(self.lineEditControlsFrame, text="Cancel", command=self.lineCancelPressed, font=("", 16))
        self.lineEditAcceptButton = tkinter.Button(self.lineEditControlsFrame, text="Accept", command=self.lineAcceptPressed, font=("", 16))
        self.lineEditCancelButton.pack(side="left")
        self.lineEditAcceptButton.pack(side="left")
        self.lineEditControlsFrame.pack(expand="true")
        self.lineEditWindow.withdraw()

        self.downloadWindow.grid_rowconfigure(0, weight=10)
        self.downloadWindow.grid_rowconfigure(1, weight=1)
        self.downloadWindow.grid_columnconfigure(0, weight=1)

        self.graphFrame = tkinter.Frame(self.downloadWindow)
        self.graphFrame.grid(row=0, column=0, sticky="NESW")

        self.graphOptions = tkinter.Frame(self.downloadWindow)
        self.graphOptions.grid(row=1, column=0, sticky="NESW")

        #Checkbox to toggle display of grid
        self.gridEnabled = tkinter.IntVar()
        self.gridEnabled.set(1)
        self.gridEnabled.trace("w", self.updateGraphOptions)
        self.gridCheckBox = tkinter.Checkbutton(self.graphOptions, text="Grid", variable=self.gridEnabled, onvalue=1, offvalue=0)
        self.gridCheckBox.pack(side="right", anchor="s")

        self.legendEnabled = tkinter.IntVar()
        self.legendEnabled.set(1)
        self.legendEnabled.trace("w", self.updateGraphOptions)
        self.legendCheckBox = tkinter.Checkbutton(self.graphOptions, text="Legend", variable=self.legendEnabled, onvalue=1, offvalue=0)
        self.legendCheckBox.pack(side="right", anchor="s")

        self.graphBackButton = tkinter.Button(self.graphOptions, text="Back", font=("", 16), command=lambda x=2: self.moveWindows(x))
        self.graphBackButton.pack(side="left", anchor="s")
        self.graphOptions.grid(row=1, column=0, sticky="NESW")

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
                    self.setupFileLabel.config(text=fileName + "loaded correctly.", fg=self.green)
                    self.setupNextButton.configure(state="normal")
                else:
                    #Display error
                    self.setupLabel.config(text="File invalid or could not be read.", fg=self.red)
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
        pass

    def nextPressedEvent(self) -> None:
        pass

    def backPressedEvent(self) -> None:
        pass
    
    def arrangeData(self, dataArray : list) -> str:
        '''Move the loaded data into arrays for hours, days and setup'''
        #Reset data arrays
        self.columns = []
        self.data = []

        if len(dataArray) < 1:
            return "File is empty"
        if len(dataArray) < 2:
            return "No data found in file"

        self.columns = dataArray[0]

        if len(self.columns) < 2:
            return "File only contains one column"

        for i in range(0, len(self.columns)):
            self.data.append([])
            for j in range(1, len(dataArray)):
                item = dataArray[j][i]
                try:
                    item = float(item)
                    if item == int(item):
                        item = int(item)
                except:
                    pass
                self.data[-1].append(item)

        return ""

    def nextChannel(self) -> None:           
        chosen = self.channelSelectVar.get()
        if chosen in self.columns:
            self.channelColumn = self.columns.index(chosen)
            self.channelList = []
            for index in range(0, len(self.data[self.channelColumn])):
                item = str(self.data[self.channelColumn][index])
                if item not in self.channelList:
                    self.channelList.append(item)
            self.channelList.sort()
        else:
            self.channelColumn = -1

        for key in self.lines:
            self.lines[key].grid_remove()
            self.lines[key].destroy()
        
        self.lines = {}
        
        self.updateLineList()
        
        self.moveWindows(2)

    def changeColumnNames(self):
        '''Change the labels for the columns'''
        #Get the menu objects and remove all values
        menu = self.channelMenu["menu"]
        menu.delete(0, tkinter.END)
        for columnNumber in range(-1, len(self.columns)):
            name = "None"
            if columnNumber != -1:
                name = self.columns[columnNumber]
            menu.add_command(label=name, command=lambda v=self.channelSelectVar, l=name: v.set(l))

    def showGraph(self) -> None:
        if len(self.lines) > 0:
            self.clearGraphs()
            for key in self.lines:
                lineData = self.lines[key]
                xAxis = lineData.xCol
                yAxis = lineData.yCol
                colour = lineData.colour
                lineName = lineData.lineName
                channel = lineData.channel
                cumulative = lineData.cumulative == 1
                total = 0
                xData = []
                yData = []
                for i in range(0, len(self.data[0])):
                    if channel == "" or str(self.data[self.channelColumn][i]) == channel:
                        xData.append(self.data[xAxis][i])
                        if cumulative:
                            total = total + self.data[yAxis][i]
                            yData.append(total)
                        else:
                            yData.append(self.data[yAxis][i])
                self.subPlot.plot(xData, yData, "-", label=lineName, color=colour)
            #Show grid if needed
            self.subPlot.grid(self.gridEnabled.get() == 1)
            #Draw legend if needed
            if self.legendEnabled.get() == 1:
                self.subPlot.legend()
            #Draw the new graph
            self.graphCanvas.draw()
            self.moveWindows(3)


    def createLine(self, name, colour, xAxis, yAxis, channel, cumulative):
        lineData = LineObject(self.internalItemFrame, self, name, colour, xAxis, yAxis, channel, cumulative, highlightbackground="black", highlightthickness=2)
        self.lines[name] = lineData
        self.updateLineList()

    def removeLine(self, lineName):
        if lineName in self.lines:
            self.lines[lineName].grid_remove()
            self.lines[lineName].destroy()
            del self.lines[lineName]
            self.updateLineList()

    def updateLineList(self):
        i = 0
        for key in self.lines:
            self.lines[key].grid_remove()
            self.internalItemFrame.grid_rowconfigure(i, minsize=0)
            i = i + 1
        self.addLineFrame.grid_remove()
        self.internalItemFrame.grid_rowconfigure(i, minsize=0)
        i = 0
        for key in self.lines:
            self.lines[key].grid(row=i, column=0, sticky="NESW")
            self.internalItemFrame.grid_rowconfigure(i, minsize=100)
            i = i + 1
        self.addLineFrame.grid(row=i, column=0, sticky="NESW")
        self.internalItemFrame.grid_rowconfigure(i, minsize=100)

    def addLine(self) -> None:
        self.addingLine = True
        self.openLineEdit("", "#FF0000", "", "", "", 0)

    def editLine(self, lineName) -> None:
        self.addingLine = False
        if lineName in self.lines:
            lineData = self.lines[lineName]
            linesName = lineData.lineName
            colourCode = lineData.colour
            xAxis = lineData.xCol
            xAxis = self.columns[xAxis]
            yAxis = lineData.yCol
            yAxis = self.columns[yAxis]
            channel = lineData.channel
            cumulative = lineData.cumulative
            self.openLineEdit(linesName, colourCode, xAxis, yAxis, channel, cumulative)
    
    def openLineEdit(self, name : str, colour : str, xA : str, yA : str, channel : str, cumulative : int):
        self.nameInputVar.set(name)
        self.currentLineName = name
        self.currentColour = colour
        self.lineEditColourDisplay.configure(bg=self.currentColour)

        validColumns = []
        for i in range(0, len(self.columns)):
            if i != self.channelColumn:
                validColumns.append(self.columns[i])
        
        xMenu = self.lineEditXAxisMenu["menu"]
        yMenu = self.lineEditYAxisMenu["menu"]
        xMenu.delete(0, tkinter.END)
        yMenu.delete(0, tkinter.END)
        xMenu.add_command(label="None", command=lambda v=self.xAxisVar, l="None": v.set(l))
        yMenu.add_command(label="None", command=lambda v=self.yAxisVar, l="None": v.set(l))
        for col in validColumns:
            xMenu.add_command(label=col, command=lambda v=self.xAxisVar, l=col: v.set(l))
            yMenu.add_command(label=col, command=lambda v=self.yAxisVar, l=col: v.set(l))

        chMenu = self.lineEditChannelMenu["menu"]
        chMenu.delete(0, tkinter.END)
        chMenu.add_command(label="Any", command=lambda v=self.lineChannelVar, l="Any": v.set(l))
        for chan in self.channelList:
            chMenu.add_command(label=chan, command=lambda v=self.lineChannelVar, l=chan: v.set(l))

        if xA not in validColumns:
            self.xAxisVar.set("None")
        else:
            self.xAxisVar.set(xA)

        if yA not in validColumns:
            self.yAxisVar.set("None")
        else:
            self.yAxisVar.set(yA)

        if channel in self.channelList:
            self.lineChannelVar.set(channel)
        else:
            self.lineChannelVar.set("Any")

        if self.channelColumn == -1:
            self.lineEditChannelFrame.configure(bg=self.offColour)
            self.lineEditChannelLabel.configure(bg=self.offColour)
            self.lineEditChannelMenu.configure(state="disabled")
        else:
            self.lineEditChannelFrame.configure(bg=self.onColour)
            self.lineEditChannelLabel.configure(bg=self.onColour)
            self.lineEditChannelMenu.configure(state="normal")

        self.lineCumulativeVar.set(cumulative)

        self.lineEditWindow.deiconify()

    def lineCancelPressed(self) -> None:
        self.lineEditWindow.withdraw()

    def lineAcceptPressed(self) -> None:
        if self.addingLine:
            allowed = True
            name = self.nameInputVar.get().strip()
            if name == "" or name in self.lines:
                allowed = False
            xAxis = self.xAxisVar.get()
            yAxis = self.yAxisVar.get()
            if xAxis not in self.columns or yAxis not in self.columns:
                allowed = False
            else:
                xAxis = self.columns.index(xAxis)
                yAxis = self.columns.index(yAxis)
            if not allowed:
                messagebox.showinfo(title="Invalid Line", message="Line must have a unique name and valid x and y columns.")
            else:
                colour = self.currentColour
                channel = self.lineChannelVar.get()
                if channel not in self.channelList:
                    channel = ""
                cumulative = self.lineCumulativeVar.get()
                self.createLine(name, colour, xAxis, yAxis, channel, cumulative)
                self.lineEditWindow.withdraw()
        else:
            allowed = True
            name = self.nameInputVar.get().strip()
            if name == "" or (name in self.lines and name != self.currentLineName):
                allowed = False
            xAxis = self.xAxisVar.get()
            yAxis = self.yAxisVar.get()
            if xAxis not in self.columns or yAxis not in self.columns:
                allowed = False
            else:
                xAxis = self.columns.index(xAxis)
                yAxis = self.columns.index(yAxis)
            if not allowed:
                messagebox.showinfo(title="Invalid Line", message="Line must have a unique name and valid x and y columns.")
            else:
                colour = self.currentColour
                channel = self.lineChannelVar.get()
                if channel not in self.channelList:
                    channel = ""
                cumulative = self.lineCumulativeVar.get()
                lineData = self.lines[self.currentLineName]
                lineData.lineName = name
                lineData.colour = colour
                lineData.xCol = xAxis
                lineData.yCol = yAxis
                lineData.channel = channel
                lineData.cumulative = cumulative
                lineData.updateWidgets()
                self.lineEditWindow.withdraw()


    def clearGraphs(self) -> None:
        self.figure.clf()
        self.subPlot = self.figure.add_subplot(111)
        self.graphCanvas.draw()

    def updateGraphOptions(self, *args) -> None:
        self.subPlot.grid(self.gridEnabled.get() == 1)
        self.showGraph()
    
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

class LineObject(tkinter.Frame):
    def __init__ (self, parent, parentObject, lineName : str, colour : str, xCol : int, yCol : int, channel : str, cumulative : bool, *args, **kwargs):
        #Initialise parent class
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        #Store the parent window
        self.window = parentObject

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        self.lineName = lineName
        self.colour = colour
        self.xCol = xCol
        self.yCol = yCol
        self.channel = channel
        self.cumulative = cumulative

        self.colourBox = tkinter.Button(self, bg=self.colour, relief="sunken", state="disabled", text="     ")
        self.colourBox.grid(row=0, column=0)

        self.nameLabel = tkinter.Label(self, text=self.lineName, font=("", 16))
        self.nameLabel.grid(row=0, column=1)
        
        self.settingsImage = tkinter.PhotoImage(file=self.window.pathTo("settingsIcon.png"))
        self.editButton = tkinter.Button(self, image=self.settingsImage, command=self.edit)
        self.editButton.grid(row=0, column=2)

        self.removeImage = tkinter.PhotoImage(file=self.window.pathTo("cancel.png"))
        self.deleteButton = tkinter.Button(self, image=self.removeImage, command=self.delete)
        self.deleteButton.grid(row=0, column=3)

    def edit(self):
        self.window.editLine(self.lineName)

    def delete(self):
        self.window.removeLine(self.lineName)
    
    def updateWidgets(self):
        self.colourBox.configure(bg=self.colour)
        self.nameLabel.configure(text=self.lineName)

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