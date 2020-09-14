from pathlib import Path
pathToThisPythonFile = Path(__file__).resolve()
import sys
sys.path.append(str(pathToThisPythonFile.parents[2]))
import myPythonLibrary.myPyFunc as myPyFunc

from pprint import pprint as pp





def isWhite(cell):

    try:
        if cell["userEnteredFormat"]["backgroundColor"]["red"] + cell["userEnteredFormat"]["backgroundColor"]["green"] + cell["userEnteredFormat"]["backgroundColor"]["blue"] == 3:
            return True
    except KeyError:
        return True

    return False


def hasFormattedValue(cell):

    for item in cell:
        if "formattedValue" in item:
            return True

    return False



def getDataWithGrid(spreadsheetIDStr, googleSheetsObj, rangesArgument):
    return googleSheetsObj.get(spreadsheetId=spreadsheetIDStr, includeGridData=True, ranges=rangesArgument).execute()





def getCellValue(dataObj, sheetPos, rowPos, colPos):
    sheetsData = myPyFunc.getFromDict(dataObj, "sheets")
    currentSheetData = myPyFunc.getFromList(sheetsData, sheetPos)
    dataOnSheet = myPyFunc.getFromList(myPyFunc.getFromDict(currentSheetData, "data"), 0)
    currentRowsData = myPyFunc.getFromDict(dataOnSheet, "rowData")
    currentRowData = myPyFunc.getFromDict(myPyFunc.getFromList(currentRowsData, rowPos), "values")
    try:
        return myPyFunc.getFromList(currentRowData, colPos)["formattedValue"]
    except:
        return ""




def getCellValueEffective(dataObj, sheetPos, rowPos, colPos):
    sheetsData = myPyFunc.getFromDict(dataObj, "sheets")
    currentSheetData = myPyFunc.getFromList(sheetsData, sheetPos)
    dataOnSheet = myPyFunc.getFromList(myPyFunc.getFromDict(currentSheetData, "data"), 0)
    currentRowsData = myPyFunc.getFromDict(dataOnSheet, "rowData")
    currentRowData = myPyFunc.getFromDict(myPyFunc.getFromList(currentRowsData, rowPos), "values")
    try:
        return myPyFunc.getFromList(currentRowData, colPos)["effectiveValue"]
    except:
        return getCellValue(dataObj, sheetPos, rowPos, colPos)



def countRows(dataObj, sheetPos):

    sheetsData = myPyFunc.getFromDict(dataObj, "sheets")

    # saveFile(sheetsData, pathlib.Path(pathlib.Path.cwd().parents[3]/"privateData"/"stockResults"/"sheetsData.json"))
    # for i in sheetsData:
    #     pp(str(i)[:50])

    currentSheetData = myPyFunc.getFromList(sheetsData, sheetPos)
    dataOnSheet = myPyFunc.getFromList(myPyFunc.getFromDict(currentSheetData, "data"), 0)

    if "rowData" in dataOnSheet:
        return len(myPyFunc.getFromDict(dataOnSheet, "rowData"))
    else:
        return 1000000





def countColumns(dataObj, sheetPos):
    sheetsData = myPyFunc.getFromDict(dataObj, "sheets")
    currentSheetData = myPyFunc.getFromList(sheetsData, sheetPos)
    dataOnSheet = myPyFunc.getFromList(myPyFunc.getFromDict(currentSheetData, "data"), 0)

    if "rowData" in dataOnSheet:
        currentRowsData = myPyFunc.getFromDict(dataOnSheet, "rowData")
        currentRowData = myPyFunc.getFromDict(myPyFunc.getFromList(currentRowsData, 0), "values")
        return len(currentRowData)
    else:
        return 1000000






