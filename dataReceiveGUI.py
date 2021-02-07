import tkinter

class mainWindow(tkinter.Frame):
    '''Class to contain all of the menus'''
    def __init__(self, parent, *args, **kwargs):
        #Setup parent configuration
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=10)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        self.selectedPort = tkinter.StringVar()
        self.selectedPort.set("Port 1")
        self.portOption = tkinter.OptionMenu(self, self.selectedPort, "Port 1", "Port 2", "Port 3", "Port 4")
        self.portOption.grid(row=0, column=0, columnspan=2, sticky="NESW")

        self.connectButton = tkinter.Button(self, text="Connect", command=self.connectPressed)
        self.connectButton.grid(row=0, column=2, sticky="NESW")

        self.disconnectButton = tkinter.Button(self, text="Disconnect", state="disabled", command=self.disconnectPressed)
        self.disconnectButton.grid(row=0, column=3, sticky="NESW")

        self.fileLabel = tkinter.Label(self, text="No file selected")
        self.fileLabel.grid(row=2, column=0, columnspan=2, sticky="NESW")

        self.downloadFileButton = tkinter.Button(self, text="Download", state="disabled")
        self.downloadFileButton.grid(row=2, column=2, sticky="NESW")

        self.deleteFileButton = tkinter.Button(self, text="Delete", state="disabled")
        self.deleteFileButton.grid(row=2, column=3, sticky="NESW")

        self.fileFrame = tkinter.Frame(self)
        self.fileFrame.grid(row=1, column=0, columnspan=4, sticky="NESW")

        self.fileCanvas = None
        self.fileScroll = None
        self.fileGridFrame = None
        self.fileButtons = []
        self.fileCanvasWindow = None

        self.connected = False
        self.selectedFile = -1

        self.defaultButtonColour = self.connectButton.cget("bg")
        self.selectedButtonColour = "#70D070"

        self.files = []
        for i in range(1, 80):
            self.files.append("File Number " + str(i))

        self.setupFiles(self.files)
        self.setdownFiles()

    def connectPressed(self):
        #Need to update to be real once working
        if not self.connected:
            self.connectButton.configure(state="disabled")
            self.connected = True
            self.setupFiles(self.files)
            self.disconnectButton.configure(state="normal")
    
    def filePressed(self, index):
        if index == self.selectedFile:
            if index > -1 and index < len(self.fileButtons):
                self.fileButtons[index].configure(bg=self.defaultButtonColour)
            self.selectedFile = -1
            self.fileLabel.configure(text="No file selected")
        else:
            if index < len(self.files):
                if self.selectedFile != -1:
                    self.fileButtons[self.selectedFile].configure(bg=self.defaultButtonColour)
                self.selectedFile = index
                self.fileLabel.configure(text=self.files[index])
                self.downloadFileButton.configure(state="normal")
                self.deleteFileButton.configure(state="normal")
                self.fileButtons[index].configure(bg=self.selectedButtonColour)

    def disconnectPressed(self):
        #Need to update to be real once working
        if self.connected:
            self.disconnectButton.configure(state="disabled")
            self.connected = False
            self.setdownFiles()
            self.connectButton.configure(state="normal")

    def setdownFiles(self):
        
        if self.selectedFile != -1:
            self.filePressed(self.selectedFile)

        self.fileCanvas.destroy()
        self.fileScroll.destroy()

        self.fileCanvas = None
        self.fileScroll = None
        self.fileGridFrame = None
        self.fileButtons = []
        self.fileCanvasWindow = None

    def setupFiles(self, fileNames):
        self.fileCanvas = tkinter.Canvas(self.fileFrame)
        self.fileScroll = tkinter.Scrollbar(self.fileFrame, orient="vertical", command=self.fileCanvas.yview)

        self.fileCanvas.pack(side="left", expand=True, fill="both")
        self.fileScroll.pack(side="right", fill="y")
        self.fileGridFrame = tkinter.Frame(self.fileCanvas)

        self.fileGridFrame.grid_columnconfigure(0, weight=1)
        for row in range(0, len(fileNames)):
            self.fileGridFrame.grid_rowconfigure(row, minsize=70)
        
        self.fileButtons = []

        for nameId in range(0, len(fileNames)):
            button = tkinter.Button(self.fileGridFrame, text=fileNames[nameId], relief="groove", command=lambda x=nameId: self.filePressed(x))
            button.grid(row=nameId, column=0, sticky="NESW")
            self.fileButtons.append(button)

        self.fileCanvasWindow = self.fileCanvas.create_window(0, 0, window=self.fileGridFrame, anchor="nw")

        self.fileGridFrame.bind("<Configure>", self.onFrameConfigure)
        self.fileCanvas.bind("<Configure>", self.frameWidth)

        self.fileCanvas.update_idletasks()

        self.fileGridFrame.bind("<Enter>", self.bindMouseWheel)
        self.fileGridFrame.bind("<Leave>", self.unbindMouseWheel)

        self.fileCanvas.configure(scrollregion=self.fileCanvas.bbox("all"), yscrollcommand=self.fileScroll.set)
    
    def onFrameConfigure(self, event):
        '''Event called when canvas frame resized'''
        #Update canvas bounding box
        self.fileCanvas.configure(scrollregion=self.fileCanvas.bbox("all"))

    def frameWidth(self, event):
        '''Event called when canvas resized'''
        canvasWidth = event.width
        #Update size of window on canvas
        self.fileCanvas.itemconfig(self.fileCanvasWindow, width=canvasWidth)
    
    def bindMouseWheel(self, event):
        if self.fileCanvas != None:
            self.fileCanvas.bind_all("<MouseWheel>", self.mouseWheelMove)

    def unbindMouseWheel(self, event):
        if self.fileCanvas != None:
            self.fileCanvas.unbind_all("<MouseWheel>")

    def mouseWheelMove(self, event):
        if self.fileCanvas != None:
            self.fileCanvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


#Only run if this is the main module being run
if __name__ == "__main__":
    #Create root window for tkinter
    root = tkinter.Tk()
    #Set the shape of the window
    root.geometry("400x500")
    #Allow for expanding sizes
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    #Set the title text of the window
    root.title("GFM Data Receive")
    #Add the editor to the root windows
    mainWindow(root).grid(row = 0, column=0, sticky="NESW")
    #Start running the root
    root.mainloop()