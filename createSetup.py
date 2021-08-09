import readSeparators

def convertArrayToString(data: list) -> str:
    '''Convert 2d array of data into comma and newline separated string with headings and End of data'''
    #Variable to hold final string
    dataStream = ""

    #Get Separators from file
    column, decimal = readSeparators.read()

    #Iterate through the rows in the data
    for row in data:
        #Iterate through the indexes in the row
        for itemIndex in range(0, len(row)):
            #Get the part - remove any commas or newlines
            #part = row[itemIndex].replace(",", "").replace("\n", "")
            part = row[itemIndex].replace(column, "").replace("\n", "")
            #Convert decimal point to decimal separator
            part = part.replace(".", decimal)
            #Add the part to the stream
            dataStream = dataStream + part
            #If this is not the end of the row
            if itemIndex != len(row) - 1:
                #Separate with column separator
                dataStream = dataStream + column
            else:
                #Otherwise separate with newline
                dataStream = dataStream + "\n"
    
    #If there is actually some data in the file
    if len(data) > 0:
        #Add the end of data marker and the appropriate number of column separators for the columns
        dataStream = dataStream + "End of data" + (column * (len(data[0]) - 1) )
    
    #Return the completed string
    return dataStream
            


def saveAsFile(filePath: str, fileInfo: str) -> bool:
    '''Create file at filepath with the information fileinfo inside'''
    #Remove the whitespace from front and end of path
    filePath = filePath.strip()

    #If there is not a csv extension on the file
    if not filePath.endswith(".csv"):
        #Add extension
        filePath = filePath + ".csv"
    
    #Attempt to save the file
    try:
        #Open the file for writing (create if not present, erase file if it already exists)
        csvFile = open(filePath, "w")
        #Write the information into the file
        csvFile.write(fileInfo)
        #Close the completed file
        csvFile.close()

        #True is returned to indicate that the file saved successfully
        return True
    except:
        #False if returned to indicate that there was an error and the file might not have saved
        return False