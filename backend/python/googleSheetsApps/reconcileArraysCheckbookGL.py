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

	pathToRepos = myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
	pathToThisProjectRoot = pathToThisPythonFile.parents[3]
	gspObj = myGspreadFunc.authorizeGspread(oAuthMode, pathToThisProjectRoot, googleAccountUsername=googleAccountUsername)


	spacingColumnIndex = 18

	gspSpreadsheet = gspObj.open(googleSheetTitle)
	gspGL = gspSpreadsheet.worksheet('GL')
	gspCheckbook = gspSpreadsheet.worksheet('Checkbook')
	gspComparison = gspSpreadsheet.worksheet('Comparison')
	gspEnding = gspSpreadsheet.worksheet('Ending')



	checkbookTrxDateColumnIndex = 1
	checkbookAmountColumnIndex = 5
	checkbookTrxTypeColumnIndex = 11
	checkbookTrxNumberColumnIndex = 12
	checkbookPaidToReceivedFromColumnIndex = 14
	checkbookTransferColumnIndex = 17
	
	checkbookArray = gspCheckbook.get_all_values()
	checkbookArray = [currentRow for currentRow in checkbookArray if currentRow[checkbookTrxDateColumnIndex] not in ['']]

	glArray = gspGL.get_all_values()



	# glStatusCol = 0

	# glTransactionTypeColumnIndex = 7
	# glAmountColumnIndex = 9
	# glDescriptionTwoColumnIndex = 11

	glTrxDateColumnIndex = 2
	glDebitColumnIndex = 5
	glCreditColumnIndex = 6
	glAmountColumnIndex = len(glArray[0])

	def addAmountColumn(currentRow):

		if currentRow[glTrxDateColumnIndex] != 'TRX Date':
			currentRow[glTrxDateColumnIndex] = str(datetime.strptime(currentRow[glTrxDateColumnIndex], '%m/%d/%Y'))

		try:
			currentRow.append(float(currentRow[glDebitColumnIndex].replace(',', '')) - float(currentRow[glCreditColumnIndex].replace(',', '')))
		except:
			currentRow.append('')			

		return currentRow


	glArray = [addAmountColumn(currentRow) for currentRow in glArray]
	glArray[0][len(glArray[0]) - 1] = 'Amount'



	for currentRowIndex, currentRow in enumerate(checkbookArray):
		if currentRowIndex == 0:
			currentRow.append('Transfer')
		else:
			currentRow[checkbookAmountColumnIndex] = float(currentRow[checkbookAmountColumnIndex].replace(',', ''))
			currentRow[checkbookTrxDateColumnIndex] = str(datetime.strptime(currentRow[checkbookTrxDateColumnIndex], '%m/%d/%Y'))

			if currentRow[checkbookPaidToReceivedFromColumnIndex]:
				if currentRow[checkbookPaidToReceivedFromColumnIndex][0:11] == 'Transfer To':
					currentRow.append('Out')
				if currentRow[checkbookPaidToReceivedFromColumnIndex][0:13] == "Transfer From":
					currentRow.append('In')
			if len(currentRow) == checkbookTransferColumnIndex:
				currentRow.append('')

			if currentRow[checkbookTrxTypeColumnIndex]:
				if not currentRow[checkbookTransferColumnIndex]:
					if currentRow[checkbookTrxTypeColumnIndex] in ['Increase Adjustment', 'Deposit']:
						currentRow[checkbookTransferColumnIndex] = "In"
					if currentRow[checkbookTrxTypeColumnIndex] in ['Decrease Adjustment', 'Withdrawl', 'Check']:
						currentRow[checkbookTransferColumnIndex] = "Out"

		if currentRow[checkbookTransferColumnIndex] == 'Out':
			currentRow[checkbookAmountColumnIndex] = -currentRow[checkbookAmountColumnIndex]


	checkbookFirstRow = checkbookArray.pop(0)
	glFirstRow = glArray.pop(0)
	


	comparisonArray = [['Checkbook'] + [''] * (len(checkbookArray[0])) + ['GL'] + [''] * (len(glArray[0]) - 1)]
	comparisonArray.append(checkbookFirstRow + ['Match Status'] + glFirstRow)



	while checkbookArray:

		checkbookCurrentRow = checkbookArray.pop(0)
		rowToAppend = checkbookCurrentRow + ['']

		glCurrentRowIndex = 0

		while glCurrentRowIndex in range(0, len(glArray) - 1) and len(rowToAppend) == len(checkbookCurrentRow) + 1:

			glRowsThatMatchComparisonCurrentRow = []
			glCurrentRow = glArray[glCurrentRowIndex]

			if glCurrentRow[glAmountColumnIndex] == checkbookCurrentRow[checkbookAmountColumnIndex]:

				if glCurrentRow[glTrxDateColumnIndex] == checkbookCurrentRow[checkbookTrxDateColumnIndex]:
        
					glRowsThatMatchComparisonCurrentRow.append({
							'glDataRowIndex': glCurrentRowIndex,
							'glDataRow': glCurrentRow})

					if glCurrentRow[glAmountColumnIndex] == -2191.7:
						p(1)

					# glDataRowToAppend = glArray.pop(glCurrentRowIndex)
					# rowToAppend = rowToAppend + glDataRowToAppend
					# rowToAppend[spacingColumnIndex] = 'Matched on amount and date'

			if len(glRowsThatMatchComparisonCurrentRow) == 1:

				glDataRowToAppend = glArray.pop(glRowsThatMatchComparisonCurrentRow[0]['glDataRowIndex'])
				rowToAppend = rowToAppend + glDataRowToAppend
				rowToAppend[spacingColumnIndex] = 'Matched on amount and date'	

			glCurrentRowIndex = glCurrentRowIndex + 1

		comparisonArray.append(rowToAppend)


	for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(comparisonArray):

		if len(comparisonCurrentRow) == len(checkbookFirstRow) + 1:

			glRowsThatMatchComparisonCurrentRow = []
			
			for glCurrentRowIndex, glCurrentRow in enumerate(glArray):

				if comparisonCurrentRow[checkbookAmountColumnIndex] == glCurrentRow[glAmountColumnIndex]: 

					glRowsThatMatchComparisonCurrentRow.append({
						'glDataRowIndex': glCurrentRowIndex,
						'glDataRow': glCurrentRow})

			if len(glRowsThatMatchComparisonCurrentRow) == 1:

				comparisonArray[comparisonCurrentRowIndex] = comparisonArray[comparisonCurrentRowIndex] + glArray.pop(glRowsThatMatchComparisonCurrentRow[0]['glDataRowIndex'])
				comparisonArray[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched on amount'
			


	# for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(comparisonArray):

	# 	if len(comparisonCurrentRow) == len(glDataFirstRow) + 1 and comparisonCurrentRow[glTransactionTypeColumnIndex] != 'Check(s) Paid':

	# 		glRowsThatMatchComparisonCurrentRow = []

	# 		# if comparisonCurrentRow[glAmountColumnIndex] == -1100.48:
	# 		# 	p(1)
			
	# 		for checkbookCurrentRowIndex in reversed(range(0, len(checkbookArray))):

	# 			if comparisonCurrentRow[glAmountColumnIndex] == checkbookArray[checkbookCurrentRowIndex][glAmountColumnIndex]:

	# 				if checkbookArray[checkbookCurrentRowIndex][glTrxTypeColumnIndex] != 'Check' or (checkbookArray[checkbookCurrentRowIndex][glTrxTypeColumnIndex] == 'Check' and len(checkbookArray[checkbookCurrentRowIndex][glTrxNumberColumnIndex])!= 5):

	# 					glRowsThatMatchComparisonCurrentRow.append({
	# 						'glDataRowIndex': checkbookCurrentRowIndex,
	# 						'glDataRow': checkbookArray[checkbookCurrentRowIndex]})

	# 		if len(glRowsThatMatchComparisonCurrentRow) == 1:
	# 			comparisonArray[comparisonCurrentRowIndex] = comparisonArray[comparisonCurrentRowIndex] + checkbookArray.pop(glRowsThatMatchComparisonCurrentRow[0]['glDataRowIndex'])
	# 			comparisonArray[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched on amount, 1 gl row with 1 gl row'

	# 		if len(glRowsThatMatchComparisonCurrentRow) > 1:

	# 			comparisonRowsThatMatchComparisonCurrentRow = []
    
	# 			for comparisonDuplicateRowIndex, comparisonDuplicateRow in enumerate(comparisonArray):
        
	# 				if comparisonDuplicateRow[glAmountColumnIndex] == comparisonCurrentRow[glAmountColumnIndex] and len(comparisonDuplicateRow) == len(glDataFirstRow) + 1:
						
	# 					comparisonRowsThatMatchComparisonCurrentRow.insert(0, {
	# 						'comparisonDuplicateRowIndex': comparisonDuplicateRowIndex,
	# 						'comparisonDuplicateRow': comparisonDuplicateRow
	# 					})

	# 			glRowsThatMatchLength = len(glRowsThatMatchComparisonCurrentRow)			
    
	# 			if glRowsThatMatchLength == len(comparisonRowsThatMatchComparisonCurrentRow):
					
	# 				for comparisonDuplicateMatchedRowIndex in range(0, len(comparisonRowsThatMatchComparisonCurrentRow)):
						
	# 					comparisonArray[comparisonRowsThatMatchComparisonCurrentRow[comparisonDuplicateMatchedRowIndex]['comparisonDuplicateRowIndex']] = comparisonArray[comparisonRowsThatMatchComparisonCurrentRow[comparisonDuplicateMatchedRowIndex]['comparisonDuplicateRowIndex']] + checkbookArray.pop(glRowsThatMatchComparisonCurrentRow[comparisonDuplicateMatchedRowIndex]['glDataRowIndex'])
	# 					comparisonArray[comparisonRowsThatMatchComparisonCurrentRow[comparisonDuplicateMatchedRowIndex]['comparisonDuplicateRowIndex']][spacingColumnIndex] = f'Matched on amount, {glRowsThatMatchLength} gl rows with {glRowsThatMatchLength} gl rows'
		


	# for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(comparisonArray):

	# 	if len(comparisonCurrentRow) == len(glDataFirstRow) + 1 and comparisonCurrentRow[glTransactionTypeColumnIndex] != 'Check(s) Paid':
	# 		# p(comparisonCurrentRow)

	# 		for dailyDepositsCurrentRow in dailyDepositsArray:
				
	# 			if comparisonCurrentRow[glAmountColumnIndex] == dailyDepositsCurrentRow[dailyDepositsAmountColumnIndex]:
					
	# 				glRowsThatMatchComparisonCurrentRow = []

	# 				for checkbookCurrentRowIndex in reversed(range(0, len(checkbookArray))):

	# 					if checkbookArray[checkbookCurrentRowIndex][glTrxNumberColumnIndex][2:7] == dailyDepositsCurrentRow[dailyDepositsTransactionIDColumnIndex]:
	# 						comparisonArray[comparisonCurrentRowIndex] = comparisonArray[comparisonCurrentRowIndex] + checkbookArray[checkbookCurrentRowIndex]
	# 						comparisonArray[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched from Daily Deposits file'


	# for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(comparisonArray):

	# 	if len(comparisonCurrentRow) == len(glDataFirstRow) + 1 and comparisonCurrentRow[glTransactionTypeColumnIndex] == 'Check(s) Paid':
    
	# 		glRowsThatMatchComparisonCurrentRow = []
			
	# 		for checkbookCurrentRowIndex, checkbookCurrentRow in enumerate(checkbookArray):

	# 			if comparisonCurrentRow[glAmountColumnIndex] == checkbookCurrentRow[glAmountColumnIndex] and comparisonCurrentRow[glDateColumnIndex] == checkbookCurrentRow[glTrxDateColumnIndex]: 

	# 				glRowsThatMatchComparisonCurrentRow.append({
	# 					'glDataRowIndex': checkbookCurrentRowIndex,
	# 					'glDataRow': checkbookCurrentRow})

	# 		if len(glRowsThatMatchComparisonCurrentRow) == 1:

	# 			comparisonArray[comparisonCurrentRowIndex] = comparisonArray[comparisonCurrentRowIndex] + checkbookArray.pop(glRowsThatMatchComparisonCurrentRow[0]['glDataRowIndex'])
	# 			comparisonArray[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched on amount and date, gl transaction is a check, gl transaction does not have the same check number'


	clearAndResizeParameters = [{
		'sheetObj': gspComparison,
		'resizeRows': 3,
		'startingRowIndexToClear': 0,
		'resizeColumns': 3
	},
	{
		'sheetObj': gspEnding,
		'resizeRows': 2,
		'startingRowIndexToClear': 0,
		'resizeColumns': 1
	}]


	gspComparison.clear_basic_filter()
	gspEnding.clear_basic_filter()
	myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)

	myGspreadFunc.updateCells(gspComparison, comparisonArray)


	glArray.insert(0, glFirstRow)
	myGspreadFunc.updateCells(gspEnding, glArray)


	gspComparison.set_basic_filter(2, 1, len(comparisonArray), len(comparisonArray[0]) + 1)
	gspEnding.set_basic_filter(1, 1, len(glArray), len(glArray[0]))

	myGspreadFunc.autoResizeColumnsOnSheet(gspSpreadsheet, 'Checkbook')
	myGspreadFunc.autoResizeColumnsOnSheet(gspSpreadsheet, 'GL')
	myGspreadFunc.autoResizeColumnsOnSheet(gspSpreadsheet, 'Comparison')
	myGspreadFunc.autoResizeColumnsOnSheet(gspSpreadsheet, 'Ending')




def mainFunction(arrayOfArguments):
    reconcileArrays(True, arrayOfArguments[1], googleAccountUsername=arrayOfArguments[2])


if __name__ == '__main__':
    p(str(pathToThisPythonFile.name) + ' is not being imported. It is being run directly...')
    mainFunction(sys.argv)
else:
	p(str(pathToThisPythonFile.name) + ' is being imported. It is not being run directly...')