def extractValues(dataObj, downloadList, sheetName):

    listToReturn = []

    sheetPos = downloadList.index(sheetName)
    numRows = countRows(dataObj, sheetPos)
    numCols = countColumns(dataObj, sheetPos)

    for indexOfRow in range(0, numRows):
        currentRowData = []

        for indexOfColumn in range(0, numCols):
            dictionary = getCellValueEffective(dataObj, sheetPos, indexOfRow, indexOfColumn)

            if not isinstance(dictionary, str):
                dictKey = list(dictionary.keys())[0]
                currentRowData.append(dictionary[dictKey])  # {"value": dictionary[dictKey], "type": dictKey})
            else:
                currentRowData.append("")  # {"value": "", "type": ""})

        listToReturn.append(currentRowData)


    return listToReturn




def extractValuesAndTypes(numRows, numCols, dataObj, sheetPos):

    listToReturn = []

    for indexOfRow in range(0, numRows):
        currentRowData = []

        for indexOfColumn in range(0, numCols):
            dictionary = getCellValueEffective(dataObj, sheetPos, indexOfRow, indexOfColumn)

            if not isinstance(dictionary, str):
                dictKey = list(dictionary.keys())[0]
                currentRowData.append({"value": dictionary[dictKey], "type": dictKey})
            else:
                currentRowData.append({"value": "", "type": ""})

        listToReturn.append(currentRowData)


    return listToReturn




def reduceSheet(rowsToKeep, columnsToKeep, sheetName, googleSheetsObj, spreadsheetID, clearSheet):

    if sheetName == "tblScrubBalanceSheet":

        sheetID = getSheetID(sheetName, googleSheetsObj, spreadsheetID)
        totalRows = 10000000
        totalColumns = 999
    else:

        googleSheetsDataWithGrid = getDataWithGrid(spreadsheetID, googleSheetsObj, sheetName)
        totalRows =  countRows(googleSheetsDataWithGrid, 0)
        totalColumns = countColumns(googleSheetsDataWithGrid, 0)
        sheetID = googleSheetsDataWithGrid["sheets"][0]["properties"]["sheetId"]


    requestObj = {}
    requestObj["requests"] = []



    if totalRows > rowsToKeep:
        requestObj["requests"].append({
                    "deleteDimension": {
                        "range": {
                            "sheetId": sheetID,
                            "dimension": "ROWS",
                            "startIndex": rowsToKeep,
                            "endIndex": totalRows
                        }
                    }
                }
        )




    if totalColumns > columnsToKeep:

        requestObj["requests"].append({
                    "deleteDimension": {
                        "range": {
                            "sheetId": sheetID,
                            "dimension": "COLUMNS",
                            "startIndex": columnsToKeep,
                            "endIndex": totalColumns
                        }
                    }
                })

    requestObj["requests"].append({
                    "clearBasicFilter": {
                        "sheetId": sheetID
                    }
                }
    )


    googleSheetsObj.batchUpdate(spreadsheetId=spreadsheetID, body=requestObj).execute()

    if clearSheet:
        googleSheetsObj.values().clear(spreadsheetId=spreadsheetID, range=sheetName, body={}).execute()





def cellOff(rowOffset, colOffset, **kwargs):

    sheetName = kwargs.get("sheetName", False)

    if sheetName:
        ref = "indirect(\"" + sheetName + "!r[" + str(rowOffset) + "]c[" + str(colOffset) + "]\",false)"
    else:
        ref = "indirect(\"" + "r[" + str(rowOffset) + "]c[" + str(colOffset) + "]\", false)"

    return ref




def createDictMapFromSheet(googleSheetsDataWithGrid, downloadList, sheetName):

    from collections import OrderedDict

    sheetIndex = downloadList.index(sheetName)
    rowTotal = countRows(googleSheetsDataWithGrid, sheetIndex)
    colTotal = countColumns(googleSheetsDataWithGrid, sheetIndex)

    mappingDict = {}

    for indexOfRow in range(0, rowTotal):

        colDict = OrderedDict()

        for indexOfColumn in range(1, colTotal):

            colTitle = getCellValue(googleSheetsDataWithGrid, sheetIndex, 0, indexOfColumn)

            colDict[colTitle] = getCellValue(googleSheetsDataWithGrid, sheetIndex, indexOfRow, indexOfColumn)

        mappingDict[getCellValue(googleSheetsDataWithGrid, sheetIndex, indexOfRow, 0)] = colDict

    return mappingDict



