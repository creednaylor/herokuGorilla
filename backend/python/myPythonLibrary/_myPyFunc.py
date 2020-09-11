from collections import OrderedDict
import copy
from cryptography.fernet import Fernet
from datetime import datetime, date
import json
from pathlib import Path
from pprint import pprint as p
# import re
import sqlite3
import time
import pyautogui as g





def printElapsedTime(priorTime, message):

    
    currentTime = time.time()

    if not priorTime:
        priorTime = currentTime

    elapsedMinutes = (currentTime - priorTime) // 60
    elapsedSeconds = round((currentTime - priorTime) % 60, 1)

    p("Split time: " + str(elapsedMinutes) + ' minutes and ' + str(elapsedSeconds) + " seconds. (" + str(round((currentTime - priorTime), 1)) + ' seconds). ' + message + ".")

    return currentTime



def convertNothingToEmptyStr(s):
    if s:
        return str(s)
    else:
        return ""



def convertSingleSpaceToZero(s):
    if s == " ":
        return 0
    else:
        return s


def convertToZero(s):
    if s in [" ", None]:
        return 0
    else:
        return s


# def excelNumToPyNum(s):
#
#     quoted = re.compile("(?<=')[^']+(?=')")
#     for value in quoted.findall(s):
#         i.append(value)
#         print(i)








def convertEmptyStrToZero(s):
    if s == "":
        return 0
    else:
        return s



def convertOutOfRangeToZero(array, index):
    if len(array) <= index:
        return 0
    else:
        return array[index]



def removeCommaFromStr(s):

    if isinstance(s, str):
        return s.replace(",", "")
    return s


def repetitiveKeyPress(numberOfTabs, keyToPress):

    import pyautogui

    for i in range(0, numberOfTabs):
        pyautogui.press(keyToPress)




def functionOnClick(x, y, button, pressed):
    if not pressed:
        print("Mouse {2} was {0} at {1}.".format("pressed" if pressed else "released", (x, y), button))
        return False




def printPythonInfo(var, length):

    p("1. Printing string of the variable: " + str(var)[0:length])
    p(var)

    p("2. Printing help() of the variable: " + str(var)[0:length])
    p(help(var))

    p("3. Printing dir() of the variable: " + str(var)[0:length])
    p(dir(var))



    p("4. Printing vars() of the variable: " + str(var)[0:length])
    try:
        p(vars(var))
    except:
        p("An exception occurred printing vars() of the variable")




    p("5. Printing and loopting through the variable: " + str(var)[0:length])
    try:
        for attr in dir(var):
            p("obj.%s = %r" % (attr, getattr(var, attr)))
    except:
        p("An exception occurred printing and loopting through the variable")



    p("6. Printing the .__dict__ of the variable: " + str(var)[0:length])
    try:
        p(var.__dict__)
    except:
        p("An exception occurred printing the .__dict__ of the variable")



    p("7. Printing the repr() of the variable: " + str(var)[0:length])
    try:
        p(repr(var))
    except:
        p("An exception occurred printing the repr() of the variable")








def convertKey(key):
    if key == "lmenu":
        return "alt"
    elif key == "oem_1":
        return ":"
    elif key == "oem_5":
        return "\\"
    else:
        return key





def getColumnLetterFromNumber(columnNumber):
    letter = ""

    while columnNumber > 0:
        columnNumber, remainder = divmod(columnNumber - 1, 26)
        letter = chr(65 + remainder) + letter

    return letter







# def startCode():
#
#     global time
#     import time
#
#     print("Comment: Importing modules and setting up variables...")
#     return time.time()




def getFromDict(dictObj, key):
    return dictObj[key]




def getFromList(listObj, position):
    return listObj[position]




def saveFile(dataObj, path):

    with open(path, "w") as out:
        p(dataObj, stream=out)




def filterListOfLists(list, filterObj):

    listToReturn = []

    for item in list:

        for dictionary in filterObj:

            filterCount = 0

            for key, value in dictionary.items():
                if item[key] == value:
                    filterCount = filterCount + 1

            if filterCount == len(dictionary):
                listToReturn.append(item)

    # p(listToReturn)

    return listToReturn



# def sumListOfLists(list, index):
#
#     runningSum = 0
#
#     for item in list:
#         runningSum = runningSum + float(item[index] or 0)
#
#     return runningSum



# def sumFormulasListOfLists(list, index):
#
#     runningFormula = "="
#
#     for item in list:
#
#         if isinstance(item[index], str):
#             runningFormula = runningFormula + "+" + item[index].strip("=")
#         else:
#             runningFormula = runningFormula + "+" + str(item[index])
#
#
#
#     return runningFormula



