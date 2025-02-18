import tkinter
from tkinter.font import Font
from tkinter import messagebox
import matplotlib.pyplot as plt
from threading import Thread
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
from serial.tools import list_ports

class MainWindow(tkinter.Frame):
    '''Class to contain all of the menus'''
    def __init__(self, parent, *args, **kwargs) -> None:
        #Setup parent configuration
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        #Number of internal rows and columns
        self.numRows = 8
        self.numColumns = 3

        #Create the rows and columns so the children are laid out right
        for row in range(0, self.numRows):
            self.grid_rowconfigure(row, weight=1)
        for col in range(0, self.numColumns):
            self.grid_columnconfigure(col, weight=1)

        #If a device is connected
        self.connected = False
        #Connection object
        self.serialConnection = None
        #If waiting for a response
        self.awaiting = False
        #If waiting for the first response
        self.awaitingCommunication = False
        #List to contain port label names for the names on the drop down
        self.portLabels = []

        #Current message being received and list of previously received but unprocessed messages
        self.currentMessage = ""
        self.receivedMessages = []

        #Setup port drop down (with debug values)
        self.selectedPort = tkinter.StringVar()
        self.selectedPort.set("Port 1")
        self.portOption = tkinter.OptionMenu(self, self.selectedPort, "Port 1", "Port 2", "Port 3", "Port 4")
        self.portOption.grid(row=0, column=0, columnspan=2, sticky="NESW")

        #Add connect button
        self.connectButton = tkinter.Button(self, text="Connect", command=self.connectPressed)
        self.connectButton.grid(row=0, column=2, sticky="NESW")

        #2D list of data for each channel, each value represents and hours total tips
        self.channelData = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

        #Set up 3 by 5 grid of plots and store figure and axes objects
        self.figure, ((ax1, ax2, ax3, ax4, ax5), (ax6, ax7, ax8, ax9, ax10), (ax11, ax12, ax13, ax14, ax15)) = plt.subplots(3, 5)
        #Arrange axes into channel id indexed list
        self.axs = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9, ax10, ax11, ax12, ax13, ax14, ax15]
        #For each of the channels
        for channelNumber in range(0, 15):
            #Set the name of the plot
            self.axs[channelNumber].set_title("Channel " + str(channelNumber + 1))
            #draw the horizontal axis line
            self.axs[channelNumber].axhline(y=0, color="k", linewidth=0.5)
            #Use only the outside markers for positions
            self.axs[channelNumber].label_outer()
            #Integer positions only
            self.axs[channelNumber].xaxis.get_major_locator().set_params(integer=True)
            self.axs[channelNumber].yaxis.get_major_locator().set_params(integer=True)
        #Create the canvas to hold the graphs, draw it and place the widget in the frame
        self.canvas = FigureCanvasTkAgg(figure=self.figure, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=0, rowspan=7, columnspan=3, sticky="NESW")

        #Timeout variables
        self.timesTried = 0
        self.timeoutAttempts = 10

        #If receiving data from the device
        self.gettingData = False

        #Start scanning for available ports
        self.scanLoop = None
        self.performScan()

        #Redraw the plots correctly
        self.updatePlots()

    def updatePlots(self) -> None:
        '''Change the data in the plots to show the most recent data'''
        #Variable which stores the y limit so the graphs can be scaled correctly
        most = 5
        #Check channel data for each value and find the maximum - otherwise 5 is used
        for channelNumber in range(0, 15):
            if len(self.channelData[channelNumber]) > 0:
                most = max(most, max(self.channelData[channelNumber]))
        
        #Iterate each graph
        for channelNumber in range(0, 15):
            last = 0
            #Get the most recent value from the data, if there is one
            if len(self.channelData[channelNumber]) > 0:
                last = self.channelData[channelNumber][-1]
            #Clear the axes
            self.axs[channelNumber].clear()
            #Change the title to include the most recent value
            self.axs[channelNumber].set_title("Channel " + str(channelNumber + 1) + "(" + str(last) + " Tip(s))", fontsize=10)
            #Redraw X axis line, in black
            self.axs[channelNumber].axhline(y=0, color="k", linewidth=0.5)
            #Plot the data
            self.axs[channelNumber].plot([n for n in range(0, len(self.channelData[channelNumber]))], self.channelData[channelNumber], "-")
            #Adjust where the ticks appear and how many
            self.axs[channelNumber].label_outer()
            self.axs[channelNumber].xaxis.get_major_locator().set_params(integer=True)
            self.axs[channelNumber].yaxis.get_major_locator().set_params(integer=True)
            #Set the y axis limit to be the same for all the graphs
            self.axs[channelNumber].set_ylim(0, most)
        #Update the display so changes appear on the screen
        self.canvas.draw()

    def connectPressed(self) -> None:
        '''Attempt to connect to selected port'''
        #If a connection does not already exist
        if not self.connected:
            #If the current port selected exists
            if self.portLabels.index(self.selectedPort.get()) > 0:
                #Set the port of the connection
                self.connectedPort = self.selectedPort.get()
                success = True
                try:
                    #Attempt to connect
                    #self.serialConnection = serial.Serial(port=self.connectedPort, baudrate=115200, dsrdtr=True, rtscts=False)
                    self.serialConnection = serial.Serial(port=self.connectedPort, baudrate=115200)
                except:
                    #If something went wrong
                    success = False
            
                if success:
                    #Switch buttons to enable disconnect and disable connect
                    self.connectButton.configure(text="Disconnect", command=self.disconnectPressed)
                    self.connected = True
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
                    self.connected = False
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
                self.connected = False
                self.awaiting = False
                self.awaitingCommunication = False
                self.connectButton.configure(text="Connect", command=self.connectPressed)
                self.portOption.configure(state="normal")
                #Display message to user to indicate that connection was lost (Occurs when connecting to a port that does is not connected to esp)
                messagebox.showinfo(title="Connection Failed", message="Connection could not be established, please check this is the correct port and try again.")
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

    def performScan(self, target = None) -> None:
        '''Perform a scan of available ports and update option list accordingly'''
        if not self.connected:
            #List to contain available ports
            found = ["No Port Selected"]
            descs = [""]
            #Scan to find all available ports
            portData = list_ports.comports()
            #Iterate through ports
            for data in portData:
                #Add the device name of the port to the list (can be used to connect to it)
                found.append(data.device)
                descs.append("(" + data.description + ")")
            
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

                i = 0
                #Iterate through labels
                for name in self.portLabels:
                    #Add the labels to the list
                    menu.add_command(label=name + " " + descs[i], command=lambda v=self.selectedPort, l=name: v.set(l))
                    i = i + 1

                targetFound = False

                if target != None:
                    if target in self.portLabels:
                        self.selectedPort.set(target)
                
                if not targetFound:
                    #If the selected item is still available
                    if self.selectedPort.get() in self.portLabels:
                        #Set the drop down value to what it was
                        self.selectedPort.set(self.selectedPort.get())
                    else:
                        #Set selected option to none
                        self.selectedPort.set(self.portLabels[0])
            
            #Scan again shortly
            self.scanLoop = self.after(150, self.performScan)
        else:
            self.scanLoop = ""

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
                                #Add to list of messages
                                self.receivedMessages.append(self.currentMessage)
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
        #print(message)
        #Split up the message into parts on spaces
        messageParts = message.split(" ")
        #If this is the information about the state of the esp32
        if len(messageParts) > 3 and messageParts[0] == "info":

            #If waiting for the response from the device
            if self.awaitingCommunication:
                #No longer waiting
                self.awaitingCommunication = False
                #Display connected message
                messagebox.showinfo(title="Success", message="Connected to port successfully.")
                #if messageParts[1] == "1":
                self.serialConnection.write("getHourly\n".encode("utf-8"))
                #else:
                    #Display not logging message
                    #messagebox.showinfo(title="No Data", message="Device is not currently logging.")
                
                
            
            #No longer waiting for a response
            self.awaiting = False
        
        #If this is a message about the number of tips this hour
        if len(messageParts) > 15 and messageParts[0] == "counts":
            #List to hold integer versions of each value
            newValues = []
            #For each channel
            for i in range(1, 16):
                #Default value
                value = 0
                #Attempt to convert to integer
                try:
                    value = int(messageParts[i])
                except:
                    pass
                #Add the value to the list
                newValues.append(value)
            #For each channel
            for i in range(0, 15):
                #Attempt to add the value to the data set
                try:
                    self.channelData[i].append(newValues[i])
                except:
                    #If it failed default to 0 - this happens when the list is not long enough
                    self.channelData[i].append(0)
            #Redraw the graphs so the new data points are shown
            self.updatePlots()
        
        #If this is part of the file information containing the tip data
        if len(messageParts) > 1 and messageParts[0] == "tipfile":
            #If this is the beginning of the file
            if messageParts[1] == "start":
                #Start receiving and clear stored data
                self.gettingData = True
                self.channelData = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
            #If this is the end of the file
            if messageParts[1] == "done":
                #Stop receiving data and update the display
                self.gettingData = False
                self.updatePlots()
            else:
                #If data is being received and it is a valid line
                if self.gettingData and len(messageParts) > 15:
                    #Go through for each of the channels
                    for i in range(0, 15):
                        try:
                            #Convert to integer and store
                            self.channelData[i].append(int(messageParts[i + 1]))
                        except:
                            #If an error occurred store a negative number so it is clearly a data error
                            self.channelData[i].append(-1)
        else:
            #If expecting more data about tips, but didn't get it
            if self.gettingData:
                #Reset and ask again
                self.gettingData = False
                self.serialConnection.write("getHourly\n".encode("utf-8"))

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
            self.connectButton.configure(text="Connect", command=self.connectPressed)
            self.portOption.configure(state="normal")
            #Display message to indicate that the connection has been closed
            messagebox.showinfo(title="Connection Closed", message="The connection has been terminated successfully.")
            self.parent.quit()
            self.parent.destroy()

    def closeWindow(self):
        try:
            self.after_cancel(self.scanLoop)
        except:
            pass
        if self.connected and self.serialConnection != None:
            self.disconnectPressed()
        else:
            self.parent.quit()
            self.parent.destroy()

#Only run if this is the main module being run
if __name__ == "__main__":
    #Create root window for tkinter
    root = tkinter.Tk()
    #Set the shape of the window
    root.geometry("1000x750")
    #Allow for expanding sizes
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    #Set minimum size
    root.minsize(1000, 750)
    #Set the title text of the window
    root.title("GFM Tip Graphs")
    #Add the editor to the root windows
    window = MainWindow(root)
    window.grid(row = 0, column=0, sticky="NESW")
    #If the window is attempted to be closed, call the close window function
    root.protocol("WM_DELETE_WINDOW", window.closeWindow)
    #Start running the root
    root.mainloop()