# clear resultArray sheet when opening google sheet...


from pathlib import Path
pathToThisPythonFile = Path(__file__).resolve()
import sys

from pprint import pprint as p
import gspread


def reconcileArraysFunction(runningOnProductionServerBoolean):

    # pathToRepos = _myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')

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
        
    gspSpreadsheet = gspObj.open('Gorilla - Public')
    gspFirstTableSheet = gspSpreadsheet.worksheet('firstTable')
    gspSecondTableSheet = gspSpreadsheet.worksheet('secondTable')
    gspComparisonTableSheet = gspSpreadsheet.worksheet('comparisonTable')
    gspEndingFirstTableSheet = gspSpreadsheet.worksheet('endingFirstTable')
    gspEndingSecondTableSheet = gspSpreadsheet.worksheet('endingSecondTable')

    firstArray = gspFirstTableSheet.get_all_values()
    secondArray = gspSecondTableSheet.get_all_values()
    firstArrayFirstRow = firstArray.pop(0)
    secondArrayFirstRow = secondArray.pop(0)

    firstArrayColumnIndexToCompare = 1
    secondArrayColumnIndexToCompare = 0

    comparisonArray = [firstArrayFirstRow + ['Side-By-Side'] + secondArrayFirstRow]

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

    # _myGspreadFunc.clearAndResizeSheets([gspComparisonTableSheet, gspEndingFirstTableSheet, gspEndingSecondTableSheet])
    _myGspreadFunc.updateCells(gspComparisonTableSheet, comparisonArray)

    firstArray.insert(0, firstArrayFirstRow)
    secondArray.insert(0, secondArrayFirstRow)

    _myGspreadFunc.updateCells(gspEndingFirstTableSheet, firstArray)
    _myGspreadFunc.updateCells(gspEndingSecondTableSheet, secondArray)

 
    with open(pathOfDecryptedFile, "w") as fileObj:
        fileObj.write('')

    return _myPyFunc.addToPath(Path("C:\\"), ['hi', 'hellowasdf'])







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