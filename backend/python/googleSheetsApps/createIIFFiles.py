from datetime import date, datetime
# import json
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



def createIIFFilesFunction(oAuthMode, googleSheetTitle, loadSavedCredentials=True, listingService='Airbnb'):

	# pathToRepos = _myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
	pathToThisProjectRoot = pathToThisPythonFile.parents[3]
	gspObj = _myGspreadFunc.authorizeGspread(oAuthMode, pathToThisProjectRoot, loadSavedCredentials)

	gspSpreadsheet = gspObj.open(googleSheetTitle)
	gspInput = gspSpreadsheet.worksheet('Input')
	gspOutput = gspSpreadsheet.worksheet('Output')
	gspMap = gspSpreadsheet.worksheet('Map')
	inputArray = gspInput.get_all_values()
	outputArray = gspOutput.get_all_values()
	mapArray = gspMap.get_all_values()

	del outputArray[3:]
	outputArray.append([''])


	for inputRow in inputArray[1:]:

		if listingService == 'Airbnb':

			transactionDate = inputRow[0]
			transactionAmount = float(inputRow[10].replace(',', ''))
			transactionDebitAmount = transactionAmount
			transactionCreditAmount = -transactionAmount
			transactionDebitAccount = '"Checking"'
			transactionDescription = 'Confirmation Code: ' + inputRow[2]
			transactionMemo = inputRow[7]

			for mapArrayRow in mapArray[1:]:
				if mapArrayRow[0] == inputRow[6]:
					transactionCreditAccount = '"' + mapArrayRow[1] + '"'


			dataToWrite = 	[
								['TRNS', '', 'General Journal', transactionDate, transactionDebitAccount, '', transactionDescription, transactionDebitAmount, '', transactionMemo],
								['SPL', '', 'General Journal', transactionDate, transactionCreditAccount, '', transactionDescription, transactionCreditAmount, '', transactionMemo],
								['ENDTRNS']
							]

			for rowFromInputIndex, rowFromInput in enumerate(dataToWrite):
				rowToWrite = []

				for columnFromInputIndex, columnFromInput in enumerate(rowFromInput):
					rowToWrite.append(dataToWrite[rowFromInputIndex][columnFromInputIndex])

				outputArray.append(rowToWrite)




		if listingService == 'VRBO':

			transactionDate = datetime.strptime('21-Jun-20', '%d-%b-%y').strftime('%#m/%#d/%Y')
			transactionDebitAmount = float(inputRow[13])
			transactionCreditAmount = -float(inputRow[13])
			transactionDebitAccount = '"Checking"'
			transactionCreditAccount = '"' + 'Income:Rental Income/San  Diego Apts.:San Diego 4' + '"'

			dataToWrite = 	[
								['TRNS', '', 'General Journal', transactionDate, transactionDebitAccount, '', 'Custom description...', transactionDebitAmount, '', 'Custom memo...'],
								['SPL', '', 'General Journal', transactionDate, transactionCreditAccount, '', 'Custom description...', transactionCreditAmount, '', 'Custom memo...'],
								['ENDTRNS']
							]

			for rowFromInputIndex, rowFromInput in enumerate(dataToWrite):
				rowToWrite = []

				for columnFromInputIndex, columnFromInput in enumerate(rowFromInput):
					rowToWrite.append(dataToWrite[rowFromInputIndex][columnFromInputIndex])

				outputArray.append(rowToWrite)




	clearAndResizeParameters = [{
		'sheetObj': gspOutput,
		'resizeRows': 3,
		'startingRowIndexToClear': 3,
	}]

	_myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)
	_myGspreadFunc.updateCells(gspOutput, outputArray)
	_myGspreadFunc.autoResizeColumnsOnSheet(gspSpreadsheet, 'Output')