import tkinter
from tkinter import filedialog, messagebox
import readSetup
import createSetup
import readSeparators
import notifypy
import os, sys

class MainWindow(tkinter.Frame):
    '''Class to contain all of the editor for the csv files'''
    def __init__(self, parent, *args, **kwargs):
        '''Setup the window and initialize all the sections'''
        #Call parent init so it sets up frame correctly
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        #Window dimension information
        self.width = 600
        self.height = 610
        #Number of rows and columns present
        self.numberRows = 17
        self.numberColumns = 11

        #Get separators from file
        self.column, self.decimal = readSeparators.read()

        #Setup pathing for files stored within one executable or in directory
        self.thisPath = os.path.abspath(".")
        try:
            self.thisPath = sys._MEIPASS
        except:
            pass

        #Configure all the rows and columns
        for rowNumber in range(0, self.numberRows):
            #Increase size of first row
            if rowNumber != 0:
                self.grid_rowconfigure(rowNumber, weight = 10)
            else:
                self.grid_rowconfigure(rowNumber, weight = 12)
        for colNumber in range(0, self.numberColumns):
            #Reduce size for 3 floating number inputs
            if colNumber > 2:
                self.grid_columnconfigure(colNumber, weight = 1)
            else:
                self.grid_columnconfigure(colNumber, weight = 2)
        
        #Column headers
        self.headers = ["Channel", "Description", "In service", "Inoculum\nonly", "Inoculum\nmass VS (g)", "Sample\nmass VS (g)", "Tumbler\nvolume (ml)", "Chimera\nChannel", "Wet\nWeight (g)", "Volatile\nSolids (%)", "Internal Gas\nVolume (ml)"]

        #Holds all the label objects
        self.headerLabels = []
        #Create each of the header labels and add to grid and list
        for col in range(0, self.numberColumns):
            bgColour = "#AAAAFF"
            if col > 6:
                bgColour = "#BABABA"
            label = tkinter.Label(self, text = self.headers[col], bg=bgColour)
            label.grid(row = 1, column = col, sticky = "NESW")
            self.headerLabels.append(label)
        
        #Lists of tube data widgets and variables
        self.tubeInfo = []
        self.tubeVariables = []
        #Number of characters width for the entry widgets
        self.entryLength = 15

        #Register callback functions for validating text entry
        self.numCheck = self.register(self.validateNumber)
        self.nameCheck = self.register(self.validateName)
        self.intCheck = self.register(self.validateInteger)

        #Setup widgets for each row of the table
        for row in range(2, self.numberRows):
            #To Hold this current row of widgets and variables
            tubeRow = []
            tubeVars = []

            channelLabel = tkinter.Label(self, text = str(row - 1))
            tubeRow.append(channelLabel)

            #Description field setup
            descVar = tkinter.StringVar()
            descriptionInput = tkinter.Entry(self, textvariable=descVar, width=self.entryLength + 12, justify="center", validatecommand=(self.nameCheck, "%P"), validate="key")
            tubeRow.append(descriptionInput)
            tubeVars.append(descVar)

            #If the tube is in use field setup
            useVar = tkinter.IntVar()
            inUse = tkinter.Checkbutton(self, variable=useVar, onvalue=1, offvalue=0)
            tubeRow.append(inUse)
            tubeVars.append(useVar)

            #If the tube is only innoculum field setup
            onlyIVar = tkinter.IntVar()
            onlyInoculum = tkinter.Checkbutton(self, variable=onlyIVar, onvalue=1, offvalue=0)
            tubeRow.append(onlyInoculum)
            tubeVars.append(onlyIVar)

            #Mass of innoculum field setup
            massIVar = tkinter.StringVar()
            massInoculum = tkinter.Entry(self, textvariable=massIVar, width=self.entryLength - 4, justify="center", validatecommand=(self.numCheck, "%P"), validate="key")
            tubeRow.append(massInoculum)
            tubeVars.append(massIVar)

            #Mass of sample field setup
            massSVar = tkinter.StringVar()
            massSample = tkinter.Entry(self, textvariable=massSVar, width=self.entryLength - 4, justify="center", validatecommand=(self.numCheck, "%P"), validate="key")
            tubeRow.append(massSample)
            tubeVars.append(massSVar)

            #Volume of tube field setup
            volumeVar = tkinter.StringVar()
            volumeTumbler = tkinter.Entry(self, textvariable=volumeVar, width=self.entryLength - 4, justify="center", validatecommand=(self.numCheck, "%P"), validate="key")
            tubeRow.append(volumeTumbler)
            tubeVars.append(volumeVar)

            chimeraChannelVar = tkinter.StringVar()
            chimeraChannelEntry = tkinter.Entry(self, textvariable=chimeraChannelVar, width=4, justify="center", validatecommand=(self.intCheck, "%P"), validate="key")
            tubeRow.append(chimeraChannelEntry)
            tubeVars.append(chimeraChannelVar)

            wetWeightVar = tkinter.StringVar() 
            wetWeightEntry = tkinter.Entry(self, textvariable=wetWeightVar, width=self.entryLength - 4, justify="center", validatecommand=(self.numCheck, "%P"), validate="key")
            tubeRow.append(wetWeightEntry)
            tubeVars.append(wetWeightVar)

            volatilePercentageVar = tkinter.StringVar()
            volatilePercentageEntry = tkinter.Entry(self, textvariable=volatilePercentageVar, width=self.entryLength - 4, justify="center", validatecommand=(self.numCheck, "%P"), validate="key")
            tubeRow.append(volatilePercentageEntry)
            tubeVars.append(volatilePercentageVar)

            manualVolumeVar = tkinter.StringVar()
            manualVolumeEntry = tkinter.Entry(self, textvariable=manualVolumeVar, width=self.entryLength - 4, justify="center", validatecommand=(self.numCheck, "%P"), validate="key")
            tubeRow.append(manualVolumeEntry)
            tubeVars.append(manualVolumeVar)

            #Add widgets and variables rows to lists
            self.tubeInfo.append(tubeRow)
            self.tubeVariables.append(tubeVars)
        
        #Iterate throug each widget in the 2d array
        for row in range(0, len(self.tubeInfo)):
            for col in range(0, len(self.tubeInfo[row])):
                #Add the widget to the grid
                self.tubeInfo[row][col].grid(row = row + 2, column = col, sticky="NESW")
        
        #Add import and export buttons with correct callbacks
        self.importButton = tkinter.Button(self, text="Load Setup", command=self.openFile)
        self.importButton.grid(row=0, column=0, sticky="NESW")
        self.exportButton = tkinter.Button(self, text="Save Setup", command=self.exportData)
        self.exportButton.grid(row=0, column=1, sticky="NESW")

        #Colours for use with mesages for indicator colour
        self.red = "#DD0000"
        self.green = "#00DD00"
        self.black = "#000000"
        
        #Allowed file types and extensions
        self.fileTypes = [("CSV Files", "*.csv")]

        #File header text used when exporting file as csv
        self.fileHeaders = ["Sample description","In service","Inoculum only","Inoculum mass VS (g)","Sample mass VS (g)","Tumbler volume (ml)", "Chimera Channel", "Wet Weight (g)", "Volatile Solids (%)", "Internal Volume (ml)"]
    

    def displayMessage(self, msg: str, title: str) -> None:
        '''Send user a popup notification with the current title and message'''
        notification = notifypy.Notify()
        notification.title = title
        notification.message = msg
        notification.icon = self.pathTo("images/icon.png")
        notification.send()

    def pathTo(self, path : str) -> str:
        '''Convert local path to find file'''
        return os.path.join(self.thisPath, path)

    def validateNumber(self, message: str) -> bool:
        '''Check if the string passed is a valid number'''
        #If a decimal point has already been found
        decimalFound = False
        #List of allowed characters
        allowed = "0123456789"

        #Number of characters checked - used to allow for negative numbers
        firstCharacter = True

        #If the string passed is a valid number
        valid = True

        #Iterate characters in the string
        for char in message:
            #If it is a number or the first decimal point or a minus sign at the beginning
            if char in allowed or (char == self.decimal and not decimalFound) or (char == "-" and firstCharacter):
                #If it is a decimal point
                if char == self.decimal:
                    #A decimal point has been found - do not allow another
                    decimalFound = True
            else:
                #It was not a valid character
                valid = False
            
            #This is no longer the first character in the string
            firstCharacter = False
        
        #Return if the string is a valid number
        return valid
    
    def validateInteger(self, message : str) -> bool:
        allowed = "0123456789"
        valid = True
        for char in message:
            if char not in allowed:
                valid = False
        
        return valid


    def validateName(self, message: str) -> bool:
        '''Test if a given string is a valid description - it must contain no commas'''
        valid = True
        
        #Iterate characters in the string
        for char in message:
            #If it is a column separator
            if char == self.column:
                #It is not a valid description
                valid = False

        #Return wheter or not the string is valid
        return valid
    
    def openFile(self) -> None:
        '''Open a selected file and read all the data from it into the table'''

        #Get the file name from a dialogue box
        fileName = filedialog.askopenfilename(title="Select setup csv file", filetypes=self.fileTypes)
        
        #Only attempt to load the file if a file was selected
        if fileName != "":
            #Read all the data from this file if possible
            fileData = readSetup.getFile(fileName)

            #Bool to store if the operation was successful
            success = True

            #If there is some data in the read file
            if len(fileData) > 0:
                #Format the information as 2d array
                dataArray = readSetup.formatData(fileData)
                for row in range(1, 16):
                    for col in range(0, len(self.tubeVariables[row - 1])):
                        if col == 0 or col > 2:
                            self.tubeVariables[row - 1][col].set("")
                        elif col == 1 or col == 2:
                            self.tubeVariables[row - 1][col].set(0)
                #Attempt to store in table
                try:
                    #Iterate through row indexes
                    for row in range(1, len(dataArray)):
                        #If it does not go beyond rows in the table
                        if row - 1 < len(self.tubeVariables):
                            #Iterate through column indexes
                            for col in range(0, len(dataArray[row])):
                                #If it is a text field
                                if col == 0 or col > 2:
                                    #Add the data as text
                                    self.tubeVariables[row - 1][col].set(dataArray[row][col])
                                #If it is a checkbox field
                                elif col == 1 or col == 2:
                                    #A 1 is a checked box
                                    if dataArray[row][col].strip() == "1":
                                        self.tubeVariables[row - 1][col].set(1)
                                    else:
                                        #Otherwise it is unchecked
                                        self.tubeVariables[row - 1][col].set(0)
                except Exception as e:
                    #If an error occurs then the file was not the correct shape/format so display error message
                    self.displayMessage("File formatted incorrectly, not all values may have been imported successfully.", "Error")
                    success = False
            else:
                #If there was no data then either a file was not chosesn or it was not readable so display error message
                self.displayMessage("Invalid file, please make sure the correct file was chosen.", "Error")
                success = False

            if success:
                #If everything worked correctly display a message indicating so
                self.displayMessage("The file was imported successfully.", "Import Successful")

    def exportData(self) -> None:
        '''Write out all the data in the table to a csv file'''
        #Array to hold all the data from the table
        gatheredData = []
        #Add the headers
        gatheredData.append(self.fileHeaders)

        #List to store where an issue in the table is first present
        errorAt = [-1, -1]

        anyGasData = False
        
        #Iterate through indexes of rows
        for rowIndex in range(0, len(self.tubeVariables)):
            #Create row to add to array
            row = []
            #Iterate through indexes of columns
            for colIndex in range(0, len(self.tubeVariables[rowIndex])):
                #Get the value from the column
                value = self.tubeVariables[rowIndex][colIndex].get()
                #If it is a number
                if colIndex > 2:
                    try:
                        #Attempt to convert to float and back to string to check it is valid (account for separator)
                        value = float(value.replace(self.decimal, "."))
                        value = str(value).replace(".", self.decimal)
                        if colIndex > 5:
                            anyGasData = True
                    except:
                        if colIndex > 5 and not anyGasData:
                            pass
                        else:
                            #Otherwise an error occurred - log it if another error is not already present
                            if errorAt[0] == -1:
                                errorAt = [rowIndex, colIndex]
                else:
                    #Convert the value to a string
                    value = str(value)
                    #If there is no data in it
                    if len(value) < 1:
                        #Store an error if one is not already present
                        if errorAt[0] == -1:
                            errorAt = [rowIndex, colIndex]
                
                #Add the value to the row
                row.append(value)
            
            #Add the complete row to the array
            gatheredData.append(row)
        
        if not anyGasData:
            for rowIndex in range(0, len(gatheredData)):
                gatheredData[rowIndex] = gatheredData[rowIndex][:6]

        #If there is an error
        if errorAt[0] != -1 and errorAt[1] != -1:
            #Display the error to the user
            self.displayMessage("Invalid entry on row: " + str(errorAt[0]) + " for " + self.headers[errorAt[1]].replace("\n", " ") + ". Please fill in all values correctly.", "Error")
        else:
            #Convert the data to be saved to a string
            dataToSave = createSetup.convertArrayToString(gatheredData)
            #Ask the user to give a save location
            path = filedialog.asksaveasfilename(title="Save setup csv file", filetypes=self.fileTypes, defaultextension=self.fileTypes)
            #Only save the file if a path was selected
            if path != "":
                #Try to save the data (success is a bool storing true if the file saved successfully)
                success = createSetup.saveAsFile(path, dataToSave)
                #Display appropriate message for if the file saved or not
                if success:
                    self.displayMessage("The file was saved successfully.", "Save Successful")
                else:
                    self.displayMessage("The file could not be saved, please check location and file name.", "Save Failed")


#Only run if this is the main module being run
if __name__ == "__main__":
    #Create root window for tkinter
    root = tkinter.Tk()
    #Set the shape of the window
    root.geometry("850x610")
    #Allow for expanding sizes
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    #Set the title text of the window
    root.title("Setup GFM")
    #Add the editor to the root windows
    MainWindow(root).grid(row = 0, column=0, sticky="NESW")
    #Start running the root
    root.mainloop()