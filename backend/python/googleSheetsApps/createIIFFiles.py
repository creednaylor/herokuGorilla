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

	pathToThisProjectRoot = pathToThisPythonFile.parents[3]
	gspObj = _myGspreadFunc.authorizeGspread(oAuthMode, pathToThisProjectRoot, loadSavedCredentials)

	gspSpreadsheet = gspObj.open(googleSheetTitle)
	gspInput = gspSpreadsheet.worksheet('Input')
	gspOutput = gspSpreadsheet.worksheet('Output')
	gspHostFeesMap = gspSpreadsheet.worksheet('Map - Host Fees')
	gspRentRevenueMap = gspSpreadsheet.worksheet('Map - Listing')
	gspPayoutMap = gspSpreadsheet.worksheet('Map - Details')
	inputArray = gspInput.get_all_values()
	outputArray = gspOutput.get_all_values()
	rentRevenueMapArray = gspRentRevenueMap.get_all_values()
	hostFeesMapArray = gspHostFeesMap.get_all_values()
	payoutMapArray = gspPayoutMap.get_all_values()

	del outputArray[3:]
	outputArray.append([''])

	def writeData(dataToWrite, payoutDate):

		for dataToWriteRowIndex in range(0, len(dataToWrite)):

			rowToWrite = []
			currentDataToWriteRow = dataToWrite[dataToWriteRowIndex]

			for dataToWriteColumnIndex in range(0, len(currentDataToWriteRow)):

				if dataToWriteRowIndex != 0 and dataToWriteColumnIndex == 0:
					rowToWrite.append('SPL')
				elif dataToWriteColumnIndex == 3:
					rowToWrite.append(payoutDate)
				else:
					rowToWrite.append(currentDataToWriteRow[dataToWriteColumnIndex])

			outputArray.append(rowToWrite)

		outputArray.append(['ENDTRNS'])

		return []


	dataToWrite = []


	for inputRowIndex in range(1, len(inputArray)):

		inputRow = inputArray[inputRowIndex] 

		if listingService == 'Airbnb':

			if inputRow[1] == 'Payout':

				if dataToWrite:
					dataToWrite = writeData(dataToWrite, payoutDate)

				payoutDate = inputRow[0]

				for payoutMapArrayRow in payoutMapArray[1:]:
					if payoutMapArrayRow[0] == inputRow[7]:
						transactionAccount = '"' + payoutMapArrayRow[1] + '"'
			
			else:

				if inputRow[6] == '':
					transactionAccount = 'Need to input manually'

				for rentRevenueMapArrayRow in rentRevenueMapArray[1:]:
					if rentRevenueMapArrayRow[0] == inputRow[6]:
						transactionAccount = '"' + rentRevenueMapArrayRow[1] + '"'

				for hostFeesMapArrayRow in hostFeesMapArray[1:]:
					if hostFeesMapArrayRow[0] == inputRow[6]:
						hostFeesAccount = '"' + hostFeesMapArrayRow[1] + '"'
	
			confirmationCode = 'Confirmation Code: ' + inputRow[2] + '; Airbnb Transaction Type: ' + inputRow[1] + '; Guest: ' + inputRow[5] + '; Nights: ' + inputRow[4]	

			if inputRow[2] == '':
				confirmationCode = 'Airbnb Transaction Type: ' + inputRow[1] + '; ' + inputRow[7]


			if inputRow[12] == '':
				hostFeeAmount = float('0'.replace(',', ''))
			else:
				hostFeeAmount = float(inputRow[12].replace(',', ''))
				dataToWrite.append(['TRNS', '', 'General Journal', '', hostFeesAccount, 'AirBNB', '', hostFeeAmount, '', confirmationCode])

			if inputRow[10] == '':
				inputRow[10] = '0'
			transactionAmount = float(inputRow[10].replace(',', ''))

			if inputRow[11] == '':
				inputRow[11] = '0'
			paidOutAmount = float(inputRow[11].replace(',', ''))

			dataToWrite.append(['TRNS', '', 'General Journal', '', transactionAccount, 'AirBNB', '', paidOutAmount - transactionAmount - hostFeeAmount, '', confirmationCode])
			
			if inputRowIndex == len(inputArray) - 1:
				writeData(dataToWrite, payoutDate)




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

			for dataToWriteRowIndex in range(0, len(dataToWrite)):
				rowToWrite = []
				currentDataToWriteRow = dataToWrite[dataToWriteRowIndex]

				for dataToWriteColumnIndex in range(0, len(currentDataToWriteRow)):
					rowToWrite.append(currentDataToWriteRow[dataToWriteColumnIndex])

				outputArray.append(rowToWrite)




	clearAndResizeParameters = [{
		'sheetObj': gspOutput,
		'resizeRows': 3,
		'startingRowIndexToClear': 3,
	}]

	_myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)
	_myGspreadFunc.updateCells(gspOutput, outputArray)
	_myGspreadFunc.autoResizeColumnsOnSheet(gspSpreadsheet, 'Output')




