import serial
import time
import os, pathlib, sys
from threading import Thread

class fileDownloader():
    def __init__(self, ports, paths, files):
        self.running = True
        self.finished = False
        self.results = []
        self.logs = []
        self.thread = None
        self.portNames = ports
        self.filePaths = paths
        self.fileNames = files

    def read(self, port):
        message = ""
        reading = True
        success = False
        fileName = ""
        file = ""
        size = 0
        startTime = time.time()
        timeout = 60 * 1
        port.write("info\n".encode("utf-8"))
        while reading and self.running:
            try:
                char = port.read()
                if len(char) > 0:
                    c = char.decode("utf-8")
                    if c != "\n":
                        message = message + c
                    else:
                        messageParts = message.split(" ")
                        if messageParts[0] == "info" and len(messageParts) > 2:
                            if messageParts[1] == "1":
                                fileName = messageParts[2]
                                port.write("download {0}\n".format(fileName).encode("utf-8"))
                        elif messageParts[0] == "download":
                            if messageParts[1] == "stop":
                                if size != 0 and size != len(file):
                                    port.write("download {0}\n".format(fileName).encode("utf-8"))
                                else:
                                    reading = False
                                    success = True
                            elif messageParts[1] == "failed":
                                port.write("download {0}\n".format(fileName).encode("utf-8"))
                            elif messageParts[1] == "start":
                                if len(messageParts) > 3:
                                    size = int(messageParts[3])
                            else:
                                file = file + messageParts[1] + "\n"#print(messageParts[1])
                                port.write("next\n".encode("utf-8"))

                        message = ""
                if time.time() - startTime > timeout:
                    success = False
                    reading = False
                    file = "Timed out"
            except:
                pass
        port.close()
        if not self.running:
            return "Cancelled", False
        file = file.replace("\r", "")
        return file, success
    
    def startThread(self) -> None:
        self.thread = Thread(target=self.getData, daemon=True)
        self.thread.start()

    def getData(self):
        self.results = []
        self.logs = []
        for index in range(0, min(len(self.portNames), len(self.filePaths), len(self.fileNames))):
            result = ["", False]
            attempts = 3
            done = False
            while not done and attempts > 0:
                try:
                    p = serial.Serial(port=self.portNames[index], baudrate=115200)
                    data, success = self.read(p)
                    result = [data, success]
                    done = True
                except:
                    attempts = attempts - 1
            if attempts == 0:
                result = ["Failed to connect", False]
            try:
                self.results.append(result[1])
                if result[1]:
                    self.logs.append(self.portNames[index] + " - Downloaded successfully")
                    pathlib.Path(self.filePaths[index]).mkdir(parents=True, exist_ok=True)
                    rawFilePath = os.path.join(self.filePaths[index], "raw_files", self.fileNames[index])
                    dataFile = open(rawFilePath, "w")
                    dataFile.write(result[0])
                    dataFile.close()
                else:
                    self.logs.append(self.portNames[index] + " - " + result[0])
            except:
                pass

            self.finished = True
    

