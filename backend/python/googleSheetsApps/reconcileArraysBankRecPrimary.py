from datetime import datetime
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



def reconcileArrays(oAuthMode, googleSheetTitle, googleAccountUsername=None):

	pathToRepos = myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
	pathBelowRepos = pathToThisPythonFile.parents[3]
	accountLevelObj = myGspreadFunc.authorizeGspread(oAuthMode, pathBelowRepos, googleAccountUsername=googleAccountUsername)

	bankStatusCol = 0
	bankDateColumnIndex = 1
	bankTransactionTypeColumnIndex = 7
	bankDebitCreditColumnIndex = 8
	bankAmountColumnIndex = 9
	bankDescriptionTwoColumnIndex = 11

	spacingColumnIndex = 14

	spreadsheetLevelObj = accountLevelObj.open(googleSheetTitle)
	sheetLevelBank = spreadsheetLevelObj.worksheet('Bank')
	sheetLevelGP = spreadsheetLevelObj.worksheet('GP')
	sheetLevelDailyDeposits = spreadsheetLevelObj.worksheet('dailyDeposits')
	sheetLevelComparison = spreadsheetLevelObj.worksheet('Comparison')
	sheetLevelEndingGP = spreadsheetLevelObj.worksheet('endingGP')


	bankArray = sheetLevelBank.get_all_values()


	def filterBankArray(currentRow):

		if currentRow[bankStatusCol] not in ['H', 'B', 'T'] and currentRow[bankTransactionTypeColumnIndex] not in ['Data', 'Ledger Balance', 'Collected + 1 Day', 'Opening Collected', 'One Day Float', '2 Day Float', '3 Day + Float', 'MTD Avg Collected', 'MTD Avg Neg Collected', 'Total Credits', 'Number of Credits', 'Total Debits', 'Number of Debits', 'Float Adjustment(s)']:
			return True
		else:
			return False

	bankArray = list(filter(filterBankArray, bankArray))

	gpTrxDateColumnIndex = 1
	gpAmountColumnIndex = 5
	gpTrxTypeColumnIndex = 11
	gpTrxNumberColumnIndex = 12
	gpPaidToReceivedFromColumnIndex = 14
	gpTransferColumnIndex = 17
	
	gpArray = sheetLevelGP.get_all_values()
	gpArray = [currentRow for currentRow in gpArray if currentRow[gpTrxDateColumnIndex] not in ['']]


	dailyDepositsAmountColumnIndex = 5
	dailyDepositsTransactionIDColumnIndex = 7
	dailyDepositsArray = sheetLevelDailyDeposits.get_all_values()


	def dailyDepositsTransform(indexAndElementData):

		currentRowIndex, currentRow = indexAndElementData

		if currentRowIndex > 0:
			currentRow[dailyDepositsAmountColumnIndex] = float(currentRow[dailyDepositsAmountColumnIndex].lstrip('$').replace(',', ''))

		return currentRow


	dailyDepositsArray = list(map(dailyDepositsTransform, enumerate(dailyDepositsArray)))


	def prepareBankArray(currentRowIndex, currentRow):

		if currentRowIndex > 0:

			currentRow[bankAmountColumnIndex] = float(currentRow[bankAmountColumnIndex].replace(',', ''))

			if len(currentRow[bankDateColumnIndex]) < 8:
				currentRow[bankDateColumnIndex] = '0' + currentRow[bankDateColumnIndex]

			currentRow[bankDateColumnIndex] = str(datetime.strptime(currentRow[bankDateColumnIndex], '%m%d%Y'))

			if currentRow[bankDebitCreditColumnIndex] == 'Debit':
				# p(currentRow[bankAmountColumnIndex])
				currentRow[bankAmountColumnIndex] = -currentRow[bankAmountColumnIndex]


	bankArray = myPyFunc.repeatActionOnArray(bankArray, prepareBankArray)

	def prepareGPArray(currentRowIndex, currentRow):

		if currentRowIndex == 0:
			currentRow.append('Transfer')
		else:
			currentRow[gpAmountColumnIndex] = float(currentRow[gpAmountColumnIndex].replace(',', ''))
			currentRow[gpTrxDateColumnIndex] = str(datetime.strptime(currentRow[gpTrxDateColumnIndex], '%m/%d/%Y'))

			if currentRow[gpPaidToReceivedFromColumnIndex]:
				if currentRow[gpPaidToReceivedFromColumnIndex][0:11] == 'Transfer To':
					currentRow.append('Out')
				if currentRow[gpPaidToReceivedFromColumnIndex][0:13] == "Transfer From":
					currentRow.append('In')
			if len(currentRow) == gpTransferColumnIndex:
				currentRow.append('')

			if currentRow[gpTrxTypeColumnIndex]:
				if not currentRow[gpTransferColumnIndex]:
					if currentRow[gpTrxTypeColumnIndex] in ['Increase Adjustment', 'Deposit']:
						currentRow[gpTransferColumnIndex] = "In"
					if currentRow[gpTrxTypeColumnIndex] in ['Decrease Adjustment', 'Withdrawl', 'Check']:
						currentRow[gpTransferColumnIndex] = "Out"

		if currentRow[gpTransferColumnIndex] == 'Out':
			currentRow[gpAmountColumnIndex] = -currentRow[gpAmountColumnIndex]

	gpArray = myPyFunc.repeatActionOnArray(gpArray, prepareGPArray)


	bankArrayFirstRow = bankArray.pop(0)
	gpArrayFirstRow = gpArray.pop(0)

	def filterGPArray(currentRow):
		if datetime.strptime(currentRow[gpTrxDateColumnIndex], '%Y-%m-%d %H:%M:%S') <= datetime(2020, 8, 31):
			return True
		else:
			return False

	gpArray = list(filter(filterGPArray, gpArray))



	def sortArrayOfArrays(array, subArrayIndexToSortBy): 
		# reverse = None (Sorts in Ascending order) 
		# key is set to sort using second element of  
		# sublist lambda has been used

		return(sorted(array, key = lambda x: x[subArrayIndexToSortBy])) 

	bankArray = sortArrayOfArrays(bankArray, bankDateColumnIndex)
	gpArray = sortArrayOfArrays(gpArray, gpTrxDateColumnIndex)


	comparisonArray = [['Bank'] + [''] * (len(bankArray[0])) + ['GP'] + [''] * (len(gpArray[0]) - 1)]
	comparisonArray.append(bankArrayFirstRow + ['Match Status'] + gpArrayFirstRow)

	

	while bankArray:

		bankArrayCurrentRow = bankArray.pop(0)
		rowToAppend = bankArrayCurrentRow + ['']

		gpArrayCurrentRowIndex = 0

		while gpArrayCurrentRowIndex in range(0, len(gpArray) - 1) and len(rowToAppend) == len(bankArrayCurrentRow) + 1:

			gpArrayCurrentRow = gpArray[gpArrayCurrentRowIndex]

			if bankArrayCurrentRow[bankAmountColumnIndex] == gpArrayCurrentRow[gpAmountColumnIndex]:

				if bankArrayCurrentRow[bankTransactionTypeColumnIndex] == 'Check(s) Paid' and gpArrayCurrentRow[gpTrxTypeColumnIndex] == 'Check':

					if bankArrayCurrentRow[bankDescriptionTwoColumnIndex] == gpArrayCurrentRow[gpTrxNumberColumnIndex]:

						gpArrayRowToAppend = gpArray.pop(gpArrayCurrentRowIndex)
						rowToAppend = rowToAppend + gpArrayRowToAppend
						rowToAppend[spacingColumnIndex] = 'Matched on amount and check number'

			gpArrayCurrentRowIndex = gpArrayCurrentRowIndex + 1

		comparisonArray.append(rowToAppend)


	for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(comparisonArray):

		if len(comparisonCurrentRow) == len(bankArrayFirstRow) + 1 and comparisonCurrentRow[bankTransactionTypeColumnIndex] != 'Check(s) Paid':

			gpRowsThatMatchComparisonCurrentRow = []
			
			for gpArrayCurrentRowIndex, gpArrayCurrentRow in enumerate(gpArray):

				if comparisonCurrentRow[bankAmountColumnIndex] == gpArrayCurrentRow[gpAmountColumnIndex] and comparisonCurrentRow[bankDateColumnIndex] == gpArrayCurrentRow[gpTrxDateColumnIndex]: 

					if gpArrayCurrentRow[gpTrxTypeColumnIndex] != 'Check' or (gpArrayCurrentRow[gpTrxTypeColumnIndex] == 'Check' and len(gpArrayCurrentRow[gpTrxNumberColumnIndex])!= 5):
						gpRowsThatMatchComparisonCurrentRow.append({
							'gpArrayRowIndex': gpArrayCurrentRowIndex,
							'gpArrayRow': gpArrayCurrentRow})

			if len(gpRowsThatMatchComparisonCurrentRow) == 1:

				comparisonArray[comparisonCurrentRowIndex] = comparisonArray[comparisonCurrentRowIndex] + gpArray.pop(gpRowsThatMatchComparisonCurrentRow[0]['gpArrayRowIndex'])
				comparisonArray[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched on amount and date'
			


	for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(comparisonArray):

		if len(comparisonCurrentRow) == len(bankArrayFirstRow) + 1 and comparisonCurrentRow[bankTransactionTypeColumnIndex] != 'Check(s) Paid':

			gpRowsThatMatchComparisonCurrentRow = []

			# if comparisonCurrentRow[bankAmountColumnIndex] == -1100.48:
			# 	p(1)
			
			for gpArrayCurrentRowIndex in reversed(range(0, len(gpArray))):

				if comparisonCurrentRow[bankAmountColumnIndex] == gpArray[gpArrayCurrentRowIndex][gpAmountColumnIndex]:

					if gpArray[gpArrayCurrentRowIndex][gpTrxTypeColumnIndex] != 'Check' or (gpArray[gpArrayCurrentRowIndex][gpTrxTypeColumnIndex] == 'Check' and len(gpArray[gpArrayCurrentRowIndex][gpTrxNumberColumnIndex])!= 5):

						gpRowsThatMatchComparisonCurrentRow.append({
							'gpArrayRowIndex': gpArrayCurrentRowIndex,
							'gpArrayRow': gpArray[gpArrayCurrentRowIndex]})

			if len(gpRowsThatMatchComparisonCurrentRow) == 1:
				comparisonArray[comparisonCurrentRowIndex] = comparisonArray[comparisonCurrentRowIndex] + gpArray.pop(gpRowsThatMatchComparisonCurrentRow[0]['gpArrayRowIndex'])
				comparisonArray[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched on amount, 1 bank row with 1 GP row'

			if len(gpRowsThatMatchComparisonCurrentRow) > 1:

				comparisonRowsThatMatchComparisonCurrentRow = []
    
				for comparisonDuplicateRowIndex, comparisonDuplicateRow in enumerate(comparisonArray):
        
					if comparisonDuplicateRow[bankAmountColumnIndex] == comparisonCurrentRow[bankAmountColumnIndex] and len(comparisonDuplicateRow) == len(bankArrayFirstRow) + 1:
						
						comparisonRowsThatMatchComparisonCurrentRow.insert(0, {
							'comparisonDuplicateRowIndex': comparisonDuplicateRowIndex,
							'comparisonDuplicateRow': comparisonDuplicateRow
						})

				gpRowsThatMatchLength = len(gpRowsThatMatchComparisonCurrentRow)			
    
				if gpRowsThatMatchLength == len(comparisonRowsThatMatchComparisonCurrentRow):
					
					for comparisonDuplicateMatchedRowIndex in range(0, len(comparisonRowsThatMatchComparisonCurrentRow)):
						
						comparisonArray[comparisonRowsThatMatchComparisonCurrentRow[comparisonDuplicateMatchedRowIndex]['comparisonDuplicateRowIndex']] = comparisonArray[comparisonRowsThatMatchComparisonCurrentRow[comparisonDuplicateMatchedRowIndex]['comparisonDuplicateRowIndex']] + gpArray.pop(gpRowsThatMatchComparisonCurrentRow[comparisonDuplicateMatchedRowIndex]['gpArrayRowIndex'])
						comparisonArray[comparisonRowsThatMatchComparisonCurrentRow[comparisonDuplicateMatchedRowIndex]['comparisonDuplicateRowIndex']][spacingColumnIndex] = f'Matched on amount, {gpRowsThatMatchLength} bank rows with {gpRowsThatMatchLength} GP rows'
		


	for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(comparisonArray):

		if len(comparisonCurrentRow) == len(bankArrayFirstRow) + 1 and comparisonCurrentRow[bankTransactionTypeColumnIndex] != 'Check(s) Paid':
			# p(comparisonCurrentRow)

			for dailyDepositsCurrentRow in dailyDepositsArray:
				
				if comparisonCurrentRow[bankAmountColumnIndex] == dailyDepositsCurrentRow[dailyDepositsAmountColumnIndex]:
					
					gpRowsThatMatchComparisonCurrentRow = []

					for gpArrayCurrentRowIndex in reversed(range(0, len(gpArray))):

						if gpArray[gpArrayCurrentRowIndex][gpTrxNumberColumnIndex][2:7] == dailyDepositsCurrentRow[dailyDepositsTransactionIDColumnIndex]:
							comparisonArray[comparisonCurrentRowIndex] = comparisonArray[comparisonCurrentRowIndex] + gpArray[gpArrayCurrentRowIndex]
							comparisonArray[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched from Daily Deposits file'


	for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(comparisonArray):

		if len(comparisonCurrentRow) == len(bankArrayFirstRow) + 1 and comparisonCurrentRow[bankTransactionTypeColumnIndex] == 'Check(s) Paid':
    
			gpRowsThatMatchComparisonCurrentRow = []
			
			for gpArrayCurrentRowIndex, gpArrayCurrentRow in enumerate(gpArray):

				if comparisonCurrentRow[bankAmountColumnIndex] == gpArrayCurrentRow[gpAmountColumnIndex] and comparisonCurrentRow[bankDateColumnIndex] == gpArrayCurrentRow[gpTrxDateColumnIndex]: 

					gpRowsThatMatchComparisonCurrentRow.append({
						'gpArrayRowIndex': gpArrayCurrentRowIndex,
						'gpArrayRow': gpArrayCurrentRow})

			if len(gpRowsThatMatchComparisonCurrentRow) == 1:

				comparisonArray[comparisonCurrentRowIndex] = comparisonArray[comparisonCurrentRowIndex] + gpArray.pop(gpRowsThatMatchComparisonCurrentRow[0]['gpArrayRowIndex'])
				comparisonArray[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched on amount and date, bank transaction is a check, GP transaction does not have the same check number'


	clearAndResizeParameters = [{
		'sheetObj': sheetLevelComparison,
		'resizeRows': 3,
		'startingRowIndexToClear': 0,
		'resizeColumns': 3
	},
	{
		'sheetObj': sheetLevelEndingGP,
		'resizeRows': 2,
		'startingRowIndexToClear': 0,
		'resizeColumns': 1
	}]


	sheetLevelComparison.clear_basic_filter()
	sheetLevelEndingGP.clear_basic_filter()
	myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)

	myGspreadFunc.updateCells(sheetLevelComparison, comparisonArray)


	gpArray.insert(0, gpArrayFirstRow)
	myGspreadFunc.updateCells(sheetLevelEndingGP, gpArray)


	sheetLevelComparison.set_basic_filter(2, 1, len(comparisonArray), len(comparisonArray[0]) + 1)
	sheetLevelEndingGP.set_basic_filter(1, 1, len(gpArray), len(gpArray[0]))

	myGspreadFunc.autoResizeColumnsOnSheet(spreadsheetLevelObj, 'Bank')
	myGspreadFunc.autoResizeColumnsOnSheet(spreadsheetLevelObj, 'GP')
	myGspreadFunc.autoResizeColumnsOnSheet(spreadsheetLevelObj, 'Comparison')
	myGspreadFunc.autoResizeColumnsOnSheet(spreadsheetLevelObj, 'endingGP')




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