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
	from ..myPythonLibrary import _myPyFunc
	from ..googleSheets.myGoogleSheetsLibrary import _myGspreadFunc
else:
	sys.path.append(str(pathToThisPythonFile.parents[1]))
	from myPythonLibrary import _myPyFunc
	from googleSheets.myGoogleSheetsLibrary import _myGspreadFunc



def reconcileArrays(oAuthMode, googleSheetTitle, googleAccountUsername=None):

	pathToRepos = _myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
	pathToThisProjectRoot = pathToThisPythonFile.parents[3]
	gspObj = _myGspreadFunc.authorizeGspread(oAuthMode, pathToThisProjectRoot, googleAccountUsername=googleAccountUsername)

	bankStatusCol = 0
	bankDateColumnIndex = 1
	bankTransactionTypeColumnIndex = 7
	bankDebitCreditColumnIndex = 8
	bankAmountColumnIndex = 9
	bankDescriptionTwoColumnIndex = 11

	spacingColumnIndex = 13

	gspSpreadsheet = gspObj.open(googleSheetTitle)
	gspBankData = gspSpreadsheet.worksheet('bankData')
	gspGPData = gspSpreadsheet.worksheet('gpData')
	gspDailyDeposits = gspSpreadsheet.worksheet('dailyDeposits')
	gspComparison = gspSpreadsheet.worksheet('bankGPComparisonData')
	gspEndingGP = gspSpreadsheet.worksheet('endingGPData')


	bankDataArray = gspBankData.get_all_values()


	def filterBankData(currentRow):

		if currentRow[bankStatusCol] not in ['H', 'B', 'T'] and currentRow[bankTransactionTypeColumnIndex] not in ['Data', 'Ledger Balance', 'Collected + 1 Day', 'Opening Collected', 'One Day Float', '2 Day Float', '3 Day + Float', 'MTD Avg Collected', 'MTD Avg Neg Collected', 'Total Credits', 'Number of Credits', 'Total Debits', 'Number of Debits', 'Float Adjustment(s)']:
			return True
		else:
			return False

	bankDataArray = list(filter(filterBankData, bankDataArray))

	gpTrxDateColumnIndex = 1
	gpAmountColumnIndex = 5
	gpTrxTypeColumnIndex = 11
	gpTrxNumberColumnIndex = 12
	gpPaidToReceivedFromColumnIndex = 14
	gpTransferColumnIndex = 16
	
	gpDataArray = gspGPData.get_all_values()

	gpDataArray = [currentRow for currentRow in gpDataArray if currentRow[gpTrxDateColumnIndex] not in ['']]
	
	dailyDepositsAmountColumnIndex = 5
	dailyDepositsTransactionIDColumnIndex = 7
	dailyDepositsArray = gspDailyDeposits.get_all_values()


	def dailyDepositsTransform(indexAndElementData):
		currentRowIndex, currentRow = indexAndElementData

		if currentRowIndex > 0:
			currentRow[dailyDepositsAmountColumnIndex] = float(currentRow[dailyDepositsAmountColumnIndex].lstrip('$').replace(',', ''))

		return currentRow


	dailyDepositsArray = list(map(dailyDepositsTransform, enumerate(dailyDepositsArray)))



	for currentRowIndex, currentRow in enumerate(bankDataArray):
		if currentRowIndex > 0:

			currentRow[bankAmountColumnIndex] = float(currentRow[bankAmountColumnIndex].replace(',', ''))

			if len(currentRow[bankDateColumnIndex]) < 8:
				currentRow[bankDateColumnIndex] = '0' + currentRow[bankDateColumnIndex]

			currentRow[bankDateColumnIndex] = str(datetime.strptime(currentRow[bankDateColumnIndex], '%m%d%Y'))

			if currentRow[bankDebitCreditColumnIndex] == 'Debit':
				# p(currentRow[bankAmountColumnIndex])
				currentRow[bankAmountColumnIndex] = -currentRow[bankAmountColumnIndex]


	for currentRowIndex, currentRow in enumerate(gpDataArray):
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
			if len(currentRow) == 16:
				currentRow.append('')

			if currentRow[gpTrxTypeColumnIndex]:
				if not currentRow[gpTransferColumnIndex]:
					if currentRow[gpTrxTypeColumnIndex] in ['Increase Adjustment', 'Deposit']:
						currentRow[gpTransferColumnIndex] = "In"
					if currentRow[gpTrxTypeColumnIndex] in ['Decrease Adjustment', 'Withdrawl', 'Check']:
						currentRow[gpTransferColumnIndex] = "Out"

		if currentRow[gpTransferColumnIndex] == 'Out':
			currentRow[gpAmountColumnIndex] = -currentRow[gpAmountColumnIndex]
	


	bankDataFirstRow = bankDataArray.pop(0)
	gpDataFirstRow= gpDataArray.pop(0)

	comparisonArray = [['bankData'] + [''] * (len(bankDataArray[0])) + ['gpData'] + [''] * (len(gpDataArray[0]) - 1)]
	comparisonArray.append(bankDataFirstRow + [''] + gpDataFirstRow)

	while bankDataArray:

		bankDataCurrentRow = bankDataArray.pop(0)
		rowToAppend = bankDataCurrentRow + ['']

		gpDataCurrentRowIndex = 0

		while gpDataCurrentRowIndex in range(0, len(gpDataArray) - 1) and len(rowToAppend) == len(bankDataCurrentRow) + 1:

			gpDataCurrentRow = gpDataArray[gpDataCurrentRowIndex]

			if bankDataCurrentRow[bankAmountColumnIndex] == gpDataCurrentRow[gpAmountColumnIndex]:

				if bankDataCurrentRow[bankTransactionTypeColumnIndex] == 'Check(s) Paid' and gpDataCurrentRow[gpTrxTypeColumnIndex] == 'Check':

					if bankDataCurrentRow[bankDescriptionTwoColumnIndex] == gpDataCurrentRow[gpTrxNumberColumnIndex]:

						gpDataRowToAppend = gpDataArray.pop(gpDataCurrentRowIndex)
						rowToAppend = rowToAppend + gpDataRowToAppend
						rowToAppend[spacingColumnIndex] = 'Matched on amount and check number'

			gpDataCurrentRowIndex = gpDataCurrentRowIndex + 1

		comparisonArray.append(rowToAppend)


	for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(comparisonArray):

		if len(comparisonCurrentRow) == len(bankDataFirstRow) + 1 and comparisonCurrentRow[bankTransactionTypeColumnIndex] != 'Check(s) Paid':

			gpRowsThatMatchComparisonCurrentRow = []
			
			for gpDataCurrentRowIndex, gpDataCurrentRow in enumerate(gpDataArray):

				if comparisonCurrentRow[bankAmountColumnIndex] == gpDataCurrentRow[gpAmountColumnIndex] and comparisonCurrentRow[bankDateColumnIndex] == gpDataCurrentRow[gpTrxDateColumnIndex]: 

					if gpDataCurrentRow[gpTrxTypeColumnIndex] != 'Check' or (gpDataCurrentRow[gpTrxTypeColumnIndex] == 'Check' and len(gpDataCurrentRow[gpTrxNumberColumnIndex])!= 5):
						gpRowsThatMatchComparisonCurrentRow.append({
							'gpDataRowIndex': gpDataCurrentRowIndex,
							'gpDataRow': gpDataCurrentRow})

			if len(gpRowsThatMatchComparisonCurrentRow) == 1:

				comparisonArray[comparisonCurrentRowIndex] = comparisonArray[comparisonCurrentRowIndex] + gpDataArray.pop(gpRowsThatMatchComparisonCurrentRow[0]['gpDataRowIndex'])
				comparisonArray[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched on amount and date'


	for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(comparisonArray):

		if len(comparisonCurrentRow) == len(bankDataFirstRow) + 1 and comparisonCurrentRow[bankTransactionTypeColumnIndex] != 'Check(s) Paid':

			gpRowsThatMatchComparisonCurrentRow = []
			
			for gpDataCurrentRowIndex in reversed(range(0, len(gpDataArray))):

				if comparisonCurrentRow[bankAmountColumnIndex] == gpDataArray[gpDataCurrentRowIndex][gpAmountColumnIndex]:

					if gpDataArray[gpDataCurrentRowIndex][gpTrxTypeColumnIndex] != 'Check' or (gpDataArray[gpDataCurrentRowIndex][gpTrxTypeColumnIndex] == 'Check' and len(gpDataArray[gpDataCurrentRowIndex][gpTrxNumberColumnIndex])!= 5):

						gpRowsThatMatchComparisonCurrentRow.append({
							'gpDataRowIndex': gpDataCurrentRowIndex,
							'gpDataRow': gpDataArray[gpDataCurrentRowIndex]})

			if len(gpRowsThatMatchComparisonCurrentRow) == 1:
				comparisonArray[comparisonCurrentRowIndex] = comparisonArray[comparisonCurrentRowIndex] + gpDataArray.pop(gpRowsThatMatchComparisonCurrentRow[0]['gpDataRowIndex'])
				comparisonArray[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched on amount'

			if len(gpRowsThatMatchComparisonCurrentRow) > 1:

				reversedListOfMatchedRowIndex = list(range(len(gpRowsThatMatchComparisonCurrentRow) - 1, 0, -1))  #[3, 2, 1]
				comparisonArrayAtCurrentRow = comparisonArray[comparisonCurrentRowIndex]
				gpMatchedLastRowIndex = len(gpRowsThatMatchComparisonCurrentRow) - 1

				for gpMatchedCurrentRowIndex, gpMatchedRow in enumerate(gpRowsThatMatchComparisonCurrentRow):

					if gpMatchedCurrentRowIndex == 0:
						comparisonArray[comparisonCurrentRowIndex] = [str(comparisonArrayAtCurrentRow[0]) + ' matched ' + str(reversedListOfMatchedRowIndex[gpMatchedCurrentRowIndex]) + ' additional row(s)'] + (len(bankDataFirstRow) - 1) * [''] + ['Matched on amount'] + gpDataArray.pop(gpMatchedRow['gpDataRowIndex'])
					elif gpMatchedCurrentRowIndex == gpMatchedLastRowIndex:
						comparisonArrayAtCurrentRow[spacingColumnIndex] = 'Matched on amount'
						comparisonArray.insert(comparisonCurrentRowIndex, comparisonArrayAtCurrentRow + gpDataArray.pop(gpMatchedRow['gpDataRowIndex']))
					else:
						comparisonArray.insert(comparisonCurrentRowIndex, [str(comparisonArrayAtCurrentRow[0]) + ' matched ' + str(reversedListOfMatchedRowIndex[gpMatchedCurrentRowIndex]) + ' additional row(s)'] + (len(bankDataFirstRow) - 1) * [''] + ['Matched on amount'] + gpDataArray.pop(gpMatchedRow['gpDataRowIndex']))


	for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(comparisonArray):

		if len(comparisonCurrentRow) == len(bankDataFirstRow) + 1 and comparisonCurrentRow[bankTransactionTypeColumnIndex] != 'Check(s) Paid':
			# p(comparisonCurrentRow)

			for dailyDepositsCurrentRow in dailyDepositsArray:
				
				if comparisonCurrentRow[bankAmountColumnIndex] == dailyDepositsCurrentRow[dailyDepositsAmountColumnIndex]:
					
					gpRowsThatMatchComparisonCurrentRow = []

					for gpDataCurrentRowIndex in reversed(range(0, len(gpDataArray))):

						if gpDataArray[gpDataCurrentRowIndex][gpTrxNumberColumnIndex][2:7] == dailyDepositsCurrentRow[dailyDepositsTransactionIDColumnIndex]:
							comparisonArray[comparisonCurrentRowIndex] = comparisonArray[comparisonCurrentRowIndex] + gpDataArray[gpDataCurrentRowIndex]
							comparisonArray[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched from Daily Deposits file'


	
	clearAndResizeParameters = [{
		'sheetObj': gspComparison,
		'resizeRows': 3,
		'startingRowIndexToClear': 0,
		'resizeColumns': 3
	},
	{
		'sheetObj': gspEndingGP,
		'resizeRows': 2,
		'startingRowIndexToClear': 5,
		'resizeColumns': 3
	}]


	gspComparison.clear_basic_filter()
	gspEndingGP.clear_basic_filter()
	_myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)

	_myGspreadFunc.updateCells(gspComparison, comparisonArray)


	gpDataArray.insert(0, gpDataFirstRow)
	_myGspreadFunc.updateCells(gspEndingGP, gpDataArray)


	gspComparison.set_basic_filter(2, 1, len(comparisonArray), len(comparisonArray[0]))
	gspEndingGP.set_basic_filter(1, 1, len(gpDataArray), len(gpDataArray[0]))

	_myGspreadFunc.autoResizeColumnsOnSheet(gspSpreadsheet, 'bankData')
	_myGspreadFunc.autoResizeColumnsOnSheet(gspSpreadsheet, 'gpData')
	_myGspreadFunc.autoResizeColumnsOnSheet(gspSpreadsheet, 'bankGPComparisonData')
	_myGspreadFunc.autoResizeColumnsOnSheet(gspSpreadsheet, 'endingGPData')




	# strToReturn = os.environ.get('urlOfKingGorillaGoogleSheetPublicStr')

	# if not strToReturn:

	# 	pathToConfigDataJSON = Path(pathToRepos, 'privateData', 'herokuGorilla', 'configData.json')
	# 	jsonFileObj = open(pathToConfigDataJSON)
	# 	strToReturn = json.load(jsonFileObj)['urlOfKingGorillaGoogleSheetPublicStr']
	
	# strToReturn = strToReturn[:-1] + '871892682'

	# return strToReturn
