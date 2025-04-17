import readSetup
import createSetup

class ContinuousRange():
    '''Object to hold a list of values and times so an average midpoint can be retreived'''
    def __init__(self, times, values):
        #Combine the times and values to 2d array
        together = zip(times, values)
        #Sort the list based on the times
        sortedList = sorted(together)
        #Split the 2d array back into times and values - now sorted and associated together
        times, values = zip(*sortedList)
        #Store data values
        self.timeData = list(times)
        self.valueData = list(values)
        #Get the minimum and maximum time values
        self.minTime = self.timeData[0]
        self.maxTime = self.timeData[-1]
    
    def getValue(self, time : int) -> float:
        '''Get the value at the given time or the average if it falls between two times'''
        #If the time is not within the range
        if time < self.minTime or time > self.maxTime:
            #Zero value as default or 'does not exist'
            return 0
        else:
            #If the time is exactly in the list of values
            if time in self.timeData:
                #Get the position of the value
                index = self.timeData.index(time)
                #Return the value at that position
                return self.valueData[index]
            
            #Iterate through the times
            for tInd in range(0, len(self.timeData) - 1):
                #Get the time at the index
                t = self.timeData[tInd]
                #If the value is less than the time
                if t < time:
                    #Get the two values
                    v1 = self.valueData[tInd]
                    v2 = self.valueData[tInd + 1]
                    #Calculate average and return
                    value = averageValue(v1, v2)
                    return value
            
            #If a valid position was not found
            return 0

def averageValue(*args) -> float:
    '''Calculate the average of the given values'''
    #If values were given
    if len(args) > 0:
        #Calculate the total
        total = sum(args)
        #Divide by number of values and return
        return total / len(args)
    #No value could be calculated
    return 0

def addZeroes(array : list, count : int) -> list:
    '''Pad out given list so that each row has count values, adding 0 to meet this length'''
    #Create empty array
    result = []
    #Iterate rows
    for lineNumber in range(0, len(array)):
        #Add new blank line
        result.append([])
        #Count items in line
        lineLength = len(array[lineNumber])
        #Iterate through items
        for itemNumber in range(0, lineLength):
            #Add item to last line
            result[-1].append(array[lineNumber][itemNumber])
        #If extra items need to be added
        if lineLength < count:
            #Iterate through difference
            for _ in range(lineLength, count):
                #Add a 0
                result[-1].append(0)
    
    #Return array of adjusted size
    return result
    
def mergeDataPhRedox(fullData : list, readingData : list, assoc : dict, parent : object) -> list:
    '''Combine ph/redox file data with event log to form ph/redox file'''
    #readingData format: [[ [Times], [[pH1 List], [pH2 List], [pH3 List], [pH4 List]], [[redox1 List], [redox2 List], [redox3 List], [redox4 List]] ], ...]
    #Pad to 5 places (adds 2 zeroes on the end)
    resultData = addZeroes(fullData, 5)

    progressCounter = 0

    #List of range objects used for data
    rangeList = [[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]]

    #Iterate through associations
    for channel in assoc:
        value = assoc[channel]
        #Get the associations given
        phAssoc = value[0]
        redoxAssoc = value[1]

        phRange = None
        redoxRange = None
        
        #If there is a valid pH association
        if phAssoc[0] > -1 and phAssoc[0] < len(readingData) and phAssoc[1] > -1 and phAssoc[1] < 4:
            #If there is data in the input
            if readingData[phAssoc[0]][1] != None:
                #Get the time and ph data lists
                timeData = readingData[phAssoc[0]][0]
                phData = readingData[phAssoc[0]][1][phAssoc[1]]
                #Create range from time and data
                phRange = ContinuousRange(timeData, phData)

        #If there is a valid redox association
        if redoxAssoc[0] > -1 and redoxAssoc[0] < len(readingData) and redoxAssoc[1] > -1 and redoxAssoc[1] < 4:
            #If there is data in the input
            if readingData[redoxAssoc[0]][2] != None:
            #if readingData[1][redoxAssoc[0]] != None:
                #Get the time and redox data lists
                timeData = readingData[redoxAssoc[0]][0]
                redoxData = readingData[redoxAssoc[0]][2][redoxAssoc[1]]
                #Create range from time and data
                redoxRange = ContinuousRange(timeData, redoxData)
        
        #Store the ranges in the list (if present)
        if phRange != None:
            rangeList[0][channel - 1] = phRange
        if redoxRange != None:
            rangeList[1][channel - 1] = redoxRange
        
    #Iterate lines in event log
    for dataLine in range(0, len(resultData)):
        #Get the channel
        channel = int(resultData[dataLine][2]) - 1
        #Get the time
        time = resultData[dataLine][1]

        #If there is a pH association
        if rangeList[0][channel] != None:
            #Get the value at that time and add it to final data
            resultData[dataLine][-2] = rangeList[0][channel].getValue(time)
        #If there is a redox association
        if rangeList[1][channel] != None:
            #Get the value at that time and add it to final data
            resultData[dataLine][-1] = rangeList[1][channel].getValue(time)

        #Attempt to update value of the progress bar if possible
        progressCounter = progressCounter + 1
        try:
            parent.newProgressValue = progressCounter
        except:
            pass
    
    #Return the processed data
    return resultData
                
def mergeDataGas(fullData : list, readingData : list, assoc : dict, parent : object) -> list:
    '''Combine ph/redox file data with event log to form ph/redox file'''
    #fullData: [[tipNumber, time, channel]...]
    #Pad to 5 places (adds 2 zeroes on the end)
    resultData = addZeroes(fullData, 5)

    ranges = []

    #Iterate through the channels
    for index in range(0, 15):
        #If there is an association for this channel
        if index in assoc:
            #Get the channel it is associated with
            asc = assoc[index]
            #Get the data for that association
            gasGroup = resultData[asc[0]]
            times = []
            co2Values = []
            ch4Values = []
            #Iterate through the data rows
            for row in range(len(gasGroup[0])):
                #If the channel matches
                if gasGroup[1][row] == index:
                    #Store the time, co2 and ch4 values
                    times.append(gasGroup[0][row])
                    co2Values.append(gasGroup[2][row])
                    ch4Values.append(gasGroup[3][row])
            
            #Create ranges for the co2 and ch4
            co2Range = ContinuousRange(times, co2Values)
            ch4Range = ContinuousRange(times, ch4Values)
            ranges.append([co2Range, ch4Range])
        else:
            ranges.append(None)

    progressCounter = 0
    
    #Iterate through the rows in the event log
    for dataRowNumber in range(0, len(resultData)):
        #Get the row
        dataRow = resultData[dataRowNumber]
        #Get the channel and time
        eventChannel = dataRow[2]
        eventTime = dataRow[1]
        #If there is an association for that channel
        if ranges[eventChannel - 1] != None:
            #Get the values from the ranges
            co2Value = ranges[eventChannel - 1][0].getValue(eventTime)
            ch4Value = ranges[eventChannel - 1][1].getValue(eventTime)
            #Add values to the array
            resultData[dataRowNumber][-2] = co2Value
            resultData[dataRowNumber][-1] = ch4Value
        
        #Attempt to update the progress bar if possible
        progressCounter = progressCounter + 1
        try:
            parent.newProgressValue = progressCounter
        except:
            pass

    #Return the processed data
    return resultData
