import readSeparators

def getFile(fileName: str) -> list:
    '''Open a file from a path and read all the data from it as a list of strings'''

    #Get separators from file
    column, decimal = readSeparators.read()

    #Attempt to open the file
    try:
        #Open file as read mode
        setupFile = open(fileName, "r")
        #Read the data and split into a list
        setupData = setupFile.read()
        setupData.replace(decimal, ".")
        setupData = setupData.split(column)
        #Return the list
        return setupData
    except: 
        #Return empty list if something went wrong
        return []


def formatData(dataList: list) -> list:
    '''Convert a 1 dimensional list of strings into a 2d array (using newline as end of row)'''
    #List to contain 2d array of information
    formattedData = []
    #List to contain the row currently being processed
    currentRow = []
    #Flag to indicate if end of data has been reached
    done = False
    
    #Iterate through all the items in the list
    for index in range(0, len(dataList)):
        #If the end has not been reached
        if not done:
            #Split the next part on new line
            parts = dataList[index].split("\n")
            #If there are parts to add
            if len(parts) > 0:
                #If the end has been reached
                if "End of data" in parts:
                    #No further data to process
                    done = True
                #If there is more than one part
                if len(parts) > 1:
                    #Iterate part index
                    for partIndex in range(0, len(parts)):
                        #Get the part
                        part = parts[partIndex]
                        #If it isn't blank or the end
                        if part != "" and part != "End of data":
                            #Add the part to the current row
                            currentRow.append(part)
                        #If this is not the last item
                        if partIndex != len(parts) - 1:
                            #Add the row
                            formattedData.append(currentRow)
                            #Restart the row
                            currentRow = []
                else:
                    #If the part contains data
                    if parts[0] != "" and parts[0] != "End of data":
                        #Add the part
                        currentRow.append(parts[0])
    
    #If there is still more to add in the row
    if len(currentRow) > 0:
        #Append the final row to the data
        formattedData.append(currentRow)
    
    #Return the 2d array of strings
    return formattedData