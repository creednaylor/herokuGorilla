#local application imports
from pathlib import Path
import sys
pathToThisPythonFile = Path(__file__).resolve()


#standard library imports
from pprint import pprint as p

#third-party imports
import gspread


def clearArray(startingRowIndex, endingRowIndex, startingColumnIndex, endingColumnIndex, arrayOfSheet):

    if endingRowIndex == -1:
        endingRowIndex = len(arrayOfSheet) - 1
    if endingColumnIndex == -1:
        endingColumnIndex = len(arrayOfSheet[len(arrayOfSheet) - 1]) - 1

    for row in range(startingRowIndex, endingRowIndex + 1):
        for column in range(startingColumnIndex, endingColumnIndex + 1):
            arrayOfSheet[row][column] = ''

    return arrayOfSheet



def clearSheet(startingRowIndex, endingRowIndex, startingColumnIndex, endingColumnIndex, gspSheetOfArray):

    arrayOfSheet = gspSheetOfArray.get_all_values()

    if len(arrayOfSheet) > 0:

        arrayOfSheet = clearArray(startingRowIndex, endingRowIndex, startingColumnIndex, endingColumnIndex, arrayOfSheet)
        updateCells(gspSheetOfArray, arrayOfSheet)

        


def clearSheets(startingRowIndex, endingRowIndex, startingColumnIndex, endingColumnIndex, arrayOfSheetObjects):
    
    for sheetObj in arrayOfSheetObjects:
        clearSheet(startingRowIndex, endingRowIndex, startingColumnIndex, endingColumnIndex, sheetObj)



def clearAndResizeSheets(arrayOfSheetObj):

    if isinstance(arrayOfSheetObj[0], dict):
        for sheetObj in arrayOfSheetObj:

            resizeParameter = 'resizeRows'
            if resizeParameter in sheetObj:
                sheetObj['sheetObj'].resize(rows=sheetObj[resizeParameter])

            resizeParameter = 'resizeColumns'
            if resizeParameter in sheetObj:
                sheetObj['sheetObj'].resize(cols=sheetObj[resizeParameter])
            
            for propertyToCheck in ['startingRowIndexToClear', 'startingColumnIndexToClear']:
                if propertyToCheck not in sheetObj: sheetObj[propertyToCheck] = 0

            for propertyToCheck in ['endingRowIndexToClear', 'endingColumnIndexToClear']:
                if propertyToCheck not in sheetObj: sheetObj[propertyToCheck] = -1
                
            clearSheet(sheetObj['startingRowIndexToClear'], sheetObj['endingRowIndexToClear'], sheetObj['startingColumnIndexToClear'], sheetObj['endingColumnIndexToClear'], sheetObj['sheetObj'])
    
    else:
        for sheetObj in arrayOfSheetObjects:
            sheetObj.resize(rows=1, cols=1)
            clearSheet(0, -1, 0, -1, sheetObj)



def updateCells(gspSheetOfArray, arrayOfSheet):

    if len(arrayOfSheet) > 0:

        numberOfRowsInArrayOfSheet = len(arrayOfSheet)
        
        arrayOfArrayLengths = [len(i) for i in arrayOfSheet]
        numberOfColumnsInArrayOfSheet = max(arrayOfArrayLengths)

        for row in arrayOfSheet:
            if len(row) > numberOfColumnsInArrayOfSheet:
                numberOfColumnsInArrayOfSheet = len(row)
        
        startingCell = 'R1C1'
        endingCell = 'R' + str(numberOfRowsInArrayOfSheet) + 'C' + str(numberOfColumnsInArrayOfSheet)
        addressOfSheet = startingCell + ':' + endingCell

        # print(addressOfSheet)
        gspSheetOfArray.update(addressOfSheet, arrayOfSheet)



def getGspSpreadsheetObj(spreadsheetName):
    #return gspread spreadsheet object

    pathToRepos = _myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
    arrayOfPartsToAddToPath = ['privateData', 'python', 'googleCredentials', 'usingServiceAccount', 'jsonWithAPIKey.json']

    pathToCredentialsFileServiceAccount = _myPyFunc.addToPath(pathToRepos, arrayOfPartsToAddToPath)

    gspObj = gspread.service_account(filename=pathToCredentialsFileServiceAccount)

    return gspObj.open(spreadsheetName)


def getObjOfSheets(spreadsheetName):
    #return dictionary of sheets

    gspSpreadsheet = getGspSpreadsheetObj(spreadsheetName)

    objOfSheets = {}

    for sheet in gspSpreadsheet.worksheets():
        objOfSheets[sheet.title] = {
            'sheetObj': sheet,
            'array': sheet.get_all_values()
        }

    return objOfSheets