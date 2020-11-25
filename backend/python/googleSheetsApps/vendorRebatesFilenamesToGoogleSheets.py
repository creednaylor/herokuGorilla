from pathlib import Path
pathToThisPythonFile = Path(__file__).resolve()
import sys
pathToAppend = Path(pathToThisPythonFile.parents[1])
sys.path.append(str(pathToAppend))
import myPythonLibrary.myPyFunc as myPyFunc
import googleSheets.myGoogleSheetsLibrary.myGspreadFunc as myGspreadFunc

from pprint import pprint as p


def getFilenamesFromDisk(pathToDirectoryOfFilesForNameExtraction, googleAccountUsername):
    # p(Path(pathToDirectoryOfFilesForNameExtraction).parents[3])
    
    extractedFilenamesToDisplay = [['Check Date', 'Vendor', 'Amount']]
    
    for node in Path(pathToDirectoryOfFilesForNameExtraction).iterdir():
        arrayToAppend = node.stem.split(' - ')
        arrayToAppend[2] = float(arrayToAppend[2])
        extractedFilenamesToDisplay.append(arrayToAppend)
    
    accountLevelObj = myGspreadFunc.getSpreadsheetLevelObj(True, pathToThisPythonFile, googleAccountUsername=googleAccountUsername)
    spreadsheetLevelObj = accountLevelObj.open('Vendor Rebates')
    sheetLevelObj = spreadsheetLevelObj.worksheet('extractedFilenames')

    clearAndResizeParameters = [{
        'sheetObj': sheetLevelObj,
        'resizeRows': 2,
        'startingRowIndexToClear': 0,
        'resizeColumns': 1
    }]

    myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)
    myGspreadFunc.displayArray(sheetLevelObj, extractedFilenamesToDisplay)
    # p(extractedFilenamesToDisplay)
    sheetLevelObj.format('C:C', {'numberFormat': {'type': 'NUMBER', 'pattern': '#,###.00'}})
    myGspreadFunc.autoAlignColumnsInSpreadsheet(spreadsheetLevelObj)
    


def mainFunction(arrayOfArguments):
    getFilenamesFromDisk(arrayOfArguments[1], arrayOfArguments[2])

if __name__ == '__main__':
    p(str(pathToThisPythonFile.name) + ' is not being imported. It is being run directly...')
    mainFunction(sys.argv)
else:
    p(str(pathToThisPythonFile.name) + ' is being imported. It is not being run directly...')