# clear resultArray sheet when opening google sheet...


import os
from pathlib import Path
import sys

from pprint import pprint as p
import gspread


def reconcileArraysFunction(runningOnProductionServerBoolean):

    # pathToRepos = _myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')

    pathToThisPythonFile = Path(__file__).resolve()

    if runningOnProductionServerBoolean:
        p('********************Running on production server****************')
        from ..python.myPythonLibrary import _myPyFunc
        from ..python.googleSheets.myGoogleSheetsLibrary import _myGoogleSheetsFunc
        from ..python.googleSheets.myGoogleSheetsLibrary import _myGspreadFunc

        loadedEncryptionKey = os.environ.get('savedEncryptionKeyStr', None)

        
    else:
        p('********************Not running on production server****************')
        sys.path.append(str(pathToThisPythonFile.parents[1]))
        from python.myPythonLibrary import _myPyFunc
        from python.googleSheets.myGoogleSheetsLibrary import _myGoogleSheetsFunc
        from python.googleSheets.myGoogleSheetsLibrary import _myGspreadFunc

        pathToRepos = _myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
        loadedEncryptionKey = _myPyFunc.openSavedKey(Path(pathToRepos, 'privateData', 'python', 'encryption', 'savedEncryptionKey.key'))
    

    pathToAPIKey = Path(pathToThisPythonFile.parents[1], 'encryption', 'encryptedAPIKey.json')
    pathOfDecryptedFile = Path(pathToAPIKey.parents[0], 'decryptedAPIKey.json')
    _myPyFunc.decryptFile(pathToAPIKey, loadedEncryptionKey, pathToSaveDecryptedFile=pathOfDecryptedFile)
        
    gspObj = gspread.service_account(filename=pathOfDecryptedFile)
        
    gspSpreadsheet = gspObj.open('King Gorilla - Public')
    gspFirstTableSheet = gspSpreadsheet.worksheet('firstTable')
    gspSecondTableSheet = gspSpreadsheet.worksheet('secondTable')
    gspComparisonTableSheet = gspSpreadsheet.worksheet('comparisonTable')
    # gspEndingFirstTableSheet = gspSpreadsheet.worksheet('endingFirstTable')
    gspEndingSecondTableSheet = gspSpreadsheet.worksheet('endingSecondTable')

    firstArray = gspFirstTableSheet.get_all_values()
    secondArray = gspSecondTableSheet.get_all_values()
    firstArrayFirstRow = firstArray.pop(0)
    secondArrayFirstRow = secondArray.pop(0)

    firstArrayColumnIndexToCompare = 1
    secondArrayColumnIndexToCompare = 0

    comparisonArray = [['firstTable'] + [''] * (len(firstArray[0])) + ['secondTable'] + [''] * (len(secondArray[0]) - 1)]
    arrayOfColumnTitles = firstArrayFirstRow + [''] + secondArrayFirstRow
    comparisonArray.append(arrayOfColumnTitles)
    # p(comparisonArray)

    while firstArray:

        firstArrayCurrentRow = firstArray.pop(0)
        # p(firstArrayCurrentRow)
        rowToAppend = firstArrayCurrentRow + ['']

        for secondArrayRowIndexCount, secondArrayCurrentRow in enumerate(secondArray):

            # p(secondArrayCurrentRow)

            if firstArrayCurrentRow[firstArrayColumnIndexToCompare] == secondArrayCurrentRow[secondArrayColumnIndexToCompare]:

                secondArrayRowToAppend = secondArray.pop(secondArrayRowIndexCount)
                rowToAppend = rowToAppend + secondArrayRowToAppend

        comparisonArray.append(rowToAppend)
        # p(comparisonArray)


    clearAndResizeParameters = [{
        'sheetObj': gspComparisonTableSheet,
        'resizeRows': 3,
        'startingRowIndexToClear': 0
    },
    {
        'sheetObj': gspEndingSecondTableSheet,
        'resizeRows': 2,
        'startingRowIndexToClear': 0
    }]


    
    _myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)


    _myGspreadFunc.updateCells(gspComparisonTableSheet, comparisonArray)

    # firstArray.insert(0, firstArrayFirstRow)
    # _myGspreadFunc.updateCells(gspEndingFirstTableSheet, firstArray)
    secondArray.insert(0, secondArrayFirstRow)
    _myGspreadFunc.updateCells(gspEndingSecondTableSheet, secondArray)

 
    with open(pathOfDecryptedFile, "w") as fileObj:
        fileObj.write('')

    # return _myPyFunc.addToPath(Path("C:\\"), ['hi', 'hellowasdf'])
    return os.environ.get('urlOfPublicGoogleSheet', 'https://www.google.com')[:-1] + '871892682'




# importing

# this works 
# import reconcileArrays.hiPackage.hiModule
# reconcileArrays.hiPackage.hiModule.hiFunction()

# this works 
# from reconcileArrays.hiPackage import hiModule
# hiModule.hiFunction()

# this works 
# from .hiPackage import hiModule
# hiModule.hiFunction()

# this works 
# from ..hiPackage import hiModule
# hiModule.hiFunction()