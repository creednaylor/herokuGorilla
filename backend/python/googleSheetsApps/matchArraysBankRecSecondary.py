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


def columnDataMatches(firstArrayCurrentRow, secondArrayCurrentRow, columnsToMatch):

	for columnIndex, column in enumerate(columnsToMatch[0]):

		if firstArrayCurrentRow[column] != secondArrayCurrentRow[columnsToMatch[1][columnIndex]]:
			return False
	
	return True


def getMatchedRows(secondArray, firstArrayCurrentRow, columnsToMatch):

	rowsThatMatch = []

	for secondArrayRowIndex, secondArrayCurrentRow in enumerate(secondArray):
			
			if columnDataMatches(firstArrayCurrentRow, secondArrayCurrentRow, columnsToMatch):
				
				rowsThatMatch.append({
					'secondArrayRowIndex': secondArrayRowIndex,
					'secondArrayRow': secondArrayCurrentRow
				})

	return rowsThatMatch


def dailyDepositsColumnDataMatches(firstArrayCurrentRow, secondArrayCurrentRow):

	if firstArrayCurrentRow[12][2:7] != secondArrayCurrentRow[8]:
		return False
	
	return True


def getMatchedDailyDepositsRows(secondArray, firstArrayCurrentRow):

	rowsThatMatch = []

	for secondArrayRowIndex, secondArrayCurrentRow in enumerate(secondArray):
			
			if dailyDepositsColumnDataMatches(firstArrayCurrentRow, secondArrayCurrentRow):
				
				rowsThatMatch.append({
					'secondArrayRowIndex': secondArrayRowIndex,
					'secondArrayRow': secondArrayCurrentRow
				})

	return rowsThatMatch




def getColumnNames(columnsToMatch, firstArrayFirstRow):

	columnNamesToMatch = []
	firstArrayColumnsToMatch = columnsToMatch[0]

	for column in firstArrayColumnsToMatch:
		columnNamesToMatch.append(firstArrayFirstRow[column])

	# p(columnNamesToMatch)
	
	return columnNamesToMatch


def getMatchStatus(columnNamesToMatch):

	# p(columnNamesToMatch)

	matchStatus = 'Matched on '

	for column in columnNamesToMatch:
		if matchStatus == 'Matched on ':
			matchStatus = matchStatus + str(column)
		else:
			matchStatus = matchStatus + ' and ' + str(column)

	return matchStatus





def elementCriteriaAreTrue(element, criteriaToCheck):

	if len(element) > criteriaToCheck['maxRowLength']:
		return False
	else:
		for criterion in criteriaToCheck['criteria']:
			if element[criterion['columnIndexToCheck']] != criterion['valueToCheckFor']:
				return False

	return True


def countNumberOfElements(arrayToCount, criteriaToCheck):

	numberOfRecords = 0

	for element in arrayToCount:
		if elementCriteriaAreTrue(element, criteriaToCheck):
			numberOfRecords = numberOfRecords + 1

	return numberOfRecords


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


	firstArray = myPyFunc.transformArray(firstArray, transformFirstArray)
	secondArray = spreadsheetLevelObj.worksheet(secondTableName).get_all_values()
	

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

	secondArray = myPyFunc.transformArray(secondArray, transformSecondArray)
	dailyDepositsArray = spreadsheetLevelObj.worksheet(dailyDepositsTableName).get_all_values()
	

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

			currentDate = currentRow[0]
			dateToAppend = None

			if currentDate != '':
				dateToAppend = currentDate
			currentRow.append(dateToAppend)

			currentRow.append(getBistrackAmount())
			currentRow.append(getBankAmount())

	dailyDepositsArray = myPyFunc.transformArray(dailyDepositsArray, transformDailyDepositsArray)

	firstArrayFirstRow = firstArray.pop(0)
	secondArrayFirstRow = secondArray.pop(0)

	matchedArray = [[firstTableName] + [''] * (len(firstArrayFirstRow) - 1) + [''] + [secondTableName] + [''] * (len(secondArrayFirstRow) - 1)]
	matchedArray.append(firstArrayFirstRow + [''] + secondArrayFirstRow)

	columnsToMatch = [
		[17, 19],
		[7, 8]
	]

	def getMatchedRowToAppend(currentRow):

		rowToAppend = currentRow
		rowsThatMatch = getMatchedRows(secondArray, currentRow, columnsToMatch)

		if len(rowsThatMatch) == 1:
			rowToAppend = rowToAppend + [getMatchStatus(getColumnNames(columnsToMatch, firstArrayFirstRow))] + secondArray.pop(rowsThatMatch[0]['secondArrayRowIndex'])
		elif len(rowsThatMatch) > 1:
			p('More rows that match first pass')

		return rowToAppend


	myPyFunc.transferToArray(firstArray, matchedArray, getMatchedRowToAppend)


	columnsToMatch = [
		[17], 
		[7]
	]


	def addMatchesFromSecondArray(currentRowIndex, currentRow):
	
		if len(currentRow) == len(firstArrayFirstRow):

			rowsThatMatch = getMatchedRows(secondArray, currentRow, columnsToMatch)

			criteriaToCheck = {
				'maxRowLength': 20,
				'criteria': [
					{
						'columnIndexToCheck': 17,
						'valueToCheckFor': currentRow[17]
					}
				]
			}

			if len(rowsThatMatch) == 1 or countNumberOfElements(matchedArray, criteriaToCheck) == len(rowsThatMatch):

				currentRow.extend([getMatchStatus(getColumnNames(columnsToMatch, firstArrayFirstRow))] + secondArray.pop(rowsThatMatch[0]['secondArrayRowIndex']))
		
	myPyFunc.transformArray(matchedArray, addMatchesFromSecondArray)


	def addMatchesFromDailyDepositsArray(currentRowIndex, currentRow):

		if len(currentRow) == len(firstArrayFirstRow):

			rowsThatMatch = getMatchedDailyDepositsRows(dailyDepositsArray, currentRow)

			if len(rowsThatMatch) == 1:
				pass
	
	myPyFunc.transformArray(matchedArray, addMatchesFromDailyDepositsArray)


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