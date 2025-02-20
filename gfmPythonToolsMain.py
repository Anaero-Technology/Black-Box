import tkinter
from tkinter import messagebox, simpledialog
import serial
from serial.tools import list_ports
from threading import Thread
import time
import os, sys
from PIL import Image, ImageTk
import pathlib
import processDataWizardGUI

class MainWindow(tkinter.Frame):
    '''Class for the settings window toplevel'''
    def __init__ (self, parent, rw = None, *args, **kwargs):
        #Initialise parent class
        tkinter.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.screenCentre = [self.parent.winfo_screenwidth() / 2, self.parent.winfo_screenheight() / 2]
        
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
        #self.portWifi = []
        #self.portSsids = []

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
        self.grid_rowconfigure(2, weight=3)
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

        self.buttonsFrame = tkinter.Frame(self)
        self.buttonsFrame.grid(row=2, column=0, sticky="NESW")
        self.buttonsFrame.grid_columnconfigure(0, weight=4)
        self.buttonsFrame.grid_columnconfigure(1, weight=1)
        self.buttonsFrame.grid_rowconfigure(0, weight=0)

        self.analysisButton = tkinter.Button(self.buttonsFrame, text="Analyse Data", font=("", 16), command=self.analysisButtonPressed)
        self.analysisButton.grid(row=0, column=0)

        self.analysisWindow = None

        self.settingsImage = tkinter.PhotoImage(file=self.pathTo("settingsIcon.png"))
        self.settingsButton = tkinter.Button(self.buttonsFrame, image=self.settingsImage, command=self.settingsButtonPressed)
        self.settingsButton.grid(row=0, column=1)

        self.settingsWindow = None

        #Connection timeouts
        self.timeout = 4000000000
        self.longTimeout = self.timeout * 8
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

        #Images used to display wifi state
        self.wifiIconOn = tkinter.PhotoImage(file=self.pathTo("wirelessIconOn.png"))
        self.wifiIconOff = tkinter.PhotoImage(file=self.pathTo("wirelessIconOff.png"))

        #Make a check for any changes
        self.checkForPortChanges()

        #Create and start a thread to scan the ports regularly
        self.portScanThread = Thread(target=self.repeatedScan, daemon=True)
        self.portScanThread.start()

    
    def pathTo(self, path):
        try:
            return os.path.join(sys._MEIPASS, path)
        except:
            return os.path.join(os.path.abspath("."), path)


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
        portObjects = list_ports.comports(include_links=True)
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
            #name, state, wifi, ssid = self.getPortInfo(port)
            name, state = self.getPortInfo(port)
            #If it is unknown
            if port not in self.ports:
                #If info was received
                if name != None and state != None:
                    #Add it to the list of known ports
                    #self.toAdd.append((port, name, state, wifi, ssid))
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
                    #self.toUpdate.append((port, name, state, wifi, ssid))
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
                    #self.addPortToList(port[0], port[1], port[2], port[3], port[4])
                    self.addPortToList(port[0], port[1], port[2])
            
            #Clear adding list
            self.toAdd = []

            #Iterate through updates
            for port in self.toUpdate:
                #Update the appropriate port
                #self.updatePortInformation(port[0], port[1], port[2], port[3], port[4])
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
        #wifiReceived = None
        #ssidReceived = None

        try:
            time.sleep(0.2)
            #Establish connection
            #self.serialConnection = serial.Serial(port=portCode, baudrate=115200, dsrdtr=False, rtscts=False)
            self.serialConnection = serial.Serial(port=portCode, baudrate=115200)
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
                                #wifi = None
                                #ssid = None
                                #If there is a name - store it
                                if len(msgParts) > 3:
                                    name = msgParts[3]
                                #If there is wifi data - store it
                                #if len(msgParts) > 5:
                                    #wifi = msgParts[4] == "wifion"
                                    #ssid = msgParts[5]
                                
                                #If there is a name
                                #if name != None and wifi != None and ssid != None:
                                if name != None:
                                    #Correctly received - completed
                                    nameReceived = name
                                    stateReceived = state
                                    #wifiReceived = wifi
                                    #ssidReceived = ssid
                                    done = True
        
        #Disconnect from serial (if there is a connection)
        if self.serialConnection != None:
            self.serialConnection.close()
            self.serialConnection = None
        #If there was data received
        if nameReceived != None and stateReceived != None:
            #Return the information (port name is already known)
            return nameReceived, stateReceived#, wifiReceived, ssidReceived
        
        #Failed - return Nones
        return None, None#, None, None

    #def addPortToList(self, portCode : str, portName : str, portState : bool, wifiState : bool, ssid : str, index = -1) -> None:
    def addPortToList(self, portCode : str, portName : str, portState : bool, index = -1) -> None:
        '''Add a port to the interface, if index is given that is its place in the list (used for updates)'''
        #Create frame to hold items
        portObject = tkinter.Frame(self.listGridFrame, highlightthickness=4, highlightbackground="black")
        #Configure the frames rows and columns
        portObject.grid_rowconfigure(0, weight=1)
        #for col in range(0, 7):
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
        #Icon defaults to disabled
        """wifiIcon = self.wifiIconOff
        #Wireless changes button
        options = ["Enable", "Change SSID", "Change Password"]
        #If the wifi is on
        if wifiState:
            #Switch to turn off and display 'on' symbol
            options[0] = "Disable"
            wifiIcon = self.wifiIconOn
        #Set the option being displayed
        portObject.optionVar = tkinter.StringVar()
        portObject.optionVar.set("WiFi")
        #Create drop down menu to select action
        wifiOption = tkinter.OptionMenu(portObject, portObject.optionVar, *options, command=lambda *args: self.wifiOptionPressed(portCode, portObject.optionVar))
        #Disable drop down indicator
        wifiOption.configure(indicatoron=False)
        wifiOption.grid(row=0, column=6, sticky="NSEW")
        #Display the state of the wifi
        wifiIndicator = tkinter.Button(portObject, text=ssid, image=wifiIcon, compound="top", state="disabled")
        wifiIndicator.grid(row=0, column=5, sticky="NESW")"""
        #If no index or an invalid index was given
        if index <= -1 or len(self.portObjects) <= index:
            #Add port to end
            self.ports.append(portCode)
            self.portNames.append(portName)
            self.portStates.append(portState)
            #self.portWifi.append(wifiState)
            #self.portSsids.append(ssid)
            self.portObjects.append(portObject)
        else:
            #Add the port at the given index
            self.ports[index] = portCode
            self.portNames[index] = portName
            self.portStates[index] = portState
            #self.portWifi[index] = wifiState
            #self.portSsids[index] = ssid
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
            #del self.portWifi[portId]
            #del self.portSsids[portId]
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
    
    #def updatePortInformation(self, portCode : str, portName : str, portState : bool, wifiState : bool, wifiSsid : str) -> None:
    def updatePortInformation(self, portCode : str, portName : str, portState : bool) -> None:
        '''Update the data of a known port'''
        #Get the id for the port (index)
        portId = self.ports.index(portCode)
        #If the port exists
        if portId != -1:
            #Change the values
            self.portNames[portId] = portName
            self.portStates[portId] = portState
            #self.portWifi[portId] = wifiState
            #self.portSsids[portId] = wifiSsid
            self.portObjects[portId].grid_remove()
            self.portObjects[portId].destroy()
            #Add the port to the list with the given position
            #self.addPortToList(portCode, portName, portState, wifiState, wifiSsid, portId)
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
                                if ch not in ['\r', '\0']:
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

                    #If the name is allowed to be used
                    if allowed:
                        #Construct message to send
                        message = "start " + fileName + "\n"
                        success = True
                        try:
                            #Open serial connection
                            self.serialConnection = serial.Serial(port=portCode, baudrate=115200)
                            
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
                            while not done and start + self.longTimeout > time.time_ns():
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
                    #self.serialConnection = serial.Serial(port=portCode, baudrate=115200, dsrdtr=False, rtscts=False)
                    self.serialConnection = serial.Serial(port=portCode, baudrate=115200)
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
                    while not done and start + self.longTimeout > time.time_ns():
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
                
                if allowed and newName != None:
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
                        #self.serialConnection = serial.Serial(port=portCode, baudrate=115200, dsrdtr=False, rtscts=False)
                        self.serialConnection = serial.Serial(port=portCode, baudrate=115200)
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

    def wifiOptionPressed(self, portCode : str, optionVar : tkinter.StringVar) -> None:
        '''When a wifi option is selected, perform the correct action'''
        #Get the selected option
        option = optionVar.get()
        #Reset the drop down - use it as a menu button rather than a multiple choice selection
        optionVar.set("WiFi")
        #Message to be sent to the device
        message = ""
        collectionRunning = False
        #If the port is known
        if portCode in self.ports:
            #Get the collecting state from the device
            index = self.ports.index(portCode)
            collectionRunning = self.portStates[index]

        #If enabling the WiFi
        if option == "Enable":
            message = "wifi enable\n"
        #If disabling the WiFi
        if option == "Disable":
            message = "wifi disable\n"
        #If requesting the change the device SSID
        if option == "Change SSID":
            #Check if running
            if not collectionRunning:
                #Ask user for new ssid
                givenSSID = simpledialog.askstring("Enter New SSID", "Enter the new SSID for this device.", parent=self)
                givenSSID.strip()
                givenSSID.replace(" ", "")
                allowed = True
                #If a value was given
                if givenSSID != "":
                    #If the value is too long
                    if len(givenSSID) > 31:
                        #Error message - too long
                        self.displayMessage("Invalid SSID", "SSID must be a maximum of 31 characters long.")
                        allowed = False
                    else:
                        #Check each character
                        for char in givenSSID:
                            if allowed:
                                #If the character is invalid
                                if char not in self.acceptedChars:
                                    #Error message - invalid characters
                                    self.displayMessage("Invalid SSID", "Please only use alphanumeric characters, underscores and hyphens.")
                                    allowed = False
                else:
                    #Error message - empty field
                    self.displayMessage("Invalid SSID", "Please ensure you enter an SSID.")
                    allowed = False
                
                #Check if allowed and store message
                if allowed:
                    message = "wifi rename " + givenSSID + "\n"
            else:
                #Error message - not possible while logging
                self.displayMessage("Cannot Change SSID", "SSID can only be changed when not logging.")
        #If requesting to change the password
        if option == "Change Password":
            #Check if running
            if not collectionRunning:
                #Ask user for new password
                givenPass = simpledialog.askstring("Enter New Password", "Enter the new password for this device.", parent=self)
                givenPass.strip()
                givenPass.replace(" ", "")
                allowed = True
                #If a value was entered
                if givenPass != "":
                    #If the value is too long
                    if len(givenPass) > 31:
                        #Error message - too long
                        self.displayMessage("Invalid Password", "Password must be a maximum of 31 characters long.")
                        allowed = False
                    else:
                        #Iterate through characters
                        for char in givenPass:
                            if allowed:
                                #If the character is not allowed
                                if char not in self.acceptedChars:
                                    #Error message - invalid characters
                                    self.displayMessage("Invalid Password", "Please only use alphanumeric characters, underscores and hyphens.")
                                    allowed = False
                else:
                    #Error message - empty field
                    self.displayMessage("Invalid Password", "Please ensure you enter a password.")
                    allowed = False

                #Check if allowed and store message
                if allowed:
                    message = "wifi newpass " + givenPass + "\n" 
            else:
                #Report not possible
                self.displayMessage("Cannot Change Password", "Password can only be changed when not logging.")

        #If a message is stored - valid input received
        if message != "":
            #Prevent multiple button presses
            if not self.communicating:
                self.communicating = True
                #Store start time of communication
                startTime = time.time_ns()
                #Wait for end of updates and scanning or for timeout
                while (self.updatingPorts or self.midScan) and startTime + self.timeout > time.time_ns():
                    pass
                #If not updating or scanning
                if not self.updatingPorts and not self.midScan:
                    success = True
                    try:
                        #Connect to serial
                        self.serialConnection = serial.Serial(port=portCode, baudrate=115200)
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
                        while not done and start + self.longTimeout > time.time_ns():
                            #If there is a message
                            if len(self.messages) > 0:
                                #Pop the message
                                msg = self.messages[0]
                                del self.messages[0]
                                #Split into parts
                                msgParts = msg.split(" ")
                                if len(msgParts) > 1:
                                    #If it is about the stop
                                    if msgParts[0] == "wifi":
                                        #Started WiFi correctly
                                        if msgParts[1] == "started":
                                            self.displayMessage("WiFi Started", "Started WiFi successfully.")
                                            done = True
                                        #Stopped WiFi correction
                                        if msgParts[1] == "stopped":
                                            self.displayMessage("WiFi Stopped", "Stopped WiFi successfully.")
                                            done = True
                                        #Could not start/stop as already in that state
                                        if msgParts[1] == "already":
                                            if msgParts[2] == "started":
                                                self.displayMessage("WiFi Already Started", "Could not start WiFi, it is already on.")
                                            if msgParts[2] == "stopped":
                                                self.displayMessage("WiFi Already Stopped", "Could not stop WiFi, it is already off.")
                                            done = True
                                        #Error / issue occurred
                                        if msgParts[1] == "failed" or (msgParts[1] == "unchanged" and msgParts[2] == "failed"):
                                            #Cannot change WiFi over wifi
                                            if msgParts[2] == "serialonly":
                                                self.displayMessage("WiFi Cannot Change", "Cannot change WiFi settings over WiFi.")
                                            else:
                                                #Other unknown issue occurred
                                                self.displayMessage("WiFi Failed", "Could not change WiFi settings, please try again.")
                                            done = True
                                        #Changed a value successfully
                                        if msgParts[1] == "changed":
                                            #SSID changed
                                            if msgParts[2] == "name":
                                               self.displayMessage("SSID Changed", "SSID has been successfully changed.")
                                               done = True
                                            #Password changed
                                            if msgParts[2] == "pass":
                                                self.displayMessage("Password Changed", "Password has been successfully changed.") 
                                                done = True
                                        #Failed to change a value
                                        if msgParts[1] == "unchanged":
                                            #No SIID value was given
                                            if msgParts[2] == "noname":
                                                self.displayMessage("No SSID Given", "A valid SSID must be entered.")
                                                done = True
                                            #No password value was given
                                            if msgParts[2] == "noPass":
                                                self.displayMessage("No Password Given", "A valid password must be entered.")
                                                done = True
                                            #Currently logging, SSID and password cannot be changed
                                            if msgParts[2] == "running":
                                                self.displayMessage("WiFi Cannot Change", "Cannot change WiFi while logging.")
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
        
        #Dissallow change to option menu
        return False

    def analysisButtonPressed(self) -> None:
        try:
            self.settingsWindow.lift()
            self.settingsWindow.focus()
        except:
            try:
                self.analysisWindow.lift()
                self.analysisWindow.focus()
            except:
                self.analysisWindow = tkinter.Toplevel(self.parent)
                self.analysisWindow.transient(self.parent)
                self.analysisWindow.geometry("850x650+{0}+{1}".format(int(self.screenCentre[0] - 425), int(self.screenCentre[1] - 325)))
                self.analysisWindow.minsize(850, 650)
                self.analysisWindow.title("Setup GFM")
                self.analysisWindow.grid_rowconfigure(0, weight=1)
                self.analysisWindow.grid_columnconfigure(0, weight=1)
                processDataWizardGUI.MainWindow(self.analysisWindow).grid(row=0, column=0, sticky="NESW")
                self.analysisWindow.focus()

    def settingsButtonPressed(self) -> None:
        try:
            self.analysisWindow.lift()
            self.analysisWindow.focus()
        except:
            try:
                self.settingsWindow.lift()
                self.settingsWindow.focus()
            except:
                self.settingsWindow = tkinter.Toplevel(self.parent)
                self.settingsWindow.transient(self.parent)
                self.settingsWindow.grid_columnconfigure(0, weight=1)
                self.settingsWindow.grid_rowconfigure(0, weight=1)
                self.settingsWindow.geometry("600x300+{0}+{1}".format(int(self.screenCentre[0] - 300), int(self.screenCentre[1] - 150)))
                self.settingsWindow.title("Settings")
                SettingsWindow(self.settingsWindow).grid(row=0, column=0, sticky="NESW")
                self.settingsWindow.focus()

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

