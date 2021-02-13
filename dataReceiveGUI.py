import tkinter
from tkinter import messagebox
import serial
from serial.tools import list_ports
from threading import Thread

class mainWindow(tkinter.Frame):
    '''Class to contain all of the menus'''
    def __init__(self, parent, *args, **kwargs) -> None:
        #Setup parent configuration
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        #Setup grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=10)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        #Setup port drop down (with debug values)
        self.selectedPort = tkinter.StringVar()
        self.selectedPort.set("Port 1")
        self.portOption = tkinter.OptionMenu(self, self.selectedPort, "Port 1", "Port 2", "Port 3", "Port 4")
        self.portOption.grid(row=0, column=0, columnspan=2, sticky="NESW")

        #Add connect button
        self.connectButton = tkinter.Button(self, text="Connect", command=self.connectPressed)
        self.connectButton.grid(row=0, column=2, sticky="NESW")
        
        #Add disconnect button
        self.disconnectButton = tkinter.Button(self, text="Disconnect", state="disabled", command=self.disconnectPressed)
        self.disconnectButton.grid(row=0, column=3, sticky="NESW")

        #Add label for selected file name
        self.fileLabel = tkinter.Label(self, text="No file selected")
        self.fileLabel.grid(row=3, column=0, columnspan=2, sticky="NESW")

        #Add download file button
        self.downloadFileButton = tkinter.Button(self, text="Download", state="disabled")
        self.downloadFileButton.grid(row=3, column=2, sticky="NESW")

        #Add delete file button
        self.deleteFileButton = tkinter.Button(self, text="Delete", state="disabled")
        self.deleteFileButton.grid(row=3, column=3, sticky="NESW")

        #Add a frame to put the list of files into
        self.fileFrame = tkinter.Frame(self)
        self.fileFrame.grid(row=2, column=0, columnspan=4, sticky="NESW")

        #Add a button to scan for ports
        self.scanButton = tkinter.Button(self, text="Scan Ports", command=self.scanPressed)
        self.scanButton.grid(row=1, column=1, sticky="NESW")

        #Add a button to initiate reading and storing the data from the arduino
        self.toggleButton = tkinter.Button(self, text="Start", command=self.togglePressed, state="disabled")
        self.toggleButton.grid(row=1, column=2, sticky="NESW")

        #Whether or not data is being recieved
        self.receiving = False

        #Setup parts for the scrolling canvas
        self.fileCanvas = None
        self.fileScroll = None
        self.fileGridFrame = None
        self.fileButtons = []
        self.fileCanvasWindow = None

        #If the device is currently connected
        self.connected = False
        #Current connected port name
        self.connectedPort = ""
        #Index of currently selected file
        self.selectedFile = -1

        #Object to hold serial connection to port
        self.serialConnection = None

        #List of available port names
        self.portLabels = []

        #Button colours
        self.defaultButtonColour = self.connectButton.cget("bg")
        self.selectedButtonColour = "#70D070"

        #List of available files (for testing)
        self.files = []
        for i in range(1, 80):
            self.files.append("File Number " + str(i))

        #Perform a first time scan
        self.scanPressed()

        #Perfom setup and set down of files to correctly size all elements
        self.setupFiles(self.files)
        self.setdownFiles()

    def connectPressed(self) -> None:
        '''Attempt to connect to selected port'''
        #If a connection does not already exist
        if not self.connected:
            #self.setupFiles(self.files)
            #If the current port selected exists
            if self.portLabels.index(self.selectedPort.get()) > 0:
                #Set the port of the connection
                self.connectedPort = self.selectedPort.get()
                success = True
                try:
                    #Attempt to connect
                    self.serialConnection = serial.Serial(port=self.connectedPort, baudrate=115200)
                except:
                    #If something went wrong
                    success = False
            
                if success:
                    #Switch buttons to enable disconnect and disable connect
                    self.connectButton.configure(state="disabled")
                    self.connected = True
                    self.disconnectButton.configure(state="normal")
                    self.portOption.configure(state="disabled")
                    self.scanButton.configure(state="disabled")
                    self.toggleButton.configure(state="normal")
                    #Display connected message
                    messagebox.showinfo(title="Success", message="Connected to port successfully.")
                    #Start reading from the port
                    readThread = Thread(target=self.readSerial, daemon=True)
                    readThread.start()
                else:
                    #Connection failed - reset
                    self.connected = False
                    #Allow for connect to be pressed and disable disconnect
                    self.connectButton.configure(state="normal")
                    self.disconnectButton.configure(state="disabled")
                    self.portOption.configure(state="normal")
                    self.scanButton.configure(state="normal")
                    self.toggleButton.configure(state="disabled")
                    #Not currently connected to a port
                    self.connectedPort = ""
                    #Display message to user
                    messagebox.showinfo(title="Failed", message="Failed to connect to port, you may need to scan again to check the port is available.")
    
    def scanPressed(self) -> None:
        '''Perform a scan of available ports and update option list accordingly (Windows only)'''
        #List to contain available ports
        found = ["No Port Selected"]
        #Iterate through port numbers
        for portNum in range(1, 255):
            try:
                #Construct the port name
                portName = "COM" + str(portNum)
                #Attempt to connect
                s = serial.Serial(portName)
                #Close the connection
                s.close()
                #Add port to available list
                found.append(portName)
            except:
                #If something went wrong then the port doesn't exist and it won't be added to the list
                pass
        
        #Update labels
        self.portLabels = found

        #Delete the old menu options
        menu = self.portOption["menu"]
        menu.delete(0, tkinter.END)
        #Iterate through labels
        for name in self.portLabels:
            #Add the labels to the list
            menu.add_command(label=name, command=lambda v=self.selectedPort, l=name: v.set(l))

        #Set selected option to none
        self.selectedPort.set(self.portLabels[0])

    def togglePressed(self) -> None:
        '''When button pressed to start/stop communications'''
        #If there is acually a connection
        if self.connected and self.serialConnection != None:
            #If currently recieving data
            if self.receiving:
                #Send the stop message
                self.serialConnection.write("stop\n".encode("utf-8"))
                #Switch the button to start mode
                self.toggleButton.configure(text="Start")
            else:
                #Send the start message
                self.serialConnection.write("start\n".encode("utf-8"))
                #Switch the button to stop mode
                self.toggleButton.configure(text="Stop")
            
            #Invert the receiving state
            self.receiving = not self.receiving
        else:
            #If no connection present - display error message (Outside case but catches errors)
            messagebox.showinfo(title="Not Connected", message="You must be connected to a port to toggle the message state.")

    def readSerial(self) -> None:
        '''While connected repeatedly read information from serial connection'''
        #If there is a connection
        if self.connected and self.serialConnection != None:
            #Attempt
            try:
                done = False
                #Until out of data
                while not done:
                    #Read the next character
                    chars = self.serialConnection.read()
                    #If there is a character
                    if len(chars) > 0:
                        try:
                            #Attempt from byte to string and pring
                            print(chars.decode("utf-8"), end="")
                        except:
                            #If it failed an unusual escape character has been read and it is simply ignored
                            pass
                    else:
                        #Finished reading - end of stream reached
                        done = True
                
                #Repeat this read function after 10ms
                self.after(10, self.readSerial)
            except:
                #Close the connection and reset the buttons
                self.serialConnection.close()
                self.serialConnection = None
                self.connected = False
                self.disconnectButton.configure(state="disabled")
                self.connectButton.configure(state="normal")
                self.portOption.configure(state="normal")
                self.scanButton.configure(state="normal")
                self.toggleButton.configure(state="disabled")
                #Display message to user to indicate that connection was lost (Occurs when device unplugged)
                messagebox.showinfo(title="Connection Lost", message="Connection to device was lost, please check connection and try again.")

    def filePressed(self, index : int) -> None:
        '''When a file is clicked on'''
        #If this is the currently selected file
        if index == self.selectedFile:
            #If it is a valid index
            if index > -1 and index < len(self.fileButtons):
                #Reset button colour to default
                self.fileButtons[index].configure(bg=self.defaultButtonColour)
            #Reset selected file index and label
            self.selectedFile = -1
            self.fileLabel.configure(text="No file selected")
        else:
            #If the index is valid
            if index < len(self.files):
                #If there is currently a selected file
                if self.selectedFile != -1:
                    #Deselect current file
                    self.fileButtons[self.selectedFile].configure(bg=self.defaultButtonColour)
                #Select new file
                self.selectedFile = index
                self.fileLabel.configure(text=self.files[index])
                #Enable button actions
                self.downloadFileButton.configure(state="normal")
                self.deleteFileButton.configure(state="normal")
                self.fileButtons[index].configure(bg=self.selectedButtonColour)

    def disconnectPressed(self) -> None:
        '''Close connection to port'''
        #If there is a connection
        if self.connected:
            #If there is a serial connection object
            if self.serialConnection != None:
                #Close the connection
                self.serialConnection.close()
                self.serialConnection = None
            #Switch buttons so disconnect is disabled and connect is enabled
            self.disconnectButton.configure(state="disabled")
            self.connected = False
            self.connectButton.configure(state="normal")
            self.portOption.configure(state="normal")
            self.scanButton.configure(state="normal")
            self.toggleButton.configure(state="disabled")
            #Display message to indicate that the connection has been closed
            messagebox.showinfo(title="Connection Closed", message="The connection has been terminated successfully.")

    def setdownFiles(self) -> None:
        '''Remove all file buttons from scroll section'''
        #If there is currently a selected file
        if self.selectedFile != -1:
            #Deselect the file
            self.filePressed(self.selectedFile)

        #Delete the canvas and scroll bar
        self.fileCanvas.destroy()
        self.fileScroll.destroy()

        #Reset all variables holding information about the section
        self.fileCanvas = None
        self.fileScroll = None
        self.fileGridFrame = None
        self.fileButtons = []
        self.fileCanvasWindow = None

    def setupFiles(self, fileNames : list) -> None:
        '''Set up the scrollable button section of each file given a list of file names'''

        #Create canvas and scroll bar
        self.fileCanvas = tkinter.Canvas(self.fileFrame)
        self.fileScroll = tkinter.Scrollbar(self.fileFrame, orient="vertical", command=self.fileCanvas.yview)

        #Add canvas and scroll bar to the frame
        self.fileCanvas.pack(side="left", expand=True, fill="both")
        self.fileScroll.pack(side="right", fill="y")

        #Create grid to hold the buttons
        self.fileGridFrame = tkinter.Frame(self.fileCanvas)
        
        #Configure the grid on the frame so it has the correct weighting and size for each file (1 column and as many rows as files)
        self.fileGridFrame.grid_columnconfigure(0, weight=1)
        for row in range(0, len(fileNames)):
            self.fileGridFrame.grid_rowconfigure(row, minsize=70)
        
        #Reset list that will store the buttons references
        self.fileButtons = []

        #Iterate through the file names
        for nameId in range(0, len(fileNames)):
            #Create a button and add it to the list
            button = tkinter.Button(self.fileGridFrame, text=fileNames[nameId], relief="groove", command=lambda x=nameId: self.filePressed(x))
            button.grid(row=nameId, column=0, sticky="NESW")
            self.fileButtons.append(button)

        #Create a window in the canvas to display the frame of buttons
        self.fileCanvasWindow = self.fileCanvas.create_window(0, 0, window=self.fileGridFrame, anchor="nw")

        #Setup the resizing commands on the canvas and frame
        self.fileGridFrame.bind("<Configure>", self.onFrameConfigure)
        self.fileCanvas.bind("<Configure>", self.frameWidth)

        #Update the initial size on the canvas (so it looks correct on first load)
        self.fileCanvas.update_idletasks()

        #Add enter and leave mousewheel binding so it can be scrolled
        self.fileGridFrame.bind("<Enter>", self.bindMouseWheel)
        self.fileGridFrame.bind("<Leave>", self.unbindMouseWheel)
        
        #Setup bounding box and scroll region so the scrolling works correctly
        self.fileCanvas.configure(scrollregion=self.fileCanvas.bbox("all"), yscrollcommand=self.fileScroll.set)
    
    def onFrameConfigure(self, event) -> None:
        '''Event called when canvas frame resized'''
        #Update canvas bounding box
        self.fileCanvas.configure(scrollregion=self.fileCanvas.bbox("all"))

    def frameWidth(self, event) -> None:
        '''Event called when canvas resized'''
        canvasWidth = event.width
        #Update size of window on canvas
        self.fileCanvas.itemconfig(self.fileCanvasWindow, width=canvasWidth)
    
    def bindMouseWheel(self, event) -> None:
        '''Add mouse wheel binding to canvas'''
        if self.fileCanvas != None:
            self.fileCanvas.bind_all("<MouseWheel>", self.mouseWheelMove)

    def unbindMouseWheel(self, event) -> None:
        '''Remove mouse wheel binding from canvas'''
        if self.fileCanvas != None:
            self.fileCanvas.unbind_all("<MouseWheel>")

    def mouseWheelMove(self, event) -> None:
        '''Change y scroll position when mouse wheel moved'''
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