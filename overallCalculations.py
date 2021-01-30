def performGeneralCalculations(setupData, eventData) -> [list, str]:
    '''Take in the setup information and list of events and convert to hourly volumes produced'''
    #List to contain data to be returned
    completeData = []

    #Number of seconds in an hour
    hourLength = 60 * 60
    #Time of the last hour start
    lastHour = 0

    #List to contain volumes for the current hour
    currentHour = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    #2d list to contain the volumes produced for each hour
    hourList = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    #A list to contain the innoculum volumes for each hour
    hourInnoculum = [[]]
    #List to contain the average innoculum volumes for each hour
    hourInnoculumAvg = []
    #List to contain the average innoculum volumes for each day
    dayInnoculumAvg = []
    #The volume procuded each hour with the average innoculum subtracted
    hourListWithoutInnoculum = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    #The volume produced, without innoculum, per hour per gram for each channel
    hourListWithoutInnoculumPerGram = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    #List to contain the volume produced each day
    dayList = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    #List to contain the volume produced each day with the innoculum average for the day subtracted
    dayListWithoutInnoculum = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    #The volume produced, without innoculum, per day, per gram for each channel
    dayListWithoutInnoculumPerGram = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    #The constant gass value for a given channel
    gassConstants = []

    #If there are less than 15 channnels in the setup
    if len(setupData) < 16:
        #Report error and stop
        return [], "Setup file not formatted correctly, ensure that all 15 rows are present as well as field names."

    #Setup information about each channel
    names = []
    inUse = []
    innoculumOnly = []
    innoculumMass = []
    sampleMass = []
    tumblerVolume = []

    #Attempt to read setup file
    try:
        #Iterate through the lines (not the first as it is the column headers)
        for row in range(1, len(setupData)):
            #Store each piece of information from the row in the correct list
            names.append(setupData[row][0])
            inUse.append(int(setupData[row][1]) == 1)
            innoculumOnly.append(int(setupData[row][2]) == 1)
            innoculumMass.append(float(setupData[row][3]))
            sampleMass.append(float(setupData[row][4]))
            tumblerVolume.append(float(setupData[row][5]))
        
        #Go through all the tubes
        for tubeId in range(0, len(tumblerVolume)):
            #Calculate the gass constant for the tube P * V / T - so that the volume can be derrived from temperature and pressure easily upon tip
            stpConst = (1013.2501 * tumblerVolume[tubeId]) / 273.13
            gassConstants.append(stpConst)

    except:
        #Formatting of setup file is incorrect - reort error and stop
        return [], "Setup file not formatted correctly, ensure that all fields are of the correct data types."

    #Attempt to process the event data
    #try:
    #Iterate through the events that occured
    for event in eventData:
        #Add relevant data for each event - update as each hour passes and each day (also store innoculum data and averages then adjust hourly values at threshold)
        #Event - event id, time (s), bucket number, temperature (deg C), pressure (hPa)

        #Get the time that the event occurred at
        time = int(float(event[1]))
        #if another hour has passed
        if time - lastHour > hourLength:

            #For each of the channels
            for hourId in range(0, len(currentHour)):

                #Add the current hour value to the list of hours
                hourList[hourId].append(currentHour[hourId])

                #If this is one of the innculum only channels - add it's value (of volume per gram) to the list
                if innoculumOnly[hourId]:
                    hourInnoculum[-1].append(currentHour[hourId] / innoculumMass[hourId])

                #Reset the current hour ready for the next one
                currentHour[hourId] = 0

                #Iterate through 1 to number of hours passed (in case multiple hours pass between tips)
                for _ in range(1, int((time - lastHour) / hourLength)):
                    #Add a 0 to the hour list
                    hourList[hourId].append(0)
                    #If this is innoculum - nothing passed here too
                    if innoculumOnly[hourId]:
                        hourInnoculum[-1].append(0)
            
            #Add a new list to the hourly inocculum totals (for the new hour)
            hourInnoculum.append([])
            
            #Add the necessary amount to the number of hours passed
            for _ in range(0, int((time - lastHour) / hourLength)):
                lastHour = lastHour + hourLength
        
        #Get the id of the channel
        idNum = int(event[2]) - 1
        #Calculate the volume - using gass constant, temperature and pressure
        volume = gassConstants[idNum] * (float(event[3]) + 237.13) / float(event[4])
        #Add this amount to the current hourly value for that channel
        currentHour[idNum] = currentHour[idNum] + volume
    
    #If the last innoculum value set is not filled - remove it
    if len(hourInnoculum[-1]) == 0:
        del hourInnoculum[-1]

    #Iterate through the hours
    for hourId in range(0, len(hourInnoculum)):
        #Calculate the average gass volume produced of innoculum (per gram)
        average = sum(hourInnoculum[hourId]) / len(hourInnoculum[hourId])
        hourInnoculumAvg.append(average)
    
    #Iterate through the tubes
    for tubeId in range(0, len(hourList)):
        #Iterate through the hours
        for hourId in range(0, len(hourList[tubeId])):
            #Calculate the total gass evolved that hour: volume - (average volume per g of innoculum * mass of innoculum)
            extraGassEvolved = hourList[tubeId][hourId] - (hourInnoculumAvg[hourId] * innoculumMass[tubeId])
            #Default volume of 0 per gram
            extraGassEvolvedPerGram = 0
            #If this tube contains a sample
            if not innoculumOnly[tubeId] and sampleMass[tubeId] > 0:
                #Divide by the mass in the tube to get volume per gram
                extraGassEvolvedPerGram = extraGassEvolved / sampleMass[tubeId]
            #Add volumes to lists total volume and per gram
            if not innoculumOnly[tubeId]:
                #If it is a sample tube
                hourListWithoutInnoculum[tubeId].append(extraGassEvolved)
                hourListWithoutInnoculumPerGram[tubeId].append(extraGassEvolvedPerGram)
            else:
                #If this is an innoculum tube
                hourListWithoutInnoculum[tubeId].append(0)
                hourListWithoutInnoculumPerGram[tubeId].append(0)
    
    #Iterate through the tubes
    for tubeId in range(len(hourList)):
        #Each of the totals is 0
        hourCount = 0
        dayVal = 0
        dayValWithoutI = 0
        dayValWithoutIPerGram = 0
        dayValInnoculumAvg = 0
        #Iterate through each hour
        for hourNumber in range(0, len(hourList[tubeId])):
            #Add the hour value to the running total for day values (volume, volume - innoculum, (volume - innoculum) / sample mass, innoculum average)
            dayVal = dayVal + hourList[tubeId][hourNumber]
            dayValWithoutI = dayValWithoutI + hourListWithoutInnoculum[tubeId][hourNumber]
            dayValWithoutIPerGram = dayValWithoutIPerGram + hourListWithoutInnoculumPerGram[tubeId][hourNumber]
            dayValInnoculumAvg = dayValInnoculumAvg + hourInnoculumAvg[hourNumber]

            #Incrament hour
            hourCount = hourCount + 1
            #If a day has passed
            if hourCount >= 24:
                #Reset counter
                hourCount = 0
                #Add values to lists
                dayList[tubeId].append(dayVal)
                dayListWithoutInnoculum[tubeId].append(dayValWithoutI)
                dayListWithoutInnoculumPerGram[tubeId].append(dayValWithoutIPerGram)
                dayInnoculumAvg.append(dayValInnoculumAvg)
                #Reset values
                dayVal = 0
                dayValWithoutI = 0
                dayValWithoutIPerGram = 0
                dayValInnoculumAvg = 0
        
        #If hours have passed but not a full day (at the end)
        if hourCount != 0:
            #Add the remaining values to form a final (partial) day
            dayList[tubeId].append(dayVal)
            dayListWithoutInnoculum[tubeId].append(dayValWithoutI)
            dayListWithoutInnoculumPerGram[tubeId].append(dayValWithoutIPerGram)
            dayInnoculumAvg.append(dayValInnoculumAvg)
        
    #except:
        #Something is wrong with the way the event log file is formatted - report error and stop
        #return [], "Event file not formatted correctly, ensure that all fields are present and of the correct data type."

    #Group setup information into list
    setup = [names, inUse, innoculumOnly, innoculumMass, sampleMass, tumblerVolume]

    #Group setup data and results into a list
    completeData = [setup, hourList, hourListWithoutInnoculum, hourListWithoutInnoculumPerGram, dayList, dayListWithoutInnoculum, dayListWithoutInnoculumPerGram, hourInnoculum, hourInnoculumAvg, dayInnoculumAvg]
    
    #Return the data and no error was found
    return completeData, None