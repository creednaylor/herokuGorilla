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
	gspOutputHFLP = gspSpreadsheet.worksheet('Output - HFLP')
	gspOutputWAFCO = gspSpreadsheet.worksheet('Output - WAFCO')
	gspHostFeesMap = gspSpreadsheet.worksheet('Map - Host Fees')
	gspRentRevenueMap = gspSpreadsheet.worksheet('Map - Listing')
	gspPayoutMap = gspSpreadsheet.worksheet('Map - Details')

	inputArray = gspInput.get_all_values()
	outputArrayHFLP = gspOutputHFLP.get_all_values()
	outputArrayWAFCO = gspOutputWAFCO.get_all_values()
	rentRevenueMapArray = gspRentRevenueMap.get_all_values()
	hostFeesMapArray = gspHostFeesMap.get_all_values()
	payoutMapArray = gspPayoutMap.get_all_values()

	for outputArray in [outputArrayHFLP, outputArrayWAFCO]:
		del outputArray[3:]
		outputArray.append([''])


	def writeData(dataToWrite, payoutDate, memoForQuickBooks, outputArray):

		for dataToWriteRowIndex in range(0, len(dataToWrite)):

			rowToWrite = []
			currentDataToWriteRow = dataToWrite[dataToWriteRowIndex]

			for dataToWriteColumnIndex in range(0, len(currentDataToWriteRow)):

				if dataToWriteRowIndex != 0 and dataToWriteColumnIndex == 0:
					rowToWrite.append('SPL')
				elif dataToWriteColumnIndex == 3:
					rowToWrite.append(payoutDate)
				elif dataToWriteColumnIndex == 9:
					rowToWrite.append(memoForQuickBooks)
				else:
					rowToWrite.append(currentDataToWriteRow[dataToWriteColumnIndex])

			outputArray.append(rowToWrite)

		outputArray.append(['ENDTRNS'])

		return outputArray


	def findTextInArrayOfArrays(textToFind, arrayOfArrays):

		# p(arrayOfArrays)
		for array in arrayOfArrays:
			for item in array:
				if isinstance(item, str) and textToFind in item:
					return True
		
		return False



	dataToWrite = []


	for inputRowIndex in range(1, len(inputArray)):

		inputRow = inputArray[inputRowIndex] 

		if listingService == 'Airbnb':

			if inputRow[1] == 'Payout':

				if dataToWrite:
					
					if findTextInArrayOfArrays('Rental Income:Hawaii Property', dataToWrite):

						# for row in outputArrayWAFO:
						# 	if 'Hawaii Nalo Road:Rental Income - Goes To WAFCO' == row[4]:
						# 		row[4] = 'Hawaii Nalo Road:Rental Income'

						outputArrayWAFCO = writeData(dataToWrite, payoutDate, memoForQuickBooks, outputArrayWAFCO)

					else:
						outputArrayHFLP = writeData(dataToWrite, payoutDate, memoForQuickBooks, outputArrayHFLP)


					dataToWrite = []

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
	
			memoForQuickBooks = 'Imported From IIF File; Confirmation Code: ' + inputRow[2] + '; Guest Name: ' + inputRow[5] + ';'

			if inputRow[2] == '':
				memoForQuickBooks = 'Imported From IIF File;'


			if inputRow[12] == '':
				hostFeeAmount = float('0'.replace(',', ''))
			else:
				hostFeeAmount = float(inputRow[12].replace(',', ''))
				dataToWrite.append(['TRNS', '', 'General Journal', '', hostFeesAccount, 'AirBNB', '', hostFeeAmount, '', ''])

			if inputRow[10] == '':
				inputRow[10] = '0'
			transactionAmount = float(inputRow[10].replace(',', ''))

			if inputRow[11] == '':
				inputRow[11] = '0'
			paidOutAmount = float(inputRow[11].replace(',', ''))

			dataToWrite.append(['TRNS', '', 'General Journal', '', transactionAccount, 'AirBNB', '', paidOutAmount - transactionAmount - hostFeeAmount, '', ''])
			
			if inputRowIndex == len(inputArray) - 1:

				if 1 == 1:
					outputArrayHFLP = writeData(dataToWrite, payoutDate, memoForQuickBooks, outputArrayHFLP)
				else:
					outputArrayWAFCO = writeData(dataToWrite, payoutDate, memoForQuickBooks, outputArrayWAFCO)



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

				outputArrayHFLP.append(rowToWrite)




	clearAndResizeParameters = [{
		'sheetObj': gspOutputHFLP,
		'resizeRows': 3,
		'startingRowIndexToClear': 3,
	},
	{
		'sheetObj': gspOutputWAFCO,
		'resizeRows': 3,
		'startingRowIndexToClear': 3,
	}]

	_myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)
	_myGspreadFunc.updateCells(gspOutputHFLP, outputArrayHFLP)
	_myGspreadFunc.updateCells(gspOutputWAFCO, outputArrayWAFCO)
	_myGspreadFunc.autoResizeColumnsOnSheet(gspSpreadsheet, 'Output - HFLP')
	_myGspreadFunc.autoResizeColumnsOnSheet(gspSpreadsheet, 'Output - WAFCO')




