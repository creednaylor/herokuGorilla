from pathlib import Path
pathToThisPythonFile = Path(__file__).resolve()
import sys

from ..python.myPythonLibrary import _myPyFunc
from ..python.googleSheets.myGoogleSheetsLibrary import _myGoogleSheetsFunc
from ..python.googleSheets.myGoogleSheetsLibrary import _myGspreadFunc


from pprint import pprint as p
import gspread


def reconcileArraysFunction(runningOnDevelopmentServerBoolean):

    if runningOnDevelopmentServerBoolean:
        # p('********************Running on development server****************')

        pathToRepos = _myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
        arrayOfPartsToAddToPath = ['privateData', 'python', 'googleCredentials', 'usingServiceAccount', 'jsonWithAPIKey.json']
        pathToCredentialsFileServiceAccount = _myPyFunc.addToPath(pathToRepos, arrayOfPartsToAddToPath)
        # gspObj = gspread.service_account(filename=pathToCredentialsFileServiceAccount)
    else:
        pass
        # p('********************Not running on development server****************')
    


    # gspSpreadsheet = gspObj.open("Reconcile Arrays")
    # gspFirstArraySheet = gspSpreadsheet.worksheet('firstArray')
    # gspSecondArraySheet = gspSpreadsheet.worksheet('secondArray')
    # gspComparisonSheet = gspSpreadsheet.worksheet('comparison')
    # gspEndingFirstArraySheet = gspSpreadsheet.worksheet('endingFirstArray')
    # gspEndingSecondArraySheet = gspSpreadsheet.worksheet('endingSecondArray')

    # firstArray = gspFirstArraySheet.get_all_values()
    # secondArray = gspSecondArraySheet.get_all_values()

    # firstArrayColumnIndexToCompare = 8
    # secondArrayColumnIndexToCompare = 5

    # comparisonArray = [[''] * len(firstArray[0]) + ['Side-By-Side'] + [''] * len(secondArray[0])]

    # # p(firstArray[0:5])
    # # p(secondArray[14])

    # while firstArray:

    #     currentFirstArrayRow = firstArray.pop(0)
    #     # p(currentFirstArrayRow)
    #     rowToAppend = currentFirstArrayRow + ['']

    #     for secondArrayRowCount, currentSecondArrayRow in enumerate(secondArray):

    #         # p(currentSecondArrayRow)

    #         if currentFirstArrayRow[firstArrayColumnIndexToCompare] == currentSecondArrayRow[secondArrayColumnIndexToCompare]:

    #             secondArrayRowToAppend = secondArray.pop(secondArrayRowCount)
    #             rowToAppend = rowToAppend + currentSecondArrayRow

    #     comparisonArray.append(rowToAppend)


    # # p(comparisonArray[0:2])

    # _myGspreadFunc.clearAndResizeSheets([gspComparisonSheet, gspEndingFirstArraySheet, gspEndingSecondArraySheet])
    # _myGspreadFunc.updateCells(gspComparisonSheet, comparisonArray)
    # _myGspreadFunc.updateCells(gspEndingFirstArraySheet, firstArray)
    # _myGspreadFunc.updateCells(gspEndingSecondArraySheet, secondArray)

    return _myPyFunc.addToPath(Path("C:\\"), ['hi', 'hellow'])






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