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

	gspScenarios = gspSpreadsheet.worksheet('Scenarios')
	scenarioArray = gspScenarios.get_all_values()

	requestObj = {
		"requests": [
		{
			"moveDimension": {
				"source": {
				"sheetId": sheetId,
				"dimension": "COLUMNS",
				"startIndex": 0,
				"endIndex": 1
			},
		"destinationIndex": 3
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
#   ],
	}


	p(scenarioArray[1])