# def convertTwoColumnListToDict(listObj, startingRow):
#
#     dictToReturn = {}
#
#     for item in listObj[1:]:
#         dictToReturn[item[0]] = item[1]
#
#     return dictToReturn




def convertSerialDateToDateWithoutDashes(serialDate):


    dateObj = date.fromordinal(date(1900, 1, 1).toordinal() + serialDate - 2)
    dateStr = str(dateObj.year) + str(dateObj.month).zfill(2) + str(dateObj.day).zfill(2)

    return dateStr



def convertSerialDateToMySQLDate(serialDate):

    dateObj = date.fromordinal(date(1900, 1, 1).toordinal() + serialDate - 2)
    dateStr = str(dateObj.year) + "-" + str(dateObj.month).zfill(2) + "-" + str(dateObj.day).zfill(2)

    return dateStr


def convertSerialDateToYear(serialDate):

    dateObj = date.fromordinal(date(1900, 1, 1).toordinal() + serialDate - 2)

    return str(dateObj.year)



def convertSerialDateToMonth(serialDate):

    dateObj = date.fromordinal(date(1900, 1, 1).toordinal() + serialDate - 2)

    return str(dateObj.month)



def convertDateToSerialDate(dateObj):

    temp = datetime.datetime(1899, 12, 30)    # Note, not 31st Dec but 30th!
    delta = dateObj - temp

    return float(delta.days) + (float(delta.seconds) / 86400)



def executeSQLStatements(sqlList, sqlCursor):

    for cmd in sqlList:
        sqlCursor.execute(cmd)





def createDatabase(databaseName, dbPath):

    dbPath = dbPath + "\\" + databaseName
    sqlObj = {"sqlConnection": sqlite3.connect(dbPath)}
    sqlObj["sqlCursor"] = sqlObj["sqlConnection"].cursor()

    return sqlObj




def closeDatabase(sqlConnection):

    sqlConnection.commit()
    sqlConnection.close()




def createColumnsDict(list):

    columnsDict = OrderedDict()

    for pair in list:
        for key, value in pair.items():
            columnsDict[key] = value

    return columnsDict




def createTable(tblName, columnsObj, sqlCursor):

    sqlList = []

    sqlList.append("drop table if exists " + tblName + ";")
    sqlCommand = "create table " + tblName + " ("

    for key, value in columnsObj.items():
        sqlCommand = sqlCommand + key + " " + value

        if key != next(reversed(columnsObj)):
            sqlCommand = sqlCommand + ", "

    sqlCommand = sqlCommand + ");"


    sqlList.append(sqlCommand)

    # sqlList.append(
    #     "create table " + tblName + " (tranDate date, account varchar(255), accountType varchar(255), accountCategory varchar(255), amount float, tranType varchar(255), stockName varchar(255), broker varchar(255), lot varchar(255), shares float);")

    # p(sqlList)
    executeSQLStatements(sqlList, sqlCursor)





def createTableAs(tblName, sqlCursor, sqlCommand):

    sqlList = ["drop table if exists " + tblName, "create table " + tblName + " as " + sqlCommand]
    executeSQLStatements(sqlList, sqlCursor)




def createAndPopulateTable(tblName, columnsObj, sqlCursor, sheetDataList, listOfDateColumns):

    createTable(tblName, columnsObj, sqlCursor)
    populateTable(len(sheetDataList), len(sheetDataList[0]), tblName, sheetDataList, sqlCursor, listOfDateColumns)




def createPopulateSelect(tblName, columnsObj, sqlCursor, sheetDataList, listOfDateColumns, sqlCommand, includeColumnNames):

    createTable(tblName, columnsObj, sqlCursor)
    populateTable(len(sheetDataList), len(sheetDataList[0]), tblName, sheetDataList, sqlCursor, listOfDateColumns)

    return getQueryResult(sqlCommand, sqlCursor, includeColumnNames)



def populateTable(totalRows, totalColumns, tblName, sheetDataList, sqlCursor, listOfDateColumns):

    sqlCommand = "insert into " + tblName + " values "

    for indexOfRow in range(1, totalRows):

        sqlCommand = sqlCommand + "("

        for indexOfColumn in range(0, totalColumns):

            sqlCommand = sqlCommand + "\""

            if indexOfColumn in listOfDateColumns:
                sqlCommand = sqlCommand + convertSerialDateToMySQLDate(
                    sheetDataList[indexOfRow][indexOfColumn])
            else:
                sqlCommand = sqlCommand + str(sheetDataList[indexOfRow][indexOfColumn])

            sqlCommand = sqlCommand + "\""

            if indexOfColumn != totalColumns - 1:
                sqlCommand = sqlCommand + ", "

        sqlCommand = sqlCommand + ")"

        if indexOfRow != totalRows - 1:
            sqlCommand = sqlCommand + ", "

    sqlCommand = sqlCommand + ";"

    # p(sqlCommand)
    executeSQLStatements([sqlCommand], sqlCursor)
     



