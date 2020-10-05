#standard library imports
import os
from pathlib import Path
from pprint import pprint as p
import sys

#third-party imports
import gspread


#local application imports
pathToThisPythonFile = Path(__file__).resolve()

if os.environ.get('runningOnProductionServer') == 'true':
	from ...myPythonLibrary import myPyFunc
	runningOnProductionServer = True
else:
	sys.path.append(str(pathToThisPythonFile.parents[2]))
	from myPythonLibrary import myPyFunc
	runningOnProductionServer = False




def clearArray(startingRowIndex, endingRowIndex, startingColumnIndex, endingColumnIndex, arrayOfSheet):

	if endingRowIndex == -1:
		endingRowIndex = len(arrayOfSheet) - 1
	if endingColumnIndex == -1:
		endingColumnIndex = len(arrayOfSheet[len(arrayOfSheet) - 1]) - 1

	for row in range(startingRowIndex, endingRowIndex + 1):
		for column in range(startingColumnIndex, endingColumnIndex + 1):
			arrayOfSheet[row][column] = ''

	return arrayOfSheet



def clearSheet(startingRowIndex, endingRowIndex, startingColumnIndex, endingColumnIndex, gspSheetOfArray):

	arrayOfSheet = gspSheetOfArray.get_all_values()

	if len(arrayOfSheet) > 0:

		arrayOfSheet = clearArray(startingRowIndex, endingRowIndex, startingColumnIndex, endingColumnIndex, arrayOfSheet)
		updateCells(gspSheetOfArray, arrayOfSheet)

		


def clearSheets(startingRowIndex, endingRowIndex, startingColumnIndex, endingColumnIndex, arrayOfSheetObjects):
	
	for sheetObj in arrayOfSheetObjects:
		clearSheet(startingRowIndex, endingRowIndex, startingColumnIndex, endingColumnIndex, sheetObj)



def clearAndResizeSheets(arrayOfSheetObj):

	if isinstance(arrayOfSheetObj[0], dict):
		for sheetObj in arrayOfSheetObj:

			resizeParameter = 'resizeRows'
			if resizeParameter in sheetObj:
				sheetObj['sheetObj'].resize(rows=sheetObj[resizeParameter])

			resizeParameter = 'resizeColumns'
			if resizeParameter in sheetObj:
				sheetObj['sheetObj'].resize(cols=sheetObj[resizeParameter])
			
			for propertyToCheck in ['startingRowIndexToClear', 'startingColumnIndexToClear']:
				if propertyToCheck not in sheetObj: sheetObj[propertyToCheck] = 0

			for propertyToCheck in ['endingRowIndexToClear', 'endingColumnIndexToClear']:
				if propertyToCheck not in sheetObj: sheetObj[propertyToCheck] = -1
				
			clearSheet(sheetObj['startingRowIndexToClear'], sheetObj['endingRowIndexToClear'], sheetObj['startingColumnIndexToClear'], sheetObj['endingColumnIndexToClear'], sheetObj['sheetObj'])
	
	else:
		for sheetObj in arrayOfSheetObjects:
			sheetObj.resize(rows=1, cols=1)
			clearSheet(0, -1, 0, -1, sheetObj)



def updateCells(gspSheetOfArray, arrayOfSheet):

	if len(arrayOfSheet) > 0:

		numberOfRowsInArrayOfSheet = len(arrayOfSheet)
		
		arrayOfArrayLengths = [len(i) for i in arrayOfSheet]
		numberOfColumnsInArrayOfSheet = max(arrayOfArrayLengths)

		for row in arrayOfSheet:
			if len(row) > numberOfColumnsInArrayOfSheet:
				numberOfColumnsInArrayOfSheet = len(row)
		
		startingCell = 'R1C1'
		endingCell = 'R' + str(numberOfRowsInArrayOfSheet) + 'C' + str(numberOfColumnsInArrayOfSheet)
		addressOfSheet = startingCell + ':' + endingCell

		# print(addressOfSheet)
		
		gspSheetOfArray.update(addressOfSheet, arrayOfSheet)



def autoResizeColumnsOnSheet(spreadsheetLevelObj, sheetName):

	requestBody = {
		"requests": [
			{
				"autoResizeDimensions": {
					"dimensions": {
						"sheetId": spreadsheetLevelObj.worksheet(sheetName)._properties['sheetId'],
						"dimension": "COLUMNS",
						"startIndex": 0
					}
				}
			}
		]
	}

	spreadsheetLevelObj.batch_update(requestBody)


