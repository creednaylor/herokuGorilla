#output data to new format


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
	gspObj = _myGspreadFunc.getSpreadsheetLevelObj(oAuthMode, pathToThisProjectRoot, loadSavedCredentials)
	outputSheetName = 'Output'
	outputOtherSheetName = 'Output - Other'

	gspSpreadsheet = gspObj.open(googleSheetTitle)
	gspInput = gspSpreadsheet.worksheet('Input')
	gspOutput = gspSpreadsheet.worksheet(outputSheetName)
	gspOutputOther = gspSpreadsheet.worksheet(outputOtherSheetName)
	gspHostFeesMap = gspSpreadsheet.worksheet('Map - Host Fees')
	gspRentRevenueMap = gspSpreadsheet.worksheet('Map - Listing')
	gspPayoutMap = gspSpreadsheet.worksheet('Map - Details')

	inputArray = gspInput.get_all_values()
	outputArray = gspOutput.get_all_values()
	outputArrayOther = gspOutputOther.get_all_values()
	rentRevenueMapArray = gspRentRevenueMap.get_all_values()
	hostFeesMapArray = gspHostFeesMap.get_all_values()
	payoutMapArray = gspPayoutMap.get_all_values()

	outputSheetFirstRowIndexOfData = 4

	for outputArrayToTrim in [outputArray, outputArrayOther]:
		del outputArrayToTrim[outputSheetFirstRowIndexOfData:]


	def getAdditionalArray(dataToWrite, payoutDate, memoForQuickBooks):

		additionalArray = []
		
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

			additionalArray.append(rowToWrite)

		additionalArray.append(['ENDTRNS'])

		return additionalArray


	def findTextInArrayOfArrays(textToFind, arrayOfArrays):

		for array in arrayOfArrays:
			for item in array:
				if isinstance(item, str) and textToFind in item:
					return True
		
		return False


	dataToWrite = []


	for inputRowIndex in range(1, len(inputArray)):

		inputRow = inputArray[inputRowIndex]

		if listingService == 'Airbnb':

			inputConfirmationColumnIndex = 2
			inputListingColumnIndex = 6
			inputDetailsColumnIndex = 7
			inputAmountColumnIndex = 10
			inputPaidOutColumnIndex = 11
			inputHostFeeColumnIndex = 12

			currentInputConfirmation = inputRow[inputConfirmationColumnIndex]
			currentInputListing = inputRow[inputListingColumnIndex]
			currentInputDetails = inputRow[inputDetailsColumnIndex]
			currentInputAmount = inputRow[inputAmountColumnIndex]
			currentInputPaidOut = inputRow[inputPaidOutColumnIndex]
			currentInputHostFee = inputRow[inputHostFeeColumnIndex]

			if inputRow[1] == 'Payout':

				if dataToWrite:
					
					# textToFind = 'PayPal:PayPal - San Diego'
					textToFind = 'PayPal - PoipuVilla'  #the only rental income that goes to WAFCO is for Poipu Villa
					# textToFind = 'St. George'

					if findTextInArrayOfArrays(textToFind, dataToWrite):
						
						outputArrayOther.extend(getAdditionalArray(dataToWrite, payoutDate, memoForQuickBooks))
						
					else:

						outputArray.extend(getAdditionalArray(dataToWrite, payoutDate, memoForQuickBooks))

					dataToWrite = []

				payoutDate = inputRow[0]

				for payoutMapArrayRow in payoutMapArray[1:]:
					if payoutMapArrayRow[0] == currentInputDetails:
						transactionAccount = '"' + payoutMapArrayRow[1] + '"'
			
			else:

				if currentInputListing == '':
					transactionAccount = 'Need to input manually'

				for rentRevenueMapArrayRow in rentRevenueMapArray[1:]:
					if rentRevenueMapArrayRow[0] == currentInputListing:
						transactionAccount = '"' + rentRevenueMapArrayRow[1] + '"'

				for hostFeesMapArrayRow in hostFeesMapArray[1:]:
					if hostFeesMapArrayRow[0] == currentInputListing:
						hostFeesAccount = '"' + hostFeesMapArrayRow[1] + '"'
	
			memoForQuickBooks = 'Imported From IIF File; Confirmation Code: ' + currentInputConfirmation + '; Guest Name: ' + inputRow[5] + ';'

			if currentInputConfirmation == '':
				memoForQuickBooks = 'Imported From IIF File;'

			if currentInputHostFee == '':
				currentInputHostFee = 0
			else:
				currentInputHostFee = float(currentInputHostFee.replace(',', ''))
				dataToWrite.append(['TRNS', '', 'General Journal', '', hostFeesAccount, 'AirBNB', '', currentInputHostFee, '', ''])

			if currentInputAmount == '':
				currentInputAmount = 0
			else:
				currentInputAmount = float(currentInputAmount.replace(',', ''))

			if currentInputPaidOut == '':
				currentInputPaidOut = 0
			else:
				currentInputPaidOut = float(currentInputPaidOut.replace(',', ''))

			dataToWrite.append(['TRNS', '', 'General Journal', '', transactionAccount, 'AirBNB', '', currentInputPaidOut - currentInputAmount - currentInputHostFee, '', ''])
			
			if inputRowIndex == len(inputArray) - 1:

				if findTextInArrayOfArrays(textToFind, dataToWrite):
					outputArrayOther.extend(getAdditionalArray(dataToWrite, payoutDate, memoForQuickBooks))
				else:
					outputArray.extend(getAdditionalArray(dataToWrite, payoutDate, memoForQuickBooks))



		# if listingService == 'VRBO':

		# 	transactionDate = datetime.strptime('21-Jun-20', '%d-%b-%y').strftime('%#m/%#d/%Y')
		# 	transactionDebitAmount = float(inputRow[13])
		# 	transactionCreditAmount = -float(inputRow[13])
		# 	transactionDebitAccount = '"Checking"'
		# 	transactionCreditAccount = '"' + 'Income:Rental Income/San  Diego Apts.:San Diego 4' + '"'

		# 	dataToWrite = 	[
		# 						['TRNS', '', 'General Journal', transactionDate, transactionDebitAccount, '', 'Custom description...', transactionDebitAmount, '', 'Custom memo...'],
		# 						['SPL', '', 'General Journal', transactionDate, transactionCreditAccount, '', 'Custom description...', transactionCreditAmount, '', 'Custom memo...'],
		# 						['ENDTRNS']
		# 					]

		# 	for dataToWriteRowIndex in range(0, len(dataToWrite)):
		# 		rowToWrite = []
		# 		currentDataToWriteRow = dataToWrite[dataToWriteRowIndex]

		# 		for dataToWriteColumnIndex in range(0, len(currentDataToWriteRow)):
		# 			rowToWrite.append(currentDataToWriteRow[dataToWriteColumnIndex])

		# 		outputArray.append(rowToWrite)


	clearAndResizeParameters = [{
		'sheetObj': gspOutput,
		'resizeRows': outputSheetFirstRowIndexOfData,
		'startingRowIndexToClear': outputSheetFirstRowIndexOfData,
	},
	{
		'sheetObj': gspOutputOther,
		'resizeRows': outputSheetFirstRowIndexOfData,
		'startingRowIndexToClear': outputSheetFirstRowIndexOfData,
	}]

	_myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)
	_myGspreadFunc.displayArray(gspOutput, outputArray)
	_myGspreadFunc.displayArray(gspOutputOther, outputArrayOther)
	_myGspreadFunc.autoResizeColumnsOnSheet(gspSpreadsheet, outputSheetName)
	_myGspreadFunc.autoResizeColumnsOnSheet(gspSpreadsheet, outputOtherSheetName)