def getQueryResult(sqlCommand, sqlCursor, includeColumnNames):

    sqlCursor.execute(sqlCommand)
    fetchResult = sqlCursor.fetchall()
    queryResult = []

    for row in fetchResult:
        queryResult.append(list(row))

    if includeColumnNames:

        colNames = []

        for column in sqlCursor.description:
            colNames.append(column[0])

        # colNames = getSQLColNamesList(sqlCursor, tblName, False)


        for i in range(0, len(colNames)):
            if colNames[i].startswith("'"):
                # p(1)
                colNames[i] = colNames[i][1:]

            if colNames[i].endswith("'"):
                # p(2)
                colNames[i] = colNames[i][:-1]


        queryResult.insert(0, colNames)

    # p(queryResult)

    return queryResult




def createPivotColDict(fieldToPivot, fieldToSum, dataList, **kwargs):

    receivedFunc = kwargs.get("customColumn", False)

    colData = []

    for fieldIndex in range(0, len(dataList[0])):
        if dataList[0][fieldIndex] == fieldToPivot:
            fieldColIndex = fieldIndex

    for row in dataList[1:]:
        colData.append(row[fieldColIndex])

    colData = list(set((colData)))
    colData.sort()

    colDict = {"colList": colData}
    pivotColStr = ""


    # p(colData)

    for colItem in colData:

        if receivedFunc:
            columnName = receivedFunc(str(colItem))
        else:
            columnName = str(colItem)


        pivotColStr = pivotColStr + "sum(case when \"" + fieldToPivot + "\" = \"" + str(colItem) + "\" then \"" + fieldToSum + "\" end) as \"" + columnName + "\""

        if colItem != colData[len(colData) - 1]:
            pivotColStr = pivotColStr + ", "

    colDict["pivotColStr"] = pivotColStr

    return colDict





def getAllColumns(colDict, sqlCursor):

    colList = []

    for i in range(0, len(colDict)):

        tableColNamesList = getSQLColNamesList(sqlCursor, colDict[i]["table"], True)

        tableColNamesWithoutExcl = []

        for col in tableColNamesList:

            excluded = False

            for excludedField in colDict[i]["excludedFields"]:
                if ".'" + excludedField + "'" in col:
                    excluded = True

            if not excluded:
                # if "additionalColumnText" in colDict[i]:
                #     tableColNamesWithoutExcl.append(col + " as '" + col.split("'")[1] + " " + colDict[i]["additionalColumnText"] + "'")
                # else:
                tableColNamesWithoutExcl.append(col)

        colList.extend(tableColNamesWithoutExcl)

    return colList





def getSQLColNamesList(sqlCursor, tblName, addTableName):

    colNames = []

    # for tblName in tblNames:

    sqlCursor.execute("pragma table_info(" + tblName + ");")
    fetchedList = sqlCursor.fetchall()

    addedTableName = ""

    if addTableName:
        addedTableName = tblName + "."

    colNames.extend([addedTableName + "'" + item[1] + "'" for item in fetchedList])

    return colNames




def fieldsDictToStr(dict, fieldBool, aliasBool):

    strToReturn = ""

    for i in range(0, len(dict)):

        if fieldBool:

            strToReturn = strToReturn + dict[i]["field"]

        if fieldBool and aliasBool:

            strToReturn = strToReturn + " as "

        if aliasBool:

            strToReturn = strToReturn + dict[i]["alias"]

        if i != len(dict) - 1:
            strToReturn = strToReturn + ", "


        # strToReturn = strToReturn + item

    return strToReturn




def listToStr(list):
    return ", ".join(list)




# def vlookup(searchTerm, map, colIndexToSearch, colIndexToReturn):
#
#     for line in map:
#
#         if searchTerm == line[colIndexToSearch]:
#             return "AAA"




def mapData(map, valueToGive, valueToGiveColIndex, valueToGetColIndex):

    valueToGet = ""

    # p(map)

    # tickerSym = _myPyFunc.vlookup(lotStockName, tickerMapUniqueExtractedValues)

    for line in map:
        if valueToGive == line[valueToGiveColIndex]:
            valueToGet = line[valueToGetColIndex]


    return valueToGet




