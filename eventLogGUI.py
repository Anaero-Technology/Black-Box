import tkinter
from tkinter import filedialog
from tkinter import messagebox
import random
import createSetup

class mainWindow(tkinter.Frame):
    '''Class to contain the menu for the event log'''
    def __init__(self, parent, *args, **kwargs):
        #Setup parent configuration
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        #Width and height of window
        self.height = 610
        self.width = 600
        #Number of rows and columns in the grid
        self.numberRows = 13
        self.numberCols = 7
        #Length of input area of numbers
        self.numberLength = 8
        
        #Create the rows
        for row in range(0, self.numberRows):
            self.grid_rowconfigure(row, minsize=self.height / self.numberRows)
        
        #Create the columns
        for col in range(0, self.numberCols):
            self.grid_columnconfigure(col, minsize=self.width/ self.numberCols)
        
        #Add a display frame for the data
        self.displayFrame = tkinter.Frame(self)
        self.displayFrame.grid(row=2, column=0, rowspan=11, columnspan=7, sticky="NESW")
        self.displayFrame.grid_columnconfigure(0, minsize=583)
        self.displayFrame.grid_columnconfigure(1, minsize=17)
        self.displayFrame.grid_rowconfigure(0, minsize=(self.height / self.numberRows * 11))
        #Add a scroll bar
        self.textScroll = tkinter.Scrollbar(self.displayFrame)
        self.textScroll.grid(row=0, column=1, sticky="NESW")
        #Add an area to display the text
        self.textList = tkinter.Listbox(self.displayFrame, yscrollcommand=self.textScroll.set)
        self.textList.grid(row=0, column=0, sticky="NESW")
        self.textScroll.config(command=self.textList.yview)
        #Adding example text to the scroll area
        self.textList.insert(tkinter.END, "No data present yet, press generate to produce data points.")

        #Register number checking function for use in entry fields
        self.numCheck = self.register(self.checkNumber)

        #Setup min and max temperature and pressure variables and entry widgets
        self.minTempVar = tkinter.StringVar()
        self.minTempInput = tkinter.Entry(self, width=self.numberLength, textvariable=self.minTempVar, justify="center", validatecommand=(self.numCheck, "%P", 0), validate="focus")
        self.minTempInput.grid(row=1, column= 0, sticky="NESW")
        self.maxTempVar = tkinter.StringVar()
        self.maxTempInput = tkinter.Entry(self, width=self.numberLength, textvariable=self.maxTempVar, justify="center", validatecommand=(self.numCheck, "%P", 1), validate="focus")
        self.maxTempInput.grid(row=1, column= 1, sticky="NESW")
        self.minPresVar = tkinter.StringVar()
        self.minPresInput = tkinter.Entry(self, width=self.numberLength, textvariable=self.minPresVar, justify="center", validatecommand=(self.numCheck, "%P", 2), validate="focus")
        self.minPresInput.grid(row=1, column= 2, sticky="NESW")
        self.maxPresVar = tkinter.StringVar()
        self.maxPresInput = tkinter.Entry(self, width=self.numberLength, textvariable=self.maxPresVar, justify="center", validatecommand=(self.numCheck, "%P", 3), validate="focus")
        self.maxPresInput.grid(row=1, column= 3, sticky="NESW")

        #Currently in use temperature and pressure
        self.tempRange = [0, 100]
        self.presRange = [0, 100]

        #Set the values of the variables
        print(str(self.tempRange[0]))
        self.minTempVar.set(str(self.tempRange[0]))
        self.maxTempVar.set(str(self.tempRange[1]))
        self.minPresVar.set(str(self.presRange[0]))
        self.maxPresVar.set(str(self.presRange[1]))

        #Setup the display labels
        self.tempLabel = tkinter.Label(self)
        self.tempLabel.grid(row=0, column=0, columnspan=2, sticky="NESW")
        self.presLabel = tkinter.Label(self)
        self.presLabel.grid(row=0, column=2, columnspan=2, sticky="NESW")

        #Setup duration and tip delay labels
        self.durationLabel = tkinter.Label(self)
        self.durationLabel.grid(row=0, column=4, sticky="NESW")
        self.tipTimeLabel = tkinter.Label(self)
        self.tipTimeLabel.grid(row=0, column=5, sticky="NESW")

        #Setup the duration and tip delay inputs and variables
        self.durationVar = tkinter.StringVar()
        self.durationInput = tkinter.Entry(self, width=self.numberLength, textvariable=self.durationVar, justify="center", validatecommand=(self.numCheck, "%P", 4), validate="focus")
        self.durationInput.grid(row=1, column=4, sticky="NESW")
        self.tipTimeVar = tkinter.StringVar()
        self.tipTimeInput = tkinter.Entry(self, width=self.numberLength, textvariable=self.tipTimeVar, justify="center", validatecommand=(self.numCheck, "%P", 5), validate="focus")
        self.tipTimeInput.grid(row=1, column=5, sticky="NESW")

        self.floatFields = [self.minTempVar, self.maxTempVar, self.minPresVar, self.maxPresVar, self.durationVar, self.tipTimeVar]

        #Default duration and tip time
        self.duration = 1440
        self.tipTime = 30

        #Set duration and tip delay defaults
        self.durationVar.set(str(self.duration))
        self.tipTimeVar.set(str(self.tipTime))

        #Update the labels and values
        self.updateValues()

        #Setup generation button
        self.generateButton = tkinter.Button(self, text="Generate", command=self.generateTips)
        self.generateButton.grid(row=0, column=6, sticky="NESW")

        #Setup export button
        self.exportButton = tkinter.Button(self, text="Export", command=self.exportDataLog)
        self.exportButton.grid(row=1, column=6, sticky="NESW")

        #There is not currently valid information in the list
        self.validData = False

        #Allowed file types and extensions
        self.fileTypes = [("CSV Files", "*.csv")]


    def checkNumber(self, message: str, id: int) -> bool:
        '''Check if the string passed is a valid number'''
        #After this action is complete update the values
        self.after(10, self.updateValues)
        try:
            #Attempt to convert to float
            float(message)
            return True
        except:
            #If this causes an error it was not a number
            #Cast the id to an integer (it is convertes to a string when passed)
            id = int(id)
            #Get the current values for the inputs
            values = [self.tempRange[0], self.tempRange[1], self.presRange[0], self.presRange[1], self.duration, self.tipTime]
            #Change the value of the validated input
            self.floatFields[id].set(values[id])
            return False


    def updateValues(self) -> None:
        '''Update the labels to show the correct values'''
        #Update the values from the fields
        self.tempRange[0] = float(self.minTempVar.get())
        self.tempRange[1] = float(self.maxTempVar.get())
        self.presRange[0] = float(self.minPresVar.get())
        self.presRange[1] = float(self.maxPresVar.get())
        self.duration = float(self.durationVar.get())
        self.tipTime = float(self.tipTimeVar.get())
        #Set the label text to be the same as the value
        self.tempLabel.configure(text="Temperature (deg)\n" + str(self.tempRange[0]) + " to " + str(self.tempRange[1]))
        self.presLabel.configure(text="Pressure (hPa)\n" + str(self.presRange[0]) + " to " + str(self.presRange[1]))
        self.durationLabel.configure(text="Duration (min)\n" + str(self.duration))
        self.tipTimeLabel.configure(text="Tip Delay (min)\n" + str(self.tipTime))
    

    def generateTips(self) -> None:
        '''Generate a list of tips given the input values'''
        #Remove all previous information
        self.textList.delete(0, tkinter.END)
        #List to hold any errors received
        errors = []
        #Error checks and messages
        if self.duration <= 0:
            errors.append("Duration must be a non-zero positive value")
        if self.tipTime <= 0:
            errors.append("Tip Delay must be a non-zero positive value")
        if self.tempRange[1] - self.tempRange[0] < 0:
            errors.append("Temperature Maximum must be greater than or equal to Temperature Minimum")
        if self.presRange[1] - self.presRange[0] < 0:
            errors.append("Pressure Maximum must be greater than or equal to Pressure Minimum")
        if self.tipTime > self.duration:
            errors.append("Tip delay must be shorter than the total Duration.")
        
        #If there are no errors
        if len(errors) < 1:
            #Setup variables
            time = 0
            tipNumber = 0
            currentBucket = 1

            #Retrieve the values from the fields
            totalSeconds = self.duration * 60
            delaySeconds = self.tipTime * 60
            tempBounds = [self.tempRange[0], self.tempRange[1]]
            presBounds = [self.presRange[0], self.presRange[1]]
            
            #Not yet complete
            done = False

            #Repeat until finished (out of time)
            while not done:
                #Increment time by tip delay
                time = time + delaySeconds
                #If there is still time remaining
                if time < totalSeconds:
                    #Get a random temperature and pressure
                    temp = round(random.uniform(tempBounds[0], tempBounds[1]), 2)
                    pres = round(random.uniform(presBounds[0], presBounds[1]), 2)

                    #Output tip data to the text list
                    self.textList.insert(tkinter.END, str(tipNumber) + " , " + str(int(time)) + " , " + str(currentBucket) + " , " + str(temp) + " , " + str(pres))

                    #Next bucket
                    currentBucket = currentBucket + 1
                    #Back to start of buckets if end reached
                    if currentBucket > 15:
                        currentBucket = 1
                    
                    #Increase tip id
                    tipNumber = tipNumber + 1
                else:
                    #If time is finished - do not generate any more
                    done = True
            
            #The data currently in the listbox is valid
            self.validData = True

        else:
            #An error occurred so the listbox does not contain valid data
            self.validData = False
            #Iterate through the errors
            for error in errors:
                #Output into the listbox
                self.textList.insert(tkinter.END, error)
    
    def exportDataLog(self) -> None:
        '''Export the information into a csv file'''
        #If the data currently in the list is valid
        if self.validData:
            #Get all the lines
            lines = self.textList.get(0, self.textList.size() - 1)
            allData = ""
            #Add all the lines to a string, separated with newlines and remove any spaces
            for line in lines:
                allData = allData + line.replace(" ", "") + "\n"
            
            #Add the end of data marker
            allData = allData + "End of data,,,,"
            #Get a path to save to
            path = filedialog.asksaveasfilename(title="Save event log csv file", filetypes=self.fileTypes, defaultextension=self.fileTypes)

            #Variable to store if the file was saved
            success = False

            #If a path was given
            if path != "":
                #Make an attempt to save it and store the result in success
                success = createSetup.saveAsFile(path, allData)
            
            #Display an appropriate message depending on success of save operation
            if success:
                messagebox.showinfo(title="Saved", message="File saved successfully.")
            else:
                messagebox.showinfo(title="Not Saved", message="File was not saved.")
        
        else:
            #If there was not valid data display a message indicating so
            messagebox.showinfo(title="No information", message="No data has been generated so it cannot be exported.")


#Only run if this is the main module being run
if __name__ == "__main__":
    #Create root window for tkinter
    root = tkinter.Tk()
    #Set the shape of the window
    root.geometry("600x610")
    #Window cannot be resized
    root.resizable(False, False)
    #Set the title text of the window
    root.title("Event Log GFM")
    #Add the editor to the root windows
    mainWindow(root).grid(row = 0, column=0, sticky="NESW")
    #Start running the root
    root.mainloop()