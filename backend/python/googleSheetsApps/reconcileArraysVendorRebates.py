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

	pathBelowRepos = pathToThisPythonFile
	spreadsheetLevelObj = myGspreadFunc.authorizeGspread(oAuthMode, pathBelowRepos, googleAccountUsername=googleAccountUsername).open(googleSheetTitle)

	# bankStatusCol = 0
	# bankDateColumnIndex = 1
	# bankTransactionTypeColumnIndex = 7
	# bankDebitCreditColumnIndex = 8
	# gpTransactionsAmountColumnIndex = 9
	# bankDescriptionTwoColumnIndex = 11

	# spacingColumnIndex = 14

	# sheetLevelDailyDeposits = spreadsheetLevelObj.worksheet('dailyDeposits')
	# sheetLevelComparison = spreadsheetLevelObj.worksheet('Comparison')
	# sheetLevelEndingGP = spreadsheetLevelObj.worksheet('endingGP')

	extractedFilenames = spreadsheetLevelObj.worksheet('extractedFilenames').get_all_values()
	gpTransactions = spreadsheetLevelObj.worksheet('gpTransactions').get_all_values()

	# gpTransactions = sheetLevelBank.get_all_values()


	# def filtergpTransactions(currentRow):

	# 	if currentRow[bankStatusCol] not in ['H', 'B', 'T'] and currentRow[bankTransactionTypeColumnIndex] not in ['Data', 'Ledger Balance', 'Collected + 1 Day', 'Opening Collected', 'One Day Float', '2 Day Float', '3 Day + Float', 'MTD Avg Collected', 'MTD Avg Neg Collected', 'Total Credits', 'Number of Credits', 'Total Debits', 'Number of Debits', 'Float Adjustment(s)']:
	# 		return True
	# 	else:
	# 		return False

	# gpTransactions = list(filter(filtergpTransactions, gpTransactions))

	# gpTrxDateColumnIndex = 1
	# gpAmountColumnIndex = 5
	# gpTrxTypeColumnIndex = 11
	# gpTrxNumberColumnIndex = 12
	# gpPaidToReceivedFromColumnIndex = 14
	# gpTransferColumnIndex = 17
	
	# extractedFilenames = sheetLevelGP.get_all_values()
	# extractedFilenames = [currentRow for currentRow in extractedFilenames if currentRow[gpTrxDateColumnIndex] not in ['']]


	# dailyDepositsAmountColumnIndex = 5
	# dailyDepositsTransactionIDColumnIndex = 7
	# dailyDepositsArray = sheetLevelDailyDeposits.get_all_values()


	# def dailyDepositsTransform(indexAndElementData):

	# 	currentRowIndex, currentRow = indexAndElementData

	# 	if currentRowIndex > 0:
	# 		currentRow[dailyDepositsAmountColumnIndex] = float(currentRow[dailyDepositsAmountColumnIndex].lstrip('$').replace(',', ''))

	# 	return currentRow


	# dailyDepositsArray = list(map(dailyDepositsTransform, enumerate(dailyDepositsArray)))

	gpTransactionsDebitColumnIndex = 5
	gpTransactionsCreditColumnIndex = gpTransactionsDebitColumnIndex + 1

	def prepareGPTransactions(currentRowIndex, currentRow):
		if currentRowIndex == 0:
			currentRow.append('Amount')
		else:
			currentRow.append(float(currentRow[gpTransactionsDebitColumnIndex].replace(',', '')) - float(currentRow[gpTransactionsCreditColumnIndex].replace(',', '')))


	gpTransactions = myPyFunc.repeatActionOnArray(gpTransactions, prepareGPTransactions)
	gpTransactionsAmountColumnIndex = 12
	spacingColumnIndex = gpTransactionsAmountColumnIndex + 1
	extractedFilenamesAmountColumnIndex = 2
	

	# def prepareextractedFilenames(currentRowIndex, currentRow):

	# 	if currentRowIndex == 0:
	# 		currentRow.append('Transfer')
	# 	else:
	# 		currentRow[gpAmountColumnIndex] = float(currentRow[gpAmountColumnIndex].replace(',', ''))
	# 		currentRow[gpTrxDateColumnIndex] = str(datetime.strptime(currentRow[gpTrxDateColumnIndex], '%m/%d/%Y'))

	# 		if currentRow[gpPaidToReceivedFromColumnIndex]:
	# 			if currentRow[gpPaidToReceivedFromColumnIndex][0:11] == 'Transfer To':
	# 				currentRow.append('Out')
	# 			if currentRow[gpPaidToReceivedFromColumnIndex][0:13] == "Transfer From":
	# 				currentRow.append('In')
	# 		if len(currentRow) == gpTransferColumnIndex:
	# 			currentRow.append('')

	# 		if currentRow[gpTrxTypeColumnIndex]:
	# 			if not currentRow[gpTransferColumnIndex]:
	# 				if currentRow[gpTrxTypeColumnIndex] in ['Increase Adjustment', 'Deposit']:
	# 					currentRow[gpTransferColumnIndex] = "In"
	# 				if currentRow[gpTrxTypeColumnIndex] in ['Decrease Adjustment', 'Withdrawl', 'Check']:
	# 					currentRow[gpTransferColumnIndex] = "Out"

	# 	if currentRow[gpTransferColumnIndex] == 'Out':
	# 		currentRow[gpAmountColumnIndex] = -currentRow[gpAmountColumnIndex]


	# extractedFilenames = myPyFunc.repeatActionOnArray(extractedFilenames, prepareextractedFilenames)


	gpTransactionsFirstRow = gpTransactions.pop(0)
	extractedFilenamesFirstRow = extractedFilenames.pop(0)

	# def filterextractedFilenames(currentRow):
	# 	if datetime.strptime(currentRow[gpTrxDateColumnIndex], '%Y-%m-%d %H:%M:%S') <= datetime(2020, 8, 31):
	# 		return True
	# 	else:
	# 		return False

	# extractedFilenames = list(filter(filterextractedFilenames, extractedFilenames))



	# def sortArrayOfArrays(array, subArrayIndexToSortBy): 
	# 	# reverse = None (Sorts in Ascending order) 
	# 	# key is set to sort using second element of  
	# 	# sublist lambda has been used

	# 	return(sorted(array, key = lambda x: x[subArrayIndexToSortBy])) 

	# gpTransactions = sortArrayOfArrays(gpTransactions, bankDateColumnIndex)
	# extractedFilenames = sortArrayOfArrays(extractedFilenames, gpTrxDateColumnIndex)


	comparedTransactions = [['GP Transactions'] + [''] * (len(gpTransactions[0])) + ['Extracted Filenames'] + [''] * (len(extractedFilenames[0]) - 1)]
	comparedTransactions.append(gpTransactionsFirstRow + ['Match Status'] + extractedFilenamesFirstRow)

	

	while gpTransactions:

		gpTransactionsCurrentRow = gpTransactions.pop(0)
		rowToAppend = gpTransactionsCurrentRow + ['']

		extractedFilenamesCurrentRowIndex = 0

		while extractedFilenamesCurrentRowIndex in range(0, len(extractedFilenames) - 1) and len(rowToAppend) == len(gpTransactionsCurrentRow) + 1:

			extractedFilenamesCurrentRow = extractedFilenames[extractedFilenamesCurrentRowIndex]

			# p(gpTransactionsCurrentRow[gpTransactionsAmountColumnIndex])
			# p(extractedFilenamesCurrentRow[extractedFilenamesAmountColumnIndex])

			if gpTransactionsCurrentRow[gpTransactionsAmountColumnIndex] == float(extractedFilenamesCurrentRow[extractedFilenamesAmountColumnIndex].replace(',', '')):


				extractedFilenamesRowToAppend = extractedFilenames.pop(extractedFilenamesCurrentRowIndex)
				rowToAppend = rowToAppend + extractedFilenamesRowToAppend
				rowToAppend[spacingColumnIndex] = 'Matched on amount'

			extractedFilenamesCurrentRowIndex = extractedFilenamesCurrentRowIndex + 1

		comparedTransactions.append(rowToAppend)


	# for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(comparedTransactions):

	# 	if len(comparisonCurrentRow) == len(gpTransactionsFirstRow) + 1 and comparisonCurrentRow[bankTransactionTypeColumnIndex] != 'Check(s) Paid':

	# 		gpRowsThatMatchComparisonCurrentRow = []
			
	# 		for extractedFilenamesCurrentRowIndex, extractedFilenamesCurrentRow in enumerate(extractedFilenames):

	# 			if comparisonCurrentRow[gpTransactionsAmountColumnIndex] == extractedFilenamesCurrentRow[gpAmountColumnIndex] and comparisonCurrentRow[bankDateColumnIndex] == extractedFilenamesCurrentRow[gpTrxDateColumnIndex]: 

	# 				if extractedFilenamesCurrentRow[gpTrxTypeColumnIndex] != 'Check' or (extractedFilenamesCurrentRow[gpTrxTypeColumnIndex] == 'Check' and len(extractedFilenamesCurrentRow[gpTrxNumberColumnIndex])!= 5):
	# 					gpRowsThatMatchComparisonCurrentRow.append({
	# 						'extractedFilenamesRowIndex': extractedFilenamesCurrentRowIndex,
	# 						'extractedFilenamesRow': extractedFilenamesCurrentRow})

	# 		if len(gpRowsThatMatchComparisonCurrentRow) == 1:

	# 			comparedTransactions[comparisonCurrentRowIndex] = comparedTransactions[comparisonCurrentRowIndex] + extractedFilenames.pop(gpRowsThatMatchComparisonCurrentRow[0]['extractedFilenamesRowIndex'])
	# 			comparedTransactions[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched on amount and date'
			


	# for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(comparedTransactions):

	# 	if len(comparisonCurrentRow) == len(gpTransactionsFirstRow) + 1 and comparisonCurrentRow[bankTransactionTypeColumnIndex] != 'Check(s) Paid':

	# 		gpRowsThatMatchComparisonCurrentRow = []

	# 		# if comparisonCurrentRow[gpTransactionsAmountColumnIndex] == -1100.48:
	# 		# 	p(1)
			
	# 		for extractedFilenamesCurrentRowIndex in reversed(range(0, len(extractedFilenames))):

	# 			if comparisonCurrentRow[gpTransactionsAmountColumnIndex] == extractedFilenames[extractedFilenamesCurrentRowIndex][gpAmountColumnIndex]:

	# 				if extractedFilenames[extractedFilenamesCurrentRowIndex][gpTrxTypeColumnIndex] != 'Check' or (extractedFilenames[extractedFilenamesCurrentRowIndex][gpTrxTypeColumnIndex] == 'Check' and len(extractedFilenames[extractedFilenamesCurrentRowIndex][gpTrxNumberColumnIndex])!= 5):

	# 					gpRowsThatMatchComparisonCurrentRow.append({
	# 						'extractedFilenamesRowIndex': extractedFilenamesCurrentRowIndex,
	# 						'extractedFilenamesRow': extractedFilenames[extractedFilenamesCurrentRowIndex]})

	# 		if len(gpRowsThatMatchComparisonCurrentRow) == 1:
	# 			comparedTransactions[comparisonCurrentRowIndex] = comparedTransactions[comparisonCurrentRowIndex] + extractedFilenames.pop(gpRowsThatMatchComparisonCurrentRow[0]['extractedFilenamesRowIndex'])
	# 			comparedTransactions[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched on amount, 1 bank row with 1 GP row'

	# 		if len(gpRowsThatMatchComparisonCurrentRow) > 1:

	# 			comparisonRowsThatMatchComparisonCurrentRow = []
    
	# 			for comparisonDuplicateRowIndex, comparisonDuplicateRow in enumerate(comparedTransactions):
        
	# 				if comparisonDuplicateRow[gpTransactionsAmountColumnIndex] == comparisonCurrentRow[gpTransactionsAmountColumnIndex] and len(comparisonDuplicateRow) == len(gpTransactionsFirstRow) + 1:
						
	# 					comparisonRowsThatMatchComparisonCurrentRow.insert(0, {
	# 						'comparisonDuplicateRowIndex': comparisonDuplicateRowIndex,
	# 						'comparisonDuplicateRow': comparisonDuplicateRow
	# 					})

	# 			gpRowsThatMatchLength = len(gpRowsThatMatchComparisonCurrentRow)			
    
	# 			if gpRowsThatMatchLength == len(comparisonRowsThatMatchComparisonCurrentRow):
					
	# 				for comparisonDuplicateMatchedRowIndex in range(0, len(comparisonRowsThatMatchComparisonCurrentRow)):
						
	# 					comparedTransactions[comparisonRowsThatMatchComparisonCurrentRow[comparisonDuplicateMatchedRowIndex]['comparisonDuplicateRowIndex']] = comparedTransactions[comparisonRowsThatMatchComparisonCurrentRow[comparisonDuplicateMatchedRowIndex]['comparisonDuplicateRowIndex']] + extractedFilenames.pop(gpRowsThatMatchComparisonCurrentRow[comparisonDuplicateMatchedRowIndex]['extractedFilenamesRowIndex'])
	# 					comparedTransactions[comparisonRowsThatMatchComparisonCurrentRow[comparisonDuplicateMatchedRowIndex]['comparisonDuplicateRowIndex']][spacingColumnIndex] = f'Matched on amount, {gpRowsThatMatchLength} bank rows with {gpRowsThatMatchLength} GP rows'
		


	# for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(comparedTransactions):

	# 	if len(comparisonCurrentRow) == len(gpTransactionsFirstRow) + 1 and comparisonCurrentRow[bankTransactionTypeColumnIndex] != 'Check(s) Paid':
	# 		# p(comparisonCurrentRow)

	# 		for dailyDepositsCurrentRow in dailyDepositsArray:
				
	# 			if comparisonCurrentRow[gpTransactionsAmountColumnIndex] == dailyDepositsCurrentRow[dailyDepositsAmountColumnIndex]:
					
	# 				gpRowsThatMatchComparisonCurrentRow = []

	# 				for extractedFilenamesCurrentRowIndex in reversed(range(0, len(extractedFilenames))):

	# 					if extractedFilenames[extractedFilenamesCurrentRowIndex][gpTrxNumberColumnIndex][2:7] == dailyDepositsCurrentRow[dailyDepositsTransactionIDColumnIndex]:
	# 						comparedTransactions[comparisonCurrentRowIndex] = comparedTransactions[comparisonCurrentRowIndex] + extractedFilenames[extractedFilenamesCurrentRowIndex]
	# 						comparedTransactions[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched from Daily Deposits file'


	# for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(comparedTransactions):

	# 	if len(comparisonCurrentRow) == len(gpTransactionsFirstRow) + 1 and comparisonCurrentRow[bankTransactionTypeColumnIndex] == 'Check(s) Paid':
    
	# 		gpRowsThatMatchComparisonCurrentRow = []
			
	# 		for extractedFilenamesCurrentRowIndex, extractedFilenamesCurrentRow in enumerate(extractedFilenames):

	# 			if comparisonCurrentRow[gpTransactionsAmountColumnIndex] == extractedFilenamesCurrentRow[gpAmountColumnIndex] and comparisonCurrentRow[bankDateColumnIndex] == extractedFilenamesCurrentRow[gpTrxDateColumnIndex]: 

	# 				gpRowsThatMatchComparisonCurrentRow.append({
	# 					'extractedFilenamesRowIndex': extractedFilenamesCurrentRowIndex,
	# 					'extractedFilenamesRow': extractedFilenamesCurrentRow})

	# 		if len(gpRowsThatMatchComparisonCurrentRow) == 1:

	# 			comparedTransactions[comparisonCurrentRowIndex] = comparedTransactions[comparisonCurrentRowIndex] + extractedFilenames.pop(gpRowsThatMatchComparisonCurrentRow[0]['extractedFilenamesRowIndex'])
	# 			comparedTransactions[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched on amount and date, bank transaction is a check, GP transaction does not have the same check number'


	# clearAndResizeParameters = [{
	# 	'sheetObj': sheetLevelComparison,
	# 	'resizeRows': 3,
	# 	'startingRowIndexToClear': 0,
	# 	'resizeColumns': 3
	# },
	# {
	# 	'sheetObj': sheetLevelEndingGP,
	# 	'resizeRows': 2,
	# 	'startingRowIndexToClear': 0,
	# 	'resizeColumns': 1
	# }]


	# sheetLevelComparison.clear_basic_filter()
	# sheetLevelEndingGP.clear_basic_filter()
	# myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)

	# myGspreadFunc.updateCells(sheetLevelComparison, comparedTransactions)


	# extractedFilenames.insert(0, extractedFilenamesFirstRow)
	myGspreadFunc.updateCells(spreadsheetLevelObj.worksheet('Comparison'), comparedTransactions)


	# sheetLevelComparison.set_basic_filter(2, 1, len(comparedTransactions), len(comparedTransactions[0]) + 1)
	# sheetLevelEndingGP.set_basic_filter(1, 1, len(extractedFilenames), len(extractedFilenames[0]))

	myGspreadFunc.autoResizeColumnsInSpreadsheet(spreadsheetLevelObj)
	# myGspreadFunc.autoResizeColumnsOnSheet(spreadsheetLevelObj, 'Bank')
	# myGspreadFunc.autoResizeColumnsOnSheet(spreadsheetLevelObj, 'GP')
	# myGspreadFunc.autoResizeColumnsOnSheet(spreadsheetLevelObj, 'Comparison')
	# myGspreadFunc.autoResizeColumnsOnSheet(spreadsheetLevelObj, 'endingGP')



def mainFunction(arrayOfArguments):
    reconcileArrays(True, arrayOfArguments[1], googleAccountUsername=arrayOfArguments[2])


if __name__ == '__main__':
    p(str(pathToThisPythonFile.name) + ' is not being imported. It is being run directly...')
    mainFunction(sys.argv)
else:
	p(str(pathToThisPythonFile.name) + ' is being imported. It is not being run directly...')