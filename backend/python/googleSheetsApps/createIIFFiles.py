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



def createIIFFilesFunction(oAuthMode, googleSheetTitle):

	pathToRepos = _myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
	pathToThisProjectRoot = pathToThisPythonFile.parents[3]
	gspObj = _myGspreadFunc.authorizeGspread(oAuthMode, pathToThisProjectRoot)

	gspSpreadsheet = gspObj.open(googleSheetTitle)
	gspInput = gspSpreadsheet.worksheet('Input')
	gspOutput = gspSpreadsheet.worksheet('Output')
	inputArray = gspInput.get_all_values()
	outputArray = gspOutput.get_all_values()
	del outputArray[3:]

	outputArray.append([''])


	for inputRow in inputArray[1:]:

		# transactionDate = datetime.strptime(inputRow[10], '%d-%b-%y').strftime('%#m/%#d/%Y')
		transactionDate = datetime.strptime('21-Jun-20', '%d-%b-%y').strftime('%#m/%#d/%Y')
		transactionDebitAmount = float(inputRow[13])
		transactionCreditAmount = -float(inputRow[13])
		transactionDebitAccount = '"Checking"'
		transactionCreditAccount = '"Income:Rental Income/San  Diego Apts.:San Diego 4"'

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



	_myGspreadFunc.updateCells(gspOutput, outputArray)