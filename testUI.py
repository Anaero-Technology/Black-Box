import tkinter
import tkinter.ttk as Ttk
from threading import Thread
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

class mainWindow(tkinter.Frame):
    '''Class to contain all of the editor for the csv files'''
    def __init__(self, parent, *args, **kwargs):
        '''Setup the window and initialize all the sections'''
        #Call parent init so it sets up frame correctly
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=20)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.calculateButton = tkinter.Button(self, text="Calculate", command=self.startCalculation)
        self.calculateButton.grid(row=0, column=0, sticky="NESW")
        #Add frame for output
        self.displayFrame = tkinter.Frame(self)
        self.displayFrame.grid(row=1, column=0, sticky="NESW")
        self.displayFrame.grid_rowconfigure(0, weight=1)
        self.displayFrame.grid_rowconfigure(1, weight=15)
        self.displayFrame.grid_columnconfigure(0, weight=1)
        self.displayFrame.grid_columnconfigure(1, weight=1)
        self.displayDataButton = tkinter.Button(self.displayFrame, text="Data", command=self.showData)
        self.displayDataButton.grid(row=0, column=0, sticky="NESW")
        self.displayGraphButton = tkinter.Button(self.displayFrame, text="Graph", command=self.showGraph)
        self.displayGraphButton.grid(row=0, column=1, sticky="NESW")
        self.dataFrame = tkinter.Frame(self.displayFrame)
        self.graphFrame = tkinter.Frame(self.displayFrame)
        self.graphFrame.grid(row=1, column=0, columnspan=2, sticky="NESW")
        self.dataFrame.grid(row=1, column=0, columnspan=2, sticky="NESW")
        #Add a scroll bar
        self.textScroll = tkinter.Scrollbar(self.dataFrame)
        self.textScroll.pack(side="right", fill="y")
        #self.textScroll.grid(row=0, column=1, sticky="NESW")
        #Add an area to display the text
        self.textList = tkinter.Listbox(self.dataFrame, yscrollcommand=self.textScroll.set)
        #self.textList.grid(row=0, column=0, sticky="NESW")
        self.textList.pack(side="left", fill="both", expand=True)
        self.textScroll.config(command=self.textList.yview)
        #Adding example text to the scroll area
        self.textList.insert(tkinter.END, "No data present yet, press calculate to produce data.")
        self.progress = Ttk.Progressbar(self, orient=tkinter.HORIZONTAL, mode="determinate", maximum=10000.0)
        self.progress.grid(row=2, column=0, sticky="NESW")
        self.progress.grid_remove()

        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.subPlot = self.figure.add_subplot(111)
        self.subPlot.plot([1,2,3,4,5,6,7], [1,1,2,3,5,8,13])
        self.graphCanvas = FigureCanvasTkAgg(self.figure, master=self.graphFrame)
        self.graphCanvas.draw()
        self.graphCanvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.graphCanvas, self.graphFrame)
        self.toolbar.update()
        self.graphCanvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        self.showData()

    def startCalculation(self):
        self.calculateButton.config(state="disabled")
        self.textList.config(state="disabled")
        if self.graphCanvas != None:
            self.graphCanvas.get_tk_widget().config(state="disabled")
        self.progress["maximum"] = 10000.0
        self.progress["value"] = 0
        self.progress.grid()
        primeThread = Thread(target=findPrimes, daemon=True)
        primeThread.start()

    def updateProgress(self, value):
        self.progress["value"] = value

    def receiveList(self, items):
        self.textList.config(state="normal")
        self.textList.delete(0, tkinter.END)
        self.progress["value"] = 0
        self.progress["maximum"] = len(items)

        numberlist = []

        for i in range(len(items)):
            self.progress["value"] = i
            self.textList.insert(tkinter.END, str(items[i]))
            numberlist.append(i + 1)
        
        self.progress.grid_remove()

        self.subPlot.plot(numberlist, items)

        self.calculateButton.config(state="normal")
    
    def showData(self):
        self.dataFrame.tkraise()
    
    def showGraph(self):
        self.graphFrame.tkraise()
        

def findPrimes():
    primeList = []
    for num in range(1, 10000):
        window.updateProgress(num)
        if num > 1:
            prime = True
            for i in range(2, num):
                if (num % i) == 0:
                    prime = False
            
            if prime:
                primeList.append(num)
    
    window.receiveList(primeList)


#Only run if this is the main module being run
if __name__ == "__main__":
    #Create root window for tkinter
    root = tkinter.Tk()
    #Set the shape of the window
    root.geometry("600x610")
    #Set the title text of the window
    root.title("Test Window")
    #Allow for expanding sizes
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    #Add the editor to the root windows
    window = mainWindow(root)
    window.grid(row = 0, column=0, sticky="NESW")
    #Start running the root
    root.mainloop()