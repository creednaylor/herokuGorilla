#rename to match

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



def reconcileArraysFunction(oAuthMode, googleSheetTitle, loadSavedCredentials=True, firstArrayColumnsToMatch=None, secondArrayColumnsToMatch=None):


	pathToRepos = _myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
	pathToThisProjectRoot = pathToThisPythonFile.parents[3]

	gspObj = _myGspreadFunc.authorizeGspread(oAuthMode, pathToThisProjectRoot, loadSavedCredentials)

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
	firstArray[0].append('Amount+-')
	secondArray[0].append('Amount+-')

	for firstArrayRowIndex in range(1, len(firstArray)):
		amount = float(firstArray[firstArrayRowIndex][5].replace(',', ''))

		if firstArray[firstArrayRowIndex][11] == 'Decrease Adjustment' or 'Transfer To' in firstArray[firstArrayRowIndex][14]:
			amount = -amount

		firstArray[firstArrayRowIndex].append(amount)


	for secondArrayRowIndex in range(1, len(secondArray)):
		if secondArray[secondArrayRowIndex][5] == '':
			secondArray[secondArrayRowIndex][5] = 0
		else:
			secondArray[secondArrayRowIndex][5] = float(secondArray[secondArrayRowIndex][5].replace('$', '').replace(',', ''))

		if secondArray[secondArrayRowIndex][6] == '':
			secondArray[secondArrayRowIndex][6] = 0
		else:
			secondArray[secondArrayRowIndex][6] = float(secondArray[secondArrayRowIndex][6].replace('$', '').replace(',', ''))
			
		debitAmount = secondArray[secondArrayRowIndex][5]
		creditAmount = secondArray[secondArrayRowIndex][6]
		secondArray[secondArrayRowIndex].append(creditAmount - debitAmount)



	firstArrayFirstRow = firstArray.pop(0)
	secondArrayFirstRow = secondArray.pop(0)

	matchedArray = [[firstTableName] + [''] * (len(firstArray[0])) + [secondTableName] + [''] * (len(secondArray[0]) - 1)]
	matchedArray.append(firstArrayFirstRow + [''] + secondArrayFirstRow)
	# p(matchedArray)


	if not firstArrayColumnsToMatch and not secondArrayColumnsToMatch:
		if oAuthMode:

			for indexOfColumnIndexFirstArray, columnTitleFirstArray in enumerate(firstArrayFirstRow):
				for indexOfColumnIndexSecondArray, columnTitleSecondArray in enumerate(secondArrayFirstRow):
					if columnTitleFirstArray == columnTitleSecondArray:
						firstArrayColumnsToMatch = [indexOfColumnIndexFirstArray]
						secondArrayColumnsToMatch = [indexOfColumnIndexSecondArray]

		else:
			firstArrayColumnsToMatch = [0]  # [0, 1, 2]
			secondArrayColumnsToMatch = [1]  # [0, 1, 2]


	while firstArray:

		firstArrayCurrentRow = firstArray.pop(0)
		tempMatchedData = []

		for secondArrayCurrentRowIndex in reversed(range(len(secondArray))):
			
			if columnsMatch(firstArrayCurrentRow, secondArray[secondArrayCurrentRowIndex], firstArrayColumnsToMatch, secondArrayColumnsToMatch):
				
				secondArrayCurrentRow = secondArray.pop(secondArrayCurrentRowIndex)

				if tempMatchedData:
					tempMatchedDataCurrentLength = len(tempMatchedData)
					tempMatchedData.append([str(tempMatchedData[0][firstArrayColumnsToMatch[0]]) + ': matched ' + str(tempMatchedDataCurrentLength) + ' additional row(s)'] + [''] * (len(firstArrayCurrentRow)) + secondArrayCurrentRow)
				else:
					tempMatchedData.append(firstArrayCurrentRow + [''] + secondArrayCurrentRow)



		# while secondArrayRowIndexCount in range(0, len(secondArray)):

		# 	if columnsMatch(firstArrayCurrentRow, secondArray[secondArrayRowIndexCount], firstArrayColumnsToMatch, secondArrayColumnsToMatch):
				
		# 		secondArrayCurrentRow = secondArray.pop(0)

		# 		if tempMatchedData:
		# 			tempMatchedData.append([''] * (len(firstArrayCurrentRow) + 1) + secondArrayCurrentRow)
		# 		else:
		# 			tempMatchedData.append(firstArrayCurrentRow + [''] + secondArrayCurrentRow)

		# 	secondArrayRowIndexCount = secondArrayRowIndexCount + 1


		if tempMatchedData:
			matchedArray.extend(tempMatchedData)
		else:
			matchedArray.append(firstArrayCurrentRow + [''])


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
	_myGspreadFunc.updateCells(gspMatchedTable, matchedArray)

	secondArray.insert(0, secondArrayFirstRow)
	_myGspreadFunc.updateCells(gspDidNotMatchTable, secondArray)


	_myGspreadFunc.autoResizeColumnsOnSheet(gspSpreadsheet, matchedTableName)
	_myGspreadFunc.autoResizeColumnsOnSheet(gspSpreadsheet, didNotMatchTableName)


	strToReturn = os.environ.get('urlOfKingGorillaGoogleSheetPublicStr')

	if not strToReturn:

		pathToConfigDataJSON = Path(pathToRepos, 'privateData', 'herokuGorilla', 'configData.json')
		jsonFileObj = open(pathToConfigDataJSON)
		strToReturn = json.load(jsonFileObj)['urlOfKingGorillaGoogleSheetPublicStr']

	strToReturn = strToReturn[:-1] + '871892682'

	return strToReturn

