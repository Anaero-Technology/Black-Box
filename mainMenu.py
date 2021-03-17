import tkinter
from tkinter.font import Font
import setupGUI
#import eventLogGUI
import dataReceiveGUI
import processDataGUI
import graphCreatorGUI


class mainWindow(tkinter.Frame):
    '''Class to contain all of the menus'''
    def __init__(self, parent, *args, **kwargs):
        #Setup parent configuration
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        #Rows needed for this frame
        self.numberRows = 5

        #Setup rows and column
        for row in range(0, self.numberRows):
            self.grid_rowconfigure(row, weight=1)
        self.grid_columnconfigure(0, weight=1)

        #Create a font for the buttons
        self.buttonFont = Font(size=16)
        
        #Setup each of the option buttons and add them to the correct row
        #Setup file configuration
        self.setupButton = tkinter.Button(self, text="Configure Setup", command=self.openSetupWindow, font=self.buttonFont)
        self.setupButton.grid(row=0, column=0)
        #Event log configuration
        self.eventLogButton = tkinter.Button(self, text="ESP Communication", command=self.openCommunicationWindow, font=self.buttonFont)
        self.eventLogButton.grid(row=1, column=0)
        #Performing calculations
        self.calculationsButton = tkinter.Button(self, text="Perform Calculations", command=self.openCalculationsWindow, font=self.buttonFont)
        self.calculationsButton.grid(row=2, column=0)
        #Creating graphs
        self.graphsButton = tkinter.Button(self, text="Create Graphs", command=self.openGraphsWindow, font=self.buttonFont)
        self.graphsButton.grid(row=3, column=0)
        #Quit all
        self.exitButton = tkinter.Button(self, text="Exit", command=self.closeAll, font=self.buttonFont)
        self.exitButton.grid(row=4, column=0)

        #Variables to hold the different windows currently in use
        self.setupWindow = None
        self.communicationWindow = None
        self.dataProcessWindow = None
        self.graphWindow = None
    
    def openSetupWindow(self) -> None:
        '''Create a new instance of the setup window, or lift and focus the current one'''
        try:
            #Attempt to lift and focus a current window (will not work if it does not exist or has been closed)
            self.setupWindow.lift()
            self.setupWindow.focus()
        except:
            #If unable to do so, create a new setup window
            self.setupWindow = tkinter.Toplevel(self.parent)
            #self.setupWindow.transient(self.parent)
            self.setupWindow.geometry("600x610")
            self.setupWindow.minsize(550, 400)
            self.setupWindow.title("Setup GFM")
            self.setupWindow.grid_rowconfigure(0, weight=1)
            self.setupWindow.grid_columnconfigure(0, weight=1)
            setupGUI.mainWindow(self.setupWindow).grid(row=0, column=0, sticky="NESW")
            self.setupWindow.focus()

    def openCommunicationWindow(self) -> None:
        '''Create a new instance of the communication window, or lift and focus the current one'''
        try:
            #Attempt to lift and focus a current window (will not work if it does not exist or has been closed)
            self.communicationWindow.lift()
            self.communicationWindow.focus()
        except:
            #If unable to do so, create a new setup window
            self.communicationWindow = tkinter.Toplevel(self.parent)
            #self.communicationWindow.transient(self.parent)
            self.communicationWindow.geometry("400x500")
            self.communicationWindow.minsize(400, 500)
            self.communicationWindow.title("GFM Data Receive")
            self.communicationWindow.grid_rowconfigure(0, weight=1)
            self.communicationWindow.grid_columnconfigure(0, weight=1)
            dataReceiveGUI.mainWindow(self.communicationWindow).grid(row = 0, column=0, sticky="NESW")
            self.communicationWindow.focus()

    def openCalculationsWindow(self) -> None:
        '''Create a new instance of the proccessing window, or lift and focus the current one'''
        try:
            #Attempt to lift and focus a current window (will not work if it does not exist or has been closed)
            self.dataProcessWindow.lift()
            self.dataProcessWindow.focus()
        except:
            #If unable to do so, create a new processing window
            self.dataProcessWindow = tkinter.Toplevel(self.parent)
            #self.dataProcessWindow.transient(self.parent)
            self.dataProcessWindow.geometry("1095x620")
            self.dataProcessWindow.minsize(800, 300)
            self.dataProcessWindow.title("Process GFM Data")
            self.dataProcessWindow.grid_rowconfigure(0, weight=1)
            self.dataProcessWindow.grid_columnconfigure(0, weight=1)
            processDataGUI.mainWindow(self.dataProcessWindow).grid(row = 0, column=0, sticky="NESW")
            self.dataProcessWindow.focus()

    def openGraphsWindow(self) -> None:
        '''Create a new instance of the graphs window, or list and focus the current one'''
        try:
            #Attempt to lift and focus a current window (will not work if it does not exist or has been closed)
            self.graphWindow.lift()
            self.graphWindow.focus()
        except:
            #If unable to do so, create a new processing window
            self.graphWindow = tkinter.Toplevel(self.parent)
            #self.graphWindow.transient(self.parent)
            self.graphWindow.geometry("800x575")
            self.graphWindow.minsize(800, 575)
            self.graphWindow.title("GFM Graph Creator")
            self.graphWindow.grid_rowconfigure(0, weight=1)
            self.graphWindow.grid_columnconfigure(0, weight=1)
            graphCreatorGUI.mainWindow(self.graphWindow).grid(row = 0, column=0, sticky="NESW")
            self.graphWindow.focus()

    def closeAll(self) -> None:
        '''Close all the tkinter windows - terminates the program'''
        self.parent.destroy()



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
    root.title("Setup GFM")
    #Add the editor to the root windows
    mainWindow(root).grid(row = 0, column=0, sticky="NESW")
    #Start running the root
    root.mainloop()