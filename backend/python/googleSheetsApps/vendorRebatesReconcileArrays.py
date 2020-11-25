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
	spreadsheetLevelObj = myGspreadFunc.getSpreadsheetLevelObj(oAuthMode, pathBelowRepos, googleAccountUsername=googleAccountUsername).open(googleSheetTitle)
	endingExtractedFilenamesSheet = spreadsheetLevelObj.worksheet('endingExtractedFilenames')
	comparisonSheet = spreadsheetLevelObj.worksheet('Comparison')

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


	def mapGPTransactions(currentRowIndex, currentRow):
		if currentRowIndex == 0:
			currentRow.append('Amount')
		else:
			currentRow.append(float(currentRow[gpTransactionsDebitColumnIndex].replace(',', '')) - float(currentRow[gpTransactionsCreditColumnIndex].replace(',', '')))
			currentRow[gpTransactionsDateColumnIndex] = myPyFunc.dateStrToStr(currentRow[gpTransactionsDateColumnIndex])
			
			for column in [gpTransactionsDebitColumnIndex, gpTransactionsCreditColumnIndex, gpTransactionsAmountColumnIndex]:
				if isinstance(currentRow[column], str):
					currentRow[column] = float(currentRow[column].replace(',', ''))

	gpTransactions = myPyFunc.mapArray(mapGPTransactions, gpTransactions)
	gpTransactionsFirstRow = gpTransactions.pop(0)

	def mapExtractedFilenames(currentRowIndex, currentRow):

		if currentRowIndex > 0:
			currentRow[extractedFilenamesAmountColumnIndex] = -float(currentRow[extractedFilenamesAmountColumnIndex].replace(',', ''))
			# currentRowDateStr = currentRow[extractedFilenamesDateColumnIndex]
			# p(currentRowDateStr[6:8])
			# currentRowDateObj = datetime(int(currentRowDate[0:4]), int(currentRowDate[6:8]), int(currentRowDate[4:6]))
			# currentRow[extractedFilenamesDateColumnIndex] = f"{currentRowDateObj.day}/{currentRowDateObj.month}/{currentRowDateObj.strftime('%y')}"

	extractedFilenames = myPyFunc.mapArray(mapExtractedFilenames, extractedFilenames)
	extractedFilenamesFirstRow = extractedFilenames.pop(0)


	comparedTransactions = [['GP Transactions'] + [''] * (len(gpTransactionsFirstRow)) + ['Extracted Filenames'] + [''] * (len(extractedFilenamesFirstRow) - 1)]
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
		'sheetObj': comparisonSheet,
		'resizeRows': 3,
		'startingRowIndexToClear': 0,
		'resizeColumns': 1
	},
	{
		'sheetObj': endingExtractedFilenamesSheet,
		'resizeRows': 2,
		'startingRowIndexToClear': 0,
		'resizeColumns': 1
	}]


	myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)

	extractedFilenames.insert(0, extractedFilenamesFirstRow)
	myGspreadFunc.displayArray(endingExtractedFilenamesSheet, extractedFilenames)
	myGspreadFunc.displayArray(comparisonSheet, comparedTransactions)

	myGspreadFunc.setFiltersOnSpreadsheet(spreadsheetLevelObj, {'Comparison': 2})
	numberFormatObj = {'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0.00;(#,##0.00)'}}

	formatParameters = [
		{
			'sheetName': 'Comparison',
			'formatRanges': ['F:F', 'G:G', 'M:M', 'Q:Q'],
			'formatObj': numberFormatObj
		},
		{
			'sheetName': 'endingExtractedFilenames',
			'formatRanges': ['C:C'],
			'formatObj': numberFormatObj
		}
	]

	myGspreadFunc.updateFormatting(spreadsheetLevelObj, formatParameters)
	myGspreadFunc.autoAlignColumnsInSpreadsheet(spreadsheetLevelObj)


def mainFunction(arrayOfArguments):
    reconcileArrays(True, arrayOfArguments[1], googleAccountUsername=arrayOfArguments[2])


if __name__ == '__main__':
    p(str(pathToThisPythonFile.name) + ' is not being imported. It is being run directly...')
    mainFunction(sys.argv)
else:
	p(str(pathToThisPythonFile.name) + ' is being imported. It is not being run directly...')