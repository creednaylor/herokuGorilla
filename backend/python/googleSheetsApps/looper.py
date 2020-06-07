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
		'startingRowIndexToClear': 0
	}]

	_myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)


	loopTableArray = gspLoopTable.get_all_values()

	for rowIndex, rowData in enumerate(loopTableArray):
		if rowIndex > 0:
			gspLoopTable.update_cell(rowIndex + 1, 2, random.randint(1,101))
			gspLoopTable.update_cell(rowIndex + 1, 3, random.randint(1,101))

	loopTableArray = gspLoopTable.get_all_values()

	for rowIndex, rowData in enumerate(loopTableArray):

		if rowIndex == 0:
			calculationTableArray = gspCalculationTable.get_all_values()

			gspResultTable.update_cell(rowIndex + 1, 0 + 1, loopTableArray[rowIndex][0])
			gspResultTable.update_cell(rowIndex + 1, 1 + 1, calculationTableArray[rowIndex][2])
		
		else:
			gspCalculationTable.update_cell(1 + 1, 0 + 1, rowData[1])
			gspCalculationTable.update_cell(1 + 1, 1 + 1, rowData[2])
			calculationTableArray = gspCalculationTable.get_all_values()

			gspResultTable.update_cell(rowIndex + 1, 0 + 1, loopTableArray[rowIndex][0])
			gspResultTable.update_cell(rowIndex + 1, 1 + 1, calculationTableArray[1][2])



	strToReturn = os.environ.get('urlOfKingGorillaGoogleSheetPublicStr')

	if not strToReturn:

		pathToConfigDataJSON = Path(pathToRepos, 'privateData', 'herokuGorilla', 'configData.json')
		jsonFileObj = open(pathToConfigDataJSON)
		strToReturn = json.load(jsonFileObj)['urlOfKingGorillaGoogleSheetPublicStr']
	
	strToReturn = strToReturn[:-1] + '871892682'

	return strToReturn
