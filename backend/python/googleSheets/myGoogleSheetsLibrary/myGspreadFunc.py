#standard library imports
import os
from pathlib import Path
from pprint import pprint as p
import sys

#third-party imports
import gspread
from google_auth_oauthlib.flow import InstalledAppFlow


#local application imports
pathToThisPythonFile = Path(__file__).resolve()

if os.environ.get('runningOnProductionServer') == 'true':
    from ...myPythonLibrary import myPyFunc
    runningOnProductionServer = True
else:
    sys.path.append(str(pathToThisPythonFile.parents[2]))
    from myPythonLibrary import myPyFunc
    runningOnProductionServer = False




def clearArray(startingRowIndex, endingRowIndex, startingColumnIndex, endingColumnIndex, arrayOfSheet):

    if endingRowIndex == -1:
        endingRowIndex = len(arrayOfSheet) - 1
    if endingColumnIndex == -1:
        endingColumnIndex = len(arrayOfSheet[len(arrayOfSheet) - 1]) - 1

    for row in range(startingRowIndex, endingRowIndex + 1):
        for column in range(startingColumnIndex, endingColumnIndex + 1):
            arrayOfSheet[row][column] = ''

    return arrayOfSheet



def clearSheet(startingRowIndex, endingRowIndex, startingColumnIndex, endingColumnIndex, sheetLevelObj):

    arrayOfSheet = sheetLevelObj.get_all_values()

    if len(arrayOfSheet) > 0:

        arrayOfSheet = clearArray(startingRowIndex, endingRowIndex, startingColumnIndex, endingColumnIndex, arrayOfSheet)
        displayArray(sheetLevelObj, arrayOfSheet)




def clearSheets(startingRowIndex, endingRowIndex, startingColumnIndex, endingColumnIndex, arrayOfSheetObjects):

    for sheetObj in arrayOfSheetObjects:
        clearSheet(startingRowIndex, endingRowIndex, startingColumnIndex, endingColumnIndex, sheetObj)



def clearAndResizeSheets(spreadsheetLevelParameters):

    for sheetLevelParameters in spreadsheetLevelParameters:

        for resizeParameter in ['resizeRows', 'resizeColumns']:
            if resizeParameter in sheetLevelParameters:
                arguments = {resizeParameter[6:9].lower() + 's': sheetLevelParameters[resizeParameter]}
                sheetLevelParameters['sheetObj'].resize(**arguments)

        clearParameters = {
            0: ['startingRowIndexToClear', 'startingColumnIndexToClear'],
            -1: ['endingRowIndexToClear', 'endingColumnIndexToClear']
        }

        for group in clearParameters:
            for parameter in clearParameters[group]:
                if parameter not in sheetLevelParameters: sheetLevelParameters[parameter] = group

        clearSheet(sheetLevelParameters['startingRowIndexToClear'], sheetLevelParameters['endingRowIndexToClear'], sheetLevelParameters['startingColumnIndexToClear'], sheetLevelParameters['endingColumnIndexToClear'], sheetLevelParameters['sheetObj'])


def updateFormatting(spreadsheetLevelObj, formatParameters):

    for sheetLevelParameters in formatParameters:

        for formatRange in sheetLevelParameters['formatRanges']:
            spreadsheetLevelObj.worksheet(sheetLevelParameters['sheetName']).format(formatRange, sheetLevelParameters['formatObj'])



def displayArray(sheetLevelObj, arrayToDisplay):

    if len(arrayToDisplay) > 0:

        numberOfRowsInArrayOfSheet = len(arrayToDisplay)
        arrayOfArrayLengths = [len(row) for row in arrayToDisplay]
        numberOfColumnsInArrayOfSheet = max(arrayOfArrayLengths)

        endingCell = 'R' + str(numberOfRowsInArrayOfSheet) + 'C' + str(numberOfColumnsInArrayOfSheet)
        addressOfSheet = 'R1C1' + ':' + endingCell

        sheetLevelObj.update(addressOfSheet, arrayToDisplay)



def autoResizeColumnsOnSheet(spreadsheetLevelObj, sheetName):

    autoResizeColsRequest = {
        "requests": [
            {
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": spreadsheetLevelObj.worksheet(sheetName)._properties['sheetId'],
                        "dimension": "COLUMNS",
                        "startIndex": 0
                    }
                }
            }
        ]
    }

    spreadsheetLevelObj.batch_update(autoResizeColsRequest)


def autoAlignColumnsInSpreadsheet(spreadsheetLevelObj):

    autoAlignColsRequest = {
        "requests": []
    }

    # p(spreadsheetLevelObj.worksheets())

    for sheetObj in spreadsheetLevelObj.worksheets():
        autoAlignColsRequest['requests'].append(
            {
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": sheetObj.id,
                        "dimension": "COLUMNS",
                        "startIndex": 0
                    }
                }
            }
        )

    spreadsheetLevelObj.batch_update(autoAlignColsRequest)


def setFiltersOnSpreadsheet(spreadsheetLevelObj, topRowsParameters):

    for sheetLevelObj in spreadsheetLevelObj.worksheets():
        if sheetLevelObj.title in topRowsParameters:
            sheetLevelObj.set_basic_filter(topRowsParameters[sheetLevelObj.title], 1, sheetLevelObj.row_count, sheetLevelObj.col_count)
        else:
            sheetLevelObj.set_basic_filter(1, 1, sheetLevelObj.row_count, sheetLevelObj.col_count)


