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


def getMatchedRow(secondArray, firstArrayCurrentRow, firstArrayColumnsToMatch, secondArrayColumnsToMatch):

	tempMatchedData = []

	for secondArrayRowIndex in reversed(range(len(secondArray))):
			
			if columnsMatch(firstArrayCurrentRow, secondArray[secondArrayRowIndex], firstArrayColumnsToMatch, secondArrayColumnsToMatch):
				
				secondArrayCurrentRow = secondArray.pop(secondArrayRowIndex)

				if tempMatchedData:
					tempMatchedDataCurrentLength = len(tempMatchedData)
					tempMatchedData.append([str(tempMatchedData[0][firstArrayColumnsToMatch[0]]) + ': matched ' + str(tempMatchedDataCurrentLength) + ' additional row(s)'] + [''] * (len(firstArrayCurrentRow)) + secondArrayCurrentRow)
				else:
					tempMatchedData.append(firstArrayCurrentRow + [''] + secondArrayCurrentRow)

	return tempMatchedData


def reconcileArrays(oAuthMode, googleSheetTitle, googleAccountUsername=None):


	pathToRepos = _myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
	pathBelowRepos = pathToThisPythonFile

	gspObj = _myGspreadFunc.authorizeGspread(oAuthMode, pathBelowRepos, googleAccountUsername=googleAccountUsername)

	gspSpreadsheet = gspObj.open(googleSheetTitle)

	firstTableName = 'First Table'
	secondTableName = 'Second Table'
	matchedTableName = 'Matched'
	didNotMatchTableName = 'Did Not Match'

	gspFirstTable = gspSpreadsheet.worksheet(firstTableName)
	gspSecondTable = gspSpreadsheet.worksheet(secondTableName)
	gspMatchedTable = gspSpreadsheet.worksheet(matchedTableName)
	gspDidNotMatchTable = gspSpreadsheet.worksheet(didNotMatchTableName)
	gspDailyDepositsTable = gspSpreadsheet.worksheet('Daily Deposits')

	firstArray = gspFirstTable.get_all_values()
	secondArray = gspSecondTable.get_all_values()
	dailyDepositsArray = gspDailyDepositsTable.get_all_values()

	firstArray[0].append('Amount+-')
	firstArray[0].append('Bank Amount')

	for firstArrayRowIndex in range(1, len(firstArray)):
		amount = float(firstArray[firstArrayRowIndex][5].replace(',', ''))

		if firstArray[firstArrayRowIndex][11] == 'Decrease Adjustment' or 'Transfer To' in firstArray[firstArrayRowIndex][14]:
			amount = -amount

		firstArray[firstArrayRowIndex].append(amount)
		firstArray[firstArrayRowIndex].append(amount)


	secondArray[0].append('Amount+-')

	for secondArrayRowIndex in range(1, len(secondArray)):
		if secondArray[secondArrayRowIndex][5] == '':
			debitAmount = 0
		else:
			debitAmount = float(secondArray[secondArrayRowIndex][5].replace('$', '').replace(',', ''))

		if secondArray[secondArrayRowIndex][6] == '':
			creditAmount = 0
		else:
			creditAmount = float(secondArray[secondArrayRowIndex][6].replace('$', '').replace(',', ''))
			
		secondArray[secondArrayRowIndex].append(creditAmount - debitAmount)

	dailyDepositsArray[0].append('Date')
	dailyDepositsArray[0].append('BisTrack Amount')
	dailyDepositsArray[0].append('Bank Amount')

	for dailyDepositsRowIndex in range(1, len(dailyDepositsArray)):

		dailyDepositsCurrentRow = dailyDepositsArray[dailyDepositsRowIndex]

		if dailyDepositsCurrentRow[0] != '':
			currentDate = dailyDepositsCurrentRow[0]
		dailyDepositsCurrentRow.append(currentDate)

		if dailyDepositsCurrentRow[6] == '':
			dailyDepositsCurrentRow.append(0)
		else:
			if dailyDepositsCurrentRow[2] == 'Debit':
				dailyDepositsCurrentRow.append(-float(dailyDepositsCurrentRow[6].replace(',', '')))
			else:
				dailyDepositsCurrentRow.append(float(dailyDepositsCurrentRow[6].replace(',', '')))

		if dailyDepositsCurrentRow[2] == 'Debit':
			dailyDepositsCurrentRow.append(-float(dailyDepositsCurrentRow[4].replace(',', '')))
		else:
			dailyDepositsCurrentRow.append(float(dailyDepositsCurrentRow[4].replace(',', '')))


	firstArrayFirstRow = firstArray.pop(0)
	secondArrayFirstRow = secondArray.pop(0)

	matchedArray = [[firstTableName] + [''] * (len(firstArray[0])) + [secondTableName] + [''] * (len(secondArray[0]) - 1)]
	matchedArray.append(firstArrayFirstRow + [''] + secondArrayFirstRow)



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
		tempMatchedData = getMatchedRow(secondArray, firstArrayCurrentRow, firstArrayColumnsToMatch, secondArrayColumnsToMatch)

		if tempMatchedData:
			matchedArray.extend(tempMatchedData)
		else:

			matchedDailyDepositsAmount = None

			for dailyDepositsArrayRowIndex in reversed(range(len(dailyDepositsArray))):

				if columnsMatch(firstArrayCurrentRow, dailyDepositsArray[dailyDepositsArrayRowIndex], firstArrayColumnsToMatch, [11]):

					dailyDepositsCurrentRow = dailyDepositsArray.pop(dailyDepositsArrayRowIndex)

					if not matchedDailyDepositsAmount:
						# p(dailyDepositsCurrentRow[12])
						matchedDailyDepositsAmount = dailyDepositsCurrentRow[12]
			
			if matchedDailyDepositsAmount:
				
				updatedFirstArrayCurrentRow = firstArrayCurrentRow[0:len(firstArrayCurrentRow) - 1] + [matchedDailyDepositsAmount]

				tempMatchedDailyDeposits = getMatchedRow(secondArray, updatedFirstArrayCurrentRow, [17], secondArrayColumnsToMatch)
				# p(tempMatchedDailyDeposits)

				if tempMatchedDailyDeposits:
					matchedArray.extend(tempMatchedDailyDeposits)
				else:
					matchedArray.append(updatedFirstArrayCurrentRow + ['Match found on Daily Deposits but not on bank transactions'])
			
			else:
				matchedArray.append(firstArrayCurrentRow + ['No match found'])

	# p(matchedArray[0:4])
	for matchedArrayRowIndex in range(2, len(matchedArray)):
		if matchedArray[matchedArrayRowIndex][18] != 'No match found':
			# p(matchedArray[matchedArrayRowIndex][18]
			matchedArray[matchedArrayRowIndex][18] = float(matchedArray[matchedArrayRowIndex][16] or 0) - float(matchedArray[matchedArrayRowIndex][17] or 0)


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

