import tkinter
from tkinter import messagebox
import serial
from serial.tools import list_ports
from threading import Thread
import datetime

class mainWindow(tkinter.Frame):
    '''Class to contain all of the menus'''
    def __init__(self, parent, *args, **kwargs) -> None:
        #Setup parent configuration
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.numRows = 10
        self.numColumns = 13

        self.serialConnection = None
        self.portLabels = []
        self.connectedPort = ""
        self.currentMessage = ""
        self.receivedMessages = []
        self.awaiting = False
        self.awaitingCommunication = False
        self.timesTried = 0
        self.timeoutAttempts = 10

        self.running = False

        for row in range(0, self.numRows):
            self.grid_rowconfigure(row, weight = 1)
        
        for col in range(0, self.numColumns):
            self.grid_columnconfigure(col, weight = 1)

        self.day = tkinter.StringVar()
        self.day.set("1")
        self.month = tkinter.StringVar()
        self.month.set("1")
        self.year = tkinter.StringVar()
        self.year.set("2021")
        self.hour = tkinter.StringVar()
        self.hour.set("0")
        self.minute = tkinter.StringVar()
        self.minute.set("0")
        self.second = tkinter.StringVar()
        self.second.set("0")

        #Setup port drop down (with debug values)
        self.selectedPort = tkinter.StringVar()
        self.selectedPort.set("Port 1")
        self.portOption = tkinter.OptionMenu(self, self.selectedPort, "Port 1", "Port 2", "Port 3", "Port 4")
        self.portOption.grid(row=0, column=0, columnspan=8, sticky="NESW")

        #Add connect button
        self.connectButton = tkinter.Button(self, text="Connect", command=self.connectPressed)
        self.connectButton.grid(row=0, column=8, columnspan=5, sticky="NESW")

        self.messageLabel = tkinter.Label(self, text="", fg="red")
        self.messageLabel.grid(row = 1, column=0, columnspan=13, sticky="NESW")

        self.dayLabel = tkinter.Label(self, textvariable=self.day)
        self.dayLabel.grid(row=4, column=1, sticky="NESW")

        self.monthLabel = tkinter.Label(self, textvariable=self.month)
        self.monthLabel.grid(row=4, column=3, sticky="NESW")

        self.yearLabel = tkinter.Label(self, textvariable=self.year)
        self.yearLabel.grid(row=4, column=5, sticky="NESW")

        self.hourLabel = tkinter.Label(self, textvariable=self.hour)
        self.hourLabel.grid(row=4, column=7, sticky="NESW")

        self.minuteLabel = tkinter.Label(self, textvariable=self.minute)
        self.minuteLabel.grid(row=4, column=9, sticky="NESW")

        self.secondLabel = tkinter.Label(self, textvariable=self.second)
        self.secondLabel.grid(row=4, column=11, sticky="NESW")

        self.dmSlash = tkinter.Label(self, text="/")
        self.dmSlash.grid(row=4, column=2, sticky="NESW")
        self.mySlash = tkinter.Label(self, text="/")
        self.mySlash.grid(row=4, column=4, sticky="NESW")
        self.hmColon = tkinter.Label(self, text=":")
        self.hmColon.grid(row=4, column=8, sticky="NESW")
        self.msColon = tkinter.Label(self, text=":")
        self.msColon.grid(row=4, column=10, sticky="NESW")

        self.timeAsString = tkinter.StringVar()
        self.currentTimeDisplay = tkinter.Label(self, textvariable=self.timeAsString)
        self.currentTimeDisplay.grid(row=6, column=0, columnspan=13, sticky="NESW")

        self.dayUpButton = tkinter.Button(self, text="▲", command=lambda:self.adjustValues(0, 1))
        self.dayUpButton.grid(row=3, column=1, sticky="NESW")
        self.dayDownButton = tkinter.Button(self, text="▼", command=lambda:self.adjustValues(0, -1))
        self.dayDownButton.grid(row=5, column=1, sticky="NESW")

        self.monthUpButton = tkinter.Button(self, text="▲", command=lambda:self.adjustValues(1, 1))
        self.monthUpButton.grid(row=3, column=3, sticky="NESW")
        self.monthDownButton = tkinter.Button(self, text="▼", command=lambda:self.adjustValues(1, -1))
        self.monthDownButton.grid(row=5, column=3, sticky="NESW")

        self.yearUpButton = tkinter.Button(self, text="▲", command=lambda:self.adjustValues(2, 1))
        self.yearUpButton.grid(row=3, column=5, sticky="NESW")
        self.yearDownButton = tkinter.Button(self, text="▼", command=lambda:self.adjustValues(2, -1))
        self.yearDownButton.grid(row=5, column=5, sticky="NESW")

        self.hourUpButton = tkinter.Button(self, text="▲", command=lambda:self.adjustValues(3, 1))
        self.hourUpButton.grid(row=3, column=7, sticky="NESW")
        self.hourDownButton = tkinter.Button(self, text="▼", command=lambda:self.adjustValues(3, -1))
        self.hourDownButton.grid(row=5, column=7, sticky="NESW")

        self.minuteUpButton = tkinter.Button(self, text="▲", command=lambda:self.adjustValues(4, 1))
        self.minuteUpButton.grid(row=3, column=9, sticky="NESW")
        self.minuteDownButton = tkinter.Button(self, text="▼", command=lambda:self.adjustValues(4, -1))
        self.minuteDownButton.grid(row=5, column=9, sticky="NESW")

        self.secondUpButton = tkinter.Button(self, text="▲", command=lambda:self.adjustValues(5, 1))
        self.secondUpButton.grid(row=3, column=11, sticky="NESW")
        self.secondDownButton = tkinter.Button(self, text="▼", command=lambda:self.adjustValues(5, -1))
        self.secondDownButton.grid(row=5, column=11, sticky="NESW")

        self.validDate = True

        self.autoCheckValue = tkinter.IntVar()
        self.autoCheckValue.trace("w", callback=self.autoTimeToggled)
        self.autoCheckValue.set(1)
        self.autoCheckBox = tkinter.Checkbutton(self, text="System Time", variable=self.autoCheckValue, onvalue=1, offvalue=0)
        self.autoCheckBox.grid(row=7, column=4, columnspan=5, sticky="NESW")

        timeThread = Thread(target=self.getSystemTime, daemon=True)
        timeThread.start()

        self.getESPTimeButton = tkinter.Button(self, text="Get Time From Clock", command=self.getTimePressed)
        self.getESPTimeButton.grid(row=8, column=1, columnspan=5, sticky="NESW")

        self.setESPTimeButton = tkinter.Button(self, text="Set Clock Time", command=self.setTimePressed)
        self.setESPTimeButton.grid(row=8, column=7, columnspan=5, sticky="NESW")

        self.performScan()

    def getSystemTime(self):
        if self.autoCheckValue.get() == 1:
            currentTime = datetime.datetime.now()
            if self.day.get() != str(currentTime.day):
                self.day.set(str(currentTime.day))
            if self.month.get() != str(currentTime.month):
                self.month.set(str(currentTime.month))
            if self.year.get() != str(currentTime.year):
                self.year.set(str(currentTime.year))
            if self.hour.get() != str(currentTime.hour):
                self.hour.set(str(currentTime.hour))
            if self.minute.get() != str(currentTime.minute):
                self.minute.set(str(currentTime.minute))
            if self.second.get() != str(currentTime.second):
                self.second.set(str(currentTime.second))
            
            self.setTimeString()
        
        self.after(100, self.getSystemTime)

    def autoTimeToggled(self, *args):
        if self.autoCheckValue.get() == 1:
            self.dayUpButton.configure(state="disabled")
            self.dayDownButton.configure(state="disabled")
            self.monthUpButton.configure(state="disabled")
            self.monthDownButton.configure(state="disabled")
            self.yearUpButton.configure(state="disabled")
            self.yearDownButton.configure(state="disabled")
            self.hourUpButton.configure(state="disabled")
            self.hourDownButton.configure(state="disabled")
            self.minuteUpButton.configure(state="disabled")
            self.minuteDownButton.configure(state="disabled")
            self.secondUpButton.configure(state="disabled")
            self.secondDownButton.configure(state="disabled")
        else:
            self.dayUpButton.configure(state="normal")
            self.dayDownButton.configure(state="normal")
            self.monthUpButton.configure(state="normal")
            self.monthDownButton.configure(state="normal")
            self.yearUpButton.configure(state="normal")
            self.yearDownButton.configure(state="normal")
            self.hourUpButton.configure(state="normal")
            self.hourDownButton.configure(state="normal")
            self.minuteUpButton.configure(state="normal")
            self.minuteDownButton.configure(state="normal")
            self.secondUpButton.configure(state="normal")
            self.secondDownButton.configure(state="normal")

    def setTimeString(self):
        
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

        day = str(self.day.get())
        dayType = "th"
        if day[-1] == "1":
            dayType = "st"
        if day[-1] == "2":
            dayType = "nd"
        if day[-1] == "3":
            dayType = "rd"

        month = months[int(self.month.get()) - 1]

        hour = self.hour.get()
        if len(hour) < 2:
            hour = "0" + hour

        minute = self.minute.get()
        if len(minute) < 2:
            minute = "0" + minute
        
        second = self.second.get()
        if len(second) < 2:
            second = "0" + second

        message = day + dayType + " " + month + " " + self.year.get() + "  " + hour + ":" + minute + ":" + second

        self.timeAsString.set(message)
        self.checkValidDate()

    def adjustValues(self, column: int, change: int) -> None:
        if self.autoCheckValue.get() != 1:
            if column == 0:
                value = int(self.day.get()) + change
                if value > 31:
                    value = value - 31
                if value < 1:
                    value = value + 31
                self.day.set(str(value))
            if column == 1:
                value = int(self.month.get()) + change
                if value > 12:
                    value = value - 12
                if value < 1:
                    value = value + 12
                self.month.set(str(value))
            if column == 2:
                value = int(self.year.get()) + change
                if value < 0:
                    value = 0
                self.year.set(str(value))
            if column == 3:
                value = int(self.hour.get()) + change
                if value > 23:
                    value = value - 24
                if value < 0:
                    value = value + 24
                self.hour.set(str(value))
            if column == 4:
                value = int(self.minute.get()) + change
                if value > 59:
                    value = value - 60
                if value < 0:
                    value = value + 60
                self.minute.set(str(value))
            if column == 5:
                value = int(self.second.get()) + change
                if value > 59:
                    value = value - 60
                if value < 0:
                    value = value + 60
                self.second.set(str(value))
            
            self.setTimeString()
    
    def checkValidDate(self):
        day = int(self.day.get())
        month = int(self.month.get())
        year = int(self.year.get())

        valid = True

        try:
            datetime.datetime(year, month, day)
        except:
            valid = False
        
        self.validDate = valid
        if not valid:
            self.currentTimeDisplay.configure(fg="red")
        else:
            self.currentTimeDisplay.configure(fg="black")

    def getTimePressed(self):
        if self.serialConnection != None:
            if not self.awaiting:
                self.serialConnection.write("getTime\n".encode("utf-8"))
                self.awaiting = True
        else:
            messagebox.showinfo(title="Not Connected", message="Must be connected to device to retrieve time.")

    def setTimePressed(self):
        if self.serialConnection != None:
            if not self.awaiting:
                if self.validDate:
                    if not self.running:
                        message = "setTime " + self.year.get() + "," + self.month.get() + "," + self.day.get() + "," + self.hour.get() + "," + self.minute.get() + "," + self.second.get() + "\n"
                        self.serialConnection.write(message.encode("utf-8"))
                        self.awaiting = True
                    else:
                        messagebox.showinfo(title="Experiment Running", message="Time cannot be adjusted while experiment is in progress.")
                else:
                    messagebox.showinfo(title="Invalid Date", message="The currently selected date is not valid.")
        else:
            messagebox.showinfo(title="Not Connected", message="Must be connected to device to adjust time.")

    def performScan(self) -> None:
        '''Perform a scan of available ports and update option list accordingly'''
        if self.serialConnection == None:
            #List to contain available ports
            found = ["No Port Selected"]
            #Scan to find all available ports
            portData = list_ports.comports()
            #Iterate through ports
            for data in portData:
                #Add the device name of the port to the list (can be used to connect to it)
                found.append(data.device)
            
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
    
    def connectPressed(self) -> None:
        '''Attempt to connect to selected port'''
        #If a connection does not already exist
        if self.serialConnection == None:
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
                    self.portOption.configure(state="disabled")
                    #Do not allow action if waiting
                    self.awaiting = True
                    self.timesTried = 0
                    self.awaitingCommunication = True
                    self.checkConnection()
                    #Start reading from the port
                    readThread = Thread(target=self.readSerial, daemon=True)
                    readThread.start()
                    #Start handling incoming messages
                    messageThread = Thread(target=self.checkMessages, daemon=True)
                    messageThread.start()
                    #Send connection information request after a short time - allows for boot messages to clear
                    self.after(200, self.sendInfoRequest)
                else:
                    #Connection failed - reset
                    self.serialConnection = None
                    #Allow for connect to be pressed and disable disconnect
                    self.portOption.configure(state="normal")
                    #Not currently connected to a port
                    self.connectedPort = ""
                    #Display message to user
                    messagebox.showinfo(title="Failed", message="Failed to connect to port, check the device is still connected and the port is available.")
                    self.performScan()
    
    def checkConnection(self) -> None:
        '''Check if a connection has been made repeatedly until timeout'''
        #If still waiting
        if self.awaitingCommunication:
            #If timeout has been reached or exceeded
            if self.timesTried >= self.timeoutAttempts:
                #Close the connection and reset the buttons
                self.serialConnection.close()
                self.serialConnection = None
                self.awaiting = False
                self.awaitingCommunication = False
                self.connectButton.configure(text="Connect", command=self.connectPressed)
                self.portOption.configure(state="normal")
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
        if self.serialConnection != None:
            #Send the information request
            self.serialConnection.write("info\n".encode("utf-8"))

    def disconnectPressed(self):
        '''Close connection to port'''
        #If there is a connection and there is not data to be recieved
        if self.serialConnection != None and not self.awaiting:
            #Close the connection
            self.serialConnection.close()
            self.serialConnection = None
            #Switch buttons so disconnect is disabled and connect is enabled
            self.connectButton.configure(text="Connect", command=self.connectPressed)
            self.portOption.configure(state="normal")
            #Display message to indicate that the connection has been closed
            messagebox.showinfo(title="Connection Closed", message="The connection has been terminated successfully.")
            self.parent.destroy()

    def closeWindow(self):
        if self.serialConnection != None:
            self.disconnectPressed()
        else:
            self.parent.destroy()

    def readSerial(self):
        '''While connected repeatedly read information from serial connection'''
        #If there is a connection
        if self.serialConnection != None:
            #Attempt
            try:
                done = False
                while not done:
                    #Read the next character
                    char = self.serialConnection.read()
                    #If there is a character
                    if len(char) > 0:
                        try:
                            #Attempt from byte to string and print
                            ch = char.decode("utf-8")
                            if ch == "\n":
                                #Add to list of messages
                                self.receivedMessages.append(self.currentMessage)
                                self.currentMessage = ""
                            else:
                                self.currentMessage = self.currentMessage + ch
                        except:
                            #If it failed an unusual escape character has been read and it is simply ignored
                            pass
                    else:
                        done = True
                
                #Repeat this read function after 1ms
                self.after(1, self.readSerial)
            except:
                #Close the connection and reset the buttons
                self.serialConnection.close()
                self.serialConnection = None
                self.connectButton.configure(text="Connect", command=self.connectPressed)
                self.portOption.configure(state="normal")
                #Display message to user to indicate that connection was lost (Occurs when device unplugged)
                messagebox.showinfo(title="Connection Lost", message="Connection to device was lost, please check connection and try again.")
                self.performScan()

    def checkMessages(self):
        '''Repeatedly check for a new message and handle it'''
        #If there is a message
        if len(self.receivedMessages) > 0:
            #Get the message
            nextMessage = self.receivedMessages[0]
            #Handle based on what the message is
            self.messageReceived(nextMessage)
            #Remove message from the list
            del self.receivedMessages[0]
        #If there is still a connection
        if self.serialConnection != None:
            #Repeat after a short delay
            self.after(1, self.checkMessages)
    
    def messageReceived(self, message):
        #DEBUG display the message
        #print(self.currentMessage)
        #Split up the message into parts on spaces
        messageParts = message.split(" ")
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
                self.running = True
                self.messageLabel.configure(text="Experiment currently running, clock time cannot be changed.")
            else:
                self.running = False
            
            #No longer waiting for a response
            self.awaiting = False
        
        if len(messageParts) > 1 and messageParts[0] == "time":
            if len(messageParts) > 6:
                try:
                    self.autoCheckValue.set(0)
                    self.year.set(messageParts[1])
                    self.month.set(messageParts[2])
                    self.day.set(messageParts[3])
                    self.hour.set(messageParts[4])
                    self.minute.set(messageParts[5])
                    self.second.set(messageParts[6])
                    messagebox.showinfo(title="Success", message="Time successfully retrieved.")
                except:
                    messagebox.showinfo(title="Failed", message="Time was not retrieved successfully, please try again.")
            
            self.awaiting = False

        if len(messageParts) > 1 and messageParts[0] == "done":
            if messageParts[1] == "setTime":
                messagebox.showinfo(title="Success", message="Time set successfully.")

            self.awaiting = False

#Only run if this is the main module being run
if __name__ == "__main__":
    #Create root window for tkinter
    root = tkinter.Tk()
    #Set the shape of the window
    root.geometry("400x400")
    root.minsize(400, 400)
    #Allow for expanding sizes
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    #Set the title text of the window
    root.title("Clock Time Configuration")
    #Add the editor to the root windows
    window = mainWindow(root)
    window.grid(row = 0, column=0, sticky="NESW")
    #If the window is attempted to be closed, call the close window function
    root.protocol("WM_DELETE_WINDOW", window.closeWindow)
    #Start running the root
    root.mainloop()