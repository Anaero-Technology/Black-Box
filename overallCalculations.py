import readSeparators
import math

def performGeneralCalculations(setupData, eventData, progress):
    '''Take in the setup information and list of events and convert to hourly volumes produced'''

    #Number of seconds in an hour
    hourLength = 60 * 60
    #Number of seconds in a day
    dayLength = hourLength * 24
    #Time of the last hour start
    lastHour = 0

    #List to contain volumes for the current hour
    currentHour = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    #2d list to contain the volumes produced for each hour
    hourList = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    #A list to contain the inoculum volumes for each hour
    hourInoculum = [[]]
    #The constant gas value for a given channel
    gasConstants = []

    eventLog = []
    cumulativeTips = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    hourlyTips = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    hourlyVolume = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    hourlyNetVolume = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    dailyTips = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    dailyVolume = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    dailyNetVolume = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    totalVolume = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    totalNetVol = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    dailyHours = 0
    startTime = 0

    hourLog = []
    dayLog = []
    gasLog = []

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
        return "Setup file not formatted correctly, ensure that all 15 rows are present as well as field names.", None, None, None, None, None

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
            #Calculate the gas constant for the tube P * V / T - so that the volume can be derrived from temperature and pressure easily upon tip
            stpConst = (273 * tumblerVolume[tubeId]) / 1013.25
            gasConstants.append(stpConst)

    except:
        #Formatting of setup file is incorrect - reort error and stop
        return "Setup file not formatted correctly, ensure that all fields are of the correct data types.", None, None, None, None, None

    #Attempt to process the event data
    try:
        startTime = 0
        #Previous hour and day values to check for days/hours passing
        lastDayValue = 0
        lastHourValue = 0
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
            if lastHourValue != hoursElapsed:
                #Update value for hours that have elapsed
                lastHourValue = hoursElapsed
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
                    hourEvent = [bucketId + 1, names[bucketId], lastHour + hourLength, daysElapsed, hoursElapsed, minutesElapsed, inUse[bucketId], hourlyTips[bucketId], round(hourlyVolume[bucketId], 3), round(hourlyNetVolume[bucketId], 3), round(totalNetVol[bucketId], 3), round(totalVolume[bucketId], 3)]
                    hourLog.append(hourEvent)
                #Iterate through each channel event that was just added
                for hourEventIndex in range(len(hourEvent) - 15, len(hourEvent)):
                    #Get the index for the channel
                    bucketIndex = hourLog[hourEventIndex][0] - 1
                    #Get the mass (or inoculum mass) for the channel
                    thisMass = sampleMass[bucketIndex]
                    if inoculumOnly[bucketIndex]:
                        thisMass = inoculumMass[bucketIndex]
                    #If no mass, set to 0
                    if thisMass == 0:
                        hourLog[hourEventIndex][10] = 0
                #Reset the hourly tip count and volume evolved
                hourlyTips = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                hourlyVolume = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                hourlyNetVolume = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                #Add one to the hour count
                dailyHours = dailyHours + 1
            
            #If a day has elapsed
            if lastDayValue != daysElapsed:
                #Update value for days that have passed
                lastDayValue = daysElapsed
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
                    #Channel, channel name, timestamp (of day), days, hours, minutes, in service (1/0), no.tips, vol this day (STP), cumulative net vol (ml/g), cumulative vol (STP)
                    dayEvent = [bucketId + 1, names[bucketId], lastHour + hourLength, daysElapsed, hoursElapsed, minutesElapsed, inUse[bucketId], dailyTips[bucketId], round(dailyVolume[bucketId], 3), round(dailyNetVolume[bucketId], 3), round(totalNetVol[bucketId], 3), round(totalVolume[bucketId], 3)]
                    dayLog.append(dayEvent)
                #Iterate through each channel event that was just added
                for dayEventIndex in range(len(dayEvent) - 15, len(dayEvent)):
                    #Get the id for the channel
                    bucketIndex = dayLog[dayEventIndex][0] - 1
                    #Get the mass of the sample (or inoculum)
                    thisMass = sampleMass[bucketIndex]
                    if inoculumOnly[bucketIndex]:
                        thisMass = inoculumMass[bucketIndex]
                    #If no mass set net value to 0
                    if thisMass == 0:
                        dayLog[dayEventIndex][10] = 0
                #Reset the daily tip count and volume evolved
                dailyTips = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                dailyVolume = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                dailyNetVolume = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                dailyHours = 0
            
            #Add one to the hourly and daily tips counts for this channel
            hourlyTips[tipChannel] = hourlyTips[tipChannel] + 1
            dailyTips[tipChannel] = dailyTips[tipChannel] + 1

            #Calculate the volume of the tip (at STP)
            #Gas Constant * temp (K) / pressure (hPA) = volume
            tipVolume = gasConstants[tipChannel] * (float(event[5]) / (float(event[4]) + 273)) 
            #Add to the hourly and daily volume for this channel
            hourlyVolume[tipChannel] = hourlyVolume[tipChannel] + tipVolume
            dailyVolume[tipChannel] = dailyVolume[tipChannel] + tipVolume
            
            #Add volume to total
            totalVolume[tipChannel] = totalVolume[tipChannel] + tipVolume

            #Vairable to store the total net volume of inoculum
            inocTotalNetVolume = 0.0
            numberChannels = 0
            #Iterate through the 15 channels
            for channelNumber in range(0, 15):
                #If this is an inoculum only channel and it is in use
                if inoculumOnly[channelNumber] and inUse[channelNumber]:
                    #Add the net volume (total volume / mass of inoculum) to the total
                    inocTotalNetVolume = inocTotalNetVolume + (totalVolume[channelNumber] / inoculumMass[channelNumber])
                    #Add one to channel count
                    numberChannels = numberChannels + 1
            
            inoculumAveragePerGram = 0.0

            #If there are inoculum channels
            if numberChannels > 0:
                #Find the average by dividing the total by the number of channels
                inoculumAveragePerGram = inocTotalNetVolume / float(numberChannels)
            
            #Net gas evolved per gram in this channel up to this tip
            totalNetVolumeAtThisTip = 0
            #Net gas evolved per gram by this tip
            netVolumeFromThisTip = 0

            #If this is not an inoculum only channel and there is valid mass and inoculum mass
            if not inoculumOnly[tipChannel] and mass > 0 and mass != math.inf and inoculumMass[tipChannel] > 0 and inUse[tipChannel]:
                #Subtract average inoculum times mass of inoculum from the total gas evolved and then divide by mass of sample to get the total net volume
                totalNetVolumeAtThisTip = (totalVolume[tipChannel]  - (inoculumMass[tipChannel] * inoculumAveragePerGram)) / mass
                #The same but using only this tip volume
                netVolumeFromThisTip = (tipVolume - (inoculumMass[tipChannel] * inoculumAveragePerGram)) / mass
            else:
                #If this is an inoculum only and there is a valid inoculum mass
                if inoculumOnly[tipChannel] and inoculumMass[tipChannel] > 0 and inUse[tipChannel]:
                    #Calculate net values by dividing volumes by inoculum mass in this channel
                    totalNetVolumeAtThisTip = totalVolume[tipChannel] / inoculumMass[tipChannel]
                    netVolumeFromThisTip = tipVolume / inoculumMass[tipChannel]
            
            #Update the total net volume
            totalNetVol[tipChannel] = totalNetVolumeAtThisTip
            #Update the hourly and daily totals
            hourlyNetVolume[tipChannel] = hourlyNetVolume[tipChannel] + netVolumeFromThisTip
            dailyNetVolume[tipChannel] = dailyNetVolume[tipChannel] + netVolumeFromThisTip

            #Bucket ID, tube name, timestamp(s), day, hour, min, tumbler volume, temp, press, cumul tips (this bucket), tip vol, total vol, no. tips day, vol day, no. tips hour, vol hour, net vol/gm
            loggedEvent = [tipChannel + 1, names[tipChannel], int(event[2]), daysElapsed, hoursElapsed, minutesElapsed, tumblerVolume[tipChannel], round(float(event[4]),2), round(float(event[5]),2), cumulativeTips[tipChannel], round(tipVolume,3), round(totalVolume[tipChannel], 3), dailyTips[tipChannel], round(dailyVolume[tipChannel],3), hourlyTips[tipChannel], round(hourlyVolume[tipChannel],3), round(totalNetVolumeAtThisTip, 3)]
            eventLog.append(loggedEvent)

            #Add the gas percentage data
            #Entry: channelNumber, name, timestamp, time, co2 percentage, ch4 percentage 
            gasLog.append([tipChannel + 1, names[tipChannel] , int(event[2]), daysElapsed, hoursElapsed, minutesElapsed, float(event[6]), float(event[7])])


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
                        hourInoculum[-1].append(currentHour[hourId] / inocMass)

                    #Reset the current hour ready for the next one
                    currentHour[hourId] = 0

                    #Iterate through 1 to number of hours passed (in case multiple hours pass between tips)
                    for _ in range(1, int((time - lastHour) / hourLength)):
                        #Add a 0 to the hour list
                        hourList[hourId].append(0)
                        #If this is inoculum - nothing passed here too
                        if inoculumOnly[hourId]:
                            hourInoculum[-1].append(0)
                
                #Add a new list to the hourly inocculum totals (for the new hour)
                hourInoculum.append([])
                
                #Add the necessary amount to the number of hours passed
                for _ in range(0, int((time - lastHour) / hourLength)):
                    lastHour = lastHour + hourLength
            
            #Get the id of the channel
            idNum = int(event[3]) - 1
            #Calculate the volume - using gas constant, temperature and pressure
            volume = gasConstants[idNum] * (float(event[4]) + 237.13) / float(event[5])
            #Add this amount to the current hourly value for that channel
            currentHour[idNum] = currentHour[idNum] + volume

            progress[0] = progress[0] + 1
        
        if sum(hourlyTips) > 0:
            #Need to add extras to hour log
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
                hourEvent = [bucketId + 1, names[bucketId], lastHour + hourLength, daysElapsed, hoursElapsed + 1, minutesElapsed, inUse[bucketId], hourlyTips[bucketId], round(hourlyVolume[bucketId], 3), round(hourlyNetVolume[bucketId], 3), round(totalNetVol[bucketId], 3), round(totalVolume[bucketId], 3)]
                hourLog.append(hourEvent)
            #Iterate through each channel event that was just added
            for hourEventIndex in range(len(hourEvent) - 15, len(hourEvent)):
                #Get the index for the channel
                bucketIndex = hourLog[hourEventIndex][0] - 1
                #Get the mass (or inoculum mass) for the channel
                thisMass = sampleMass[bucketIndex]
                if inoculumOnly[bucketIndex]:
                    thisMass = inoculumMass[bucketIndex]
                #If no mass, set to 0
                if thisMass == 0:
                    hourLog[hourEventIndex][10] = 0
        if sum(dailyTips) > 0:
            #Need to add extras to day log
            for bucketId in range(0, 15):
                #Get the mass of sample (or inoculum) for this channel
                thisMass = sampleMass[tipChannel]
                if inoculumOnly[bucketId]:
                    thisMass = inoculumMass[bucketId]
                #If no mass, set to infinity (will set values to 0 when divided by not cause an error)
                if thisMass == 0:
                    thisMass = math.inf
                #Create the event data
                #Channel, channel name, timestamp (of day), days, hours, minutes, in service (1/0), no.tips, vol this day (STP), cumulative net vol (ml/g), cumulative vol (STP)
                dayEvent = [bucketId + 1, names[bucketId], (daysElapsed + 1) * dayLength, daysElapsed + 1, 0, 0, inUse[bucketId], dailyTips[bucketId], round(dailyVolume[bucketId], 3), round(dailyNetVolume[bucketId], 3), round(totalNetVol[bucketId], 3), round(totalVolume[bucketId], 3)]
                dayLog.append(dayEvent)
            #Iterate through each channel event that was just added
            for dayEventIndex in range(len(dayEvent) - 15, len(dayEvent)):
                #Get the id for the channel
                bucketIndex = dayLog[dayEventIndex][0] - 1
                #Get the mass of the sample (or inoculum)
                thisMass = sampleMass[bucketIndex]
                if inoculumOnly[bucketIndex]:
                    thisMass = inoculumMass[bucketIndex]
                #If no mass set net value to 0
                if thisMass == 0:
                    dayLog[dayEventIndex][10] = 0
    
    except:
        #Something is wrong with the way the event log file is formatted - report error and stop
        return "Event file not formatted correctly, ensure that all fields are present and of the correct data type.", None, None, None, None, None

    #Group setup information into list
    setup = [names, inUse, inoculumOnly, inoculumMass, sampleMass, tumblerVolume]

    #Convert all values to strings (so that they can be output to a file neatly)
    for r in range(0, len(eventLog)):
        for c in range(0, len(eventLog[r])):
            eventLog[r][c] = str(eventLog[r][c])
    for r in range(0, len(hourLog)):
        for c in range(0, len(hourLog[r])):
            hourLog[r][c] = str(hourLog[r][c])
    for r in range(0, len(dayLog)):
        for c in range(0, len(dayLog[r])):
            dayLog[r][c] = str(dayLog[r][c])
    for r in range(0, len(gasLog)):
        for c in range(0, len(gasLog[r])):
            gasLog[r][c] = str(gasLog[r][c])

    eventLog.insert(0, ["Channel Number", "Name", "Timestamp", "Days", "Hours", "Minutes", "Tumbler Volume (ml)", "Temperature (C)", "Pressure (hPA)", "Cumulative Total Tips", "Volume This Tip (STP)", "Total Volume (STP)", "Tips This Day", "Volume This Day (STP)", "Tips This Hour", "Volume This Hour (STP)", "Net Volume Per Gram (ml/g)"])
    hourLog.insert(0, ["Channel Number", "Name", "Timestamp", "Days", "Hours", "Minutes", "In Service", "Tips This Hour", "Volume This Hour at STP (ml)", "Net Volume This Hour (ml/g)", "Cumulative Net Vol (ml/g)", "Cumulative Volume at STP (ml)"])
    dayLog.insert(0, ["Channel Number", "Name", "Timestamp", "Days", "Hours", "Minutes", "In Service", "Tips This Day", "Volume This Day at STP (ml)", "Net Volume This Day (ml/g)", "Cumulative Net Vol (ml/g)", "Cumulative Volume at STP (ml)"])
    gasLog.insert(0, ["Channel Number", "Name", "Timestamp", "Days", "Hours", "Minutes", "CO2 Percent", "CH4 Percent"])

    #Return the data and no error was found
    return None, eventLog, hourLog, dayLog, gasLog, setup