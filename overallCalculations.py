import readSeparators
import math

def performGeneralCalculations(setupData, eventData):
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
    #A list to contain the inoculum volumes for each hour
    hourinoculum = [[]]
    #List to contain the average inoculum volumes for each hour
    hourinoculumAvg = []
    #List to contain the average inoculum volumes for each day
    dayinoculumAvg = []
    #The volume procuded each hour with the average inoculum subtracted
    hourListWithoutinoculum = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    #The volume produced, without inoculum, per hour per gram for each channel
    hourListWithoutinoculumPerGram = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    #List to contain the volume produced each day
    dayList = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    #List to contain the volume produced each day with the inoculum average for the day subtracted
    dayListWithoutinoculum = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    #The volume produced, without inoculum, per day, per gram for each channel
    dayListWithoutinoculumPerGram = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    #The constant gass value for a given channel
    gasConstants = []

    eventLog = []
    cumulativeTips = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    hourlyTips = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    hourlyVolume = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    dailyTips = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    dailyVolume = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    totalVolume = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    totalNetVol = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    dailyHours = 0
    startTime = 0
    inoculumValues = [[], []]

    hourLog = []
    dayLog = []

    column, decimal = readSeparators.read()

    for row in range(0, len(setupData)):
        for col in range(0, len(setupData[row])):
            setupData[row][col] = setupData[row][col].replace(decimal, ".")
    
    for row in range(0, len(eventData)):
        for col in range(0, len(eventData[row])):
            eventData[row][col] = eventData[row][col].replace(decimal, ".")

    #If there are less than 15 channnels in the setup
    if len(setupData) < 16:
        #Report error and stop
        return [], "Setup file not formatted correctly, ensure that all 15 rows are present as well as field names."

    #Setup information about each channel
    names = []
    inUse = []
    inoculumOnly = []
    inoculumMass = []
    sampleMass = []
    tumblerVolume = []

    #Attempt to read setup file
    try:
        #Iterate through the lines (not the first as it is the column headers)
        for row in range(1, len(setupData)):
            #Store each piece of information from the row in the correct list
            names.append(setupData[row][0])
            inUse.append(int(setupData[row][1]) == 1)
            inoculumOnly.append(int(setupData[row][2]) == 1)
            inoculumMass.append(float(setupData[row][3]))
            sampleMass.append(float(setupData[row][4]))
            tumblerVolume.append(float(setupData[row][5]))
        
        #Go through all the tubes
        for tubeId in range(0, len(tumblerVolume)):
            #Calculate the gass constant for the tube P * V / T - so that the volume can be derrived from temperature and pressure easily upon tip
            stpConst = (1013.2501 * tumblerVolume[tubeId]) / 273.13
            gasConstants.append(stpConst)

    except:
        #Formatting of setup file is incorrect - reort error and stop
        return [], "Setup file not formatted correctly, ensure that all fields are of the correct data types.", None, None, None

    #Attempt to process the event data
    try:
        startTime = int(eventData[0][2])
        #Iterate through the events that occured
        for event in eventData:
            #Add relevant data for each event - update as each hour passes and each day (also store inoculum data and averages then adjust hourly values at threshold)
            #Event - event id, time(YYYY:MM:DD:HH:MM:SS), time (s), bucket number, temperature (deg C), pressure (hPa)

            #Get the time that the event occurred at
            time = int(float(event[2]))

            #Add the data to the event log as needed
            
            #Get the id of the channel that the tip occured on
            tipChannel = int(event[3]) - 1
            #Add one to the total number of tips on that channel
            cumulativeTips[tipChannel] = cumulativeTips[tipChannel] + 1

            #Calculate number of minutes since start
            minutesElapsed = int((time - startTime) / 60)
            hoursElapsed = 0
            daysElapsed = 0
            #Repeatedly remove hour chunks of minutes while adding to hours
            while minutesElapsed > 59:
                minutesElapsed = minutesElapsed - 60
                hoursElapsed = hoursElapsed + 1
            #Repeatedly remove day chunks of hours while adding to days
            while hoursElapsed > 23:
                hoursElapsed = hoursElapsed - 24
                daysElapsed = daysElapsed + 1
            
            #Get the mass for the channel
            mass = sampleMass[tipChannel]
            #If there is only inoculum in this channel
            if inoculumOnly[tipChannel] or mass == 0:
                #Use the inoculum mass
                mass = inoculumMass[tipChannel]

            #If no mass, set to infinity (will set values to 0 when divided by not cause an error)
            if mass == 0:
                mass = math.inf
            
            #Checks for resets due to hour and day rollovers
            #If an hour has elapsed
            if time - lastHour > hourLength:
                #Variables to store the inoculum volume, net volume and number of channels
                inocVol = 0
                inocNetVol = 0
                inocCount = 0
                #Iterate through each channel
                for bucketId in range(0, 15):
                    #Get the mass of sample (or inoculum)
                    thisMass = sampleMass[bucketId]
                    if inoculumOnly[bucketId]:
                        thisMass = inoculumMass[bucketId]
                    #If no mass, set to infinity (will set values to 0 when divided by not cause an error)
                    if thisMass == 0:
                        thisMass = math.inf
                    
                    #Create the event data
                    #Channel, channel name, timestamp (of hour), days, hours, minutes, in service (1/0), no.tips, vol this hour, cumulative net vol (ml/g), cumulative vol 
                    hourEvent = [bucketId + 1, names[bucketId], lastHour + hourLength, daysElapsed, hoursElapsed, minutesElapsed, inUse[bucketId], hourlyTips[bucketId], round(hourlyVolume[bucketId], 3), round(hourlyVolume[bucketId] / thisMass, 3), totalNetVol[bucketId], round(totalVolume[bucketId], 3)]
                    hourLog.append(hourEvent)
                    #If this is an inoculum channel
                    if inoculumOnly[bucketId]:
                        #Add 1 to the counter
                        inocCount = inocCount + 1
                        #Add the volume and net volume to the inoculum values
                        inocVol = inocVol + hourlyVolume[bucketId]
                        inocNetVol = inocNetVol + (hourlyVolume[bucketId] / thisMass)
                #Add the averaged volume and net volume to the hour part of the inoculum data array
                if inocCount > 0:
                    inoculumValues[0].append([(inocVol / inocCount), (inocNetVol / inocCount)])
                else:
                    inoculumValues[0].append([0, 0])
                #Iterate through each channel event that was just added
                for hourEventIndex in range(len(hourEvent) - 15, len(hourEvent)):
                    #Get the index for the channel
                    bucketIndex = hourLog[hourEventIndex][0] - 1
                    #Get the mass (or inoculum mass) for the channel
                    thisMass = sampleMass[bucketIndex]
                    if inoculumOnly[bucketIndex]:
                        thisMass = inoculumMass[bucketIndex]
                    #If no mass, set to infinity (will set values to 0 when divided by not cause an error)
                    if thisMass == 0:
                        thisMass = math.inf
                    #Subtract the average net volume of inoculum from the net volume evolved - adjusted for the mass of inoculum in the channel
                    #net volume per gram * sample mass - net volume inoculum per gram * inoculum mass = net volume evolved
                    #net volume evolved / sample mass = net volume evolved per gram
                    hourLog[hourEventIndex][9] = round(((hourLog[hourEventIndex][9] * thisMass) - (inoculumMass[bucketIndex] * inoculumValues[0][-1][1])) / thisMass, 3)
                #Reset the hourly tip count and volume evolved
                hourlyTips = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                hourlyVolume = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                #Add one to the hour count
                dailyHours = dailyHours + 1
            
            #If a day has elapsed
            if dailyHours >= 24:
                #Variables to store the inoculum volume, net volume and number of channels
                inocVol = 0
                inocNetVol = 0
                inocCount = 0
                #Iterate through each channel
                for bucketId in range(0, 15):
                    #Get the mass of sample (or inoculum) for this channel
                    thisMass = sampleMass[tipChannel]
                    if inoculumOnly[bucketId]:
                        thisMass = inoculumMass[bucketId]
                    #If no mass, set to infinity (will set values to 0 when divided by not cause an error)
                    if thisMass == 0:
                        thisMass = math.inf
                    #Create the event data
                    #Channel, channel name, timestamp (of day), days, hours, minutes, in service (1/0), no.tips, vol this day, cumulative net vol (ml/g), cumulative vol 
                    dayEvent = [bucketId + 1, names[bucketId], lastHour + hourLength, daysElapsed, hoursElapsed, minutesElapsed, inUse[bucketId], dailyTips[bucketId], round(dailyVolume[bucketId], 3), round(dailyVolume[bucketId] / thisMass, 3), totalNetVol[bucketId], round(totalVolume[bucketId], 3)]
                    dayLog.append(dayEvent)
                    #If this is an inoculum only channel
                    if inoculumOnly[bucketId]:
                        #Add one to inoculum count
                        inocCount = inocCount + 1
                        #Add volume and net volumes to the inoculum values
                        inocVol = inocVol + hourlyVolume[bucketId]
                        inocNetVol = inocNetVol + (hourlyVolume[bucketId] / thisMass)
                #Add the averaged volume and net volume to the day part of the inoculum data array
                if inocCount > 0:
                    inoculumValues[1].append([(inocVol / inocCount), (inocNetVol / inocCount)])
                else:
                    inoculumValues[1].append([0, 0])
                #Iterate through each channel event that was just added
                for dayEventIndex in range(len(dayEvent) - 15, len(dayEvent)):
                    #Get the id for the channel
                    bucketIndex = dayLog[dayEventIndex][0] - 1
                    #Get the mass of the sample (or inoculum)
                    thisMass = sampleMass[bucketIndex]
                    if inoculumOnly[bucketIndex]:
                        thisMass = inoculumMass[bucketIndex]
                    #If no mass, set to infinity (will set values to 0 when divided by not cause an error)
                    if thisMass == 0:
                        thisMass = math.inf
                    #Subtract the average net volume of inoculum from the net volume evolved - adjusted for the mass of inoculum in the channel
                    #net volume per gram * sample mass - net volume inoculum per gram * inoculum mass = net volume evolved
                    #net volume evolved / sample mass = net volume evolved per gram
                    dayLog[dayEventIndex][9] = round((dayLog[dayEventIndex][9] * thisMass) - (inoculumMass[bucketIndex] * inoculumValues[1][-1][1]), 3)
                #Reset the daily tip count and volume evolved
                dailyTips = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                dailyVolume = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                dailyHours = 0
            
            #Add one to the hourly and daily tips counts for this channel
            hourlyTips[tipChannel] = hourlyTips[tipChannel] + 1
            dailyTips[tipChannel] = dailyTips[tipChannel] + 1

            #Calculate the volume of the tip (at STP)
            #Gas Constant * temp (K) / pressure (hPA) = volume
            tipVolume = gasConstants[tipChannel] * (float(event[4]) + 237.13) / float(event[5])
            #Add to the hourly and daily volume for this channel
            hourlyVolume[tipChannel] = hourlyVolume[tipChannel] + tipVolume
            dailyVolume[tipChannel] = dailyVolume[tipChannel] + tipVolume
            
            #Add volume to total
            totalVolume[tipChannel] = totalVolume[tipChannel] + tipVolume

            #Calculate the net volume (per gram)
            totalNetVol[tipChannel] = totalNetVol[tipChannel] + (tipVolume / mass)

            #Bucket ID, tube name, timestamp(s), day, hour, min, tumbler volume, temp, press, cumul tips (this bucket), tip vol, total vol, no. tips day, vol day, no. tips hour, vol hour, net vol/gm
            loggedEvent = [tipChannel + 1, names[tipChannel], int(event[2]), daysElapsed, hoursElapsed, minutesElapsed, tumblerVolume[tipChannel], round(float(event[4]),2), round(float(event[5]),1), cumulativeTips[tipChannel], round(tipVolume,3), round(totalVolume[tipChannel], 3), dailyTips[tipChannel], round(dailyVolume[tipChannel],3), hourlyTips[tipChannel], round(hourlyVolume[tipChannel],3), round(totalNetVol[tipChannel],3)]
            eventLog.append(loggedEvent)


            #if another hour has passed
            if time - lastHour > hourLength:

                #For each of the channels
                for hourId in range(0, len(currentHour)):

                    #Add the current hour value to the list of hours
                    hourList[hourId].append(currentHour[hourId])

                    #If this is one of the innculum only channels - add its value (of volume per gram) to the list
                    if inoculumOnly[hourId]:
                        inocMass = inoculumMass[hourId]
                        #If no mass, set to infinity (will set values to 0 when divided by not cause an error)
                        if inocMass == 0:
                            inocMass = math.inf
                        hourinoculum[-1].append(currentHour[hourId] / inocMass)

                    #Reset the current hour ready for the next one
                    currentHour[hourId] = 0

                    #Iterate through 1 to number of hours passed (in case multiple hours pass between tips)
                    for _ in range(1, int((time - lastHour) / hourLength)):
                        #Add a 0 to the hour list
                        hourList[hourId].append(0)
                        #If this is inoculum - nothing passed here too
                        if inoculumOnly[hourId]:
                            hourinoculum[-1].append(0)
                
                #Add a new list to the hourly inocculum totals (for the new hour)
                hourinoculum.append([])
                
                #Add the necessary amount to the number of hours passed
                for _ in range(0, int((time - lastHour) / hourLength)):
                    lastHour = lastHour + hourLength
            
            #Get the id of the channel
            idNum = int(event[3]) - 1
            #Calculate the volume - using gass constant, temperature and pressure
            volume = gasConstants[idNum] * (float(event[4]) + 237.13) / float(event[5])
            #Add this amount to the current hourly value for that channel
            currentHour[idNum] = currentHour[idNum] + volume
        
        #If there were tips that were not added
        if sum(currentHour) > 0:
            #Iterate through the tubes
            for hourId in range(0, len(currentHour)):
                #Add the data to the hour list
                hourList[hourId].append(currentHour[hourId])

                #If this is an inoculum only tube
                if inoculumOnly[hourId]:
                    #Add volume produced per gram to inoculum list
                    inocMass = inoculumMass[hourId]
                    if inocMass == 0:
                        inocMass = math.inf
                    hourinoculum[-1].append(currentHour[hourId] / inocMass)
        
        #If the last inoculum value set is not filled - remove it
        #Removed as it changes nothing and causes a crash if there is no inoculum only channel
        '''if len(hourinoculum[-1]) == 0:
            del hourinoculum[-1]'''

        #Iterate through the hours
        for hourId in range(0, len(hourinoculum)):
            #Calculate the average gass volume produced of inoculum (per gram)
            average = 0
            #If there is data present
            if len(hourinoculum[hourId]) > 0:
                average = sum(hourinoculum[hourId]) / len(hourinoculum[hourId])
            hourinoculumAvg.append(average)
        
        #Iterate through the tubes
        for tubeId in range(0, len(hourList)):
            #Iterate through the hours
            for hourId in range(0, len(hourList[tubeId])):
                #Calculate the total gass evolved that hour: volume - (average volume per g of inoculum * mass of inoculum)
                extraGassEvolved = hourList[tubeId][hourId] - (hourinoculumAvg[hourId] * inoculumMass[tubeId])
                #Default volume of 0 per gram
                extraGassEvolvedPerGram = 0
                #If this tube contains a sample
                if not inoculumOnly[tubeId] and sampleMass[tubeId] > 0:
                    #Divide by the mass in the tube to get volume per gram
                    tubeMass = sampleMass[tubeId]
                    #If no mass, set to infinity (will set values to 0 when divided by not cause an error)
                    if tubeMass == 0:
                        tubeMass = math.inf
                    extraGassEvolvedPerGram = extraGassEvolved / tubeMass
                #Add volumes to lists total volume and per gram
                if not inoculumOnly[tubeId]:
                    #If it is a sample tube
                    hourListWithoutinoculum[tubeId].append(extraGassEvolved)
                    hourListWithoutinoculumPerGram[tubeId].append(extraGassEvolvedPerGram)
                else:
                    #If this is an inoculum tube
                    hourListWithoutinoculum[tubeId].append(0)
                    hourListWithoutinoculumPerGram[tubeId].append(0)
        
        #Iterate through the tubes
        for tubeId in range(len(hourList)):
            #Each of the totals is 0
            hourCount = 0
            dayVal = 0
            dayValWithoutI = 0
            dayValWithoutIPerGram = 0
            dayValinoculumAvg = 0
            #Iterate through each hour
            for hourNumber in range(0, len(hourList[tubeId])):
                #Add the hour value to the running total for day values (volume, volume - inoculum, (volume - inoculum) / sample mass, inoculum average)
                dayVal = dayVal + hourList[tubeId][hourNumber]
                dayValWithoutI = dayValWithoutI + hourListWithoutinoculum[tubeId][hourNumber]
                dayValWithoutIPerGram = dayValWithoutIPerGram + hourListWithoutinoculumPerGram[tubeId][hourNumber]
                dayValinoculumAvg = dayValinoculumAvg + hourinoculumAvg[hourNumber]

                #Incrament hour
                hourCount = hourCount + 1
                #If a day has passed
                if hourCount >= 24:
                    #Reset counter
                    hourCount = 0
                    #Add values to lists
                    dayList[tubeId].append(dayVal)
                    dayListWithoutinoculum[tubeId].append(dayValWithoutI)
                    dayListWithoutinoculumPerGram[tubeId].append(dayValWithoutIPerGram)
                    dayinoculumAvg.append(dayValinoculumAvg)
                    #Reset values
                    dayVal = 0
                    dayValWithoutI = 0
                    dayValWithoutIPerGram = 0
                    dayValinoculumAvg = 0
            
            #If hours have passed but not a full day (at the end)
            if hourCount != 0:
                #Add the remaining values to form a final (partial) day
                dayList[tubeId].append(dayVal)
                dayListWithoutinoculum[tubeId].append(dayValWithoutI)
                dayListWithoutinoculumPerGram[tubeId].append(dayValWithoutIPerGram)
                dayinoculumAvg.append(dayValinoculumAvg)

        inoculumTotalNetVolume = 0
        numberInoculumTips = 0

        #Iterate through all events
        for e in eventLog:
            #Get channel index
            bucketId = e[0] - 1
            #If this is an inoculum channel
            if inoculumOnly[bucketId]:
                #Add to inoculum net volume total
                inocMass = inoculumMass[bucketId]
                #If no mass, set to infinity (will set values to 0 when divided by not cause an error)
                if inocMass == 0:
                    inocMass = math.inf
                inoculumTotalNetVolume = inoculumTotalNetVolume + (e[10] / inocMass)
                numberInoculumTips = numberInoculumTips + 1
        
        #Calculate average volume per gram of inoculum
        inoculumAverage = 0
        #Only calculate if there were tips
        if numberInoculumTips > 0:
            inoculumAverage = inoculumTotalNetVolume / numberInoculumTips

        #Iterate through event indexes
        for index in range(0, len(eventLog)):
            #Get the channel index
            bucketId = eventLog[index][0] - 1
            #If this is not inoculum
            if not inoculumOnly[bucketId]:
                #Subtract the inoculum volume (based on amount of inoculum present) from net volume
                bucketMass = sampleMass[bucketId]
                #If no mass, set to infinity (will set values to 0 when divided by not cause an error)
                if bucketMass == 0:
                    bucketMass = math.inf
                eventLog[index][16] = ( (eventLog[index][16] * sampleMass[bucketId]) - (inoculumAverage * inoculumMass[bucketId]) ) / bucketMass
        
    except:
        #Something is wrong with the way the event log file is formatted - report error and stop
        return [], "Event file not formatted correctly, ensure that all fields are present and of the correct data type.", None, None, None

    #Group setup information into list
    setup = [names, inUse, inoculumOnly, inoculumMass, sampleMass, tumblerVolume]

    #Group setup data and results into a list
    completeData = [setup, hourList, hourListWithoutinoculum, hourListWithoutinoculumPerGram, dayList, dayListWithoutinoculum, dayListWithoutinoculumPerGram, hourinoculum, hourinoculumAvg, dayinoculumAvg]

    for r in range(0, len(eventLog)):
        for c in range(0, len(eventLog[r])):
            eventLog[r][c] = str(eventLog[r][c])
    for r in range(0, len(hourLog)):
        for c in range(0, len(hourLog[r])):
            hourLog[r][c] = str(hourLog[r][c])
    for r in range(0, len(dayLog)):
        for c in range(0, len(dayLog[r])):
            dayLog[r][c] = str(dayLog[r][c])

    eventLog.insert(0, ["Channel Number", "Name", "Timestamp", "Days", "Hours", "Minutes", "Tumbler Volume (ml)", "Temperature (C)", "Pressure (hPA)", "Cumulative Total Tips", "Volume This Tip (STP)", "Total Volume (STP)", "Tips This Day", "Volume This Day (STP)", "Tips This Hour", "Volume This Hour (STP)", "Net Volume Per Gram (ml/g)"])
    hourLog.insert(0, ["Channel Number", "Name", "Timestamp", "Days", "Hours", "Minutes", "In Service", "Tips This Hour", "Volume This Hour at STP (ml)", "Net Volume This Hour (ml/g)", "Cumulative Net Vol (ml/g)", "Cumulative Volume at STP (ml)"])
    dayLog.insert(0, ["Channel Number", "Name", "Timestamp", "Days", "Hours", "Minutes", "In Service", "Tips This Day", "Volume This Day at STP (ml)", "Net Volume This Day (ml/g)", "Cumulative Net Vol (ml/g)", "Cumulative Volume at STP (ml)"])

    #Return the data and no error was found
    return completeData, None, eventLog, hourLog, dayLog