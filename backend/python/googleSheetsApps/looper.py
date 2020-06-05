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

	gspFirstTableSheet = gspSpreadsheet.worksheet('firstTable')
	gspSecondTableSheet = gspSpreadsheet.worksheet('secondTable')
	gspComparisonTableSheet = gspSpreadsheet.worksheet('comparisonTable')
	gspEndingSecondTableSheet = gspSpreadsheet.worksheet('endingSecondTable')

	firstArray = gspFirstTableSheet.get_all_values()
	secondArray = gspSecondTableSheet.get_all_values()
	firstArrayFirstRow = firstArray.pop(0)
	secondArrayFirstRow = secondArray.pop(0)

	matchingColumnTitle = ''

	for indexOfColumnIndexFirstArray, columnTitleFirstArray in enumerate(firstArrayFirstRow):
		for indexOfColumnIndexSecondArray, columnTitleSecondArray in enumerate(secondArrayFirstRow):
			if columnTitleFirstArray == columnTitleSecondArray:
				firstArrayColumnIndexToCompare = indexOfColumnIndexFirstArray
				secondArrayColumnIndexToCompare = indexOfColumnIndexSecondArray

	comparisonArray = [['firstTable'] + [''] * (len(firstArray[0])) + ['secondTable'] + [''] * (len(secondArray[0]) - 1)]
	comparisonArray.append(firstArrayFirstRow + [''] + secondArrayFirstRow)
	# p(comparisonArray)


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
		# p(comparisonArray)


	clearAndResizeParameters = [{
		'sheetObj': gspComparisonTableSheet,
		'resizeRows': 3,
		'startingRowIndexToClear': 0
	},
	{
		'sheetObj': gspEndingSecondTableSheet,
		'resizeRows': 2,
		'startingRowIndexToClear': 0
	}]


	
	_myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)
	_myGspreadFunc.updateCells(gspComparisonTableSheet, comparisonArray)

	secondArray.insert(0, secondArrayFirstRow)
	_myGspreadFunc.updateCells(gspEndingSecondTableSheet, secondArray)

	strToReturn = os.environ.get('urlOfKingGorillaGoogleSheetPublicStr')

	if not strToReturn:

		pathToConfigDataJSON = Path(pathToRepos, 'privateData', 'herokuGorilla', 'configData.json')
		jsonFileObj = open(pathToConfigDataJSON)
		strToReturn = json.load(jsonFileObj)['urlOfKingGorillaGoogleSheetPublicStr']
	
	strToReturn = strToReturn[:-1] + '871892682'

	return strToReturn
