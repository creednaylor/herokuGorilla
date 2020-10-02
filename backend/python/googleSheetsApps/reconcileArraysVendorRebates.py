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

	extractedFilenames = spreadsheetLevelObj.worksheet('extractedFilenames').get_all_values()
	gpTransactions = spreadsheetLevelObj.worksheet('gpTransactions').get_all_values()

	gpTransactionsDebitColumnIndex = 5
	gpTransactionsCreditColumnIndex = gpTransactionsDebitColumnIndex + 1
	gpTransactionsAmountColumnIndex = 12
	gpTransactionsVendorColumnIndex = 9
	gpTransactionsDateColumnIndex = 2
	spacingColumnIndex = gpTransactionsAmountColumnIndex + 1
	extractedFilenamesAmountColumnIndex = 2
	extractedFilenamesVendorColumnIndex = 1
	extractedFilenamesDateColumnIndex = 0


	def transformGPTransactions(currentRowIndex, currentRow):
		if currentRowIndex == 0:
			currentRow.append('Amount')
		else:
			currentRow.append(float(currentRow[gpTransactionsDebitColumnIndex].replace(',', '')) - float(currentRow[gpTransactionsCreditColumnIndex].replace(',', '')))
			currentRowDateArray = currentRow[gpTransactionsDateColumnIndex].split('/')
			currentRow[gpTransactionsDateColumnIndex] = currentRowDateArray[2] + currentRowDateArray[0].zfill(2) + currentRowDateArray[1].zfill(2)

	gpTransactions = myPyFunc.repeatActionOnArray(gpTransactions, transformGPTransactions)
	gpTransactionsFirstRow = gpTransactions.pop(0)

	def transformExtractedFilenames(currentRowIndex, currentRow):

		if currentRowIndex > 0:
			currentRow[extractedFilenamesAmountColumnIndex] = float(currentRow[extractedFilenamesAmountColumnIndex].replace(',', ''))
			# currentRowDateStr = currentRow[extractedFilenamesDateColumnIndex]
			# p(currentRowDateStr[6:8])
			# currentRowDateObj = datetime(int(currentRowDate[0:4]), int(currentRowDate[6:8]), int(currentRowDate[4:6]))
			# currentRow[extractedFilenamesDateColumnIndex] = f"{currentRowDateObj.day}/{currentRowDateObj.month}/{currentRowDateObj.strftime('%y')}"

	extractedFilenames = myPyFunc.repeatActionOnArray(extractedFilenames, transformExtractedFilenames)
	extractedFilenamesFirstRow = extractedFilenames.pop(0)


	comparedTransactions = [['GP Transactions'] + [''] * (len(gpTransactions[0])) + ['Extracted Filenames'] + [''] * (len(extractedFilenames[0]) - 1)]
	comparedTransactions.append(gpTransactionsFirstRow + ['Match Status'] + extractedFilenamesFirstRow)


	while gpTransactions:

		gpTransactionsCurrentRow = gpTransactions.pop(0)
		rowToAppend = gpTransactionsCurrentRow + ['']

		extractedFilenamesCurrentRowIndex = 0

		while extractedFilenamesCurrentRowIndex in range(0, len(extractedFilenames) - 1) and len(rowToAppend) == len(gpTransactionsCurrentRow) + 1:

			extractedFilenamesCurrentRow = extractedFilenames[extractedFilenamesCurrentRowIndex]

			if gpTransactionsCurrentRow[gpTransactionsAmountColumnIndex] == extractedFilenamesCurrentRow[extractedFilenamesAmountColumnIndex] and gpTransactionsCurrentRow[gpTransactionsVendorColumnIndex] == extractedFilenamesCurrentRow[extractedFilenamesVendorColumnIndex] and gpTransactionsCurrentRow[gpTransactionsDateColumnIndex] == extractedFilenamesCurrentRow[extractedFilenamesDateColumnIndex]:

				extractedFilenamesRowToAppend = extractedFilenames.pop(extractedFilenamesCurrentRowIndex)
				rowToAppend = rowToAppend + extractedFilenamesRowToAppend
				rowToAppend[spacingColumnIndex] = 'Matched on amount, vendor, and date'

			extractedFilenamesCurrentRowIndex = extractedFilenamesCurrentRowIndex + 1

		comparedTransactions.append(rowToAppend)


	for comparedTransactionsCurrentRowIndex, comparedTransactionsCurrentRow in enumerate(comparedTransactions):

		if len(comparedTransactionsCurrentRow) == len(gpTransactionsFirstRow) + 1:

			gpTransactionsRowsThatMatchComparedTransactionsCurrentRow = []
			
			for extractedFilenamesCurrentRowIndex, extractedFilenamesCurrentRow in enumerate(extractedFilenames):

				if comparedTransactionsCurrentRow[gpTransactionsAmountColumnIndex] == extractedFilenamesCurrentRow[extractedFilenamesAmountColumnIndex] and comparedTransactionsCurrentRow[gpTransactionsVendorColumnIndex] == extractedFilenamesCurrentRow[extractedFilenamesVendorColumnIndex]:
        
					gpTransactionsRowsThatMatchComparedTransactionsCurrentRow.append({
						'extractedFilenamesRowIndex': extractedFilenamesCurrentRowIndex,
						'extractedFilenamesRow': extractedFilenamesCurrentRow})

			if len(gpTransactionsRowsThatMatchComparedTransactionsCurrentRow) == 1:

				comparedTransactions[comparedTransactionsCurrentRowIndex] = comparedTransactions[comparedTransactionsCurrentRowIndex] + extractedFilenames.pop(gpTransactionsRowsThatMatchComparedTransactionsCurrentRow[0]['extractedFilenamesRowIndex'])
				comparedTransactions[comparedTransactionsCurrentRowIndex][spacingColumnIndex] = 'Matched on amount and vendor'


	for comparedTransactionsCurrentRowIndex, comparedTransactionsCurrentRow in enumerate(comparedTransactions):

		if len(comparedTransactionsCurrentRow) == len(gpTransactionsFirstRow) + 1:

			gpTransactionsRowsThatMatchComparedTransactionsCurrentRow = []
			
			for extractedFilenamesCurrentRowIndex, extractedFilenamesCurrentRow in enumerate(extractedFilenames):

				if comparedTransactionsCurrentRow[gpTransactionsAmountColumnIndex] == extractedFilenamesCurrentRow[extractedFilenamesAmountColumnIndex]:
        
					gpTransactionsRowsThatMatchComparedTransactionsCurrentRow.append({
						'extractedFilenamesRowIndex': extractedFilenamesCurrentRowIndex,
						'extractedFilenamesRow': extractedFilenamesCurrentRow})

			if len(gpTransactionsRowsThatMatchComparedTransactionsCurrentRow) == 1:

				comparedTransactions[comparedTransactionsCurrentRowIndex] = comparedTransactions[comparedTransactionsCurrentRowIndex] + extractedFilenames.pop(gpTransactionsRowsThatMatchComparedTransactionsCurrentRow[0]['extractedFilenamesRowIndex'])
				comparedTransactions[comparedTransactionsCurrentRowIndex][spacingColumnIndex] = 'Matched on amount'
			


	clearAndResizeParameters = [{
		'sheetObj': spreadsheetLevelObj.worksheet('Comparison'),
		'resizeRows': 3,
		'startingRowIndexToClear': 0,
		'resizeColumns': 1
	},
	{
		'sheetObj': spreadsheetLevelObj.worksheet('endingExtractedFilenames'),
		'resizeRows': 2,
		'startingRowIndexToClear': 0,
		'resizeColumns': 1
	}]


	# sheetLevelComparison.clear_basic_filter()
	# sheetLevelEndingGP.clear_basic_filter()
	myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)

	extractedFilenames.insert(0, extractedFilenamesFirstRow)
	myGspreadFunc.updateCells(spreadsheetLevelObj.worksheet('endingExtractedFilenames'), extractedFilenames)

	myGspreadFunc.updateCells(spreadsheetLevelObj.worksheet('Comparison'), comparedTransactions)


	# sheetLevelComparison.set_basic_filter(2, 1, len(comparedTransactions), len(comparedTransactions[0]) + 1)
	# sheetLevelEndingGP.set_basic_filter(1, 1, len(extractedFilenames), len(extractedFilenames[0]))

	myGspreadFunc.autoResizeColumnsInSpreadsheet(spreadsheetLevelObj)


def mainFunction(arrayOfArguments):
    reconcileArrays(True, arrayOfArguments[1], googleAccountUsername=arrayOfArguments[2])


if __name__ == '__main__':
    p(str(pathToThisPythonFile.name) + ' is not being imported. It is being run directly...')
    mainFunction(sys.argv)
else:
	p(str(pathToThisPythonFile.name) + ' is being imported. It is not being run directly...')