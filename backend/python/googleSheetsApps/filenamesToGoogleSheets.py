from pathlib import Path
pathToThisPythonFile = Path(__file__).resolve()
import sys
pathToAppend = Path(pathToThisPythonFile.parents[1])
sys.path.append(str(pathToAppend))
import myPythonLibrary.myPyFunc as myPyFunc
import googleSheets.myGoogleSheetsLibrary.myGspreadFunc as myGspreadFunc

from pprint import pprint as p


def getFilenamesFromDisk(pathToDirectoryOfFiles, googleAccountUsername):
    # p(Path(pathToDirectoryOfFiles).parents[3])
    
    arrayOfPDFFiles = [['Check Date', 'Vendor', 'Repeat Number']]
    
    for node in Path(pathToDirectoryOfFiles).iterdir():
        if node.suffix == '.pdf':
            arrayOfPDFFiles.append(node.stem.split(' - '))
    
    accountLevelObj = myGspreadFunc.authorizeGspread(True, pathToThisPythonFile, googleAccountUsername=googleAccountUsername)
    spreadsheetLevelObj = accountLevelObj.open('Vendor Rebates')
    sheetLevelObj = spreadsheetLevelObj.worksheet('extractedFilenames')
    myGspreadFunc.updateCells(sheetLevelObj, arrayOfPDFFiles)




def mainFunction(arrayOfArguments):
    getFilenamesFromDisk(arrayOfArguments[1], arrayOfArguments[2])

if __name__ == '__main__':
    p(str(pathToThisPythonFile.name) + ' is not being imported. It is being run directly...')
    mainFunction(sys.argv)
else:
	p(str(pathToThisPythonFile.name) + ' is being imported. It is not being run directly...')