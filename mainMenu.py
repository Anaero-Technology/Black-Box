import tkinter
from tkinter.font import Font
from tkinter import messagebox
import setupGUI
#import eventLogGUI
import dataReceiveGUI
import processDataGUI
import graphCreatorGUI
import configureClockGUI

class settingsWindow(tkinter.Frame):
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
        self.headerFont = Font(size=14)
        self.textFont = Font(size=10)

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
            settingsFile = open("options.txt", "r")
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
        settingsFile = open("options.txt", "w")
        #Write the data
        settingsFile.write(data)
        #Close the file
        settingsFile.close()
    
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



class mainWindow(tkinter.Frame):
    '''Class to contain all of the menus'''
    def __init__(self, parent, *args, **kwargs):
        #Setup parent configuration
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        #Rows needed for this frame
        self.numberRows = 6
        self.numberColumns = 7

        #Setup rows and columns
        for row in range(0, self.numberRows):
            self.grid_rowconfigure(row, weight=1)
        for col in range(0, self.numberColumns):
            self.grid_columnconfigure(col, weight=1)

        #Create a font for the buttons
        self.buttonFont = Font(size=16)
        self.headerFont = Font(size=14)
        self.textFont = Font(size=10)
        
        #Setup each of the option buttons and add them to the correct row
        #Setup file configuration
        self.setupButton = tkinter.Button(self, text="Experiment Settings", command=self.openSetupWindow, font=self.buttonFont)
        self.setupButton.grid(row=1, column=1, columnspan = 5)
        #Event log configuration
        self.eventLogButton = tkinter.Button(self, text="Connect to GFM", command=self.openCommunicationWindow, font=self.buttonFont)
        self.eventLogButton.grid(row=0, column=1, columnspan=5)
        #Performing calculations
        self.calculationsButton = tkinter.Button(self, text="Analyse Data", command=self.openCalculationsWindow, font=self.buttonFont)
        self.calculationsButton.grid(row=2, column=1, columnspan=5)
        #Creating graphs
        self.graphsButton = tkinter.Button(self, text="Create Graphs", command=self.openGraphsWindow, font=self.buttonFont)
        self.graphsButton.grid(row=3, column=1, columnspan=5)
        #Setting clock time
        self.clockButton = tkinter.Button(self, text="Set Date/Time", command=self.openClockWindow, font=self.buttonFont)
        self.clockButton.grid(row=4, column=1, columnspan=5)
        #Quit all
        self.exitButton = tkinter.Button(self, text="Exit", command=self.closeAll, font=self.buttonFont)
        self.exitButton.grid(row=5, column=2, columnspan=3)

        self.settingsImage = tkinter.PhotoImage(file="settingsIcon.png")

        self.settingsButton = tkinter.Button(self, image=self.settingsImage, command=self.openSettingsWindow)
        self.settingsButton.grid(row=5, column=5)

        #Get the centre of the screen
        self.screenCentre = [self.parent.winfo_screenwidth() / 2, self.parent.winfo_screenheight() / 2]

        #Variables to hold the different windows currently in use
        self.setupWindow = None
        self.communicationWindow = None
        self.dataProcessWindow = None
        self.graphWindow = None
        self.clockWindow = None
        self.settingsWindow = None

        self.dataReceiveTopLevel = None
    
    def openSetupWindow(self) -> None:
        '''Create a new instance of the setup window, or lift and focus the current one'''
        try:
            self.settingsWindow.lift()
            self.settingsWindow.destroy()
            self.settingsWindow = None
        except:
            pass
        try:
            #Attempt to lift and focus a current window (will not work if it does not exist or has been closed)
            self.setupWindow.lift()
            self.setupWindow.focus()
        except:
            #If unable to do so, create a new setup window
            self.setupWindow = tkinter.Toplevel(self.parent)
            self.setupWindow.transient(self.parent)
            self.setupWindow.geometry("600x610+{0}+{1}".format(int(self.screenCentre[0] - 300), int(self.screenCentre[1] - 305)))
            self.setupWindow.minsize(550, 400)
            self.setupWindow.title("Setup GFM")
            self.setupWindow.grid_rowconfigure(0, weight=1)
            self.setupWindow.grid_columnconfigure(0, weight=1)
            setupGUI.mainWindow(self.setupWindow).grid(row=0, column=0, sticky="NESW")
            self.setupWindow.focus()

    def openCommunicationWindow(self) -> None:
        '''Create a new instance of the communication window, or lift and focus the current one'''
        try:
            #If the settings window is open - destroy it
            self.settingsWindow.lift()
            self.settingsWindow.destroy()
            self.settingsWindow = None
        except:
            pass
        try:
            #Attempt to lift and focus a current window (will not work if it does not exist or has been closed)
            self.communicationWindow.lift()
            self.communicationWindow.focus()
        except:
            #If unable to do so, create a new communication window
            self.communicationWindow = tkinter.Toplevel(self.parent)
            self.communicationWindow.transient(self.parent)
            self.communicationWindow.geometry("400x500+{0}+{1}".format(int(self.screenCentre[0] - 200), int(self.screenCentre[1] - 250)))
            self.communicationWindow.minsize(400, 500)
            self.communicationWindow.title("GFM Data Receive")
            self.communicationWindow.grid_rowconfigure(0, weight=1)
            self.communicationWindow.grid_columnconfigure(0, weight=1)
            self.dataReceiveTopLevel = dataReceiveGUI.mainWindow(self.communicationWindow)
            self.dataReceiveTopLevel.grid(row = 0, column=0, sticky="NESW")
            self.communicationWindow.protocol("WM_DELETE_WINDOW", self.dataReceiveTopLevel.closeWindow)
            self.communicationWindow.focus()

    def openCalculationsWindow(self) -> None:
        '''Create a new instance of the proccessing window, or lift and focus the current one'''
        try:
            #If the settings window is open - destroy it
            self.settingsWindow.lift()
            self.settingsWindow.destroy()
            self.settingsWindow = None
        except:
            pass
        try:
            #Attempt to lift and focus a current window (will not work if it does not exist or has been closed)
            self.dataProcessWindow.lift()
            self.dataProcessWindow.focus()
        except:
            #If unable to do so, create a new processing window
            self.dataProcessWindow = tkinter.Toplevel(self.parent)
            self.dataProcessWindow.transient(self.parent)
            self.dataProcessWindow.geometry("1095x620+{0}+{1}".format(int(self.screenCentre[0] - 547), int(self.screenCentre[1] - 310)))
            self.dataProcessWindow.minsize(800, 300)
            self.dataProcessWindow.title("Process GFM Data")
            self.dataProcessWindow.grid_rowconfigure(0, weight=1)
            self.dataProcessWindow.grid_columnconfigure(0, weight=1)
            processDataGUI.mainWindow(self.dataProcessWindow).grid(row = 0, column=0, sticky="NESW")
            self.dataProcessWindow.focus()

    def openGraphsWindow(self) -> None:
        '''Create a new instance of the graphs window, or lift and focus the current one'''
        try:
            #If the settings window is open - destroy it
            self.settingsWindow.lift()
            self.settingsWindow.destroy()
            self.settingsWindow = None
        except:
            pass
        try:
            #Attempt to lift and focus a current window (will not work if it does not exist or has been closed)
            self.graphWindow.lift()
            self.graphWindow.focus()
        except:
            #If unable to do so, create a new graphs window
            self.graphWindow = tkinter.Toplevel(self.parent)
            self.graphWindow.transient(self.parent)
            self.graphWindow.geometry("800x575+{0}+{1}".format(int(self.screenCentre[0] - 400), int(self.screenCentre[1] - 287)))
            self.graphWindow.minsize(800, 575)
            self.graphWindow.title("GFM Graph Creator")
            self.graphWindow.grid_rowconfigure(0, weight=1)
            self.graphWindow.grid_columnconfigure(0, weight=1)
            graphCreatorGUI.mainWindow(self.graphWindow).grid(row = 0, column=0, sticky="NESW")
            self.graphWindow.focus()

    def openClockWindow(self) -> None:
        '''Create a new instance of the time configuration window, or lift and focus the current one'''
        try:
            #Attempt to lift and focus a current window (will not work if it does not exist or has been closed)
            self.clockWindow.lift()
            self.clockWindow.focus()
        except:
            #If unable to do so, create a new time window
            self.clockWindow = tkinter.Toplevel(self.parent)
            self.clockWindow.transient(self.parent)
            self.clockWindow.geometry("400x400+{0}+{1}".format(int(self.screenCentre[0] - 200), int(self.screenCentre[1] - 200)))
            self.clockWindow.minsize(400, 400)
            self.clockWindow.title("Clock Time Configuration")
            self.clockWindow.grid_rowconfigure(0, weight=1)
            self.clockWindow.grid_columnconfigure(0, weight=1)
            configureClockGUI.mainWindow(self.clockWindow).grid(row = 0, column=0, sticky="NESW")
            self.clockWindow.focus()

    def openSettingsWindow(self) -> None:
        '''Create a new instance of the settings window, or lift and focus the current one'''
        #Counter for number of other windows open
        windowsPresent = 0
        try:
            #Try to access the setup window
            self.setupWindow.lift()
            windowsPresent = windowsPresent + 1
        except:
            pass
        try:
            #Try to access the communication window
            self.communicationWindow.lift()
            windowsPresent = windowsPresent + 1
        except:
            pass
        try:
            #Try to access the processing window
            self.dataProcessWindow.lift()
            windowsPresent = windowsPresent + 1
        except:
            pass
        try:
            #Try to access the graphing window
            self.graphWindow.lift()
            windowsPresent = windowsPresent + 1
        except:
            pass
        
        #If there were any other windows open
        if windowsPresent > 0:
            #Display message to indicate that the other windows should be closed first
            messagebox.showinfo(title="Other Windows Open", message="Please close all other GFM windows before changing the settings.")
        else:
            #Open the settings window
            try:
                #Attempt to lift and focus a current window (will not work if it does not exist or has been closed)
                self.settingsWindow.lift()
                self.settingsWindow.focus()
            except:
                #If unable to do so, create a new settings window
                self.settingsWindow = tkinter.Toplevel(self.parent)
                self.settingsWindow.transient(self.parent)
                self.settingsWindow.grid_columnconfigure(0, weight=1)
                self.settingsWindow.grid_rowconfigure(0, weight=1)
                self.settingsWindow.geometry("600x300+{0}+{1}".format(int(self.screenCentre[0] - 300), int(self.screenCentre[1] - 150)))
                self.settingsWindow.title("Settings")
                settingsWindow(self.settingsWindow).grid(row=0, column=0, sticky="NESW")
                self.settingsWindow.focus()

    def closeAll(self) -> None:
        '''Close all the tkinter windows - terminates the program'''
        try:
            self.dataReceiveTopLevel.closeWindow()
        except:
            pass
        self.parent.destroy()



#Only run if this is the main module being run
if __name__ == "__main__":
    #Create root window for tkinter
    root = tkinter.Tk()
    #Calculate the position of the centre of the screen
    screenMiddle = [root.winfo_screenwidth() / 2, root.winfo_screenheight() / 2]
    #Set the shape of the window and place it in the centre of the screen
    root.geometry("400x500+{0}+{1}".format(int(screenMiddle[0] - 200), int(screenMiddle[1] - 250)))
    #Allow for expanding sizes
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    #Set the title text of the window
    root.title("Setup GFM")
    #Add the editor to the root windows
    mainWindow(root).grid(row = 0, column=0, sticky="NESW")
    #Start running the root
    root.mainloop()