def autoResizeColumnsInSpreadsheet(spreadsheetLevelObj):

	requestBody = {
		"requests": []
	}

	# p(spreadsheetLevelObj.worksheets())

	for sheetObj in spreadsheetLevelObj.worksheets():
		requestBody['requests'].append(
			{
				"autoResizeDimensions": {
					"dimensions": {
						"sheetId": sheetObj._properties['sheetId'],
						"dimension": "COLUMNS",
						"startIndex": 0
					}
				}
			}
		)

		# p(sheetObj)
	
	# p(requestBody)
	spreadsheetLevelObj.batch_update(requestBody)


def getGspSpreadsheetObj(spreadsheetName):
	#return gspread spreadsheet object

	pathToRepos = myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
	arrayOfPartsToAddToPath = ['privateData', 'python', 'googleCredentials', 'usingServiceAccount', 'jsonWithAPIKey.json']

	pathToCredentialsFileServiceAccount = myPyFunc.addToPath(pathToRepos, arrayOfPartsToAddToPath)

	gspObj = gspread.service_account(filename=pathToCredentialsFileServiceAccount)

	return gspObj.open(spreadsheetName)


def getObjOfSheets(spreadsheetName):
	#return dictionary of sheets

	spreadsheetLevelObj = getGspSpreadsheetObj(spreadsheetName)

	objOfSheets = {}

	for sheet in spreadsheetLevelObj.worksheets():
		objOfSheets[sheet.title] = {
			'sheetObj': sheet,
			'array': sheet.get_all_values()
		}

	return objOfSheets






def authorizeGspread(oAuthMode, pathBelowRepos, loadSavedCredentials=True, googleAccountUsername=None):

	from google_auth_oauthlib.flow import InstalledAppFlow
	from pprint import pprint as p

	pathToConfigData = Path(pathBelowRepos, 'backend', 'configData')

	# p('pathToConfigData {}'.format(pathToConfigData))
	# p('oAuthMode {}'.format(oAuthMode))
	# p('runningOnProductionServer {}'.format(runningOnProductionServer))


	if runningOnProductionServer:
		loadedEncryptionKey = os.environ.get('savedEncryptionKeyStr', None)
	else:
		pathToRepos = myPyFunc.getPathUpFolderTree(pathBelowRepos, 'repos')
		pathToGoogleCredentials = Path(pathToRepos, 'privateData', 'python', 'googleCredentials')


	if oAuthMode:

		scopesArray = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
		credentialsObj = None

		if runningOnProductionServer:

			pathToDecryptedJSONCredentialsFile = myPyFunc.decryptIntoSameFolder(pathToConfigData, 'JSONCredentialsFile.json', loadedEncryptionKey)
			pathToDecryptedAuthorizedUserFile = myPyFunc.decryptIntoSameFolder(pathToConfigData, 'AuthorizedUserFile.json', loadedEncryptionKey)
			decryptedFilesToClear = [pathToDecryptedJSONCredentialsFile, pathToDecryptedAuthorizedUserFile]

		if not runningOnProductionServer:

			pathToDecryptedJSONCredentialsFile = Path(pathToGoogleCredentials, 'usingOAuthGspread', 'jsonCredentialsFile.json')
			
			pathToCheckForDecryptedAuthorizedUserFile = Path(pathToGoogleCredentials, 'usingOAuthGspread', googleAccountUsername, 'authorizedUserFile.json')

			if googleAccountUsername and pathToCheckForDecryptedAuthorizedUserFile.exists():
				credentialsObj = gspread.auth.load_credentials(filename=pathToCheckForDecryptedAuthorizedUserFile)

		if not credentialsObj:

			flowObj = InstalledAppFlow.from_client_secrets_file(pathToDecryptedJSONCredentialsFile, scopesArray)
			credentialsObj = flowObj.run_local_server(port=0)

			if not runningOnProductionServer:
				gspread.auth.store_credentials(credentialsObj, filename=pathToCheckForDecryptedAuthorizedUserFile)

		gspObj = gspread.client.Client(auth=credentialsObj)


	if not oAuthMode:

		if runningOnProductionServer:
			
			pathToDecryptedAPIKey = myPyFunc.decryptIntoSameFolder(pathToConfigData, 'APIKey.json', loadedEncryptionKey)
			decryptedFilesToClear = [pathToDecryptedAPIKey]

		if not runningOnProductionServer: pathToDecryptedAPIKey = Path(pathToGoogleCredentials, 'usingServiceAccount', 'jsonWithAPIKey.json')

		gspObj = gspread.service_account(filename=pathToDecryptedAPIKey)


	if runningOnProductionServer: myPyFunc.clearDecryptedFiles(decryptedFilesToClear)

	return gspObj



def updateCell(sheetToUpdate, rowIndex, columnIndex, valueToUpdate):

	sheetToUpdate.update_cell(rowIndex + 1, columnIndex + 1, valueToUpdate)
