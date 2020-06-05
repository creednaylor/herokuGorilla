from google_auth_oauthlib.flow import InstalledAppFlow
import json
import os
from pathlib import Path
from pprint import pprint as p
import sys

import gspread


def decryptIntoSameFolder(pathToFolder, fileName, encryptionKey):
	_myPyFunc.decryptFile(Path(pathToFolder, 'encrypted' + fileName), encryptionKey, pathToSaveDecryptedFile=Path(pathToFolder, 'decrypted' + fileName))
	return Path(pathToFolder, fileNameDecrypted)


def clearDecryptedFiles(decryptedFilesToClear):
	for decryptedFileToClear in decryptedFilesToClear:
			with open(decryptedFileToClear, "w") as fileObj:
				fileObj.write('')



def reconcileArraysFunction(runningOnProductionServer, oAuthMode, googleSheetTitle):

	pathToThisPythonFile = Path(__file__).resolve()
	pathToConfigData = Path(pathToThisPythonFile.parents[2], 'configData')

	if runningOnProductionServer:
		from ..myPythonLibrary import _myPyFunc
		from ..googleSheets.myGoogleSheetsLibrary import _myGspreadFunc
		loadedEncryptionKey = os.environ.get('savedEncryptionKeyStr', None)

	if not runningOnProductionServer:
		sys.path.append(str(pathToThisPythonFile.parents[1]))
		from myPythonLibrary import _myPyFunc
		from googleSheets.myGoogleSheetsLibrary import _myGspreadFunc

		pathToRepos = _myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
		pathToGoogleCredentials = Path(pathToRepos, 'privateData', 'python', 'googleCredentials')

	if oAuthMode:

		scopesArray = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

		if runningOnProductionServer:

			pathToDecryptedJSONCredentialFile = decryptIntoSameFolder(pathToConfigData, 'JSONCredentialsFile.json', loadedEncryptionKey)
			pathToDecryptedAuthorizedUserFile = decryptIntoSameFolder(pathToConfigData, 'AuthorizedUserFile.json', loadedEncryptionKey)
			decryptedFilesToClear = [pathToDecryptedJSONCredentialsFile, pathToDecryptedAuthorizedUserFile]

		if not runningOnProductionServer:

			pathToDecryptedJSONCredentialsFile = Path(pathToGoogleCredentials, 'usingOAuthGspread', 'jsonCredentialsFile.json')
			pathToDecryptedAuthorizedUserFile = Path(pathToGoogleCredentials, 'usingOAuthGspread', 'authorizedUserFile.json')

		credentialsObj = gspread.auth.load_credentials(filename=pathToDecryptedAuthorizedUserFile)

		if not credentialsObj:

			flowObj = InstalledAppFlow.from_client_secrets_file(pathToDecryptedJSONCredentialsFile, scopesArray)
			credentialsObj = flowObj.run_local_server(port=0)

			gspread.auth.store_credentials(credentialsObj, filename=pathToDecryptedAuthorizedUserFile)

		gspObj = gspread.client.Client(auth=credentialsObj)
			

	if not oAuthMode:

		if runningOnProductionServer:
			
			pathToDecryptedAPIKey = decryptIntoSameFolder(pathToConfigData, 'APIKey.json', loadedEncryptionKey)
			decryptedFilesToClear = [pathToDecryptedAPIKey]

		if not runningOnProductionServer: pathToDecryptedAPIKey = Path(pathToGoogleCredentials, 'usingServiceAccount', 'jsonWithAPIKey.json')

		gspObj = gspread.service_account(filename=pathToDecryptedAPIKey)


	if runningOnProductionServer: clearDecryptedFiles(decryptedFilesToClear)

	gspSpreadsheet = gspObj.open(googleSheetTitle)

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

	strToReturn = os.environ.get('urlOfKingGorillaGoogleSheetPublicStr')

	if not strToReturn:

		pathToConfigDataJSON = Path(pathToRepos, 'privateData', 'herokuGorilla', 'configData.json')
		jsonFileObj = open(pathToConfigDataJSON)
		strToReturn = json.load(jsonFileObj)['urlOfKingGorillaGoogleSheetPublicStr']
	
	strToReturn = strToReturn[:-1] + '871892682'

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
#	 """Login to Google API using OAuth2 credentials.
#	 This is a shortcut function which
#	 instantiates `client_class`.
#	 By default :class:`gspread.Client` is used.
#	 :returns: `client_class` instance.
#	 """