def checkForSheet(sheetName, googleSheetsObj, spreadsheetID):

    allSheetsResponse = googleSheetsObj.get(spreadsheetId=spreadsheetID, includeGridData=False, fields="sheets/properties(title)").execute().get("sheets", "")

    for rsp in allSheetsResponse:
        if sheetName == rsp.get("properties", "").get("title", ""):
            return True

    return False




def createSheet(sheetName, googleSheetsObj, spreadsheetID):

    spreadsheetBody = {
        "requests": [
            {
                "addSheet": {
                    "properties": {
                        "title": sheetName,
                        "gridProperties": {
                            "rowCount": 1,
                            "columnCount": 1
                        },
                        "tabColor": {
                            "red": 0,
                            "green": 0,
                            "blue": 0
                        }
                    }
                }
            }
        ]
    }

    googleSheetsObj.batchUpdate(spreadsheetId=spreadsheetID, body=spreadsheetBody).execute()



def getSheetID(sheetName, googleSheetsObj, spreadsheetID):

    allSheetsResponse = googleSheetsObj.get(spreadsheetId=spreadsheetID, includeGridData=False, fields="sheets/properties(title,sheetId)").execute().get(
        "sheets", "")

    for rsp in allSheetsResponse:
        responseProperties = rsp.get("properties", "")

        if sheetName == responseProperties.get("title", ""):
            return responseProperties.get("sheetId", "")




def populateSheet(rowsToKeep, colsToKeep, sheetName, googleSheetsObj, spreadsheetID, valuesList, clearSheet, **kwargs):

    writeToSheet = kwargs.get("writeToSheet", False)
    columnRow = kwargs.get("columnRow", True)
    cellFormattingRequest = kwargs.get("cellFormattingRequest", [])



    messageToPrint = "Task completed"

    if writeToSheet:

        if not checkForSheet(sheetName, googleSheetsObj, spreadsheetID):
            createSheet(sheetName, googleSheetsObj, spreadsheetID)
        else:
            reduceSheet(rowsToKeep, colsToKeep, sheetName, googleSheetsObj, spreadsheetID, clearSheet)

        googleSheetsObj.values().update(spreadsheetId=spreadsheetID, range=sheetName, valueInputOption="USER_ENTERED", body={"values": valuesList}).execute()
        lastColumnNum = len(valuesList[0]) + 1
        sheetID = getSheetID(sheetName, googleSheetsObj, spreadsheetID)


        formatCellsRequest = {
            "requests": [
                {
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": sheetID,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": lastColumnNum
                        }
                    }
                }
            ]
        }

        if cellFormattingRequest:
            formatCellsRequest["requests"].extend(cellFormattingRequest)



        if columnRow:

            formatCellsRequest["requests"].extend([
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheetID,
                            "startRowIndex": 0,
                            "endRowIndex": 1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "textFormat": {
                                    "bold": True
                                }
                            }
                        },
                        "fields": "userEnteredFormat(textFormat)"
                    }
                },
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": sheetID,
                            "gridProperties": {
                                "frozenRowCount": 1
                            }
                        },
                        "fields": "gridProperties.frozenRowCount"
                    }
                },
                {
                    "setBasicFilter": {
                        "filter": {
                            "range": {
                                "sheetId": sheetID,
                                "startRowIndex": 0,
                                "endRowIndex": len(valuesList)
                            }
                        }

                    }
                }

            ])







        googleSheetsObj.batchUpdate(spreadsheetId=spreadsheetID, body=formatCellsRequest).execute()


        # pp(sheetName)
        # pp(kwargs)

        messageToPrint = "Finished writing to " + sheetName




    splitTime = kwargs.get("splitTimeArg", None)


    if splitTime:
        return myPyFunc.printElapsedTime(splitTime, messageToPrint)






