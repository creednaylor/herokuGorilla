# clear resultArray sheet when opening google sheet...

import json
import os
from pathlib import Path
from pprint import pprint as p
import sys

import gspread

def reconcileArraysFunction(runningOnProductionServerBoolean):

	pathToThisPythonFile = Path(__file__).resolve()

	if runningOnProductionServerBoolean:
		p('********************Running on production server****************')
		from ..myPythonLibrary import _myPyFunc
		from ..googleSheets.myGoogleSheetsLibrary import _myGoogleSheetsFunc
		from ..googleSheets.myGoogleSheetsLibrary import _myGspreadFunc

		loadedEncryptionKey = os.environ.get('savedEncryptionKeyStr', None)
		
	else:
		p('********************Not running on production server****************')

		sys.path.append(str(pathToThisPythonFile.parents[1]))
		from myPythonLibrary import _myPyFunc
		from googleSheets.myGoogleSheetsLibrary import _myGoogleSheetsFunc
		from googleSheets.myGoogleSheetsLibrary import _myGspreadFunc

		pathToRepos = _myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
		loadedEncryptionKey = _myPyFunc.openSavedKey(Path(pathToRepos, 'privateData', 'python', 'encryption', 'savedEncryptionKey.key'))
	

	strToReturn = 'hellowasdf'
	strToReturn = os.environ.get('urlOfKingGorillaGoogleSheetPublicStr')

	if not strToReturn:

		pathToConfigDataJSON = Path(pathToRepos, 'privateData', 'herokuGorilla', 'configData.json')

		jsonFileObj = open(pathToConfigDataJSON)
		strToReturn = json.load(jsonFileObj)['urlOfKingGorillaGoogleSheetPublicStr']
	
	strToReturn = strToReturn[:-1] + '871892682'


	pathToAPIKey = Path(pathToThisPythonFile.parents[2], 'configData', 'encryptedAPIKey.json')
	pathOfDecryptedFile = Path(pathToAPIKey.parents[0], 'decryptedAPIKey.json')
	_myPyFunc.decryptFile(pathToAPIKey, loadedEncryptionKey, pathToSaveDecryptedFile=pathOfDecryptedFile)
		
	gspObj = gspread.service_account(filename=pathOfDecryptedFile)
		
	gspSpreadsheet = gspObj.open('King Gorilla - Public')
	gspFirstTableSheet = gspSpreadsheet.worksheet('firstTable')
	gspSecondTableSheet = gspSpreadsheet.worksheet('secondTable')
	gspComparisonTableSheet = gspSpreadsheet.worksheet('comparisonTable')
	gspEndingSecondTableSheet = gspSpreadsheet.worksheet('endingSecondTable')

	firstArray = gspFirstTableSheet.get_all_values()
	secondArray = gspSecondTableSheet.get_all_values()
	firstArrayFirstRow = firstArray.pop(0)
	secondArrayFirstRow = secondArray.pop(0)


	matchingColumnTitle = ''

	for indexOfColumnIndexFirstArray, columnTitleFirstArray in enumerate(firstArrayFirstRow):
		for indexOfColumnIndexSecondArray, columnTitleSecondArray in enumerate(secondArrayFirstRow):
			if columnTitleFirstArray == columnTitleSecondArray:
				firstArrayColumnIndexToCompare = indexOfColumnIndexFirstArray
				secondArrayColumnIndexToCompare = indexOfColumnIndexSecondArray

	comparisonArray = [['firstTable'] + [''] * (len(firstArray[0])) + ['secondTable'] + [''] * (len(secondArray[0]) - 1)]
	comparisonArray.append(firstArrayFirstRow + [''] + secondArrayFirstRow)
	# p(comparisonArray)


	while firstArray:

		firstArrayCurrentRow = firstArray.pop(0)
		# p(firstArrayCurrentRow)
		rowToAppend = firstArrayCurrentRow + ['']

		for secondArrayRowIndexCount, secondArrayCurrentRow in enumerate(secondArray):

			# p(secondArrayCurrentRow)

			if firstArrayCurrentRow[firstArrayColumnIndexToCompare] == secondArrayCurrentRow[secondArrayColumnIndexToCompare]:

				secondArrayRowToAppend = secondArray.pop(secondArrayRowIndexCount)
				rowToAppend = rowToAppend + secondArrayRowToAppend

		comparisonArray.append(rowToAppend)
		# p(comparisonArray)


	clearAndResizeParameters = [{
		'sheetObj': gspComparisonTableSheet,
		'resizeRows': 3,
		'startingRowIndexToClear': 0
	},
	{
		'sheetObj': gspEndingSecondTableSheet,
		'resizeRows': 2,
		'startingRowIndexToClear': 0
	}]


	
	_myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)


	_myGspreadFunc.updateCells(gspComparisonTableSheet, comparisonArray)


	secondArray.insert(0, secondArrayFirstRow)
	_myGspreadFunc.updateCells(gspEndingSecondTableSheet, secondArray)

 
	with open(pathOfDecryptedFile, "w") as fileObj:
		fileObj.write('')


	return strToReturn





# for oauth

# Advanced Usage
# Custom Authentication
# Google Colaboratory
# If you familiar with the Jupyter Notebook, Google Colaboratory is probably the easiest way to get started using gspread:

# from google.colab import auth
# auth.authenticate_user()

# import gspread
# from oauth2client.client import GoogleCredentials

# gc = gspread.authorize(GoogleCredentials.get_application_default())




# def authorize(credentials, client_class=Client):
#     """Login to Google API using OAuth2 credentials.
#     This is a shortcut function which
#     instantiates `client_class`.
#     By default :class:`gspread.Client` is used.
#     :returns: `client_class` instance.
#     """

#     client = client_class(auth=credentials)
#     return client





# importing

# this works 
# import reconcileArrays.hiPackage.hiModule
# reconcileArrays.hiPackage.hiModule.hiFunction()

# this works 
# from reconcileArrays.hiPackage import hiModule
# hiModule.hiFunction()

# this works 
# from .hiPackage import hiModule
# hiModule.hiFunction()

# this works 
# from ..hiPackage import hiModule
# hiModule.hiFunction()