def removeRepeatedDataFromList(listToProcess):

    newList = copy.deepcopy(listToProcess)

    # for row in listToProcess:
    #     p(type(row))

    for rowIndex in range(0, len(listToProcess)):
        if rowIndex != 0:
            for colIndex in range(0, len(listToProcess[rowIndex])):
                if listToProcess[rowIndex][colIndex] == listToProcess[rowIndex - 1][colIndex] and listToProcess[rowIndex][colIndex] is not None:
                    newList[rowIndex][colIndex] = ""
                    # p("repeat val: " + listToProcess[rowIndex][colIndex])

    return newList



def addTotal(listToProcess, colToTotal, totalsList):

    newList = copy.deepcopy(listToProcess)

    for rowIndex in range(1, len(listToProcess)):

        if rowIndex > 1:

            if listToProcess[rowIndex - 1][colToTotal] != listToProcess[rowIndex][colToTotal]:

                # p(totalsList[0])
                newList.insert(rowIndex, totalsList[0])
                # p(listToProcess[rowIndex][colToTotal])

            if rowIndex == len(listToProcess) - 1:

                newList.append(totalsList[1])

    return newList







def getShortenedPathLib(pathToShorten, lastDirectoryToInclude):

    

    shortenedPath = pathToShorten.parts[:pathToShorten.parts.index('repos') + 1]
  
    return Path(*shortenedPath)





def getPathUpFolderTree(pathToClimb, directoryToFind):

    for x in range(0, len(pathToClimb.parts) - 1):

        # print(pathToClimb.parents[x])

        if pathToClimb.parents[x].name == directoryToFind:
            return pathToClimb.parents[x]

    return pathToClimb



def replacePartOfPath(pathToConvert, partToBeReplaced, partToReplace):
    
    return Path(str(pathToConvert).replace(partToBeReplaced, partToReplace))




def saveToFile(dataObj, nameOfDataObj, fileExtensionToSave, pathToSaveFileTo):
    
    if pathToSaveFileTo:
        
        fullPathToSaveFileTo = Path(pathToSaveFileTo, nameOfDataObj + '.' + fileExtensionToSave)

        if fileExtensionToSave == 'json':
            with open(fullPathToSaveFileTo, 'w+') as fileObj:
                json.dump(dataObj, fileObj)
        else:
            fileObj = open(fullPathToSaveFileTo, 'w+')
            fileObj.write(nameOfDataObj + ' = ' + str(dataObj))
            fileObj.close()
    



def addToPath(basePath, arrayOfPathParts):

    tempPath = basePath

    for pathPart in arrayOfPathParts:
        tempPath = Path(tempPath, pathPart)

    return tempPath




def getVariableNameStr(dictionaryOfVariables, variableToFind):

    return [k for k, v in dictionaryOfVariables if v == variableToFind][0]








def generateKey(pathToKeyFile):
    """
    Generates a key and save it into a file
    """
    
    generatedKey = Fernet.generate_key()

    with open(pathToKeyFile, 'wb') as keyFileObj:
        keyFileObj.write(generatedKey)



def openSavedKey(pathToKeyFile):
    """
    Loads the key from the current directory named `keyFile.key`
    """

    return open(pathToKeyFile, 'rb').read()



def encryptFile(pathOfFileToProcess, loadedKey, pathToSaveEncryptedFile=None):
    """
    Given a pathOfFileToProcess (str) and key (bytes), it encrypts the file and write it
    """

    fernetObjUsingKey = Fernet(loadedKey)

    with open(pathOfFileToProcess, "rb") as fileObj:
        # read all file data
        fileData = fileObj.read()


    # encrypt data
    encryptedFileData = fernetObjUsingKey.encrypt(fileData)

    # write the encrypted file
    with open(pathToSaveEncryptedFile, "wb") as fileObj:
        fileObj.write(encryptedFileData)



def decryptFile(pathOfEncryptedFile, loadedKey, pathToSaveDecryptedFile=None):
    """
    Given a pathOfEncryptedFile (str) and key (bytes), it decrypts the file and write it
    """

    fernetObjUsingKey = Fernet(loadedKey)

    with open(pathOfEncryptedFile, "rb") as fileObj:
        # read the encrypted data
        encryptedFileData = fileObj.read()

    # decrypt data
    decryptedFileData = fernetObjUsingKey.decrypt(encryptedFileData)


    # write the original file
    with open(pathToSaveDecryptedFile, "wb") as fileObj:
        fileObj.write(decryptedFileData)




def decryptIntoSameFolder(pathToFolder, fileName, encryptionKey):

	pathToDecryptedFile = Path(pathToFolder, 'decrypted' + fileName)

	decryptFile(Path(pathToFolder, 'encrypted' + fileName), encryptionKey, pathToSaveDecryptedFile=pathToDecryptedFile)
	return pathToDecryptedFile



