import json
from flask import Flask, request, render_template, Response
import os
from pathlib import Path
from pprint import pprint as p
import sys


# def runningOnProductionServer(urlStr):

# 	strToSearch = urlStr

# 	if any(strToFind in strToSearch for strToFind in ['127.0.0.1:5000', 'localhost:5000', '0.0.0.0:5000']):
# 		return False
	
# 	return True


def setupFlaskServer(flaskApp):

	flaskApp.config['TEMPLATES_AUTO_RELOAD'] = True
	urlOfSheet = os.environ.get('urlOfKingGorillaGoogleSheetPublicStr')

	if not urlOfSheet:

		runningOnProductionServer = False
		pathToThisPythonFile = Path(__file__).resolve()
		sys.path.append(str(pathToThisPythonFile.parents[0]))
		from backend.python.myPythonLibrary import _myPyFunc	
		pathToRepos = _myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
		pathToConfigDataJSON = Path(pathToRepos, 'privateData', 'herokuGorilla', 'configData.json')

		jsonFileObj = open(pathToConfigDataJSON)
		urlOfSheet = json.load(jsonFileObj)['urlOfKingGorillaGoogleSheetPublicStr']



	@flaskApp.route('/datarequests', methods=['GET', 'POST'])
	def datarequests():

		# if request.method == 'GET':
		# 	dataToSendToFrontend = {
		# 		'cat eyes': 'yellow',
		# 		'collar': 'red'
		# 	}

		# 	return Response(json.dumps(dataToSendToFrontend), mimetype='application/json')


		if request.method == 'POST':
			requestObj = request.json

			if 'processToRun' in requestObj:

				if requestObj['processToRun'] == ['reconcileArrays.py']:
					from backend.python.googleSheetsApps import reconcileArrays
					returnValue = reconcileArrays.reconcileArraysFunction(requestObj['oAuth'], requestObj['googleSheetTitle'])
					return render_template(requestObj['htmlPathToLoad'], valueFromBackend=returnValue)
				
				if requestObj['processToRun'] == ['looper.py']:
					from backend.python.googleSheetsApps import looper
					returnValue = looper.looperFunction(requestObj['oAuth'], requestObj['googleSheetTitle'])
					return render_template(requestObj['htmlPathToLoad'], valueFromBackend=returnValue)

			else:
				return render_template(requestObj['htmlPathToLoad'], valueFromBackend=urlOfSheet)



	@flaskApp.route('/')
	def returnMainPage():
		return render_template('frontend/htmlTemplates/index.html')
		
	if __name__ == '__main__':
		
		flaskApp.run()


kingGorillaFlaskApp = Flask(__name__, template_folder='./', static_folder='./frontend')
setupFlaskServer(kingGorillaFlaskApp)