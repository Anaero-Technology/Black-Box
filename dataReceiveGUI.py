import tkinter
from tkinter import messagebox, simpledialog, filedialog
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
        self.connectButton.grid(row=0, column=2, columnspan=2, sticky="NESW")

        #Add label for selected file name
        self.fileLabel = tkinter.Label(self, text="No file selected")
        self.fileLabel.grid(row=3, column=0, columnspan=2, sticky="NESW")

        #Add download file button
        self.downloadFileButton = tkinter.Button(self, text="Download", state="disabled", command=self.downloadPressed)
        self.downloadFileButton.grid(row=3, column=2, sticky="NESW")

        #Add delete file button
        self.deleteFileButton = tkinter.Button(self, text="Delete", state="disabled", command=self.deletePressed)
        self.deleteFileButton.grid(row=3, column=3, sticky="NESW")

        #Add a frame to put the list of files into
        self.fileFrame = tkinter.Frame(self, bg="#FFFFFF")
        self.fileFrame.grid(row=2, column=0, columnspan=4, sticky="NESW")

        #Add a button to initiate reading and storing the data from the arduino
        self.toggleButton = tkinter.Button(self, text="No Port", command=self.togglePressed, state="disabled")
        self.toggleButton.grid(row=1, column=2, sticky="NESW")

        #Add a button to open the file structure of the esp flash memory
        self.openFilesButton = tkinter.Button(self, text="No Port", command=self.fileTogglePressed, state="disabled")
        self.openFilesButton.grid(row=1, column=3, sticky="NESW")

        #Add a label for the currently connected port
        self.openPortLabel = tkinter.Label(self, text="Not connected")
        self.openPortLabel.grid(row=1, column=0, columnspan=2, sticky="NESW")

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
        self.files = ["File Number 1", "File Number 2"]
        self.fileSizes = []

        #Perform a first time scan
        self.performScan()

        #Perfom setup and set down of files to correctly size all elements
        self.setupFiles(self.files, True)
        self.setdownFiles()

        #The message that is being read
        self.currentMessage = ""
        #If waiting for a response from the esp32 (possibly add a timeout)
        self.awaiting = False
        self.downloading = False

        #If the file display is currently open
        self.filesOpen = False

        #List of accepted characters for file names as a string
        self.acceptedChars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijlkmnopqrstuvwxyz-_"

        #Name of file being saved to
        self.fileNameToSave = ""
        #Information being saved to the file
        self.fileDataToSave = ""

        #If still waiting for first response
        self.awaitingCommunication = False
        #Timeout timers
        self.timesTried = 0
        self.timeoutAttempts = 10

        #Valid file save types
        self.fileTypes = [("CSV Files", "*.csv")]

    def checkConnection(self) -> None:
        '''Check if a connection has been made repeatedly until timeout'''
        #If still waiting
        if self.awaitingCommunication:
            #If timeout has been reached or exceeded
            if self.timesTried >= self.timeoutAttempts:
                #Close the connection and reset the buttons
                self.serialConnection.close()
                self.serialConnection = None
                self.connected = False
                self.awaiting = False
                self.awaitingCommunication = False
                if self.filesOpen:
                    self.setdownFiles()
                self.connectButton.configure(text="Connect", command=self.connectPressed)
                self.portOption.configure(state="normal")
                self.toggleButton.configure(state="disabled", text="No Port")
                self.openFilesButton.configure(state="disabled", text="No Port")
                self.openPortLabel.configure(text="Not Connected")
                #Display message to user to indicate that connection was lost (Occurs when connecting to a port that does is not connected to esp)
                messagebox.showinfo(title="Connection Failed", message="Connection could not be established, please check this is correct port and try again.")
                self.performScan()
            else:
                #Increment timeout
                self.timesTried = self.timesTried + 1
                #Test again in .5 seconds
                self.after(500, self.checkConnection)

    def sendInfoRequest(self) -> None:
        '''Send the initial request for communication (in function so that it can be delayed)'''
        #If there is a connection
        if self.connected and self.serialConnection != None:
            #Send the information request
            self.serialConnection.write("info\n".encode("utf-8"))

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
                    self.serialConnection = serial.Serial(port=self.connectedPort, baudrate=115200, dsrdtr=True, rtscts=False)
                except:
                    #If something went wrong
                    success = False
            
                if success:
                    #Switch buttons to enable disconnect and disable connect
                    self.connectButton.configure(text="Disconnect", command=self.disconnectPressed)
                    self.connected = True
                    self.portOption.configure(state="disabled")
                    self.openPortLabel.configure(text="Port " + self.connectedPort)
                    self.openFilesButton.configure(state="disabled", text="Waiting")
                    #Do not allow action if waiting
                    self.awaiting = True
                    self.timesTried = 0
                    self.awaitingCommunication = True
                    self.checkConnection()
                    #Start reading from the port
                    readThread = Thread(target=self.readSerial, daemon=True)
                    readThread.start()
                    #Send connection information request after a short time - allows for boot messages to clear
                    self.after(200, self.sendInfoRequest)
                else:
                    #Connection failed - reset
                    self.connected = False
                    #Allow for connect to be pressed and disable disconnect
                    self.portOption.configure(state="normal")
                    self.toggleButton.configure(state="disabled", text="No Port")
                    self.openFilesButton.configure(state="disabled", text="No Port")
                    #Not currently connected to a port
                    self.connectedPort = ""
                    #Display message to user
                    messagebox.showinfo(title="Failed", message="Failed to connect to port, check the device is still connected and the port is available.")
                    self.performScan()
    
    def performScan(self) -> None:
        '''Perform a scan of available ports and update option list accordingly'''
        if not self.connected:
            #List to contain available ports
            found = ["No Port Selected"]
            #Scan to find all available ports
            portData = list_ports.comports()
            #Iterate through ports
            for data in portData:
                #Add the name of the port to the list (can be used to connect to it)
                found.append(data.name)
            
            #If the old and new lists are different
            different = False
            #Test if the lists are different lengths
            if len(found) != len(self.portLabels):
                different = True
            else:
                #Iterate through
                for item in found:
                    #Check if they contain the same things (order unimportant)
                    if item not in self.portLabels:
                        different = True

            #If there was a change
            if different:
                #Update labels
                self.portLabels = found

                #Delete the old menu options
                menu = self.portOption["menu"]
                menu.delete(0, tkinter.END)
                #Iterate through labels
                for name in self.portLabels:
                    #Add the labels to the list
                    menu.add_command(label=name, command=lambda v=self.selectedPort, l=name: v.set(l))

                #If the selected item is still available
                if self.selectedPort.get() in self.portLabels:
                    #Set the drop down value to what it was
                    self.selectedPort.set(self.selectedPort.get())
                else:
                    #Set selected option to none
                    self.selectedPort.set(self.portLabels[0])
            
            #Scan again shortly
            self.after(150, self.performScan)

    def togglePressed(self) -> None:
        '''When button pressed to start/stop communications'''
        #If there is acually a connection
        if self.connected and self.serialConnection != None:
            #If not currently waiting for a response from the esp32
            if not self.awaiting:
                #If currently recieving data
                if self.receiving:
                    #Send the stop message
                    self.serialConnection.write("stop\n".encode("utf-8"))
                    self.awaiting = True
                else:
                    #Ask for file name
                    fileName = simpledialog.askstring("Enter File Name To Store Data", "Enter file name (without extension)", parent=self)
                    #If a name was given
                    if fileName != None:
                        #Remove whitespace
                        fileName = fileName.replace(" ", "")
                        allowed = True

                        #Check characters were entered
                        if len(fileName) < 1:
                            allowed = False
                            messagebox.showinfo(title="Invalid File Name", message="File name must contain at least 1 character.")

                        #Check maximum name length
                        if len(fileName) > 26:
                            allowed = False
                            messagebox.showinfo(title="Invalid File Name", message="File name must not exceed 26 characters.")

                        #Check for invalid characters
                        for char in fileName:
                            if allowed:
                                if char not in self.acceptedChars:
                                    allowed = False
                                    messagebox.showinfo(title="Invalid File Name", message="File name must be alphanumeric, only hyphens and underscores are allowed.")
                        
                        #If the name is allowed to be used
                        if allowed:
                            startMessage = "start /" + fileName + ".txt\n"
                            #Send the start message
                            self.serialConnection.write(startMessage.encode("utf-8"))
                            self.awaiting = True
                            if self.filesOpen:
                                self.setdownFiles()
        else:
            #If no connection present - display error message (Outside case but catches errors)
            messagebox.showinfo(title="Not Connected", message="You must be connected to a port to toggle the message state.")

    def fileTogglePressed(self):
        '''Ask the esp32 for the list of held files'''
        #If opening the files
        if not self.filesOpen:
            #If there is a connection
            if self.connected and self.serialConnection != None:
                #If not currently running data collection
                if not self.receiving:
                    #If not waiting for a response
                    if not self.awaiting:
                        self.files = []
                        self.fileSizes = []
                        #Ask for the list of files
                        self.serialConnection.write("files\n".encode("utf-8"))
                        self.awaiting = True
                else:
                    messagebox.showinfo(title="Collection Running", message="Cannot access files while data collection is running.")
            else:
                messagebox.showinfo(title="Not Connected", message="You must be connected to a port to access the files.")
        else:
            #Close the files section
            self.setdownFiles()

    def deletePressed(self) -> None:
        '''Delete the currently selected file from the memory'''
        #If the connection is running
        if self.connected and self.serialConnection != None:
            #If the device is not collecting data
            if not self.receiving:
                #If not waiting for a response
                if not self.awaiting:
                    #If there is a file selected (and a valid one)
                    if self.selectedFile != -1 and len(self.files) > self.selectedFile:
                        #Ask for confirmation
                        confirm = messagebox.askyesno(title="Confirm Delete", message="Are you sure you want to delete " + self.files[self.selectedFile] + "?\nThis action cannot be undone.")
                        if confirm:
                            #Send signal to delete file
                            message = "delete " + self.files[self.selectedFile] + "\n"
                            self.serialConnection.write(message.encode("utf-8"))
                            #Wait for confirmation of deletion
                            self.awaiting = True
                    else:
                        messagebox.showinfo(title="No File Selected", message="Please select a file to delete.")
            else:
                messagebox.showinfo(title="Collection Running", message="Cannot delete files while data collection is running.")
        else:
            messagebox.showinfo(title="Not Connected", message="You must be connected to a port to delete files.")

    def downloadPressed(self) -> None:
        '''Send request to download the selected file to the computer'''
        #If there is a connection
        if self.connected and self.serialConnection != None:
            #If not currently collecting data
            if not self.receiving:
                #If not waiting for a response
                if not self.awaiting:
                    #If a file has been selected (and a valid one)
                    if self.selectedFile != -1 and len(self.files) > self.selectedFile:
                        #Default name to save file as - same as the file name on the esp32
                        defaultName = self.files[self.selectedFile][1:-4]
                        #Ask where to save the file
                        path = filedialog.asksaveasfilename(title="Save file location", filetypes=self.fileTypes, defaultextension=self.fileTypes, initialfile=defaultName)
                        #Remove whitespace
                        path = path.strip()
                        #If there is a file name
                        if path != None and path != "":
                            #If it doesn't have a .csv extension for some reason - then add one
                            if not path.endswith(".csv"):
                                path = path + ".csv"
                            #Store the save path
                            self.fileNameToSave = path
                            #Send message to download
                            message = "download " + self.files[self.selectedFile] + "\n"
                            self.serialConnection.write(message.encode("utf-8"))
                            self.awaiting = True
                    else:
                        messagebox.showinfo(title="No File Selected", message="Please select a file to download.")
            else:
                messagebox.showinfo(title="Collection Running", message="Cannot download files while data collection is running.")
        else:
            messagebox.showinfo(title="Not Connected", message="You must be connected to a port to download files.")

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
                    char = self.serialConnection.read()
                    #If there is a character
                    if len(char) > 0:
                        try:
                            #Attempt from byte to string and print
                            ch = char.decode("utf-8")
                            if ch == "\n":
                                self.messageReceived()
                                self.currentMessage = ""
                            else:
                                self.currentMessage = self.currentMessage + ch
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
                if self.filesOpen:
                    self.setdownFiles()
                self.connectButton.configure(text="Connect", command=self.connectPressed)
                self.portOption.configure(state="normal")
                self.toggleButton.configure(state="disabled", text="No Port")
                self.openFilesButton.configure(state="disabled", text="No Port")
                self.openPortLabel.configure(text="Not Connected")
                #Display message to user to indicate that connection was lost (Occurs when device unplugged)
                messagebox.showinfo(title="Connection Lost", message="Connection to device was lost, please check connection and try again.")
                self.performScan()

    def messageReceived(self):
        #DEBUG display the message
        print(self.currentMessage)
        #Split up the message into parts on spaces
        messageParts = self.currentMessage.split(" ")
        #If this is the information about the state of the esp32
        if len(messageParts) > 1 and messageParts[0] == "info":

            #If waiting for the response from the device
            if self.awaitingCommunication:
                #No longer waiting
                self.awaitingCommunication = False
                #Display connected message
                messagebox.showinfo(title="Success", message="Connected to port successfully.")
            
            #If the esp32 is collecting information
            if messageParts[1] == "1":
                #Set UI to correct states
                self.receiving = True
                self.toggleButton.configure(text="Stop", state="normal")
                self.openFilesButton.configure(text="Stop to open", state="disabled")
            else:
                #Set UI to state for allowing starting / interrogating
                self.receiving = False
                self.toggleButton.configure(text="Start", state="normal")
                self.openFilesButton.configure(text="Open Files", state="normal")
            
            #No longer waiting for a response
            self.awaiting = False
        
        #If an action has been successfully performed
        if len(messageParts) > 1 and messageParts[0] == "done":
            #Started receiving
            if messageParts[1] == "start":
                #Configure UI state
                self.receiving = True
                self.toggleButton.configure(text="Stop")
                self.openFilesButton.configure(text="Stop to open", state="disabled")
            #Stopped receiving
            if messageParts[1] == "stop":
                #Configure UI state
                self.receiving = False
                self.toggleButton.configure(text="Start")
                self.openFilesButton.configure(text="Open Files", state="normal")
            #Finished sending files
            if messageParts[1] == "files":
                #Display the files that were received
                self.setupFiles(self.files)

            #No longer waiting for a response
            self.awaiting = False

            #Finished deleting file
            if messageParts[1] == "delete":
                #Show message that files were deleted
                messagebox.showinfo(title="File Deleted", message="File was deleted sucessfully.")
                self.setdownFiles()
                self.fileTogglePressed()

        #If an action failed because it was already in a given state
        if len(messageParts) > 1 and messageParts[0] == "already":
            #Was already receiving data
            if messageParts[1] == "start":
                self.receiving = True
                self.toggleButton.configure(text="Stop")
                self.openFilesButton.configure(text="Stop to open", state="disabled")
                if self.filesOpen:
                    self.setdownFiles()
            #Was already stopped
            if messageParts[1] == "stop":
                self.receiving = False
                self.toggleButton.configure(text="Start")
                self.openFilesButton.configure(text="Open Files", state="normal")
            
            #No longer waiting for a response
            self.awaiting = False
        
        #If an action failed with an error message
        if len(messageParts) > 2 and messageParts[0] == "failed":
            #Attempting to start collecting
            if messageParts[1] == "start":
                #Display appropriate error message (invalid file names, some should not occur but are present in case they are needed)
                if messageParts[2] == "noname":
                    messagebox.showinfo(title="No File Name", message="A file name must be given to store the data in.")
                elif messageParts[2] == "namelength":
                    messagebox.showinfo(title="Name Too Long", message="The file name must have a maximum of 28 characters.")
                elif messageParts[2] == "invalidname":
                    messagebox.showinfo(title="Invalid File Name", message="The file name must not contain any special chatacters.")
                elif messageParts[2] == "alreadyexists":
                    messagebox.showinfo(title="File Already Exists", message="A file with that name already exists, please choose a different name or delete the existing file.")
                elif messageParts[2] == "nofiles":
                    messagebox.showinfo(title="File System Failed", message="The file system failed, please restart esp32 and try again.")
                #Set UI for stopped
                self.receiving = False
                self.toggleButton.configure(text="Start")
                self.openFilesButton.configure(text="Open Files", state="normal")
            if messageParts[1] == "stop":
                if messageParts[2] == "nofiles":
                    messagebox.showinfo(title="File System Failed", message="The file system failed, please reconnect esp32 and try again.")
            if messageParts[1] == "download":
                if messageParts[2] == "nofile":
                    messagebox.showinfo(title="File Not Found", message="The requested file could not be found, download stopped.")
                self.downloading = False
            if messageParts[1] == "delete":
                if messageParts[2] == "nofile":
                    messagebox.showinfo(title="File Not Found", message="The requested file could not be found, delete could not be completed.")
            
            #No longer waiting for a response
            self.awaiting = False

        #If it is a file name being given
        if len(messageParts) > 1 and messageParts[0] == "file":
            #If it is not the configuration file
            if messageParts[1] != "/setup.txt":
                #Add to the list
                self.files.append(messageParts[1])
                size = -1
                if len(messageParts) > 2:
                    try:
                        size = int(messageParts[2])
                    except:
                        pass
                self.fileSizes.append(size)

        
        #If it is part of the file download sequence
        if len(messageParts) > 1 and messageParts[0] == "download":
            #If it is a new file
            if len(messageParts) > 2 and messageParts[1] == "start":
                #Reset the file data
                self.fileDataToSave = ""
                #Currently downloading a file
                self.downloading = True
            #If it is the end of a file
            elif messageParts[1] == "stop":
                #Attempt to save the file
                try:
                    #Open the file to write
                    saveFile = open(self.fileNameToSave, "w")
                    #Write the data
                    saveFile.write(self.fileDataToSave)
                    #Close the file
                    saveFile.close()
                    #Success message
                    messagebox.showinfo(title="Download Successful", message="File successfully downloaded.")
                except:
                    #Something went wrong - failed message
                    messagebox.showinfo(title="Download Failed", message="File was not downloaded correctly, please try again.")
                
                #No longer downloading or waiting for a response
                self.downloading = False
                self.awaiting = False
            #Otherwise it is a line in the file (if currently expecting data)
            elif self.downloading:
                #Iterate through parts (except for first)
                for i in range(1, len(messageParts)):
                    #Remove any carriage returns
                    self.fileDataToSave = self.fileDataToSave + messageParts[i].replace("\r", "")
                    #If this is not the last in the message
                    if i != len(messageParts) - 1:
                        #Add a comma
                        self.fileDataToSave = self.fileDataToSave + ","
                    else:
                        #Add a new line
                        self.fileDataToSave = self.fileDataToSave + "\n"

        if len(messageParts) > 2 and messageParts[0] == "memory":
            try:
                total = int(messageParts[1])
                used = int(messageParts[2])
                percentage = int((used / total) * 100)
                total = int(total / 100000) / 10
                used = int(used / 100000) / 10
                message = "Port " + self.connectedPort + " " + str(used) + "/" + str(total) + "MB (" + str(percentage) + "%)"
                self.openPortLabel.configure(text=message)
            except:
                pass
                    
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
            self.downloadFileButton.configure(state="disabled")
            self.deleteFileButton.configure(state="disabled")
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
        #If there is a connection and there is not data to be recieved
        if self.connected and not self.awaiting:
            #If there is a serial connection object
            if self.serialConnection != None:
                #Close the connection
                self.serialConnection.close()
                self.serialConnection = None
            #Switch buttons so disconnect is disabled and connect is enabled
            self.connected = False
            if self.filesOpen:
                self.setdownFiles()
            self.connectButton.configure(text="Connect", command=self.connectPressed)
            self.portOption.configure(state="normal")
            self.toggleButton.configure(state="disabled", text="No Port")
            self.openFilesButton.configure(state="disabled", text="No Port")
            self.openPortLabel.configure(text="Not Connected")
            #Display message to indicate that the connection has been closed
            messagebox.showinfo(title="Connection Closed", message="The connection has been terminated successfully.")
            self.performScan()

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

        self.filesOpen = False
        self.openFilesButton.configure(text="Open Files")
        self.downloadFileButton.configure(state="disabled")
        self.deleteFileButton.configure(state="disabled")
        self.files = []

    def setupFiles(self, fileNames : list, first = False) -> None:
        '''Set up the scrollable button section of each file given a list of file names'''

        self.filesOpen = True
        #Create canvas and scroll bar
        self.fileCanvas = tkinter.Canvas(self.fileFrame, bg="#FFFFFF")
        self.fileScroll = tkinter.Scrollbar(self.fileFrame, orient="vertical", command=self.fileCanvas.yview)

        #Add canvas and scroll bar to the frame
        self.fileScroll.pack(side="right", fill="y")
        self.fileCanvas.pack(side="left", expand=True, fill="both")

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
            sizePart = ""
            if len(self.fileSizes) > nameId and self.fileSizes[nameId] != -1:
                size = self.fileSizes[nameId]
                if size / 1000000 > 1:
                    sizePart = str(int(size / 1000000)) + "MB"
                elif size / 1000 > 1:
                    sizePart = str(int(size / 1000)) + "KB"
                else:
                    sizePart = str(size) + "B"
            #Create a button and add it to the list
            button = tkinter.Button(self.fileGridFrame, text=fileNames[nameId] + "   " + sizePart, relief="groove", command=lambda x=nameId: self.filePressed(x))
            button.grid(row=nameId, column=0, sticky="NESW")
            self.fileButtons.append(button)

        #Create a window in the canvas to display the frame of buttons
        self.fileCanvasWindow = self.fileCanvas.create_window(0, 0, window=self.fileGridFrame, anchor="nw")

        #Setup the resizing commands on the canvas and frame
        self.fileGridFrame.bind("<Configure>", self.onFrameConfigure)
        self.fileCanvas.bind("<Configure>", self.frameWidth)
        self.frameWidth(None)

        #Update the initial size on the canvas (so it looks correct on first load)
        self.fileCanvas.update_idletasks()

        #Add enter and leave mousewheel binding so it can be scrolled
        self.fileGridFrame.bind("<Enter>", self.bindMouseWheel)
        self.fileGridFrame.bind("<Leave>", self.unbindMouseWheel)
        
        #Setup bounding box and scroll region so the scrolling works correctly
        self.fileCanvas.configure(scrollregion=self.fileCanvas.bbox("all"), yscrollcommand=self.fileScroll.set)
        
        self.openFilesButton.configure(text="Close Files")
    
    def onFrameConfigure(self, event) -> None:
        '''Event called when canvas frame resized'''
        #Update canvas bounding box
        self.fileCanvas.configure(scrollregion=self.fileCanvas.bbox("all"))

    def frameWidth(self, event) -> None:
        '''Event called when canvas resized'''
        #canvasWidth = event.width
        canvasWidth = self.fileCanvas.winfo_width()
        #Update size of window on canvas
        self.fileCanvas.itemconfig(self.fileCanvasWindow, width=canvasWidth - 1)
    
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
    root.minsize(400, 500)
    #Allow for expanding sizes
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    #Set the title text of the window
    root.title("GFM Data Receive")
    #Add the editor to the root windows
    mainWindow(root).grid(row = 0, column=0, sticky="NESW")
    #Start running the root
    root.mainloop()