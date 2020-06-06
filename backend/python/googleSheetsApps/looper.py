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
	runningOnProductionServer = True
else:
	sys.path.append(str(pathToThisPythonFile.parents[1]))
	from myPythonLibrary import _myPyFunc
	from googleSheets.myGoogleSheetsLibrary import _myGspreadFunc
	runningOnProductionServer = False



def reconcileArraysFunction(oAuthMode, googleSheetTitle):

	pathToRepos = _myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
	pathToThisProjectRoot = pathToThisPythonFile.parents[3]
	gspObj = _myGspreadFunc.authorizeGspread(oAuthMode, pathToThisProjectRoot)

	gspSpreadsheet = gspObj.open(googleSheetTitle)
	gspLoopTable = gspSpreadsheet.worksheet('loopTable')
	gspResultTable = gspSpreadsheet.worksheet('resultTable')
	
	loopTableArray = gspLoopTable.get_all_values()


	for rowIndex, rowData in enumerate(loopTableArray):
		if rowIndex > 0:
			gspLoopTable.update_cell(rowIndex + 1, 3, random.randint(1,101))

	loopTableArray = gspLoopTable.get_all_values()

	clearAndResizeParameters = [{
		'sheetObj': gspResultTable,
		'resizeRows': 2,
		'startingRowIndexToClear': 0
	}]

	_myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)



	resultTableForUpdateArray = []

	for rowIndex, rowData in enumerate(loopTableArray):
		if rowIndex > 0:
			resultTableForUpdateArray.append([int(loopTableArray[rowIndex][0]), int(loopTableArray[rowIndex][3])])
		else:
			resultTableForUpdateArray.append([loopTableArray[rowIndex][0], loopTableArray[rowIndex][3]])
		

	_myGspreadFunc.updateCells(gspResultTable, resultTableForUpdateArray)



# 
	strToReturn = os.environ.get('urlOfKingGorillaGoogleSheetPublicStr')

	if not strToReturn:

		pathToConfigDataJSON = Path(pathToRepos, 'privateData', 'herokuGorilla', 'configData.json')
		jsonFileObj = open(pathToConfigDataJSON)
		strToReturn = json.load(jsonFileObj)['urlOfKingGorillaGoogleSheetPublicStr']
	
	strToReturn = strToReturn[:-1] + '871892682'

	return strToReturn