def authFunc(*optionalParameterPathToGoogleCredentials):

    import pickle, pathlib, googleapiclient.discovery, google_auth_oauthlib.flow, google.auth.transport.requests
    # print(pathlib.Path.cwd().parents[3])

    if optionalParameterPathToGoogleCredentials:
        credentialsPath = str(optionalParameterPathToGoogleCredentials[0]) + "\\googleCredentials.json"
        tokenPath = str(optionalParameterPathToGoogleCredentials[0]) + "\\googleToken.pickle"
    else:
        credentialsPath = str(pathlib.Path.cwd().parents[3]) + "\\privatedata\\googleCredentials\\googleCredentials.json"
        tokenPath = str(pathlib.Path.cwd().parents[3]) + "\\privatedata\\googleCredentials\\googleToken.pickle"
    
    googleScopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentialsObj = None


    if pathlib.Path.exists(pathlib.Path(tokenPath)):
        with open(tokenPath, "rb") as tokenObj:
            credentialsObj = pickle.load(tokenObj)


    # If there are no (valid) credentials available, let the user log in.
    if not credentialsObj or not credentialsObj.valid:
        if credentialsObj and credentialsObj.expired and credentialsObj.refresh_token:
            credentialsObj.refresh(google.auth.transport.requests.Request())
        else:
            flowObj = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(credentialsPath, googleScopes)
            credentialsObj = flowObj.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokenPath, "wb") as tokenObj:
            pickle.dump(credentialsObj, tokenObj)


    return googleapiclient.discovery.build("sheets", "v4", credentials=credentialsObj).spreadsheets()





#######################################################################################################


def getGoogleSheetsAPIObj(arrayOfPathParts=None, pathToCredentialsDirectory=None, pathToCredentialsFileServiceAccount=None):

    from pathlib import Path
    pathToThisPythonFile = Path(__file__).resolve()
    import sys
    sys.path.append(str(Path(pathToThisPythonFile.parents[2], 'myPythonLibrary')))
    import myPyFunc
    
    import pickle, googleapiclient.discovery, google_auth_oauthlib.flow, google.auth.transport.requests
    from pprint import pprint as pp


    googleSheetsAPIScopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentialsObj = None


    if pathToCredentialsFileServiceAccount:

        import google.oauth2
        credentialsObj = google.oauth2.service_account.Credentials.from_service_account_file(pathToCredentialsFileServiceAccount)
        return googleapiclient.discovery.build("sheets", "v4", credentials=credentialsObj).spreadsheets()

    else:

        if pathToCredentialsDirectory:
            pathToJSONForCredentialsRetrieval = Path(pathToCredentialsDirectory, 'jsonForCredentialsRetrieval.json')
            pathToPickleFileWithCredentials = Path(pathToCredentialsDirectory, 'pickleFileWithCredentials.pickle')
        else:
            pathToRepos = myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
            pathToJSONForCredentialsRetrieval = myPyFunc.addToPath(pathToRepos, arrayOfPathParts + ['jsonForCredentialsRetrieval.json'])
            pathToPickleFileWithCredentials = myPyFunc.addToPath(pathToRepos, arrayOfPathParts + ['pickleFileWithCredentials.pickle'])




        #if the pickle is file is available from persistent memory, then get the credentials object from it
        #otherwise, check if the credentials object can be refreshed and do that
        #if the credentials object can't be refreshed, then get them

        if Path.exists(pathToPickleFileWithCredentials):
            with open(pathToPickleFileWithCredentials, "rb") as pickleFileObj:
                credentialsObj = pickle.load(pickleFileObj)
        else:

            if not credentialsObj or not credentialsObj.valid:
                if credentialsObj and credentialsObj.expired and credentialsObj.refresh_token:
                    credentialsObj.refresh(google.auth.transport.requests.Request())
                else:
                    flowObj = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(pathToJSONForCredentialsRetrieval, googleSheetsAPIScopes)
                    credentialsObj = flowObj.run_local_server(port=0)
                
                #save the credentials in persistent memeory
                
                with open(pathToPickleFileWithCredentials, "wb") as pickleFileObj:
                    pickle.dump(credentialsObj, pickleFileObj)

        return googleapiclient.discovery.build("sheets", "v4", credentials=credentialsObj).spreadsheets()





