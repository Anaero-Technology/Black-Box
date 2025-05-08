import readSeparators
import dataCombination
import sys
import datetime
#import traceback

def convertSeconds(seconds) -> tuple:
    '''Converts timestamp in seconds to number of days, hours minutes and seconds'''
    #Calculate number of seconds in a minute, hour and day
    secondsInMinute = 60
    secondsInHour = secondsInMinute * 60
    secondsInDay = secondsInHour * 24
    #Take the days off first
    d = seconds // secondsInDay
    seconds = seconds - (d * secondsInDay)
    #Take the hours off
    h = seconds // secondsInHour
    seconds = seconds - (h * secondsInHour)
    #Take the minutes off
    m = seconds // secondsInMinute
    seconds = seconds - (m * secondsInMinute)
    return d, h, m, seconds

def convertDate(dateString, separator) -> int:
    '''Converts timestamp in year month day hour minute second to seconds since the epoch'''
    parts = dateString.split(separator)
    try:
        date = datetime.datetime(int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5]))
        return date.timestamp()
    except:
        return -1

def performGeneralCalculations(setupData : list, eventData : list, gasData : list, progress):
    '''Convert from setup information and events to a fully processed event, day and hour logs with net volumes'''
    column, decimal = readSeparators.read()
    
    #Convert alternative decimal value to "."
    for row in range(0, len(setupData)):
        for col in range(0, len(setupData[row])):
            setupData[row][col] = setupData[row][col].replace(decimal, ".")
    
    for row in range(0, len(eventData)):
        for col in range(0, len(eventData[row])):
            eventData[row][col] = eventData[row][col].replace(decimal, ".")

    #If there are less than 15 channnels in the setup
    if len(setupData) < 16:
        #Report error and stop
        return "Setup file not formatted correctly, ensure that all 15 rows are present as well as field names.", None, None, None, None

    #Setup information about each channel
    setup = {"names" : [], "inUse" : [], "inoculumOnly" : [], "inoculumMass" : [], "sampleMass" : [], "tumblerVolume" : [], "inoculumCount" : 0, "gasConstants" : [], "chimeraChannel" : [], "wetWeight" : [], "internalVolume1" : [], "internalVolume2" : []}
    #Attempt to read setup file
    try:
        #Iterate through the lines (not the first as it is the column headers)
        for row in range(1, len(setupData)):
            #Store each piece of information from the row in the correct list
            setup["names"].append(setupData[row][0])
            setup["inUse"].append(int(setupData[row][1]) == 1)
            #Count the number of inoculum channels
            if int(setupData[row][2]) == 1:
                setup["inoculumCount"] = setup["inoculumCount"] + 1
            setup["inoculumOnly"].append(int(setupData[row][2]) == 1)
            setup["inoculumMass"].append(float(setupData[row][3]))
            setup["sampleMass"].append(float(setupData[row][4]))
            setup["tumblerVolume"].append(float(setupData[row][5]))
            if gasData != None and len(gasData) > 0:
                setup["chimeraChannel"].append(int(setupData[row][6]) - 1)
                setup["wetWeight"].append(float(setupData[row][7]))
                setup["internalVolume1"].append(float(setupData[row][9]))
                setup["internalVolume2"].append(float(setupData[row][10]))
        
        #Go through all the tubes
        for tubeId in range(0, len(setup["tumblerVolume"])):
            #Calculate the gas constant for the tube P * V / T - so that the volume can be derrived from temperature and pressure easily upon tip
            stpConst = (273 * setup["tumblerVolume"][tubeId]) / 1013.25
            setup["gasConstants"].append(stpConst)

    except Exception:
        #traceback.print_exc()
        #Formatting of setup file is incorrect - reort error and stop
        return "Setup file not formatted correctly, ensure that all fields are of the correct data types.", None, None, None, None
    
    methaneForChannels = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
    carbonForChannels = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]

    usingGas = False
    
    if gasData != None and len(gasData) > 0:
        usingGas = True
        try:
            association = [-1] * 15
            for i in range(0, 15):
                association = setup["chimeraChannel"]
            gasChannels = []
            for i in range(0, 15):
                gasChannels.append({"times":[], "ch4":[], "co2":[]})
            for dataRow in gasData:
                time = convertDate(dataRow[0], "/")
                gasChannel = int(dataRow[1])
                methane = float(dataRow[4])
                carbonDioxide = float(dataRow[5])
                if gasChannel > 0 and gasChannel < 16:
                    gasChannels[gasChannel - 1]["times"].append(time)
                    gasChannels[gasChannel - 1]["ch4"].append(methane)
                    gasChannels[gasChannel - 1]["co2"].append(carbonDioxide)
            
            for index in range(0, 15):
                if association[index] > 0 and association[index] < 16:
                    if len(gasChannels[association[index] - 1]["times"]) > 0 and len(gasChannels[association[index] - 1]["ch4"]) > 0:
                        methaneForChannels[index] = dataCombination.ContinuousRange(gasChannels[association[index] - 1]["times"], gasChannels[association[index] - 1]["ch4"])
                    else:
                        methaneForChannels[index] = dataCombination.ContinuousRange([0], [0])
                    if len(gasChannels[association[index] - 1]["times"]) > 0 and len(gasChannels[association[index] - 1]["co2"]) > 0:
                        carbonForChannels[index] = dataCombination.ContinuousRange(gasChannels[association[index] - 1]["times"], gasChannels[association[index] - 1]["co2"])
                    else:
                        carbonForChannels[index] = dataCombination.ContinuousRange([0], [-1])
        except Exception:
            #traceback.print_exc()
            return "Gas file not formatted correctly, ensure that all fields are of the correct data types.", None, None, None, None

    #Dicionary to store overall running information for all channels
    overall = {"tips" : [0] * 15, "volumeSTP" : [0.0] * 15, "volumeNet" : [0.0] * 15, "inoculumVolume" : 0.0, "inoculumMass" : 0.0}
    #Arrays to hold dictionaries of hour and day information for each channel
    hours = [] #{"tips" : [0] * 15, "volumeSTP" : [0.0] * 15, "volumeNet" : [0.0] * 15, "totalCH4" : [0.0] * 15, "totalCO2" : [0.0] * 15}
    days = [] #{"tips" : [0] * 15, "volumeSTP" : [0.0] * 15, "volumeNet" : [0.0] * 15}
    #Array to hold final event log information (as it can be gathered immediately)
    eventArray = []

    lastHourNetVolume = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    lastDayNetVolume = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    eventCount = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    eventGasInfo = []

    progress[2] = "Processing: {0}%"

    try:
        #Iterate through every event in the log
        for event in eventData:
            #Event - event id, time(YYYY:MM:DD:HH:MM:SS), time (s), bucket number, temperature (deg C), pressure (hPa)
            #Get the channel number
            channelId = int(event[3]) - 1
            #If this channel should be logging
            if setup["inUse"][channelId]:
                #Get the time, temperature and pressure
                eventTime = int(float(event[2]))
                dateTime = convertDate(event[1], ".")
                temperatureC = float(event[4])
                temperatureK = temperatureC + 273
                pressure = float(event[5])

                #Find the time as parts
                day, hour, mins, sec = convertSeconds(eventTime)
                #Total hour count
                totalHour = hour + (day * 24)
                #Extend the day and hour arrays to store new values
                while len(days) <= day:
                    if len(days) > 0:
                        for channel in range(0, 15):
                            lastDayNetVolume[channel] = lastDayNetVolume[channel] + days[-1]["volumeNet"][channel]
                    days.append({"tips" : [0] * 15, "volumeSTP" : [0.0] * 15, "volumeNet" : [0.0] * 15})
                while len(hours) <= totalHour:
                    if len(hours) > 0:
                        for channel in range(0, 15):
                            lastHourNetVolume[channel] = lastHourNetVolume[channel] + hours[-1]["volumeNet"][channel]
                    hours.append({"tips" : [0] * 15, "volumeSTP" : [0.0] * 15, "volumeNet" : [0.0] * 15, "totalCH4" : [0.0] * 15, "totalCO2" : [0.0] * 15})

                #Calculate the volume for the tip
                eventVolume = setup["gasConstants"][channelId] * (pressure / temperatureK)

                #Add tip to overall, day and hour as well as the volume for each
                overall["tips"][channelId] = overall["tips"][channelId] + 1
                overall["volumeSTP"][channelId] = overall["volumeSTP"][channelId] + eventVolume
                days[-1]["tips"][channelId] = days[-1]["tips"][channelId] + 1
                days[-1]["volumeSTP"][channelId] = days[-1]["volumeSTP"][channelId] + eventVolume
                hours[-1]["tips"][channelId] = hours[-1]["tips"][channelId] + 1
                hours[-1]["volumeSTP"][channelId] = hours[-1]["volumeSTP"][channelId] + eventVolume

                #thisNetVolume = eventVolume
                totalNetVolume = overall["volumeSTP"][channelId]
                #If this is an inoculum only channel
                if setup["inoculumOnly"][channelId]:
                    #If there is inoculum mass
                    if setup["inoculumMass"][channelId] != 0:
                        #Net volume is the total volume divided by the inoculum mass
                        #thisNetVolume = eventVolume / setup["inoculumMass"][channelId]
                        totalNetVolume = overall["volumeSTP"][channelId] / setup["inoculumMass"][channelId]
                        #Add the mass and volume to overall running total
                        overall["inoculumVolume"] = overall["inoculumVolume"] + eventVolume
                        overall["inoculumMass"] = overall["inoculumMass"] + setup["inoculumMass"][channelId]
                else:
                    #If there is sample mass
                    if setup["sampleMass"][channelId] != 0:
                        #Check that there have been inoculum tips - this is to prevent divide by zero errors before inoculum tips or when expreiment has none
                        #if overall["inoculumMass"] != 0 and setup["inoculumCount"] != 0:
                        if overall["inoculumMass"] != 0:
                            #Net volume is: (event volume - (inoculum volume / inoculum mass) / inoculum channel count * inoculum mass for this channel) / sample mass
                            #thisNetVolume = (eventVolume - (((overall["inoculumVolume"] / overall["inoculumMass"]) / setup["inoculumCount"]) * setup["inoculumMass"][channelId])) / setup["sampleMass"][channelId]
                            #thisNetVolume = (eventVolume - ((overall["inoculumVolume"] / overall["inoculumMass"]) * setup["inoculumMass"][channelId])) / setup["sampleMass"][channelId]
                            inoculumAdjust = 0
                            inoculumCount = 0
                            for channel in range(0, 15):
                                if setup["inoculumOnly"][channel] and setup["inoculumMass"][channel] != 0:
                                    inoculumAdjust = inoculumAdjust + (overall["volumeSTP"][channel] / setup["inoculumMass"][channel])
                                    inoculumCount = inoculumCount + 1
                            inoculumAdjust = inoculumAdjust / inoculumCount
                            totalNetVolume = (overall["volumeSTP"][channelId] - (inoculumAdjust * setup["inoculumMass"][channelId])) / setup["sampleMass"][channelId]
                        else:
                            totalNetVolume = overall["volumeSTP"][channelId] / setup["sampleMass"][channelId]
                
                #Add the net volume for this tip to the hourly and daily information for this channel
                days[-1]["volumeNet"][channelId] = totalNetVolume - lastDayNetVolume[channelId]
                hours[-1]["volumeNet"][channelId] = totalNetVolume - lastHourNetVolume[channelId]
                overall["volumeNet"][channelId] = totalNetVolume

                ch4 = "-"
                co2 = "-"

                if methaneForChannels[channelId] != None:
                    ch4 = methaneForChannels[channelId].getValue(dateTime)
                if carbonForChannels[channelId] != None:
                    co2 = carbonForChannels[channelId].getValue(dateTime)

                if usingGas:
                    if type(ch4) == float:
                        hours[-1]["totalCH4"][channelId] = hours[-1]["totalCH4"][channelId] + ch4
                    if type(co2) == float:
                        hours[-1]["totalCO2"][channelId] = hours[-1]["totalCO2"][channelId] + co2

                #Channel Number, Name, Timestamp, Days, Hours, Minutes, Tumbler Volume (ml), Temperature (C), Pressure (hPA), Cumulative Total Tips, Volume This Tip (STP), Total Volume (STP), Tips This Day, Volume This Day (STP), Tips This Hour, Volume This Hour (STP), Net Volume Per Gram (ml/g)
                eventArray.append([channelId + 1, setup["names"][channelId], eventTime, day, hour, mins, setup["tumblerVolume"][channelId], temperatureC, pressure, overall["tips"][channelId], eventVolume, overall["volumeSTP"][channelId], days[-1]["tips"][channelId], days[-1]["volumeSTP"][channelId], hours[-1]["tips"][channelId], hours[-1]["volumeSTP"][channelId], overall["volumeNet"][channelId]])
                eventCount[channelId] = eventCount[channelId] + 1
                eventGasInfo.append([channelId, hour, ch4, co2])
            #Move progress bar forward
            progress[0] = progress[0] + 1

    except Exception:
        #traceback.print_exc()
        #Something is wrong with the way the event log file is formatted - report error and stop
        return "Event file not formatted correctly, ensure that all fields are present and of the correct data type.", None, None, None, None

    if usingGas:
        dilutions = []
        methaneConcentrations = [[[0, 0]] * 15]
        carbonConcentrations = [[[0, 0]] * 15]
        for hour in hours:
            volumesProduced = hour["volumeSTP"]
            dilutions.append([])
            methaneConcentrations.append([[0, 0]] * 15)
            carbonConcentrations.append([[0, 0]] * 15)
            for channel in range(0, 15):
                averageSensorReadings = [{"value" : 0.0, "type" : "ch4"}, {"value" : 0.0, "type" : "co2"}]
                if hour["tips"][channel] > 0:
                    averageSensorReadings[0]["value"] = (hour["totalCH4"][channel] / hour["tips"][channel]) / 100.0
                    averageSensorReadings[1]["value"] = (hour["totalCO2"][channel] / hour["tips"][channel]) / 100.0
                results = []
                for sensorReading in averageSensorReadings:
                    previousStage1 = 0.0
                    previousStage2 = 0.0
                    if sensorReading["type"] == "ch4":
                        previousStage1 = methaneConcentrations[-2][channel][0]
                        previousStage2 = methaneConcentrations[-2][channel][1]
                    elif sensorReading["type"] == "co2":
                        previousStage1 = carbonConcentrations[-2][channel][0]
                        previousStage2 = carbonConcentrations[-2][channel][1]
                    volumeProduced = volumesProduced[channel]
                    if volumeProduced > 0:
                        internalVolume1 = setup["internalVolume1"][channel]
                        internalVolume2 = setup["internalVolume2"][channel]
                        dilution = 1.0
                        constant1 = internalVolume1 / volumeProduced
                        constant2 = ((internalVolume2 / volumeProduced) + 1) * ((internalVolume1 / volumeProduced) + 1)
                        constantBetween = ((internalVolume1 + volumeProduced) * internalVolume2) / (volumeProduced ** 2)
                        realGas = (constant2 * sensorReading["value"]) - (constantBetween * previousStage2) - (constant1 * previousStage1)
                        if sensorReading["value"] > 0:
                            dilution = realGas / sensorReading["value"]
                        firstStageConcentration = ((internalVolume1 * previousStage1) + (volumeProduced * realGas)) / (internalVolume1 + volumeProduced)
                        secondStageConcentration = ((internalVolume2 * previousStage2) + (volumeProduced * previousStage1)) / (internalVolume2 + volumeProduced)
                        if sensorReading["type"] == "ch4":
                            methaneConcentrations[-1][channel][0] = firstStageConcentration
                            methaneConcentrations[-1][channel][1] = secondStageConcentration
                        if sensorReading["type"] == "co2":
                            carbonConcentrations[-1][channel][0] = firstStageConcentration
                            carbonConcentrations[-1][channel][1] = secondStageConcentration
                        results.append(dilution)
                    else:
                        results.append(1.0)
                        if sensorReading["type"] == "ch4":
                            methaneConcentrations[-1][channel][0] = previousStage1
                            methaneConcentrations[-1][channel][1] = previousStage2
                        if sensorReading["type"] == "co2":
                            carbonConcentrations[-1][channel][0] = previousStage1
                            carbonConcentrations[-1][channel][1] = previousStage2
                    
                dilutions[-1].append(results)
        
        for eventId in range(0, min(len(eventGasInfo), len(eventArray))):
            channel = eventGasInfo[eventId][0]
            hour = eventGasInfo[eventId][1]
            ch4 = eventGasInfo[eventId][2]
            co2 = eventGasInfo[eventId][3]
            eventArray[eventId].append(str(ch4))
            eventArray[eventId].append(str(co2))
            if type(ch4) == float and type(co2) == float and channel > -1 and channel < 15 and hour < len(dilutions):
                ch4 = ch4 * dilutions[hour][channel][0]
                co2 = co2 * dilutions[hour][channel][1]
            eventArray[eventId].append(str(ch4))
            eventArray[eventId].append(str(co2))
    
    progress[2] = "Creating Files: {0}%"
    progress[1] = len(hours) + len(days)
    progress[0] = 0
    #Array to store hour data output
    hourArray = []
    #Stored totals for each channel
    totalVolume = [0.0] * 15
    totalNetVolume = [0.0] * 15
    h = 0
    d = 0
    #Iterate through hours
    for hour in hours:
        #Increment hour count
        h = h + 1
        #Adjust for day rollover
        if h > 23:
            d = d + 1
            h = h - 24
        #Calculate the timestamp of the hour
        timestamp = ((60 * 60 * 24) * d) + ((60 * 60) * h)
        #Iterate channels
        for channelId in range(0, 15):
            #Add to the total volumes
            totalVolume[channelId] = totalVolume[channelId] + hour["volumeSTP"][channelId]
            totalNetVolume[channelId] = totalNetVolume[channelId] + hour["volumeNet"][channelId]
            #Channel Number", "Name", "Timestamp", "Days", "Hours", "Minutes", "In Service", "Tips This Hour", "Volume This Hour at STP (ml)", "Net Volume This Hour (ml/g)", "Cumulative Net Vol (ml/g)", "Cumulative Volume at STP (ml)
            hourArray.append([channelId + 1, setup["names"][channelId], timestamp, d, h, 0, setup["inUse"][channelId], hour["tips"][channelId], round(hour["volumeSTP"][channelId], 3), round(hour["volumeNet"][channelId], 3), round(totalNetVolume[channelId], 3), round(totalVolume[channelId], 3)])
        progress[0] = progress[0] + 1
    #Array to store day data output
    dayArray = []
    #Stored totals for each channel
    totalVolume = [0.0] * 15
    totalNetVolume = [0.0] * 15
    d = 0
    #Iterate through days
    for day in days:
        #Increment day count
        d = d + 1
        #Calculate the timestamp of the day
        timestamp = (60 * 60 * 24) * d
        #Iterate channels
        for channelId in range(0, 15):
            #Add tot the total volumes
            totalVolume[channelId] = totalVolume[channelId] + day["volumeSTP"][channelId]
            totalNetVolume[channelId] = totalNetVolume[channelId] + day["volumeNet"][channelId]
            #Channel Number", "Name", "Timestamp", "Days", "Hours", "Minutes", "In Service", "Tips This Day", "Volume This Day at STP (ml)", "Net Volume This Day (ml/g)", "Cumulative Net Vol (ml/g)", "Cumulative Volume at STP (ml)
            dayArray.append([channelId + 1, setup["names"][channelId], timestamp, d, 0, 0, setup["inUse"][channelId], day["tips"][channelId], round(day["volumeSTP"][channelId], 3), round(day["volumeNet"][channelId], 3), round(totalNetVolume[channelId], 3), round(totalVolume[channelId], 3)])
        progress[0] = progress[0] + 1
    #Add text headers
    eventArray.insert(0, ["Channel Number", "Name", "Timestamp", "Days", "Hours", "Minutes", "Tumbler Volume (ml)", "Temperature (C)", "Pressure (hPA)", "Cumulative Total Tips", "Volume This Tip (STP)", "Total Volume (STP)", "Tips This Day", "Volume This Day (STP)", "Tips This Hour", "Volume This Hour (STP)", "Cumulative Net Volume Per Gram (ml/g) or (ml/gVS)","Raw CH4 %", "Raw CO2 %", "CH4 %", "CO2 %"])
    hourArray.insert(0, ["Channel Number", "Name", "Timestamp", "Days", "Hours", "Minutes", "In Service", "Tips This Hour", "Volume This Hour at STP (ml)", "Net Volume This Hour (ml/g)", "Cumulative Net Vol (ml/g)", "Cumulative Volume at STP (ml)"])
    dayArray.insert(0, ["Channel Number", "Name", "Timestamp", "Days", "Hours", "Minutes", "In Service", "Tips This Day", "Volume This Day at STP (ml)", "Net Volume This Day (ml/g)", "Cumulative Net Vol (ml/g)", "Cumulative Volume at STP (ml)"])
    setupArray = [setup["names"], setup["inUse"], setup["inoculumOnly"], setup["inoculumMass"], setup["sampleMass"], setup["tumblerVolume"]]
    #Return correct information
    return None, eventArray, hourArray, dayArray, setupArray