def getGspSpreadsheetObj(spreadsheetName):
    #return gspread spreadsheet object

    pathToRepos = myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
    arrayOfPartsToAddToPath = ['privateData', 'python', 'googleCredentials', 'usingServiceAccount', 'jsonWithAPIKey.json']

    pathToCredentialsFileServiceAccount = myPyFunc.addToPath(pathToRepos, arrayOfPartsToAddToPath)

    spreadsheetLevelObj = gspread.service_account(filename=pathToCredentialsFileServiceAccount)

    return spreadsheetLevelObj.open(spreadsheetName)


def getObjOfSheets(spreadsheetName):
    #return dictionary of sheets

    spreadsheetLevelObj = getGspSpreadsheetObj(spreadsheetName)

    objOfSheets = {}

    for sheet in spreadsheetLevelObj.worksheets():
        objOfSheets[sheet.title] = {
            'sheetObj': sheet,
            'array': sheet.get_all_values()
        }

    return objOfSheets




def getSpreadsheetLevelObj(oAuthMode, pathBelowRepos, loadSavedCredentials=True, googleAccountUsername=None):

    pathToConfigData = Path(pathBelowRepos, 'backend', 'configData')

    # p('pathToConfigData {}'.format(pathToConfigData))
    # p('oAuthMode {}'.format(oAuthMode))
    # p('runningOnProductionServer {}'.format(runningOnProductionServer))


    if runningOnProductionServer:
        loadedEncryptionKey = os.environ.get('savedEncryptionKeyStr', None)
    else:
        pathToRepos = myPyFunc.getPathUpFolderTree(pathBelowRepos, 'repos')
        pathToGoogleCredentials = Path(pathToRepos, 'privateData', 'python', 'googleCredentials')


    if oAuthMode:

        scopesArray = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        credentialsObj = None

        if runningOnProductionServer:

            pathToDecryptedJSONCredentialsFile = myPyFunc.decryptIntoSameFolder(pathToConfigData, 'JSONCredentialsFile.json', loadedEncryptionKey)
            pathToDecryptedAuthorizedUserFile = myPyFunc.decryptIntoSameFolder(pathToConfigData, 'AuthorizedUserFile.json', loadedEncryptionKey)
            decryptedFilesToClear = [pathToDecryptedJSONCredentialsFile, pathToDecryptedAuthorizedUserFile]

        if not runningOnProductionServer:

            pathToDecryptedJSONCredentialsFile = Path(pathToGoogleCredentials, 'usingOAuthGspread', 'jsonCredentialsFile.json')

            pathToCheckForDecryptedAuthorizedUserFile = Path(pathToGoogleCredentials, 'usingOAuthGspread', googleAccountUsername, 'authorizedUserFile.json')

            if googleAccountUsername and pathToCheckForDecryptedAuthorizedUserFile.exists():
                credentialsObj = gspread.auth.load_credentials(filename=pathToCheckForDecryptedAuthorizedUserFile)

        if not credentialsObj:

            flowObj = InstalledAppFlow.from_client_secrets_file(pathToDecryptedJSONCredentialsFile, scopesArray)
            credentialsObj = flowObj.run_local_server(port=0)

            if not runningOnProductionServer:
                gspread.auth.store_credentials(credentialsObj, filename=pathToCheckForDecryptedAuthorizedUserFile)

        spreadsheetLevelObj = gspread.client.Client(auth=credentialsObj)


    if not oAuthMode:

        if runningOnProductionServer:

            pathToDecryptedAPIKey = myPyFunc.decryptIntoSameFolder(pathToConfigData, 'APIKey.json', loadedEncryptionKey)
            decryptedFilesToClear = [pathToDecryptedAPIKey]

        if not runningOnProductionServer: pathToDecryptedAPIKey = Path(pathToGoogleCredentials, 'usingServiceAccount', 'jsonWithAPIKey.json')

        spreadsheetLevelObj = gspread.service_account(filename=pathToDecryptedAPIKey)


    if runningOnProductionServer: myPyFunc.clearDecryptedFiles(decryptedFilesToClear)

    return spreadsheetLevelObj



def updateCell(sheetToUpdate, rowIndex, columnIndex, valueToUpdate):

    sheetToUpdate.update_cell(rowIndex + 1, columnIndex + 1, valueToUpdate)



def setFormattingOnSpreadsheet(spreadsheetLevelObj, formatParameters):

    horizontalRightAlignRequest = {
        'requests': []
    }

    for sheetObj in spreadsheetLevelObj.worksheets():
        if sheetObj.title in formatParameters:
            for formatToPerform in formatParameters[sheetObj.title]:
                for range in formatToPerform['range']:
                    if formatToPerform['format'] == 'currencyWithoutSymbol':
                        sheetObj.format(range, {'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0.00; (#,##0.00)'},}) # 'horizontalAlignment': 'RIGHT'})

                        startColumnIndex = columnLetteringToNumber(range.split(':')[0])

                        horizontalRightAlignRequest['requests'].append(
                            {
                                "repeatCell": {
                                    "range": {
                                        "sheetId": spreadsheetLevelObj.worksheet(sheetObj.title)._properties['sheetId'],
                                        "startColumnIndex": startColumnIndex,
                                        "endColumnIndex": startColumnIndex + 1
                                    },
                                    "cell": {
                                        "userEnteredFormat": {
                                            "horizontalAlignment" : "RIGHT",
                                        }
                                    },
                                    "fields": "userEnteredFormat(horizontalAlignment)"
                                }
                            }
                        )

    spreadsheetLevelObj.batch_update(horizontalRightAlignRequest)


def columnLetteringToNumber(columnLettering):

    columnLettering = columnLettering.upper()

    numberToReturn = 0

    for letter in columnLettering:
        numberToReturn = 26 * numberToReturn + (ord(letter) - 64)
            
    return numberToReturn - 1