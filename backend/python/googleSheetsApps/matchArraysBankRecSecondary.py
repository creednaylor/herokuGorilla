from google_auth_oauthlib.flow import InstalledAppFlow
import json
import os
from pathlib import Path
from pprint import pprint as p
import sys

import gspread

pathToThisPythonFile = Path(__file__).resolve()

if os.environ.get('runningOnProductionServer') == 'true':
	from ..myPythonLibrary import myPyFunc
	from ..googleSheets.myGoogleSheetsLibrary import myGspreadFunc
else:
	sys.path.append(str(pathToThisPythonFile.parents[1]))
	from myPythonLibrary import myPyFunc
	from googleSheets.myGoogleSheetsLibrary import myGspreadFunc


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


	# pathToRepos = myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
	pathBelowRepos = pathToThisPythonFile
	spreadsheetLevelObj = myGspreadFunc.authorizeGspread(oAuthMode, pathBelowRepos, googleAccountUsername=googleAccountUsername).open(googleSheetTitle)

	firstTableName = 'First Table'
	secondTableName = 'Second Table'
	matchedTableName = 'Matched'
	didNotMatchTableName = 'Did Not Match'

	firstArray = spreadsheetLevelObj.worksheet(firstTableName).get_all_values()
	secondArray = spreadsheetLevelObj.worksheet(secondTableName).get_all_values()
	dailyDepositsArray = spreadsheetLevelObj.worksheet('Daily Deposits').get_all_values()

	firstArrayAmountColumnIndex = 5
	firstArrayTypeColumnIndex = 11
	firstArrayPaidToColumnIndex = 14

	def transformFirstArray(currentRowIndex, currentRow):
		if currentRowIndex == 0:
			currentRow.append('Amount+-')
			currentRow.append('Bank Amount')
		else:
			amount = float(currentRow[firstArrayAmountColumnIndex].replace(',', ''))

			if currentRow[firstArrayTypeColumnIndex] == 'Decrease Adjustment' or 'Transfer To' in currentRow[firstArrayPaidToColumnIndex]:
				amount = -amount

			currentRow.append(amount)
			currentRow.append(amount)


	firstArray = myPyFunc.repeatActionOnArray(firstArray, transformFirstArray)

	def transformSecondArray(currentRowIndex, currentRow):
		if currentRowIndex == 0:
			currentRow.append('Amount+-')
		else:
			if currentRow[5] == '':
				debitAmount = 0
			else:
				debitAmount = float(currentRow[5].replace('$', '').replace(',', ''))

			if currentRow[6] == '':
				creditAmount = 0
			else:
				creditAmount = float(currentRow[6].replace('$', '').replace(',', ''))
				
			currentRow.append(creditAmount - debitAmount)

	secondArray = myPyFunc.repeatActionOnArray(secondArray, transformSecondArray)


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
		'sheetObj': spreadsheetLevelObj.worksheet(matchedTableName),
		'resizeRows': 3,
		'startingRowIndexToClear': 0,
		'resizeColumns': 1
	},
	{
		'sheetObj': spreadsheetLevelObj.worksheet(didNotMatchTableName),
		'resizeRows': 2,
		'startingRowIndexToClear': 0,
		'resizeColumns': 1
	}]


	myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)
	myGspreadFunc.updateCells(spreadsheetLevelObj.worksheet(matchedTableName), matchedArray)

	secondArray.insert(0, secondArrayFirstRow)
	myGspreadFunc.updateCells(spreadsheetLevelObj.worksheet(didNotMatchTableName), secondArray)


	myGspreadFunc.autoResizeColumnsInSpreadsheet(spreadsheetLevelObj)


	# strToReturn = os.environ.get('urlOfKingGorillaGoogleSheetPublicStr')

	# if not strToReturn:

	# 	pathToConfigDataJSON = Path(pathToRepos, 'privateData', 'herokuGorilla', 'configData.json')
	# 	jsonFileObj = open(pathToConfigDataJSON)
	# 	strToReturn = json.load(jsonFileObj)['urlOfKingGorillaGoogleSheetPublicStr']

	# strToReturn = strToReturn[:-1] + '871892682'

	# return strToReturn



def mainFunction(arrayOfArguments):
    reconcileArrays(True, arrayOfArguments[1], googleAccountUsername=arrayOfArguments[2])


if __name__ == '__main__':
    p(str(pathToThisPythonFile.name) + ' is not being imported. It is being run directly...')
    mainFunction(sys.argv)
else:
	p(str(pathToThisPythonFile.name) + ' is being imported. It is not being run directly...')