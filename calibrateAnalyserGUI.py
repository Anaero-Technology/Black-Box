import tkinter
from tkinter import messagebox, simpledialog
import serial
from serial.tools import list_ports
from threading import Thread
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy

class mainWindow(tkinter.Frame):
    '''Class to contain all of the menus'''
    def __init__(self, parent, *args, **kwargs) -> None:
        #Setup parent configuration
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        #Number of rows and columns
        self.numRows = 8
        self.numColumns = 13

        #Serial connection object
        self.serialConnection = None
        #List of available port names
        self.portLabels = []
        #Which port is currently connected
        self.connectedPort = ""
        #The message being read and list of messages read but unhandled
        self.currentMessage = ""
        self.receivedMessages = []
        #If waiting for a response from the esp
        self.awaiting = False
        self.awaitingCommunication = False
        #Timeout for the initial connection
        self.timesTried = 0
        self.timeoutAttempts = 10
        self.connectedGFM = False

        #If the system is currently running an experiment
        self.running = False

        #Configure rows
        for row in range(0, self.numRows):
            self.grid_rowconfigure(row, weight = 1)
        
        #Configure columns
        for col in range(0, self.numColumns):
            self.grid_columnconfigure(col, weight = 1)

        #Setup port drop down (with debug values)
        self.selectedPort = tkinter.StringVar()
        self.selectedPort.set("Port 1")
        self.portOption = tkinter.OptionMenu(self, self.selectedPort, "Port 1", "Port 2", "Port 3", "Port 4")
        self.portOption.grid(row=0, column=0, columnspan=8, sticky="NESW")

        #Add connect button
        self.connectButton = tkinter.Button(self, text="Connect", command=self.connectPressed)
        self.connectButton.grid(row=0, column=8, columnspan=5, sticky="NESW")
        
        #Label to indicate if the experiment is running
        self.messageLabel = tkinter.Label(self, text="", fg="red")
        self.messageLabel.grid(row=1, column=0, columnspan=13, sticky="NESW")

        #Buttons to start calibration for CO2 and CH4
        self.calibrationStartCo2Button = tkinter.Button(self, text="CO2 Calibration", state="disabled", command=self.startCalibrationCo2)
        self.calibrationStartCo2Button.grid(row=6, column=0, columnspan=3, sticky="NSEW")
        self.calibrationStartCh4Button = tkinter.Button(self, text="CH4 Calibration", state="disabled", command=self.startCalibrationCh4)
        self.calibrationStartCh4Button.grid(row=7, column=0, columnspan=3, sticky="NSEW")

        #Button to add calibration point
        self.addPointButton = tkinter.Button(self, text="Add Point", state="disabled", command=self.addPoint)
        self.addPointButton.grid(row=6, rowspan=2, column=3, columnspan=7, sticky="NESW")

        #Button to finish calibration
        self.calibrationEndButton = tkinter.Button(self, text="Finish Calibration", state="disabled", command=self.completeCalibration)
        self.calibrationEndButton.grid(row=6, rowspan=2, column=10, columnspan=3, sticky="NSEW")
        
        #Frame to hold the graph
        self.graphFrame = tkinter.Frame(self)
        self.graphFrame.grid(row=2, rowspan=4, column=0, columnspan=13, sticky="NESW")

        #Add graph
        self.figure = Figure(figsize=(4, 4), dpi=100)
        self.subPlot = self.figure.add_subplot(111)
        self.graphCanvas = FigureCanvasTkAgg(self.figure, master=self.graphFrame)
        self.graphCanvas.draw()
        self.graphCanvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.graphCanvas, self.graphFrame)
        self.toolbar.update()
        self.graphCanvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        #If currently calibrating CO2
        self.co2 = False
        #If currently performing a calibration
        self.calibrating = False

        self.xMin = None
        self.xMax = None

        #Most recent percentage value
        self.lastPercent = 0
        #Total number of calibrated points
        self.calibratedPoints = 0

        #Start scanning for ports
        self.performScan()

    def clearPlot(self) -> None:
        '''Clear the graph ready for new data'''
        self.subPlot.clear()
        self.graphCanvas.draw()

    def addPoint(self) -> None:
        '''Get the data for a new point and send to Gas Analyser'''
        #If there is a connection and not waiting
        if self.serialConnection != None and not self.awaiting:
            #Correct gas name
            gas = "Methane"
            if self.co2:
                gas = "Carbon Dioxide"
            
            #Ask the user to enter the percentage of the gas
            percent = simpledialog.askfloat("Enter Gas Percentage", "Enter the percentage of " + gas, minvalue=0, maxvalue=100)
            #If a valid value was entered
            if percent != None and percent >= 0 and percent <= 100:
                #Store percentage
                self.lastPercent = percent
                #Create message for analyser : calibrate [gasName] [percentage]\n
                message = "calibrate "
                if self.co2:
                    message = message + "co2 "
                else:
                    message = message + "ch4 "
                message = message + str(percent) + "\n"
                #Send the message
                self.serialConnection.write(message.encode("utf-8"))
                self.awaiting = True
    
    def drawPoint(self, x : float, y : float) -> None:
        '''Add a point to the graph'''
        #Store maximum and minimum of x values
        if self.xMin == None or self.xMin > x:
            self.xMin = x
        if self.xMax == None or self.xMax < x:
            self.xMax = x
        
        #Plot point as a blue circle
        self.subPlot.plot(x, y, "bo")
        #Update the canvas
        self.graphCanvas.draw()

    def drawLine(self, m : float, c : float, l : str, colour : str) -> None:
        '''Add a line to the graph'''
        #Create 100 points from minimum to maximum
        x = numpy.linspace(self.xMin, self.xMax, 100)
        #Calculate y values using gradient and intercept
        y = (m * x) + c
        #Add line to plot with name label
        self.subPlot.plot(x, y, colour, label=l)
        #Update the canvas
        self.subPlot.legend()
        self.graphCanvas.draw()

    def drawLineFromY(self, m : float, c : float, l : str, colour : str) -> None:
        '''Add a line  to the graph without x end points'''
        #Create 100 points for y
        y = numpy.linspace(0, 100, 100)
        #Calculate x values using gradient and intercept
        x = (y - c) / m
        #Add line to plot with name label
        self.subPlot.plot(x, y, colour, label=l)
        #Update the canvas
        self.subPlot.legend()
        self.graphCanvas.draw()

    def startCalibrationCo2(self) -> None:
        '''Trigger CO2 calibration'''
        self.co2 = True
        self.startCalibration()
    
    def startCalibrationCh4(self) -> None:
        '''Trigger CH4 calibration'''
        self.co2 = False
        self.startCalibration()

    def startCalibration(self) -> None:
        '''Start a calibration run'''
        #If connected and not waiting
        if self.serialConnection != None and not self.awaiting:
            #Disable start buttons
            self.calibrationStartCo2Button.configure(state="disabled")
            self.calibrationStartCh4Button.configure(state="disabled")
            #Clear the graph
            self.clearPlot()
            #Message to send to Gas Analyser
            message = "calibrate begin "
            #Add correct gas
            if self.co2:
                message = message + "co2\n"
            else:
                message = message + "ch4\n"
            #Send message
            self.serialConnection.write(message.encode("utf-8"))
            #Waiting for response and started calibration
            self.awaiting = True
            self.calibrating = True

    def completeCalibration(self) -> None:
        '''Send message to trigger calibration calculations'''
        #If connected and not waiting
        if self.serialConnection != None and not self.awaiting:
            ##Disable add and end buttons
            self.addPointButton.configure(state="disabled")
            self.calibrationEndButton.configure(state="disabled")
            
            #Send message to analyser
            self.serialConnection.write("calibrate end\n".encode("utf-8"))
            self.awaiting = True

    def performScan(self) -> None:
        '''Perform a scan of available ports and update option list accordingly'''
        if self.serialConnection == None:
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
                    self.connectedGFM = False
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
                if not self.connectedGFM:
                    #Display message to user to indicate that connection was lost (Occurs when connecting to a port that does is not connected to esp)
                    messagebox.showinfo(title="Connection Failed", message="Connection could not be established, please check this is correct port and try again.")
                    self.messageLabel.configure(text="", fg="black")
                else:
                    messagebox.showinfo(title="Connection Failed", message="Connection to gas analyser could not be established, please check it is connected and try again.")
                    self.messageLabel.configure(text="", fg="black")
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

    def disconnectPressed(self) -> None:
        '''Close connection to port'''
        #If there is a connection and there is not data to be recieved
        if self.serialConnection != None and not self.awaiting:
            #Close the connection
            self.serialConnection.close()
            self.serialConnection = None
            #Switch buttons so disconnect is disabled and connect is enabled
            self.connectButton.configure(text="Connect", command=self.connectPressed)
            self.portOption.configure(state="normal")
            self.calibrationStartCo2Button.configure(state="disabled")
            self.calibrationStartCh4Button.configure(state="disabled")
            self.addPointButton.configure(state="disabled")
            self.calibrationEndButton.configure(state="disabled")
            #Display message to indicate that the connection has been closed
            messagebox.showinfo(title="Connection Closed", message="The connection has been terminated successfully.")
            self.parent.destroy()

    def closeWindow(self) -> None:
        '''When a window close is attempted'''
        #If there is a connection
        if self.serialConnection != None:
            #Attempt a disconnect
            self.disconnectPressed()
        else:
            #Destroy the window
            self.parent.destroy()

    def readSerial(self) -> None:
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
                self.calibrationStartCo2Button.configure(state="disabled")
                self.calibrationStartCh4Button.configure(state="disabled")
                self.addPointButton.configure(state="disabled")
                self.calibrationEndButton.configure(state="disabled")
                #Display message to user to indicate that connection was lost (Occurs when device unplugged)
                messagebox.showinfo(title="Connection Lost", message="Connection to device was lost, please check connection and try again.")
                self.performScan()

    def checkMessages(self) -> None:
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
    
    def messageReceived(self, message: str):
        #DEBUG output the message coming from GFM ESP
        #print("Message: {0}".format(message))
        #Split up the message into parts on spaces
        messageParts = message.split(" ")
        #If this is the information about the state of the esp32
        if len(messageParts) > 1 and messageParts[0] == "info":

            #If waiting for the response from the device
            if self.awaitingCommunication:
                self.connectedGFM = True
                #Display connected message
                messagebox.showinfo(title="Success", message="Connected to port successfully.")
            
            #If the esp32 is collecting information
            if messageParts[1] == "1":
                self.running = True
                self.messageLabel.configure(text="Experiment currently running, analyser calibration cannot be changed.", fg="red")
                self.calibrationStartCo2Button.configure(state="disabled")
                self.calibrationStartCh4Button.configure(state="disabled")
                self.addPointButton.configure(state="disabled")
                self.calibrationEndButton.configure(state="disabled")
                #No longer waiting
                self.awaitingCommunication = False
                #No longer waiting for a response
                self.awaiting = False
            else:
                self.running = False
                self.messageLabel.configure(text="Connecting to analyser, please wait.", fg="black")
                self.calibrationStartCo2Button.configure(state="disabled")
                self.calibrationStartCh4Button.configure(state="disabled")
                self.addPointButton.configure(state="disabled")
                self.calibrationEndButton.configure(state="disabled")
                if self.awaitingCommunication:
                    #Reset tries and wait for analyser check
                    self.timesTried = 0
                    self.serialConnection.write("checkAnalyser\n".encode("utf-8"))

        #If something whent wrong
        if len(messageParts) > 1 and messageParts[0] == "failed":
            #Connection to the gas analyser could not be made
            if messageParts[2] == "noanalyser":
                messagebox.showinfo(title="No Gas Analyser", message="The gas analyser was not found, please ensure it is connected and try again.")
                self.messageLabel.configure(text="Analyser connection error, please try again.", fg="red")
                self.awaiting = False

        #If the system is already running an experiment
        if len(messageParts) > 1 and messageParts[0] == "already":
            #Cannot perform action due to experiment running
            if messageParts[2] == "start":
                self.messageLabel.configure(text="Experiment currently running, analyser calibration cannot be changed.", fg="red")
                messagebox.showinfo(title="Experiment running", message="The experiment is currently running, please stop it before adjusting the calibration.")
                self.awaiting = False
            
        #If this is a calibration data point
        if len(messageParts) > 1 and messageParts[0] == "point":
            #If it was successfully calibrated
            if messageParts[1] == "success":
                #Add to number of points
                self.calibratedPoints = self.calibratedPoints + 1
                #If there is data
                if len(messageParts) > 2:
                    try:
                        #Convert to float
                        value = float(messageParts[2])
                        #Add point to graph
                        self.drawPoint(self.lastPercent, value)
                    except:
                        pass
            #If it was not successfully calibrated
            elif messageParts[1] == "failed":
                #Display failed message
                messagebox.showinfo(title="Calibration Point Failed", message="Something went wrong and the point could not be calibrated, please try again.")
            #No longer waiting for response
            self.awaiting = False
        
        #If this was a message about the overall calibration
        if len(messageParts) > 1 and messageParts[0] == "calibration":
            #If it was a successfully completed calibration
            if messageParts[1] == "success":
                #If there are enough data items for two lines
                if len(messageParts) > 4:
                    try:
                        #Get m and c values for the line of the current gas
                        m = 0
                        c = 0
                        label = ""
                        lineColour = "-r"
                        if self.co2:
                            m = float(messageParts[2])
                            c = float(messageParts[3])
                            label = "Co2"
                            lineColour = "-y"
                        else:
                            m = float(messageParts[4])
                            c = float(messageParts[5])
                            label = "Ch4"
                            lineColour = "-g"

                        #Add line to chart
                        self.drawLine(m, c, label, lineColour)
                    except:
                        pass
                    
                    #Set state of start buttons to enabled
                    self.calibrationStartCo2Button.configure(state="normal")
                    self.calibrationStartCh4Button.configure(state="normal")
                    #Send message to request plots
                    self.serialConnection.write("checkAnalyser\n".encode("utf-8"))
            #If the calibration failed
            elif messageParts[1] == "failed":
                #Show failed messages
                messagebox.showinfo(title="Calibration Failed", message="Calibration was not successful, please try again.")
                self.messageLabel.configure(text="Calibration failed, try again.", fg="red")
                #Reset start buttons to enabled
                self.calibrationStartCo2Button.configure(state="normal")
                self.calibrationStartCh4Button.configure(state="normal")
            #If it was started successfully
            elif messageParts[1] == "started":
                #Enable add and end buttons
                self.addPointButton.configure(state="normal")
                self.calibrationEndButton.configure(state="normal")
                self.awaiting = False

            #Check the state of the analyer
            self.serialConnection.write("checkanalyser\n".encode("utf-8"))

        #If both calibrations are complete
        if len(messageParts) > 1 and messageParts[0] == "ready":
            #Show ready message
            self.messageLabel.configure(text="Analyser connected, ready to analyse.", fg="black")
            #Default state for all buttons
            self.calibrationStartCo2Button.configure(state="normal")
            self.calibrationStartCh4Button.configure(state="normal")
            self.addPointButton.configure(state="disabled")
            self.calibrationEndButton.configure(state="disabled")
            #Send message to request calibration data
            self.serialConnection.write("getCalibration\n".encode("utf-8"))
            #No longer awaiting inital communication
            self.awaitingCommunication = False
        
        #If currently performing a calibration
        if len(messageParts) > 2 and messageParts[0] == "calibrating":
            try:
                gasType = ""
                #Get the gas type
                if messageParts[1] == "co2":
                    gasType = "Co2"
                    self.co2 = True
                elif messageParts[1] == "ch4":
                    gasType = "Ch4"
                    self.co2 = False
                
                #Get the number of calibrated points
                self.calibratedPoints = int(messageParts[2])

                #Display message to indicate request for data
                self.messageLabel.configure(text="Analyser connected, calibrating {0}.".format(gasType), fg="black")
                #Buttons to calibrating position
                self.calibrationStartCo2Button.configure(state="disabled")
                self.calibrationStartCh4Button.configure(state="disabled")
                self.addPointButton.configure(state="normal")
                self.calibrationEndButton.configure(state="normal")
                #Send message to request previous points
                self.serialConnection.write("points\n".encode("utf-8"))
                #No longer awaiting inital communication 
                self.awaitingCommunication = False
            except:
                #Message for failing to connect correctly
                messagebox.showinfo(title="Error Connecting To Analyser", message="Something went wrong connecting to the analyser, please try again.")
                self.messageLabel.configure(text="Analyser connection error, please try again.", fg="red")
                #Disable buttons
                self.calibrationStartCo2Button.configure(state="disabled")
                self.calibrationStartCh4Button.configure(state="disabled")
                self.addPointButton.configure(state="disabled")
                self.calibrationEndButton.configure(state="disabled")
                #Not waiting for communications
                self.awaiting = False
                self.awaitingCommunication = False
        
        #If the analyser is waiting for a calibration
        if len(messageParts) > 2 and messageParts[0] == "waiting":
            #If CO2 or CH4 or Both need calibration
            co2 = messageParts[1] == "true"
            ch4 = messageParts[2] == "true"
            #Message to display
            displayMessage = "Analyser connected, need to calibrate "
            #Add correct gas(ses)
            if not co2:
                displayMessage = displayMessage + "Co2"
                if not ch4:
                    displayMessage = displayMessage + " and Ch4"
            else:
                if not ch4:
                    displayMessage = displayMessage + "Ch4"
            
            #Display message
            self.messageLabel.configure(text=displayMessage, fg="black")
            #Activate start buttons
            self.calibrationStartCo2Button.configure(state="normal")
            self.calibrationStartCh4Button.configure(state="normal")
            self.addPointButton.configure(state="disabled")
            self.calibrationEndButton.configure(state="disabled")
            #No longer awaiting communications
            self.awaiting = False
            self.awaitingCommunication = False
        
        #If this is a message regarding point values
        if len(messageParts) > 1 and messageParts[0] == "data":
            #If all the points are done
            if messageParts[1] == "done":
                #Not waiting for more
                self.awaiting = False
            else:
                #If there is enough data
                if len(messageParts) > 2:
                    try:
                        #Convert to floats
                        x = float(messageParts[1])
                        y = float(messageParts[2])
                        #Plot the point
                        self.drawPoint(x, y)
                    except:
                        pass
        
        #If this is a set of calibration values
        if len(messageParts) > 4 and messageParts[0] == "calvalues":
            try:
                #Convert to floats for gradients and intercepts
                co2m = float(messageParts[1])
                co2c = float(messageParts[2])
                ch4m = float(messageParts[3])
                ch4c = float(messageParts[4])
                #Plot the lines with their labels
                self.drawLineFromY(co2m, co2c, "CO2", "-y")
                self.drawLineFromY(ch4m, ch4c, "CH4", "-g")
            except:
                pass
            
            #Not waiting for a response
            self.awaiting = False



#Only run if this is the main module being run
if __name__ == "__main__":
    #Create root window for tkinter
    root = tkinter.Tk()
    #Set the shape of the window
    root.geometry("500x600")
    root.minsize(500, 600)
    #Allow for expanding sizes
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    #Set the title text of the window
    root.title("Calibrate Gas Analyser")
    #Add the editor to the root windows
    window = mainWindow(root)
    window.grid(row = 0, column=0, sticky="NESW")
    #If the window is attempted to be closed, call the close window function
    root.protocol("WM_DELETE_WINDOW", window.closeWindow)
    #Start running the root
    root.mainloop()