class SettingsWindow(tkinter.Frame):
    '''Class for the settings window toplevel'''
    def __init__ (self, parent, *args, **kwargs):
        #Initialise parent class
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        
        #Setup internal grid
        self.grid_rowconfigure(0, weight=1)
        for col in range(0, 3):
            self.grid_columnconfigure(col, weight=1)

        #Colours to use for the highlighting
        self.defaultColour = self.cget("bg")
        self.selectedColour = "#AADDAA"

        #Create a font for the text
        self.headerFont = ("", 14)
        self.textFont = ("", 10)

        self.thisPath = os.path.abspath(".")
        try:
            self.thisPath = sys._MEIPASS
        except:
            pass

        #Section to hold comma separated option
        self.commaSection = tkinter.Frame(self)
        self.commaSection.grid(row=0, column=0, sticky="NSEW")
        #Section to hold semicolon separated option
        self.semicolonSection = tkinter.Frame(self)
        self.semicolonSection.grid(row=0, column=1, sticky="NSEW")
        #Section to hold custom separator option
        self.customSection = tkinter.Frame(self)
        self.customSection.grid(row=0, column=2, sticky="NSEW")
        #Set up rows for each
        for row in range(0, 4):
            self.commaSection.grid_rowconfigure(row, weight=1)
            self.semicolonSection.grid_rowconfigure(row, weight=1)
            self.customSection.grid_rowconfigure(row, weight=1)
        #Set up single column for each
        self.commaSection.grid_columnconfigure(0, weight=1)
        self.semicolonSection.grid_columnconfigure(0, weight=1)
        self.customSection.grid_columnconfigure(0, weight=1)

        #Create frame for inputing custom column separator
        self.customColumnFrame = tkinter.Frame(self.customSection)
        self.customColumnFrame.grid(row=1, column=0, sticky="NESW")
        self.customColumnFrame.grid_rowconfigure(0, weight=1)
        self.customColumnFrame.grid_rowconfigure(1, weight=1)
        self.customColumnFrame.grid_columnconfigure(0, weight=1)

        #Create frame for inputting custom decimal symbol
        self.customDecimalFrame = tkinter.Frame(self.customSection)
        self.customDecimalFrame.grid(row=2, column=0, sticky="NESW")
        self.customDecimalFrame.grid_rowconfigure(0, weight=1)
        self.customDecimalFrame.grid_rowconfigure(1, weight=1)
        self.customDecimalFrame.grid_columnconfigure(0, weight=1)
        
        #Comma separated text
        self.commaSeparatedHeader = tkinter.Label(self.commaSection, text="Comma Separated", font=self.headerFont)
        self.commaSeparatedColumn = tkinter.Label(self.commaSection, text="Column Separator: ,", font=self.textFont)
        self.commaSeparatedDecimal = tkinter.Label(self.commaSection, text="Decimal Point: .", font=self.textFont)
        self.commaSeparatedHeader.grid(row=0, column=0)
        self.commaSeparatedColumn.grid(row=1, column=0)
        self.commaSeparatedDecimal.grid(row=2, column=0)
        #Semicolon separated text
        self.semicolonSeparatedHeader = tkinter.Label(self.semicolonSection, text="Semicolon Separated", font=self.headerFont)
        self.semicolonSeparatedColumn = tkinter.Label(self.semicolonSection, text="Column Separator: ;", font=self.textFont)
        self.semicolonSeparatedDecimal = tkinter.Label(self.semicolonSection, text="Decimal Point: ,", font=self.textFont)
        self.semicolonSeparatedHeader.grid(row=0, column=0)
        self.semicolonSeparatedColumn.grid(row=1, column=0)
        self.semicolonSeparatedDecimal.grid(row=2, column=0)
        #Custom separated text
        self.customSeparatedHeader = tkinter.Label(self.customSection, text="Custom Separators", font=self.headerFont)
        self.customSeparatedColumn = tkinter.Label(self.customColumnFrame, text="Column Separator:", font=self.textFont)
        self.customSeparatedDecimal = tkinter.Label(self.customDecimalFrame, text="Decimal Point:", font=self.textFont)
        self.customSeparatedHeader.grid(row=0, column=0)
        self.customSeparatedColumn.grid(row=0, column=0)
        self.customSeparatedDecimal.grid(row=0, column=0)
        
        #Which option is selected
        self.selectorType = tkinter.IntVar()
        #Add radio buttons for each option
        self.separatorOptionComma = tkinter.Radiobutton(self.commaSection, variable=self.selectorType, value=0, command=lambda x=0: self.chooseSeparator(x))
        self.separatorOptionSemicolon = tkinter.Radiobutton(self.semicolonSection, variable=self.selectorType, value=1, command=lambda x=1: self.chooseSeparator(x))
        self.separatorOptionCustom = tkinter.Radiobutton(self.customSection, variable=self.selectorType, value=2, command=lambda x=2: self.chooseSeparator(x))
        self.separatorOptionComma.grid(row=3, column=0)
        self.separatorOptionSemicolon.grid(row=3, column=0)
        self.separatorOptionCustom.grid(row=3, column=0)

        #Values for custom separators
        self.customColumnEntryValue = tkinter.StringVar()
        self.customDecimalEntryValue = tkinter.StringVar()

        #Read the separators from the file
        self.readSeparators()
        #Widgets for custom separator entry
        self.customColumnEntry = tkinter.Entry(self.customColumnFrame, justify="center", width=3, textvariable=self.customColumnEntryValue)
        self.customColumnEntry.grid(row=1, column=0)
        self.customDecimalEntry = tkinter.Entry(self.customDecimalFrame, justify="center", width=3, textvariable=self.customDecimalEntryValue)
        self.customDecimalEntry.grid(row=1, column=0)

        #Add callback to check if input is valid
        self.separatorCheck = self.register(self.validateCustomSeparator)
        #Add validation to entries
        self.customColumnEntry.configure(validate="key", validatecommand=(self.separatorCheck, "%P"))
        self.customDecimalEntry.configure(validate="key", validatecommand=(self.separatorCheck, "%P"))

        #Setup which option is selected
        self.chooseSeparator(self.selectorType.get())

    def chooseSeparator(self, type : int) -> None:
        '''Update which option is chosen'''
        #Write the values to a file
        self.writeSeparators()
        #If comma is selected - highlight it and return the others to normal
        if type == 0:
            self.commaSection.configure(bg=self.selectedColour)
            self.commaSeparatedHeader.configure(bg=self.selectedColour)
            self.commaSeparatedColumn.configure(bg=self.selectedColour)
            self.commaSeparatedDecimal.configure(bg=self.selectedColour)
            self.separatorOptionComma.configure(bg=self.selectedColour)
            self.semicolonSection.configure(bg=self.defaultColour)
            self.semicolonSeparatedHeader.configure(bg=self.defaultColour)
            self.semicolonSeparatedColumn.configure(bg=self.defaultColour)
            self.semicolonSeparatedDecimal.configure(bg=self.defaultColour)
            self.separatorOptionSemicolon.configure(bg=self.defaultColour)
            self.customSection.configure(bg=self.defaultColour)
            self.customSeparatedHeader.configure(bg=self.defaultColour)
            self.customSeparatedColumn.configure(bg=self.defaultColour)
            self.customSeparatedDecimal.configure(bg=self.defaultColour)
            self.separatorOptionCustom.configure(bg=self.defaultColour)
            self.customColumnFrame.configure(bg=self.defaultColour)
            self.customDecimalFrame.configure(bg=self.defaultColour)
        #If semicolon is selected - highlight it and return the others to normal
        elif type == 1:
            self.commaSection.configure(bg=self.defaultColour)
            self.commaSeparatedHeader.configure(bg=self.defaultColour)
            self.commaSeparatedColumn.configure(bg=self.defaultColour)
            self.commaSeparatedDecimal.configure(bg=self.defaultColour)
            self.separatorOptionComma.configure(bg=self.defaultColour)
            self.semicolonSection.configure(bg=self.selectedColour)
            self.semicolonSeparatedHeader.configure(bg=self.selectedColour)
            self.semicolonSeparatedColumn.configure(bg=self.selectedColour)
            self.semicolonSeparatedDecimal.configure(bg=self.selectedColour)
            self.separatorOptionSemicolon.configure(bg=self.selectedColour)
            self.customSection.configure(bg=self.defaultColour)
            self.customSeparatedHeader.configure(bg=self.defaultColour)
            self.customSeparatedColumn.configure(bg=self.defaultColour)
            self.customSeparatedDecimal.configure(bg=self.defaultColour)
            self.separatorOptionCustom.configure(bg=self.defaultColour)
            self.customColumnFrame.configure(bg=self.defaultColour)
            self.customDecimalFrame.configure(bg=self.defaultColour)
        #If comma is selected - highlight it and return the others to normal
        elif type == 2:
            self.commaSection.configure(bg=self.defaultColour)
            self.commaSeparatedHeader.configure(bg=self.defaultColour)
            self.commaSeparatedColumn.configure(bg=self.defaultColour)
            self.commaSeparatedDecimal.configure(bg=self.defaultColour)
            self.separatorOptionComma.configure(bg=self.defaultColour)
            self.semicolonSection.configure(bg=self.defaultColour)
            self.semicolonSeparatedHeader.configure(bg=self.defaultColour)
            self.semicolonSeparatedColumn.configure(bg=self.defaultColour)
            self.semicolonSeparatedDecimal.configure(bg=self.defaultColour)
            self.separatorOptionSemicolon.configure(bg=self.defaultColour)
            self.customSection.configure(bg=self.selectedColour)
            self.customSeparatedHeader.configure(bg=self.selectedColour)
            self.customSeparatedColumn.configure(bg=self.selectedColour)
            self.customSeparatedDecimal.configure(bg=self.selectedColour)
            self.separatorOptionCustom.configure(bg=self.selectedColour)
            self.customColumnFrame.configure(bg=self.selectedColour)
            self.customDecimalFrame.configure(bg=self.selectedColour)

    def readSeparators(self) -> None:
        '''Read the separators from the file and assign to variables'''
        try:
            #Attempt to open the file and read
            optionPath = os.path.join(os.path.expanduser("~"), "AppData", "Local", "AnaeroGFM", "options.txt")
            settingsFile = open(optionPath, "r")
            data = settingsFile.read()
            settingsFile.close()
            data = data.split("\n")
            #Iterate through rows
            for row in data:
                #Remove excess whitespace
                row = row.strip()
                #Split into parts
                parts = row.split(" ")
                #If this is info about which option is selected
                if parts[0] == "selected:":
                    #Set the selector type to the value on that row
                    self.selectorType.set(int(parts[1]))
                #If this is info about the custom column separator
                if parts[0] == "column:":
                    #Check if the part is valid
                    if self.validateCustomSeparator(parts[1], True):
                        #Set the custom separator
                        self.customColumnEntryValue.set(parts[1])
                    else:
                        #If invalid - set as a comma
                        self.customColumnEntryValue.set(",")
                #If this is info about the custom decimal symbol
                if parts[0] == "decimal:":
                    #Check if the part is valid
                    if self.validateCustomSeparator(parts[1], True):
                        #Set custom decimal symbol
                        self.customDecimalEntryValue.set(parts[1])
                    else:
                        #If invalid - set as period
                        self.customDecimalEntryValue.set(".")

        except:
            #If something went wrong (file missing or invalid structure)
            #Default custom to comma separated
            self.customColumnEntryValue.set(",")
            self.customDecimalEntryValue.set(".")
            #Write the file
            self.writeSeparators()
    
    def writeSeparators(self) -> None:
        '''Write the separator options to a file'''
        #Create data with selected option and custom separators
        data = "selected: {0}\ncolumn: {1}\ndecimal: {2}\n".format(self.selectorType.get(), self.customColumnEntryValue.get(), self.customDecimalEntryValue.get())
        #Open the file
        optionPath = os.path.join(os.path.expanduser("~"), "AppData", "Local", "AnaeroGFM")
        pathlib.Path(optionPath).mkdir(parents=True, exist_ok=True)
        settingsFile = open(os.path.join(optionPath, "options.txt"), "w")
        #Write the data
        settingsFile.write(data)
        #Close the file
        settingsFile.close()

    def pathTo(self, path):
        return os.path.join(self.thisPath, path)
    
    def validateCustomSeparator(self, value, noSave = False) -> bool:
        '''Returns True if the given valus is a valid separator'''

        #If there is more than one character
        if len(value) > 1:
            #It is not valid
            return False

        #String of characters that cannot be used
        disallowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -"

        #If the value given is any of the characters in the string
        if any(d in value for d in disallowed):
            #It is not valid
            return False
        
        #If the separator matches the other separator given
        if self.customColumnEntryValue.get() == value or self.customDecimalEntryValue.get() == value:
            #It is not valid
            return False

        #Unless told to do so (when loading data)
        if not noSave:
            #Save the values into the file after a short delay (to allow for data to be stored in variables after validation)
            self.after(100, self.writeSeparators)

        #The separator is valid and the entry value can be updated
        return True

#Only run if this is the main module being run
if __name__ == "__main__":
    #Create root window for tkinter
    root = tkinter.Tk()
    #Calculate the position of the centre of the screen
    screenMiddle = [root.winfo_screenwidth() / 2, root.winfo_screenheight() / 2]
    #Set the shape of the window and place it in the centre of the screen
    root.geometry("750x600+{0}+{1}".format(int(screenMiddle[0] - 375), int(screenMiddle[1] - 250)))
    root.minsize(750, 600)
    #Allow for expanding sizes
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    #Set the title text of the window
    root.title("GFM Python Tools V2.0")
    #Add the editor to the root windows
    window = MainWindow(root)
    window.grid(row = 0, column=0, sticky="NESW")
    ico = Image.open(window.pathTo("icon.png"))
    photo = ImageTk.PhotoImage(ico)
    root.wm_iconphoto(True, photo)
    #Start running the root
    root.mainloop()