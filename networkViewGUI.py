import tkinter
from tkinter import messagebox, simpledialog
import serial
from serial.tools import list_ports
from threading import Thread
import time

class MainWindow(tkinter.Frame):
    '''Class for the settings window toplevel'''
    def __init__ (self, parent, rw = None, *args, **kwargs):
        #Initialise parent class
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        
        #Object to hold serial connection information
        self.serialConnection = None;
        #Received message
        self.messages = []
        #The current message being received
        self.currentMessage = ""
        #List of ports, names, states and objects
        self.ports = []
        self.portNames = []
        self.portStates = []
        self.portObjects = []

        #The root window (of the main menu)
        self.rootWindow = rw

        #Frame to hold the list of ports
        self.listFrame = tkinter.Frame(self)
        #Frame to hold the update text
        self.updateFrame = tkinter.Frame(self)
        #Grid for update frame
        self.updateFrame.grid_rowconfigure(0, weight=1)
        self.updateFrame.grid_columnconfigure(0, weight=1)

        #Grid for main frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=10)
        self.grid_columnconfigure(0, weight=1)

        #Grid in both frames
        self.listFrame.grid(row=1, column=0, sticky="NESW")
        self.updateFrame.grid(row=0, column=0, sticky="NESW")

        #Canvas to hold and control scrolling region
        self.listCanvas = tkinter.Canvas(self.listFrame)
        #Scrollbar to control scrolling
        self.listScroll = tkinter.Scrollbar(self.listFrame, orient="vertical")

        #Frame to contain scrollable content
        self.listGridFrame = tkinter.Frame(self.listCanvas)

        #Current number of available rows
        self.rowsDone = 10

        #Configure the scrollable frame's grid
        self.listGridFrame.grid_columnconfigure(0, weight=1)
        for row in range(0, self.rowsDone):
            self.listGridFrame.grid_rowconfigure(row, minsize=60)

        #Create a window in the canvas using the frame
        self.listCanvasWindow = self.listCanvas.create_window(0, 0, window=self.listGridFrame, anchor="nw")

        #Update the canvas so it is correctly sized
        self.listCanvas.update_idletasks()

        #Bind the configures of the frame and canvas to update the windows
        self.listGridFrame.bind("<Configure>", self.onFrameConfigure)
        self.listCanvas.bind("<Configure>", self.frameWidth)
        self.frameWidth(None)

        #Bind the mouse enter and leave so the scroll wheel can be used to scroll
        self.listGridFrame.bind("<Enter>", self.bindMouseWheel)
        self.listGridFrame.bind("<Leave>", self.unbindMouseWheel)

        #Configure the scrollbar for the canvas
        self.listCanvas.configure(scrollregion=self.listCanvas.bbox("all"), yscrollcommand=self.listScroll.set)

        #Pack the canvas and scrollbar
        self.listScroll.pack(side="right", fill="y")
        self.listCanvas.pack(side="left", expand=True, fill="both")
        
        #Set the update text and place it in the frame
        self.updateText = tkinter.Label(self.updateFrame, text="No Devices Found, Try Reconnecting")
        self.updateText.grid(row=0, column=0, sticky="NESW")

        #Connection timeout
        self.timeout = 2000000000
        #Characters that can be used for names
        self.acceptedChars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijlkmnopqrstuvwxyz-_"

        #Port data to be added, updated and removed
        self.toAdd = []
        self.toUpdate = []
        self.toRemove = []

        #List of ports that should be checked for updates
        self.updateChecks = []

        #List of ports that have been checked and should not be checked again as they were not valid
        self.ignoreList = []

        #If currently scanning the ports
        self.scanning = True
        #If currently updating the ports
        self.updatingPorts = False
        #If currently transferring information
        self.communicating = False
        #If currently scanning the ports
        self.midScan = False

        #Make a check for any changes
        self.checkForPortChanges()

        #Create and start a thread to scan the ports regularly
        self.portScanThread = Thread(target=self.repeatedScan, daemon=True)
        self.portScanThread.start()

    def repeatedScan(self) -> None:
        '''Repeatedly scan the ports if possible'''
        #Unless scanning is terminated
        while self.scanning:
            #If not currently updating or transferring data
            if not self.updatingPorts and not self.communicating:
                #Perform a scan
                self.scanPorts()
                #Wait a tenth of a second
                time.sleep(0.1)
    
    def scanPorts(self) -> None:
        '''Scan the available ports and determine if anything needs to change'''
        #Starting scan - prevents multiple serial connections at once
        self.midScan = True
        #Get a list of the ports
        portObjects = list_ports.comports()
        portNames = []

        #Convert to port names
        for obj in portObjects:
            portNames.append(obj.device)

        #List of ports that need to be checked
        toTest = []

        #Iterate ports
        for port in portNames:
            #If the port is not known or ignored
            if port not in self.ports and port not in self.ignoreList:
                #Need to test that port
                toTest.append(port)

        #List of ports to remove
        toDel = []
        #Iterate through known ports
        for port in self.ports:
            #If the port is no longer available
            if port not in portNames:
                #Remove it from the list
                toDel.append(port)

        #List of ignored ports to forget
        toRemoveFromIgnore = []
        #Iterate through the ignored ports
        for port in self.ignoreList:
            #If the port is no longer available
            if port not in portNames:
                #Forget that port
                toRemoveFromIgnore.append(port)
        
        #Remove all the forgotten ports
        for item in toRemoveFromIgnore:
            self.ignoreList.remove(item)

        #If the port is scheduled for an update check
        for port in self.updateChecks:
            #If it isn't already being checked
            if port not in toTest:
                #Add it to the check list
                toTest.append(port)
        
        #Reset the update check list
        self.updateChecks = []
        
        #Iterate through ports needing to be tested
        for port in toTest:
            #Attempt to get the port info
            name, state = self.getPortInfo(port)
            #If it is unknown
            if port not in self.ports:
                #If info was received
                if name != None and state != None:
                    #Add it to the list of known ports
                    self.toAdd.append((port, name, state))
                else:
                    #If it is not already ignored
                    if port not in self.ignoreList:
                        #Add the port to list of ignored ports
                        self.ignoreList.append(port)
            else:
                #If info was received
                if name != None and state != None:
                    #Add it to the list of ports to be updated
                    self.toUpdate.append((port, name, state))
                else:
                    #If it is not ignored
                    if port not in self.ignoreList:
                        #Add to ignored list
                        self.ignoreList.append(port)
                    #If the port is known and not being removed
                    if port in self.ports and port not in self.toRemove:
                        #Remove the port
                        self.toRemove.append(port)
        
        #Iterate through the ports to be deleted
        for port in toDel:
            #If it is not already being removed
            if port not in self.toRemove:
                #Add to queue to remove
                self.toRemove.append(port)
            #If it is not ignored
            if port in self.ignoreList:
                #Add to ignored list
                self.ignoreList.remove(port)
        
        #No longer scanning
        self.midScan = False
    
    def checkForPortChanges(self) -> None:
        '''Check the lists for updates and change the interface to match'''
        #If not currently transferring data
        if not self.communicating:
            #Started updating the port information
            self.updatingPorts = True

            #Check if there are any changes to make
            changes = len(self.toAdd) > 0 or len(self.toUpdate) > 0 or len(self.toRemove) > 0

            #Iterate through ports that need adding
            for port in self.toAdd:
                #If it isn't already there
                if port[0] not in self.ports:
                    #Add the port
                    self.addPortToList(port[0], port[1], port[2])
            
            #Clear adding list
            self.toAdd = []

            #Iterate through updates
            for port in self.toUpdate:
                #Update the appropriate port
                self.updatePortInformation(port[0], port[1], port[2])

            #Clear update list
            self.toUpdate = []

            #Iterate through removals
            for port in self.toRemove:
                #If the port is known
                if port in self.ports:
                    #Remove the port
                    self.removePortFromList(port)

            #Clear the removal list
            self.toRemove = []
            
            #If a change was made
            if changes:
                #Update the display to show changes
                self.updatePortListDisplay()
            
            #Count the number of known devices
            numberDevices = len(self.ports)
            #If there are devices
            if numberDevices > 0:
                #If there is one device
                if numberDevices == 1:
                    #Singular message
                    self.updateText.configure(text="1 Device Connected")
                else:
                    #Multiple message
                    self.updateText.configure(text=str(numberDevices) + " Devices Connected")
            else:
                #None message
                self.updateText.configure(text="No Devices Found, Try Reconnecting")
        #No longer updating the ports
        self.updatingPorts = False
        #Repeat check in a tenth of a second
        self.after(100, self.checkForPortChanges)

    def getPortInfo(self, portCode : str) -> list:
        '''Attempt to get the info regarding a port'''
        connectedSuccessfully = True
        nameReceived = None
        stateReceived = None

        try:
            time.sleep(0.2)
            #Establish connection
            self.serialConnection = serial.Serial(port=portCode, baudrate=115200, dsrdtr=False, rtscts=False)
            #Start the reading thread
            readThread = Thread(target=self.readSerial, daemon=True)
            readThread.start()
            
            time.sleep(0.2)
        except:
            #Something went wrong
            connectedSuccessfully = False
        
        if connectedSuccessfully:
            #Clear incoming messages
            self.purgeMessages()
            #Ask for device information
            self.serialConnection.write("info\n".encode("utf-8"))
            done = False
            start = time.time_ns()
            #Repeat until complete or timeout reached
            while not done and start + self.timeout > time.time_ns():
                #If there are messages
                if len(self.messages) > 0:
                    #Pop first message
                    msg = self.messages[0]
                    del self.messages[0]
                    #Spilt into parts
                    msgParts = msg.split(" ")
                    if len(msgParts) > 0:
                        #If it is an info response
                        if msgParts[0] == "info":
                            if len(msgParts) > 1:
                                #Check what the logging state is
                                state = msgParts[1] == "1"

                                name = None
                                #If there is a name - store it
                                if len(msgParts) > 4:
                                    name = msgParts[4]
                                
                                #If there is a name
                                if name != None:
                                    #Correctly received - completed
                                    nameReceived = name
                                    stateReceived = state
                                    done = True
        
        #Disconnect from serial (if there is a connection)
        if self.serialConnection != None:
            self.serialConnection.close()
            self.serialConnection = None
        #If there was data received
        if nameReceived != None and stateReceived != None:
            #Return the information (port name is already known)
            return nameReceived, stateReceived
        
        #Failed - return Nones
        return None, None

    def addPortToList(self, portCode : str, portName : str, portState : bool, index = -1) -> None:
        '''Add a port to the interface, if index is given that is its place in the list (used for updates)'''
        #Create frame to hold items
        portObject = tkinter.Frame(self.listGridFrame, highlightthickness=4, highlightbackground="black")
        #Configure the frames rows and columns
        portObject.grid_rowconfigure(0, weight=1)
        for col in range(0, 5):
            portObject.grid_columnconfigure(col, weight=1)
        #Label for the port name
        codeLabel = tkinter.Label(portObject, text="Port:\n" + portCode)
        codeLabel.grid(row=0, column=0, sticky="NESW")
        #Label for the device name
        nameLabel = tkinter.Label(portObject, text="Name:\n" + portName)
        nameLabel.grid(row=0, column=1, sticky="NESW")
        #Start or stop button
        toggleButton = tkinter.Button(portObject, text="Start", command=lambda x = portCode: self.startPressed(x))
        if portState:
            toggleButton.configure(text="Stop", command=lambda x = portCode: self.stopPressed(x))
        toggleButton.grid(row=0, column=2, sticky="NESW")
        #Change name button
        nameChangeButton = tkinter.Button(portObject, text="Rename", command=lambda x = portCode: self.renamePressed(x))
        if portState:
            nameChangeButton.configure(state="disabled")
        nameChangeButton.grid(row=0, column=3, sticky="NESW")
        #Open window button
        openButton = tkinter.Button(portObject, text="Full View", command=lambda x = portCode: self.openPressed(x))
        openButton.grid(row=0, column=4, sticky="NESW")
        #If no index or an invalid index was given
        if index <= -1 or len(self.portObjects) <= index:
            #Add port to end
            self.ports.append(portCode)
            self.portNames.append(portName)
            self.portStates.append(portState)
            self.portObjects.append(portObject)
        else:
            #Add the port at the given index
            self.ports[index] = portCode
            self.portNames[index] = portName
            self.portStates[index] = portState
            self.portObjects[index] = portObject

    def removePortFromList(self, portCode : str) -> None:
        '''Remove the port object from the list'''
        #Get the id position
        portId = self.ports.index(portCode)
        #If it is a port
        if portId != -1:
            #Delete port data fromt the list
            del self.ports[portId]
            del self.portNames[portId]
            del self.portStates[portId]
            #Remove the object
            self.portObjects[portId].grid_remove()
            self.portObjects[portId].destroy()
            del self.portObjects[portId]

    def updatePortListDisplay(self) -> None:
        '''Update the displayed ports'''
        #If there are not enough rows
        if len(self.portObjects) > self.rowsDone:
            #Iterate rows
            for row in range(self.rowsDone, len(self.portObjects)):
                #Configure the extra rows
                self.grid_rowconfigure(row, weight=1)
            self.rowsDone = len(self.portObjects)
        
        #Iterate through the objects
        for index in range(0, len(self.portObjects)):
            #Remove them from the grid
            self.portObjects[index].grid_remove()
        #Iterate through the objects
        for index in range(0, len(self.portObjects)):
            #Add them back to the grid
            self.portObjects[index].grid(row=index, column=0, sticky="NESW")
    
    def updatePortInformation(self, portCode : str, portName : str, portState : bool) -> None:
        '''Update the data of a known port'''
        #Get the id for the port (index)
        portId = self.ports.index(portCode)
        #If the port exists
        if portId != -1:
            #Change the values
            self.portNames[portId] = portName
            self.portStates[portId] = portState
            self.portObjects[portId].grid_remove()
            self.portObjects[portId].destroy()
            #Add the port to the list with the given position
            self.addPortToList(portCode, portName, portState, portId)

    def readSerial(self) -> None:
        '''Read the incoming characters from the serial connection'''
        #If there is a connection
        if self.serialConnection != None:
            try:
                done = False
                #Repeat until out of characters
                while not done:
                    #Read the character
                    char = self.serialConnection.read()
                    #If there were characters
                    if len(char) > 0:
                        try:
                            #Decode to utf-8 text
                            ch = char.decode("utf-8")
                            #If it is a newline
                            if ch == "\n":
                                #Add to received messages and clear message
                                self.messages.append(self.currentMessage)
                                self.currentMessage = ""
                            else:
                                #If it isnt a line feed (prevents extra characters)
                                if ch not in ['\r']:
                                    #Add character to message
                                    self.currentMessage = self.currentMessage + ch
                        except:
                            pass
                    else:
                        done = True
                
                #Repeat after short delay
                self.after(10, self.readSerial)
            except:
                #Stops if there is no connection
                pass

    def purgeMessages(self) -> None:
        '''Clear all incoming messages'''
        self.messages = []
        self.currentMessage = ""

    def startPressed(self, portCode : str) -> None:
        '''Start button pressed on port'''
        #Prevent multiple button presses
        if not self.communicating:
            self.communicating = True
            startTime = time.time_ns()
            #Wait unti no longer updating or scanning (for timeout)
            while (self.updatingPorts or self.midScan) and startTime + self.timeout > time.time_ns():
                pass
            #If allowed to communicate
            if not self.updatingPorts and not self.midScan:
                #Get the file name to store
                fileName = simpledialog.askstring("Enter File Name To Store Data", "Enter file name (without extension)", parent=self)
                #If a name was given
                if fileName != None:
                    #Remove whitespace
                    fileName = fileName.replace(" ", "")
                    allowed = True

                    #Check characters were entered
                    if len(fileName) < 1:
                        allowed = False
                        self.displayMessage("Invalid File Name", "File name must contain at least 1 character.")

                    #Check maximum name length
                    if len(fileName) > 26:
                        allowed = False
                        self.displayMessage("Invalid File Name", "File name must not exceed 26 characters.")

                    #Check for invalid characters
                    for char in fileName:
                        if allowed:
                            if char not in self.acceptedChars:
                                allowed = False
                                self.displayMessage("Invalid File Name", "File name must be alphanumeric, only hyphens and underscores are allowed.")
                    
                    #Add extensions
                    fileName = "/" + fileName + ".txt"

                    #If the analyser is being used
                    gasAnalysis = False

                    if allowed:
                        #Ask if the user wants to use the analyser
                        gasAnalysis = messagebox.askyesno(title="Use Gas Analyser?", message="Would you like to collect information from a connected gas analyser? Please make sure the analyser is connected if you want to use it.")

                    #If the name is allowed to be used and an answer was given to gas analysis
                    if allowed:
                        #Construct message to send
                        message = "start " + fileName + " " + str(gasAnalysis).lower() + "\n"
                        success = True
                        try:
                            #Open serial connection
                            self.serialConnection = serial.Serial(port=portCode, baudrate=115200, dsrdtr=False, rtscts=False)
                            
                            #Start reading thread
                            readThread = Thread(target=self.readSerial, daemon=True)
                            readThread.start()
                        
                            time.sleep(0.6)
                        except:
                            success = False
                    
                        if success:
                            #Clear the messages
                            self.purgeMessages()
                            #Send the start message
                            self.serialConnection.write(message.encode("utf-8"))
                            done = False
                            start = time.time_ns()
                            #Repeatedly read until completed or timed out
                            while not done and start + self.timeout * 2 > time.time_ns():
                                #If there is a message
                                if len(self.messages) > 0:
                                    #Pop the message
                                    msg = self.messages[0]
                                    del self.messages[0]
                                    #Split into parts
                                    msgParts = msg.split(" ")
                                    if len(msgParts) > 1:
                                        #If this is a message about the start
                                        if msgParts[1] == "start":
                                            #Completed successfully
                                            if msgParts[0] == "done":
                                                self.displayMessage("Done", "Started logging successfully.")
                                                done = True
                                            #Error
                                            elif msgParts[0] == "failed":
                                                code = ""
                                                if len(msgParts) > 2:
                                                    code = "\nError : " + msgParts[2]
                                                #Report error message
                                                self.displayMessage("Failed", "Something went wrong, please try again." + code)
                                                done = True
                                            #Started already
                                            elif msgParts[0] == "already":
                                                self.displayMessage("Already Started", "The logger is already running.")
                                                done = True
                            
                            if not done:
                                #Did not receive a response
                                self.displayMessage("Timed out", "No response received, timeout occurred.")
                            
                            #Disconnect serial connection (if it was established)
                            if self.serialConnection != None:
                                self.serialConnection.close()
                                self.serialConnection = None
            else:
                #Could not connect
                self.displayMessage("Could Not Send", "Connection attempt timed out, please try again.")
            
            #Perform an update check on this port
            self.updateChecks.append(portCode)
            #No longer communicating
            self.communicating = False
    
    def stopPressed(self, portCode : str) -> None:
        '''Stop button pressed on port'''
        #Prevent multiple button presses
        if not self.communicating:
            self.communicating = True
            startTime = time.time_ns()
            #Wait for end of updates and scanning or for timeout
            while (self.updatingPorts or self.midScan) and startTime + self.timeout > time.time_ns():
                pass
            #If not updating or scanning
            if not self.updatingPorts and not self.midScan:
                #Construct message
                message = "stop\n"
                success = True
                try:
                    #Connect to serial
                    self.serialConnection = serial.Serial(port=portCode, baudrate=115200, dsrdtr=False, rtscts=False)
                    #Start reading thread
                    readThread = Thread(target=self.readSerial, daemon=True)
                    readThread.start()
                        
                    time.sleep(0.2)
                except:
                    success = False
                    
                if success:
                    #Clear message
                    self.purgeMessages()
                    #Send stop message
                    self.serialConnection.write(message.encode("utf-8"))
                    done = False
                    start = time.time_ns()
                    #Repeat until complete or timed out
                    while not done and start + self.timeout * 2 > time.time_ns():
                        #If there is a message
                        if len(self.messages) > 0:
                            #Pop the message
                            msg = self.messages[0]
                            del self.messages[0]
                            #Split into parts
                            msgParts = msg.split(" ")
                            if len(msgParts) > 1:
                                #If it is about the stop
                                if msgParts[1] == "stop":
                                    #Completed successfully
                                    if msgParts[0] == "done":
                                        self.displayMessage("Done", "Stopped logging successfully.")
                                        done = True
                                    #Error occurred
                                    elif msgParts[0] == "failed":
                                        code = ""
                                        if len(msgParts) > 2:
                                            code = "\nError : " + msgParts[2]
                                        #Display error message
                                        self.displayMessage("Failed", "Something went wrong, please try again." + code)
                                        done = True
                                    #Already stopped
                                    elif msgParts[0] == "already":
                                        self.displayMessage("Already Stopped", "The logger is not running.")
                                        done = True
                    
                    if not done:
                        #No response received
                        self.displayMessage("Timed out", "No response received, timeout occurred.")

                    #Disconnect serial connection if present
                    if self.serialConnection != None:
                        self.serialConnection.close()
                        self.serialConnection = None
            else:
                #Unable to send message another process blocked
                self.displayMessage("Could Not Send", "Connection attempt timed out, please try again.")
            
            #Check the port for updates
            self.updateChecks.append(portCode)
            #No longer communicating
            self.communicating = False

    def renamePressed(self, portCode : str) -> None:
        '''Rename button pressed on port'''
        #Prevent multiple button presses
        if not self.communicating:
            self.communicating = True
            extraString = ""
            #If the port is valid
            if portCode in self.ports:
                extraString = " : {0}".format(self.portNames[self.ports.index(portCode)])
            startTime = time.time_ns()
            #Wait until updates and scans are done or until timeout
            while (self.updatingPorts or self.midScan) and startTime + self.timeout > time.time_ns():
                pass
            #If not updating or scanning
            if not self.updatingPorts and not self.midScan:
                
                #Ask for a name
                newName = simpledialog.askstring("Rename", "Enter a new name for the device{0}.".format(extraString), parent=self)

                allowed = True
                #Cannot be nothing (or cancel pressed)
                if newName == None:
                    allowed = False

                #Remove spaces
                newName = newName.replace(" ", "")

                #If length requirement not met
                if allowed and len(newName) < 3:
                    allowed = False
                    #Display length error message
                    self.displayMessage("Enter A Name", "Name must be at least 3 characters without spaces.")
                
                if allowed:
                    #Iterate characters
                    for ch in newName:
                        #If there is an invalid character - it is not allowed
                        if ch not in self.acceptedChars:
                            allowed = False
                    
                    if not allowed:
                        #Display character error message
                        self.displayMessage("Invalid Name", "Name must be alphanumeric with hypens and underscores only.")

                if allowed:
                    #Construct message
                    message = "setName {0}\n".format(newName)
                    success = True
                    try:
                        #Establish serial connection
                        self.serialConnection = serial.Serial(port=portCode, baudrate=115200, dsrdtr=False, rtscts=False)
                        #Start reading thread
                        readThread = Thread(target=self.readSerial, daemon=True)
                        readThread.start()
                            
                        time.sleep(0.2)
                    except:
                        success = False
                        
                    if success:
                        #Clear the messages
                        self.purgeMessages()
                        #Write the message
                        self.serialConnection.write(message.encode("utf-8"))
                        time.sleep(0.2)
                    
                    #No response expected here

                    #Disconnect from serial (if present)
                    if self.serialConnection != None:
                        self.serialConnection.close()
                        self.serialConnection = None
                    
            else:
                #Blocked by another process
                self.displayMessage("Could Not Send", "Connection attempt timed out, please try again.")

            #Check the port for any changes
            self.updateChecks.append(portCode)
            #No longer communicating
            self.communicating = False

    def openPressed(self, portCode : str) -> None:
        '''If open button is pressed on a port'''
        #If not currently mid action
        if not self.communicating:
            try:
                #Open the communication window for the given port
                self.rootWindow.openCommunicationWindow(portCode)
            except:
                #Something went wrong - probably there is no parent window (occurrs when run standalone, impossible once packaged)
                self.displayMessage("Cannot Open", "Unable to open connection window, please try again or open the connection screen manually.")

    def displayMessage(self, title : str, message : str) -> None:
        '''Display a message box - slight shorthand'''
        messagebox.showinfo(title=title, message=message)

    def onFrameConfigure(self, event) -> None:
        '''Event called when canvas frame resized'''
        #Update canvas bounding box
        self.listCanvas.configure(scrollregion=self.listCanvas.bbox("all"))

    def frameWidth(self, event) -> None:
        '''Event called when canvas resized'''
        #canvasWidth = event.width
        canvasWidth = self.listCanvas.winfo_width()
        #Update size of window on canvas
        self.listCanvas.itemconfig(self.listCanvasWindow, width=canvasWidth - 1)
    
    def bindMouseWheel(self, event) -> None:
        '''Add mouse wheel binding to canvas'''
        if self.listCanvas != None:
            self.listCanvas.bind_all("<MouseWheel>", self.mouseWheelMove)

    def unbindMouseWheel(self, event) -> None:
        '''Remove mouse wheel binding from canvas'''
        if self.listCanvas != None:
            self.listCanvas.unbind_all("<MouseWheel>")

    def mouseWheelMove(self, event) -> None:
        '''Change y scroll position when mouse wheel moved'''
        if self.listCanvas != None:
            self.listCanvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


#Only run if this is the main module being run
if __name__ == "__main__":
    #Create root window for tkinter
    root = tkinter.Tk()
    #Calculate the position of the centre of the screen
    screenMiddle = [root.winfo_screenwidth() / 2, root.winfo_screenheight() / 2]
    #Set the shape of the window and place it in the centre of the screen
    root.geometry("600x500+{0}+{1}".format(int(screenMiddle[0] - 300), int(screenMiddle[1] - 250)))
    root.minsize(600, 500)
    #Allow for expanding sizes
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    #Set the title text of the window
    root.title("Network View")
    #Add the editor to the root windows
    MainWindow(root).grid(row = 0, column=0, sticky="NESW")
    #Start running the root
    root.mainloop()