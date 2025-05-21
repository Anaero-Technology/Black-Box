import os, sys
import pathlib

def read() -> list:
    '''Read separators from file and return them'''
    try:
        #Attempt to read
        #Find path to file
        filePath = os.path.join(os.path.expanduser("~"), "AppData", "Local", "AnaeroGFM", "options.txt")
        #Open the file
        separatorFile = open(filePath, "r")
        #Read all data from it
        data = separatorFile.read()
        data = data.split("\n")
        unallowed = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -"
        columnSeparator = ","
        decimalSeparator = "."
        custom  = False
        #Iterate through lines
        for line in data:
            #Remove excess white space
            line = line.strip()
            #Split based on space
            parts = line.split(" ")
            #If this line indicates the selected option
            if parts[0] == "selected:":
                #If it is 0
                if parts[1] == "0":
                    #Return comma separated
                    return ",", "."
                #If it is 1
                elif parts[1] == "1":
                    #Return semicolon separated
                    return ";", ","
                #If it is 2
                elif parts[1] == "2":
                    #It is the custom option
                    custom = True
            #If this is the line specifying the custom column
            elif parts[0] == "column:":
                #If it is an allowed character and only 1
                if len(parts[1]) == 1 and parts[1] not in unallowed:
                    #Set the custom column symbol
                    columnSeparator = parts[1]
            #If this is the line specifying the custom decimal
            elif parts[0] == "decimal:":
                #If it is an allowed character and only 1
                if len(parts[1]) == 1 and parts[1] not in unallowed:
                    #Set the custom decimal symbol
                    decimalSeparator = parts[1]
        
        #If custom was chosen and the two separators do not match
        if custom and columnSeparator != decimalSeparator:
            #Return the custom separators
            return columnSeparator, decimalSeparator
    
        #If nothing was chosen - default to comma separated
        writeSeparators(0, ",", ".")
        return ",", "."
    
    except Exception as e:
        print(e)
        #If something went wrong (no file or format error) - default to comma separated
        writeSeparators(0, ",", ".")
        return ",", "."

def writeSeparators(selection, customColumn, customDecimal) -> None:
        '''Write the separator options to a file'''
        #Create data with selected option and custom separators
        data = "selected: {0}\ncolumn: {1}\ndecimal: {2}\n".format(selection, customColumn, customDecimal)
        #Find path to file
        basePath = os.path.expanduser("~")
        basePath = os.path.join(basePath, "AppData", "Local", "AnaeroGFM")
        pathlib.Path(basePath).mkdir(parents=True, exist_ok=True)
        #Open the file
        settingsFile = open(os.path.join(basePath, "options.txt"), "w")
        #Write the data
        settingsFile.write(data)
        #Close the file
        settingsFile.close()