def clearDecryptedFiles(decryptedFilesToClear):
	for decryptedFileToClear in decryptedFilesToClear:
			with open(decryptedFileToClear, "w") as fileObj:
				fileObj.write('')



# createRow(listToProcess[rowIndex], colToTotal, listToProcess[rowIndex - 1][colToTotal])

# def createRow(row, colToTotal, colToTotalName):
#
#     newRow = []
#
#     for colIndex in range(0, len(row)):
#         if colIndex == colToTotal:
#             newRow.append("Total " + colToTotalName)
#         else:
#             newRow.append("")
#
#     return newRow





    #
    # while column > 0:
    #     temp = (column - 1) % 26
    #     print(temp + 65)
    #     letter = ''.join(map(chr, temp + 65))
    #     # letter = String.fromCharCode(temp + 65) + letter
    #     column = (column - temp - 1) / 26
    #
    # # return letter
    # return column



# function letterToColumn(letter)
# {
#   var column = 0, length = letter.length;
#   for (var i = 0; i < length; i++)
#   {
#     column += (letter.charCodeAt(i) - 64) * Math.pow(26, length - i - 1);
#   }
#   return column;
# }









# def pynputPressRel(controllerObj, keyToPress):
#     controllerObj.press(keyToPress)
#     controllerObj.release(keyToPress)

#
# def emptyCell(f):
#     if f:
#         return float(f)
#     else:
#         return 0




# def returnCellValue(row, column, array):
#     value = array[row - 1][column - 1]
#     return value


def typeCharactersOnRemoteDesktop(charactersToType, priorPyAutoGuiPause, pause=None):

    import pyautogui
    charactersNeedingShift = (list(range(123, 127)) + list(range(94, 96)) + list(range(62, 91)) + [60, 58] + list(range(40, 44)) + list(range(33, 39)))
    

    for characterToType in charactersToType:

        if ord(characterToType) in charactersNeedingShift:

            if pause == None:
                pyautogui.PAUSE = .0001
            else:
                pyautogui.PAUSE = pause

            # pyautogui.hotkey('shift', characterToType)
            pyautogui.keyDown('shift')
            pyautogui.press(characterToType)
            pyautogui.keyUp('shift')
            pyautogui.PAUSE = priorPyAutoGuiPause

        else:
            pyautogui.press(characterToType)



def getKeyState(keyCode):

    import ctypes
    obj = ctypes.WinDLL("User32.dll")

    if (obj.GetKeyState(keyCode) & 0xffff) != 0:
        return True
    return False


def numLockIsOff():

    VK_NUMLOCK = 0x90
    VK_CAPITAL = 0x14

    return getKeyState(VK_NUMLOCK)


def clickImageAfterWaiting(pngFileName, confidence=.9):

    g.click(getCoordinatesAfterWaiting(pngFileName, confidence=confidence))


def getCoordinatesAfterWaiting(pngFileName, confidence=.9, center=True):

    coordinatesToReturn = None

    while not coordinatesToReturn:
        p(f'Looking for {pngFileName[:-4]}')

        if center:
            coordinatesToReturn = g.locateCenterOnScreen(pngFileName, confidence=confidence)
        else:
            coordinatesToReturn = g.locateOnScreen(pngFileName, confidence=confidence)

    return coordinatesToReturn


def waitUntilGone(pngFileName, confidence=.9, center=True):

    coordinatesToReturn = g.locateOnScreen(pngFileName, confidence=confidence)

    while coordinatesToReturn:
        p(f'Waiting for {pngFileName[:-4]} to disappear.')

        if center:
            coordinatesToReturn = g.locateCenterOnScreen(pngFileName, confidence=confidence)
        else:
            coordinatesToReturn = g.locateOnScreen(pngFileName, confidence=confidence)

    return coordinatesToReturn


def operateOnAllFileObj(rootFolder, actionToPerformOnEachFileObj, pathsToExclude=[]): 

    def listOfSubFolders(folderPath):

        subFolderArray = []

        try:
            for node in folderPath.iterdir():
                if not node.is_file() and node not in pathsToExclude:
                    subFolderArray.append(node)
        except:
            pass

        return subFolderArray

    folderArray = [rootFolder]

    while folderArray:

        currentFolder = folderArray.pop(0)
        folderArray.extend(listOfSubFolders(currentFolder))

        try:
            returnedFile = actionToPerformOnEachFileObj(currentFolder, 'git')

            if returnedFile:
                return returnedFile

        except:
            pass

    return None