def getDataWithGridForRange(spreadsheetIDStr, googleSheetsAPIObj, rangesArgument):
    return googleSheetsAPIObj.get(spreadsheetId=spreadsheetIDStr, includeGridData=True, ranges=rangesArgument).execute()





def getJSONOfAllSheets(spreadsheetIDStr, googleSheetsAPIObj, fieldMask=None):

    if fieldMask:
        return googleSheetsAPIObj.get(spreadsheetId=spreadsheetIDStr, fields=fieldMask).execute()        
    else:
        return googleSheetsAPIObj.get(spreadsheetId=spreadsheetIDStr, includeGridData=True).execute()




def getJSONOfOneSheet(jsonOfAllSheets, sheetNameStr):

    sheetsArray = jsonOfAllSheets['sheets']

    for sheetObj in sheetsArray:
        sheetNameFromJSON = sheetObj['properties']['title']

        if sheetNameStr == sheetNameFromJSON:
            return sheetObj


def getSheetIDOfOneSheet(jsonOfAllSheets, sheetNameStr):

    sheetsArray = jsonOfAllSheets['sheets']

    for sheetObj in sheetsArray:
        sheetNameFromJSON = sheetObj['properties']['title']

        if sheetNameStr == sheetNameFromJSON:
            return sheetObj['properties']['sheetId']




def getArrayFromJSONOfOneSheet(jsonOfOneSheet, googleSheetsAPIObj, spreadsheetIDStr, sheetNameStr):

    arrayOfRowData = getArrayOfRowData(jsonOfOneSheet)
    lengthOfLongestRow = getLengthOfLongestRow(arrayOfRowData)
    
    arrayOfOneSheet = []

    for rowObj in arrayOfRowData:
        
        valuesArray = rowObj['values']
        # print(valuesArray)
        arrayOfOneRow = []

        for cellObj in valuesArray:
            
            if 'formattedValue' in cellObj:
                valueToAppend = cellObj['formattedValue']
            else:
                valueToAppend = ''
            arrayOfOneRow.append(valueToAppend)

        while len(arrayOfOneRow) < lengthOfLongestRow:
            arrayOfOneRow.append('')

        arrayOfOneSheet.append(arrayOfOneRow)


    return arrayOfOneSheet



def getArrayOfRowData(jsonOfOneSheet):

    sheetDataArray = jsonOfOneSheet['data']

    for sheetObj in sheetDataArray:
                    
        if 'rowData' in sheetObj:

            return sheetObj['rowData']
            

# def getCellDataObjWithRowColumn(jsonOfOneSheet, row, column):

#     arrayOfRowData = getArrayOfRowData(jsonOfOneSheet)
#     rowObject = arrayOfRowData[row]
#     valuesArray = rowObject['values']
#     return valuesArray[column]
    



def getLengthOfLongestRow(arrayOfRowData):
    
    maxRowLength = 0

    for rowObj in arrayOfRowData:

        if len(rowObj['values']) > maxRowLength:
            maxRowLength = len(rowObj['values'])

    return maxRowLength



def getStrOfAllFieldMasks(arrayOfAllFieldMasks=None):

    if not arrayOfAllFieldMasks:
        return None
    else:
        strOfAllFieldMAsks = ''
        
        for fieldMaskIndex, fieldMaskArray in enumerate(arrayOfAllFieldMasks):

            for itemIndex, item in enumerate(fieldMaskArray):

                strOfAllFieldMAsks = strOfAllFieldMAsks + item

                if itemIndex != len(fieldMaskArray) - 1:
                    
                    strOfAllFieldMAsks = strOfAllFieldMAsks + '/'

            # if fieldMaskIndex != len(arrayOfAllFieldMasks) - 1:
            strOfAllFieldMAsks = strOfAllFieldMAsks + ','

        return strOfAllFieldMAsks



