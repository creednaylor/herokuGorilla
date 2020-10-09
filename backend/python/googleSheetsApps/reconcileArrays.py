#rename to match
#add "Matched" and "Not Matched"

from google_auth_oauthlib.flow import InstalledAppFlow
import json
import os
from pathlib import Path
from pprint import pprint as p
import sys

import gspread



pathToThisPythonFile = Path(__file__).resolve()

if os.environ.get('runningOnProductionServer') == 'true':
	from ..myPythonLibrary import _myPyFunc
	from ..googleSheets.myGoogleSheetsLibrary import _myGspreadFunc
else:
	sys.path.append(str(pathToThisPythonFile.parents[1]))
	from myPythonLibrary import _myPyFunc
	from googleSheets.myGoogleSheetsLibrary import _myGspreadFunc


def columnsMatch(firstArrayCurrentRow, secondArrayCurrentRow, firstArrayColumnsToMatch, secondArrayColumnsToMatch):

	for columnIndex in range(0, len(firstArrayColumnsToMatch)):

		if firstArrayCurrentRow[firstArrayColumnsToMatch[columnIndex]] != secondArrayCurrentRow[secondArrayColumnsToMatch[columnIndex]]:
			return False
	
	return True



def reconcileArrays(oAuthMode, googleSheetTitle, firstArrayColumnsToMatch=None, secondArrayColumnsToMatch=None, googleAccountUsername=None):


	pathToRepos = _myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
	pathToThisProjectRoot = pathToThisPythonFile.parents[3]

	gspObj = _myGspreadFunc.getSpreadsheetLevelObj(oAuthMode, pathToThisProjectRoot, googleAccountUsername=googleAccountUsername)

	gspSpreadsheet = gspObj.open(googleSheetTitle)

	firstTableName = 'First Table'
	secondTableName = 'Second Table'
	matchedTableName = 'Matched'
	didNotMatchTableName = 'Did Not Match'

	gspFirstTable = gspSpreadsheet.worksheet(firstTableName)
	gspSecondTable = gspSpreadsheet.worksheet(secondTableName)
	gspMatchedTable = gspSpreadsheet.worksheet(matchedTableName)
	gspDidNotMatchTable = gspSpreadsheet.worksheet(didNotMatchTableName)

	firstArray = gspFirstTable.get_all_values()
	secondArray = gspSecondTable.get_all_values()

	firstArrayFirstRow = firstArray.pop(0)
	secondArrayFirstRow = secondArray.pop(0)

	matchedArray = [[firstTableName] + [''] * (len(firstArray[0])) + [secondTableName] + [''] * (len(secondArray[0]) - 1)]
	matchedArray.append(firstArrayFirstRow + [''] + secondArrayFirstRow)
	# # p(matchedArray)


	if not firstArrayColumnsToMatch:
		firstArrayColumnsToMatch = [0]

	if not secondArrayColumnsToMatch:
		secondArrayColumnsToMatch = [0]


	while firstArray:

		firstArrayCurrentRow = firstArray.pop(0)
		tempMatchedData = []

		for secondArrayCurrentRowIndex in reversed(range(len(secondArray))):
			
			if columnsMatch(firstArrayCurrentRow, secondArray[secondArrayCurrentRowIndex], firstArrayColumnsToMatch, secondArrayColumnsToMatch):
				
				secondArrayCurrentRow = secondArray.pop(secondArrayCurrentRowIndex)

				# if tempMatchedData:
				# 	tempMatchedDataCurrentLength = len(tempMatchedData)
				# 	tempMatchedData.append([str(tempMatchedData[0][firstArrayColumnsToMatch[0]]) + ': matched ' + str(tempMatchedDataCurrentLength) + ' additional row(s)'] + [''] * (len(firstArrayCurrentRow)) + secondArrayCurrentRow)
				# else:
				
				tempMatchedData.append(firstArrayCurrentRow + ['Matched'] + secondArrayCurrentRow)


		if tempMatchedData:
			matchedArray.extend(tempMatchedData)
		else:
			matchedArray.append(firstArrayCurrentRow + ['Not Matched'])


	clearAndResizeParameters = [{
		'sheetObj': gspMatchedTable,
		'resizeRows': 3,
		'startingRowIndexToClear': 0,
		'resizeColumns': 1
	},
	{
		'sheetObj': gspDidNotMatchTable,
		'resizeRows': 2,
		'startingRowIndexToClear': 0,
		'resizeColumns': 1
	}]


	_myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)
	_myGspreadFunc.displayArray(gspMatchedTable, matchedArray)

	secondArray.insert(0, secondArrayFirstRow)
	_myGspreadFunc.displayArray(gspDidNotMatchTable, secondArray)


	_myGspreadFunc.autoResizeColumnsOnSheet(gspSpreadsheet, matchedTableName)
	_myGspreadFunc.autoResizeColumnsOnSheet(gspSpreadsheet, didNotMatchTableName)


	# strToReturn = os.environ.get('urlOfKingGorillaGoogleSheetPublicStr')

	# if not strToReturn:

	# 	pathToConfigDataJSON = Path(pathToRepos, 'privateData', 'herokuGorilla', 'configData.json')
	# 	jsonFileObj = open(pathToConfigDataJSON)
	# 	strToReturn = json.load(jsonFileObj)['urlOfKingGorillaGoogleSheetPublicStr']

	# strToReturn = strToReturn[:-1] + '871892682'

	# return strToReturn

