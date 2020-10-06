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

def getMatchStatus(firstArrayColumnsToMatch):

	matchStatus = 'Matched on '

	for column in firstArrayColumnsToMatch:
		if matchStatus == 'Matched on ':
			matchStatus = matchStatus + str(column)
		else:
			matchStatus = matchStatus + ' and ' + str(column)

	return matchStatus

def getMatchedRows(secondArray, firstArrayCurrentRow, firstArrayColumnsToMatch, secondArrayColumnsToMatch):

	tempMatchedData = []

	for secondArrayRowIndex in reversed(range(len(secondArray))):
			
			if columnsMatch(firstArrayCurrentRow, secondArray[secondArrayRowIndex], firstArrayColumnsToMatch, secondArrayColumnsToMatch):
				
				secondArrayCurrentRow = secondArray.pop(secondArrayRowIndex)

				if tempMatchedData:
					tempMatchedDataCurrentLength = len(tempMatchedData)
					tempMatchedData.append([str(tempMatchedData[0][firstArrayColumnsToMatch[0]]) + ': matched ' + str(tempMatchedDataCurrentLength) + ' additional row(s)'] + [''] * (len(firstArrayCurrentRow)) + secondArrayCurrentRow)
				else:
					tempMatchedData.append(firstArrayCurrentRow + [getMatchStatus(firstArrayColumnsToMatch)] + secondArrayCurrentRow)

	return tempMatchedData


def reconcileArrays(oAuthMode, googleSheetTitle, googleAccountUsername=None):


	# pathToRepos = myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
	pathBelowRepos = pathToThisPythonFile
	spreadsheetLevelObj = myGspreadFunc.authorizeGspread(oAuthMode, pathBelowRepos, googleAccountUsername=googleAccountUsername).open(googleSheetTitle)

	firstTableName = 'First Table'
	secondTableName = 'Second Table'
	matchedTableName = 'Matched'
	didNotMatchTableName = 'Did Not Match'
	dailyDepositsTableName = 'Daily Deposits'

	firstArray = spreadsheetLevelObj.worksheet(firstTableName).get_all_values()
	secondArray = spreadsheetLevelObj.worksheet(secondTableName).get_all_values()
	dailyDepositsArray = spreadsheetLevelObj.worksheet(dailyDepositsTableName).get_all_values()
	amountColumnName = 'Amount+-'
	dateStrColumnName = 'Date String'

	def transformFirstArray(currentRowIndex, currentRow):
		if currentRowIndex == 0:
			currentRow.append(amountColumnName)
			currentRow.append('Bank Amount')
			currentRow.append(dateStrColumnName)
		else:
			currentAmount = currentRow[5]
			currentType = currentRow[11]
			currentPaidTo = currentRow[14]
			currentDate = currentRow[1]

			amount = myPyFunc.strToFloat(currentAmount)

			if 'Decrease Adjustment' == currentType or 'Transfer To' in currentPaidTo:
				amount = -amount

			currentRow.append(amount)
			currentRow.append(amount)
			currentRow.append(myPyFunc.dateStrToStr(currentDate))


	firstArray = myPyFunc.repeatActionOnArray(firstArray, transformFirstArray)
	# p(firstArray[0:2])

	def transformSecondArray(currentRowIndex, currentRow):
		if currentRowIndex == 0:
			currentRow.append(amountColumnName)
			currentRow.append(dateStrColumnName)
		else:
			currentDebitAmount = currentRow[5]
			currentCreditAmount = currentRow[6]
			currentDate = currentRow[0]

			currentRow.append(myPyFunc.strToFloat(currentCreditAmount) - myPyFunc.strToFloat(currentDebitAmount))
			currentRow.append(myPyFunc.dateStrToStr(currentDate))

	secondArray = myPyFunc.repeatActionOnArray(secondArray, transformSecondArray)


	for dailyDepositsRowIndex in range(1, len(dailyDepositsArray)):
		dailyDepositsCurrentRow = dailyDepositsArray[dailyDepositsRowIndex]
		dailyDepositsDateColumnIndex = 0

		if dailyDepositsCurrentRow[dailyDepositsDateColumnIndex] != '':
			currentDate = dailyDepositsCurrentRow[dailyDepositsDateColumnIndex]
		dailyDepositsCurrentRow.append(currentDate)


	def transformDailyDepositsArray(currentRowIndex, currentRow):

		if currentRowIndex == 0:
			currentRow.append('BisTrack Amount')
			currentRow.append('Bank Amount')
		else:
			currentType = currentRow[2]
			
			def getBistrackAmount():
				currentBistrackAmount = currentRow[6]
				return myPyFunc.ifConditionFlipSign(myPyFunc.strToFloat(currentBistrackAmount), currentType, 'Debit')

			def getBankAmount():
				currentBankAmount = currentRow[4]
				return myPyFunc.ifConditionFlipSign(myPyFunc.strToFloat(currentBankAmount), currentType, 'Debit')

			currentRow.append(getBistrackAmount())
			currentRow.append(getBankAmount())

	dailyDepositsArray = myPyFunc.repeatActionOnArray(dailyDepositsArray, transformDailyDepositsArray)


	firstArrayFirstRow = firstArray.pop(0)
	secondArrayFirstRow = secondArray.pop(0)

	matchedArray = [[firstTableName] + [''] * (len(firstArrayFirstRow)) + [secondTableName] + [''] * (len(secondArrayFirstRow) - 1)]
	matchedArray.append(firstArrayFirstRow + [''] + secondArrayFirstRow)

	firstArrayAmountColumnIndex = 17
	firstArrayDateColumnIndex = 19
	secondArrayAmountColumnIndex = 7
	secondArrayDateColumnIndex = 8

	firstArrayColumnsToMatch = [firstArrayAmountColumnIndex, firstArrayDateColumnIndex]
	secondArrayColumnsToMatch = [secondArrayAmountColumnIndex, secondArrayDateColumnIndex]
	

	while firstArray:

		firstArrayCurrentRow = firstArray.pop(0)
		
	# 	# p(firstArrayColumnsToMatch)
	# 	# p(secondArrayColumnsToMatch)

		tempMatchedData = getMatchedRows(secondArray, firstArrayCurrentRow, firstArrayColumnsToMatch, secondArrayColumnsToMatch)

		if len(tempMatchedData) == 1:
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

				tempMatchedDailyDeposits = getMatchedRows(secondArray, updatedFirstArrayCurrentRow, [17], secondArrayColumnsToMatch)
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