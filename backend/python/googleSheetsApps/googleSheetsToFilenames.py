from pathlib import Path
pathToThisPythonFile = Path(__file__).resolve()
import sys
pathToAppend = Path(pathToThisPythonFile.parents[1])
sys.path.append(str(pathToAppend))
import myPythonLibrary.myPyFunc as myPyFunc
import googleSheets.myGoogleSheetsLibrary.myGspreadFunc as myGspreadFunc

from pprint import pprint as p


def getFilenamesFromGoogleSheets(pathToDirectoryOfFiles, googleAccountUsername):
    
    accountLevelObj = myGspreadFunc.authorizeGspread(True, pathToThisPythonFile, googleAccountUsername=googleAccountUsername)
    spreadsheetLevelObj = accountLevelObj.open('Vendor Rebates')
    sheetLevelObj = spreadsheetLevelObj.worksheet('filenamesToWrite')
    filenamesToWriteArray = sheetLevelObj.get_all_values()

    for filename in filenamesToWriteArray[1:]:
        
        if filename[2] == '':
            filenameCurrentPath = str(Path(pathToDirectoryOfFiles, ' - '.join(filename[0:2]) + '.pdf'))
        else:
            filenameCurrentPath = str(Path(pathToDirectoryOfFiles, ' - '.join(filename[0:3]) + '.pdf'))
            
        newFilenamePath = str(Path(pathToDirectoryOfFiles, filename[0] + ' - ' + filename[1] + ' - ' + filename[3] + '.pdf')) 
        
        command = 'mv "' + filenameCurrentPath + '" "' + newFilenamePath + '"'
        p(command)
    
    
    

def mainFunction(arrayOfArguments):
    getFilenamesFromGoogleSheets(arrayOfArguments[1], arrayOfArguments[2])

if __name__ == '__main__':
    p(str(pathToThisPythonFile.name) + ' is not being imported. It is being run directly...')
    mainFunction(sys.argv)
else:
	p(str(pathToThisPythonFile.name) + ' is being imported. It is not being run directly...')