def getArrayOfOneSheet(googleSheetsAPIObj, spreadsheetIDStr, sheetNameStr, strOfAllFieldMasks, pathToSaveFile=None):

    from pathlib import Path
    pathToThisPythonFile = Path(__file__).resolve()


    # jsonOfAllSheetsWithoutAddedColumn = getJSONOfAllSheets(spreadsheetIDStr, googleSheetsAPIObj, fieldMask=strOfAllFieldMAsks)
    # myPyFunc.saveToFile(jsonOfAllSheetsWithoutAddedColumn, 'jsonOfAllSheetsWithoutAddedColumn', 'json', pathToSaveFile)
    # addColumnToSheet()
    jsonOfAllSheets = getJSONOfAllSheets(spreadsheetIDStr, googleSheetsAPIObj, fieldMask=strOfAllFieldMasks)
    myPyFunc.saveToFile(jsonOfAllSheets, 'jsonOfAllSheets', 'json', pathToSaveFile)
    jsonOfOneSheet = getJSONOfOneSheet(jsonOfAllSheets, sheetNameStr)
    myPyFunc.saveToFile(jsonOfOneSheet, 'jsonOfOneSheet', 'json', pathToSaveFile)
    return getArrayFromJSONOfOneSheet(jsonOfOneSheet, googleSheetsAPIObj, spreadsheetIDStr, sheetNameStr)    




def addColumnToOneSheet(googleSheetsAPIObj, spreadsheetIDStr, sheetNameStr, strOfAllFieldMasks):

    jsonOfAllSheets = getJSONOfAllSheets(spreadsheetIDStr, googleSheetsAPIObj, fieldMask=strOfAllFieldMasks)
    jsonOfOneSheet = getJSONOfOneSheet(jsonOfAllSheets, sheetNameStr)
    arrayOfRowData = getArrayOfRowData(jsonOfOneSheet)
    lengthOfLongestRowBeforeColumnAdd = getLengthOfLongestRow(arrayOfRowData)
    sheetID = getSheetIDOfOneSheet(jsonOfAllSheets, sheetNameStr)


    requestAppendColumn = {
        "requests": [
            {
                "appendDimension": {
                    "sheetId": sheetID,
                    "dimension": "COLUMNS",
                    "length": 1
                }
            }
        ]   
    }

    googleSheetsAPIObj.batchUpdate(spreadsheetId=spreadsheetIDStr, body=requestAppendColumn).execute()


    
    columnLetterOfLastColumn = myPyFunc.getColumnLetterFromNumber(lengthOfLongestRowBeforeColumnAdd + 1)
    numberOfRows = len(arrayOfRowData)
    rangeToWriteTo = sheetNameStr + '!' + columnLetterOfLastColumn + '1' + ':' + columnLetterOfLastColumn + str(numberOfRows)
    valuesToWrite = ['Last Column' for i in range(numberOfRows)]


    requestToWriteToCells = {
        "valueInputOption": "USER_ENTERED",
        "data": [
            {
                "range": rangeToWriteTo,
                "majorDimension": "COLUMNS",
                "values": [
                    valuesToWrite
                ]
            }
        ]
    }
        
  
    googleSheetsAPIObj.values().batchUpdate(spreadsheetId=spreadsheetIDStr, body=requestToWriteToCells).execute()



    requestDeleteColumn = {
        "requests": [
            {
                "deleteDimension": {
                    "range": {
                        "sheetId": sheetID,
                        "dimension": "COLUMNS",
                        "startIndex": lengthOfLongestRowBeforeColumnAdd,
                        "endIndex": lengthOfLongestRowBeforeColumnAdd + 1
                    }
                    
                }
            }
        ]   
    }

    googleSheetsAPIObj.batchUpdate(spreadsheetId=spreadsheetIDStr, body=requestDeleteColumn).execute()

