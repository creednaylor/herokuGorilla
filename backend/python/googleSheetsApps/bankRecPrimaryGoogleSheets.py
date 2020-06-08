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



def bankRecPrimaryFunction(oAuthMode, googleSheetTitle):

	pathToRepos = _myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
	pathToThisProjectRoot = pathToThisPythonFile.parents[3]
	gspObj = _myGspreadFunc.authorizeGspread(oAuthMode, pathToThisProjectRoot)

	gspSpreadsheet = gspObj.open(googleSheetTitle)
	gspBankData = gspSpreadsheet.worksheet('bankData')
	gspGPData = gspSpreadsheet.worksheet('gpData')
	gspComparisonSheet = gspSpreadsheet.worksheet('bankGPComparisonData')
	gspEndingGPSheet = gspSpreadsheet.worksheet('endingGPData')

	bankDataArray = gspBankData.get_all_values()
	gpDataArray = gspGPData.get_all_values()

	bankStatusCol = 0
	bankDateCol = 1
	bankTypeCol = 7
	bankDebitCreditCol = 8
	bankAmountCol = 9
	bankDescTwoCol = 11

	# bankDateCol = 13
	# bankOrigDateCol = 1
	# bankDescCol = 12
	# bankColumns = 12
	
	gpTrxDateCol = 1
	gpAmountCol = 5
	gpTrxTypeCol = 11
	gpTrxNumCol = 12
	gpNameCol = 14
	gpTransferCol = 16
	

	bankDataArray = [currentRow for currentRow in bankDataArray if currentRow[bankStatusCol] not in ['H', 'B', 'T'] and currentRow[bankTypeCol] not in ['Data', 'Ledger Balance', 'Collected + 1 Day', 'Opening Collected', 'One Day Float', '2 Day Float', '3 Day + Float', 'MTD Avg Collected', 'MTD Avg Neg Collected', 'Total Credits', 'Number of Credits', 'Total Debits', 'Number of Debits', 'Float Adjustment(s)']]

	for currentRowIndex, currentRow in enumerate(bankDataArray):
		if currentRowIndex > 0:

			currentRow[bankAmountCol] = float(currentRow[bankAmountCol].replace(',', ''))

			if len(currentRow[bankDateCol]) < 8:
				currentRow[bankDateCol] = '0' + currentRow[bankDateCol]

			currentRow[bankDateCol] = str(datetime.strptime(currentRow[bankDateCol], '%m%d%Y'))

			if currentRow[bankDebitCreditCol] == 'Debit':
				# p(currentRow[bankAmountCol])
				currentRow[bankAmountCol] = -currentRow[bankAmountCol]


	for currentRowIndex, currentRow in enumerate(gpDataArray):
		if currentRowIndex == 0:
			currentRow.append('Transfer')
		else:
			currentRow[gpAmountCol] = float(currentRow[gpAmountCol].replace(',', ''))
			currentRow[gpTrxDateCol] = str(datetime.strptime(currentRow[gpTrxDateCol], '%m/%d/%Y'))

			if currentRow[gpNameCol]:
				if currentRow[gpNameCol][0:11] == 'Transfer To':
					currentRow.append('Out')
				if currentRow[gpNameCol][0:13] == "Transfer From":
					currentRow.append('In')
			if len(currentRow) == 16:
				currentRow.append('')

			if currentRow[gpTrxTypeCol]:
				if not currentRow[gpTransferCol]:
					if currentRow[gpTrxTypeCol] in ['Increase Adjustment', 'Deposit']:
						currentRow[gpTransferCol] = "In"
					if currentRow[gpTrxTypeCol] in ['Decrease Adjustment', 'Withdrawl', 'Check']:
						currentRow[gpTransferCol] = "Out"

		if currentRow[gpTransferCol] == 'Out':
			currentRow[gpAmountCol] = -currentRow[gpAmountCol]
	


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

			if bankDataCurrentRow[bankAmountCol] == gpDataCurrentRow[gpAmountCol]:

				if bankDataCurrentRow[bankTypeCol] == 'Check(s) Paid' and gpDataCurrentRow[gpTrxTypeCol] == 'Check':

					if bankDataCurrentRow[bankDescTwoCol] == gpDataCurrentRow[gpTrxNumCol]:

						gpDataRowToAppend = gpDataArray.pop(gpDataCurrentRowIndex)
						rowToAppend = rowToAppend + gpDataRowToAppend

			gpDataCurrentRowIndex = gpDataCurrentRowIndex + 1

		comparisonArray.append(rowToAppend)



	for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(comparisonArray):

		if len(comparisonCurrentRow) == len(bankDataFirstRow) + 1 and comparisonCurrentRow[bankTypeCol] != 'Check(s) Paid':

			gpRowsThatMatchComparisonCurrentRow = []
			
			for gpDataCurrentRowIndex, gpDataCurrentRow in enumerate(gpDataArray):

				if comparisonCurrentRow[bankAmountCol] == gpDataCurrentRow[gpAmountCol]: # and gpDataCurrentRow[gpTrxTypeCol] != 'Check':

					if gpDataCurrentRow[gpTrxTypeCol] != 'Check' or (gpDataCurrentRow[gpTrxTypeCol] == 'Check' and len(gpDataCurrentRow[gpTrxNumCol])!= 5):
						gpRowsThatMatchComparisonCurrentRow.append({
							'gpDataRowIndex': gpDataCurrentRowIndex,
							'gpDataRow': gpDataCurrentRow})

			if len(gpRowsThatMatchComparisonCurrentRow) == 1 and comparisonCurrentRow[bankDateCol] == gpRowsThatMatchComparisonCurrentRow[0]['gpDataRow'][gpTrxDateCol]:

				comparisonArray[comparisonCurrentRowIndex] = comparisonArray[comparisonCurrentRowIndex] + gpDataArray.pop(gpRowsThatMatchComparisonCurrentRow[0]['gpDataRowIndex'])



	for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(comparisonArray):

		if len(comparisonCurrentRow) == len(bankDataFirstRow) + 1 and comparisonCurrentRow[bankTypeCol] != 'Check(s) Paid':

			gpRowsThatMatchComparisonCurrentRow = []
			
			for gpDataCurrentRowIndex, gpDataCurrentRow in enumerate(gpDataArray):

				if comparisonCurrentRow[bankAmountCol] == gpDataCurrentRow[gpAmountCol]: # and gpDataCurrentRow[gpTrxTypeCol] != 'Check':

					if gpDataCurrentRow[gpTrxTypeCol] != 'Check' or (gpDataCurrentRow[gpTrxTypeCol] == 'Check' and len(gpDataCurrentRow[gpTrxNumCol])!= 5):

						gpRowsThatMatchComparisonCurrentRow.append({
							'gpDataRowIndex': gpDataCurrentRowIndex,
							'gpDataRow': gpDataCurrentRow})

			if len(gpRowsThatMatchComparisonCurrentRow) == 1:

				comparisonArray[comparisonCurrentRowIndex] = comparisonArray[comparisonCurrentRowIndex] + gpDataArray.pop(gpRowsThatMatchComparisonCurrentRow[0]['gpDataRowIndex'])





	
	clearAndResizeParameters = [{
		'sheetObj': gspComparisonSheet,
		'resizeRows': 3,
		'startingRowIndexToClear': 0,
		'resizeColumns': 3
	},
	{
		'sheetObj': gspEndingGPSheet,
		'resizeRows': 2,
		'startingRowIndexToClear': 0,
		'resizeColumns': 1
	}]


	
	_myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)
	_myGspreadFunc.updateCells(gspComparisonSheet, comparisonArray)

	gpDataArray.insert(0, gpDataFirstRow)
	_myGspreadFunc.updateCells(gspEndingGPSheet, gpDataArray)

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
