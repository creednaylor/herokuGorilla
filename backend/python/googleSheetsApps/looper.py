from google_auth_oauthlib.flow import InstalledAppFlow
import json
import os
from pathlib import Path
from pprint import pprint as p
import sys

import gspread

import random

pathToThisPythonFile = Path(__file__).resolve()

if os.environ.get('runningOnProductionServer') == 'true':
	from ..myPythonLibrary import _myPyFunc
	from ..googleSheets.myGoogleSheetsLibrary import _myGspreadFunc
else:
	sys.path.append(str(pathToThisPythonFile.parents[1]))
	from myPythonLibrary import _myPyFunc
	from googleSheets.myGoogleSheetsLibrary import _myGspreadFunc



def looperFunction(oAuthMode, googleSheetTitle):

	pathToRepos = _myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
	pathToThisProjectRoot = pathToThisPythonFile.parents[3]
	gspObj = _myGspreadFunc.authorizeGspread(oAuthMode, pathToThisProjectRoot)

	gspSpreadsheet = gspObj.open(googleSheetTitle)
	gspLoopTable = gspSpreadsheet.worksheet('loopTable')
	gspCalculationTable = gspSpreadsheet.worksheet('calculationTable')
	gspResultTable = gspSpreadsheet.worksheet('resultTable')
	
	clearAndResizeParameters = [{
		'sheetObj': gspResultTable,
		'startingRowIndexToClear': 0,
		'resizeColumns': 1
	}]

	_myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)


	loopTableArray = gspLoopTable.get_all_values()


	if oAuthMode:
		pass
	else:
		for rowIndex, rowData in enumerate(loopTableArray):
			if rowIndex > 0:
				_myGspreadFunc.updateCell(gspLoopTable, rowIndex, 1, random.randint(1,101))
				_myGspreadFunc.updateCell(gspLoopTable, rowIndex, 2, random.randint(1,101))

		loopTableArray = gspLoopTable.get_all_values()


		calculationTableArray = gspCalculationTable.get_all_values()
		resultTableArray = [[loopTableArray[0][0], calculationTableArray[0][2]]]

		for rowIndex, rowData in enumerate(loopTableArray):

			if rowIndex > 0:
				_myGspreadFunc.updateCell(gspCalculationTable, 1, 0, rowData[1])
				_myGspreadFunc.updateCell(gspCalculationTable, 1, 1, rowData[2])
				calculationTableArray = gspCalculationTable.get_all_values()

				resultTableArray.append([loopTableArray[rowIndex][0], calculationTableArray[1][2]])


	_myGspreadFunc.updateCells(gspResultTable, resultTableArray)


	strToReturn = os.environ.get('urlOfKingGorillaGoogleSheetPublicStr')

	if not strToReturn:

		pathToConfigDataJSON = Path(pathToRepos, 'privateData', 'herokuGorilla', 'configData.json')
		jsonFileObj = open(pathToConfigDataJSON)
		strToReturn = json.load(jsonFileObj)['urlOfKingGorillaGoogleSheetPublicStr']
	
	strToReturn = strToReturn[:-1] + '871892682'

	return strToReturn
