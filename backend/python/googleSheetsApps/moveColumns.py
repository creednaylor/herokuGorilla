from google_auth_oauthlib.flow import InstalledAppFlow
import json
import os
from pathlib import Path
from pprint import pprint as p
import sys

import gspread
from pprint import pprint as p


pathToThisPythonFile = Path(__file__).resolve()

if os.environ.get('runningOnProductionServer') == 'true':
	from ..myPythonLibrary import _myPyFunc
	from ..googleSheets.myGoogleSheetsLibrary import _myGspreadFunc
else:
	sys.path.append(str(pathToThisPythonFile.parents[1]))
from myPythonLibrary import _myPyFunc
from googleSheets.myGoogleSheetsLibrary import _myGspreadFunc



def moveColumns(googleSheetTitle, googleAccountUsername=None):

	pathToRepos = _myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
	pathToThisProjectRoot = pathToThisPythonFile.parents[3]

	oAuthMode = False

	if googleAccountUsername:
		oAuthMode = True

	gspObj = _myGspreadFunc.authorizeGspread(oAuthMode, pathToThisProjectRoot, googleAccountUsername=googleAccountUsername)
	gspSpreadsheet = gspObj.open(googleSheetTitle)

	sheetName = 'Scenarios'
	gspScenarios = gspSpreadsheet.worksheet(sheetName)
	scenarioArray = gspScenarios.get_all_values()

	p(scenarioArray[1][1:])


	def moveColumn(columnIndexToMove, destinationColumnIndex):

		if columnIndexToMove > destinationColumnIndex:
			destinationIndex = destinationColumnIndex
		else:
			destinationIndex = destinationColumnIndex + 1	

		requestObj = {
			"requests": [
				{
					"moveDimension": {
						"source": {
							"sheetId": gspSpreadsheet.worksheet(sheetName)._properties['sheetId'],
							"dimension": "COLUMNS",
							"startIndex": columnIndexToMove,
							"endIndex": columnIndexToMove + 1
						},
					"destinationIndex": destinationIndex
					}
				},
	#	 {
	#	   "moveDimension": {
	#		 "source": {
	#		   "sheetId": sheetId,
	#		   "dimension": "ROWS",
	#		   "startIndex": 4,
	#		   "endIndex": 10
	#		 },
	#		 "destinationIndex": 19
	#	   }
	#	 },
			],
		}

		gspSpreadsheet.batch_update(requestObj)



	def bubbleSort(arr):

		indexingLength = len(arr) - 1
		arrayIsSorted = False

		while not arrayIsSorted:

			arrayIsSorted = True
			
			for currentIndex in range(0, indexingLength):

				if arr[currentIndex] > arr[currentIndex + 1]:

					arrayIsSorted = False
					arr[currentIndex], arr[currentIndex + 1] = arr[currentIndex + 1], arr[currentIndex]

					moveColumn(currentIndex + 1, currentIndex + 2)

		return arr

	p(bubbleSort(scenarioArray[1][1:]))



	# def insertionSort(arr):

	# 	for currentIndex in range(len(arr)):

	# 		cursor = arr[currentIndex]
	# 		pos = currentIndex
			
	# 		while pos > 0 and arr[pos - 1] > cursor:
	# 			# Swap the number down the list

	# 			arr[pos] = arr[pos - 1]
	# 			moveColumn(pos + 1, )
				
	# 			pos = pos - 1
	# 		# Break and do the final swap


	# 		arr[pos] = cursor

	# 	return arr

	# p(insertionSort(scenarioArray[1][1:]))



	# moveColumn(0 + 1, 0 + 1)
	# moveColumn(1 + 1, 0 + 1)




	# p(scenarioArray[1])