#	 client = client_class(auth=credentials)
#	 return client


#################################################################################################


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



###################################################################################################

		# # from __future__ import print_function
		# import pickle
		# import os.path
		# from googleapiclient.discovery import build
		# from google_auth_oauthlib.flow import InstalledAppFlow
		# from google.auth.transport.requests import Request

		# # If modifying these scopes, delete the file token.pickle.
		# SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

		# # The ID and range of a sample spreadsheet.
		# SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
		# SAMPLE_RANGE_NAME = 'Class Data!A2:E'


		# """Shows basic usage of the Sheets API.
		# Prints values from a sample spreadsheet.
		# """
		# creds = None
		


		# # The file token.pickle stores the user's access and refresh tokens, and is
		# # created automatically when the authorization flow completes for the first
		# # time.
		
		# if os.path.exists(pathToPickleCredentialsFile):
		# 	with open(pathToPickleCredentialsFile, 'rb') as token:
		# 		creds = pickle.load(token)
		
		# # If there are no (valid) credentials available, let the user log in.
		# if not creds or not creds.valid:
		# 	if creds and creds.expired and creds.refresh_token:
		# 		creds.refresh(Request())
		# 	else:
		# 		flow = InstalledAppFlow.from_client_secrets_file(
		# 			pathToDecryptedJSONCredentialsFile, SCOPES)
		# 		creds = flow.run_local_server(port=0)
			
		# 	# Save the credentials for the next run
		# 	with open(pathToPickleCredentialsFile, 'wb') as token:
		# 		pickle.dump(creds, token)

		# service = build('sheets', 'v4', credentials=creds)

		# # Call the Sheets API
		# sheet = service.spreadsheets()
		# result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
		# 							range=SAMPLE_RANGE_NAME).execute()
		# values = result.get('values', [])

		# if not values:
		# 	print('No data found.')
		# else:
		# 	print('Name, Major:')
		# 	for row in values:
		# 		# Print columns A and E, which correspond to indices 0 and 4.
		# 		print('%s, %s' % (row[0], row[4]))



###############################################################################################################



			# pathToPickleCredentialsFile = Path(pathToOAuthCredentialsFolder, 'pickleFileWithCredentials.pickle')


			# import pickle
			# import os.path
			# from googleapiclient.discovery import build
			# from google_auth_oauthlib.flow import InstalledAppFlow
			# from google.auth.transport.requests import Request

			# # If modifying these scopes, delete the file token.pickle.
			# SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

			# # The ID and range of a sample spreadsheet.
			# SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
			# SAMPLE_RANGE_NAME = 'Class Data!A2:E'

			# creds = None
			# usePickleFile = False

			# if usePickleFile:

			# 	# The file token.pickle stores the user's access and refresh tokens, and is
			# 	# created automatically when the authorization flow completes for the first
			# 	# time.
				
			# 	if os.path.exists(pathToPickleCredentialsFile):
			# 		with open(pathToPickleCredentialsFile, 'rb') as token:
			# 			creds = pickle.load(token)
			

			# # If there are no (valid) credentials available, let the user log in.
			# if not creds or not creds.valid:

			# 	if usePickleFile and creds and creds.expired and creds.refresh_token:
			# 		creds.refresh(Request())

			# 	else:

			# 		flowObj = InstalledAppFlow.from_client_secrets_file(pathToDecryptedJSONCredentialsFile, SCOPES)
			# 		creds = flowObj.run_local_server(port=0)
			# 		p(flowObj)
				
			# 	if usePickleFile:
			# 		# Save the credentials for the next run
			# 		with open(pathToPickleCredentialsFile, 'wb') as token:
			# 			pickle.dump(creds, token)


			# service = build('sheets', 'v4', credentials=creds)


			# sheet = service.spreadsheets()
			# result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()
			# values = result.get('values', [])

			# if not values:
			# 	print('No data found.')
			# else:
			# 	print(values)