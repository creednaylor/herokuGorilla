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

	# loopTableArrayFirstRow = loopTableArray.pop(0)
	# resultTableArrayFirstRow = resultTableArray.pop(0)

	for rowIndex, rowData in enumerate(loopTableArray):
		if rowIndex > 0:
			gspLoopTable.update_cell(rowIndex + 1, 2, random.randint(1,101))

	resultTableArray = gspResultTable.get_all_values()

	# _myGspreadFunc.updateCells(gspLoopTable, loopTableArray)

	# clearAndResizeParameters = [{
	# 	'sheetObj': gspComparisonTableSheet,
	# 	'resizeRows': 3,
	# 	'startingRowIndexToClear': 0
	# },
	# {
	# 	'sheetObj': gspEndingSecondTableSheet,
	# 	'resizeRows': 2,
	# 	'startingRowIndexToClear': 0
	# }]

	
	# _myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)
	

	# secondArray.insert(0, secondArrayFirstRow)
	# _myGspreadFunc.updateCells(gspEndingSecondTableSheet, secondArray)
# 
	strToReturn = os.environ.get('urlOfKingGorillaGoogleSheetPublicStr')

	if not strToReturn:

		pathToConfigDataJSON = Path(pathToRepos, 'privateData', 'herokuGorilla', 'configData.json')
		jsonFileObj = open(pathToConfigDataJSON)
		strToReturn = json.load(jsonFileObj)['urlOfKingGorillaGoogleSheetPublicStr']
	
	strToReturn = strToReturn[:-1] + '871892682'

	return strToReturn
