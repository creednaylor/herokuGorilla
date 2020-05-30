#get public spreadsheet from encryption, or something similar

import json
from flask import Flask, request, render_template, Response
import os
from pprint import pprint as p


def runningOnProductionServer(urlStr):
	if any(strToFind in urlStr for strToFind in ['127.0.0.1:5000', 'localhost:5000', '0.0.0.0']):
		return False
	else:
		return True


def setupFlaskServer(flaskApp):

	flaskApp.config['TEMPLATES_AUTO_RELOAD'] = True

	urlOfSheet = os.environ.get('urlOfPublicGoogleSheet', 'https://www.google.com')


	@flaskApp.route('/datarequests', methods=['GET', 'POST'])
	def datarequests():

		if request.method == 'GET':
			dataToSendToFrontend = {
				'cat eyes': 'yellow',
				'collar': 'red'
			}

			return Response(json.dumps(dataToSendToFrontend), mimetype='application/json')


		if request.method == 'POST':
			requestObj = request.json

			if 'processToRun' in requestObj:

				from backend.reconcileArrays import reconcileArrays as reconcileArrays
				returnValue = reconcileArrays.reconcileArraysFunction(runningOnProductionServer(request.url_root))
				return render_template(requestObj['htmlPathToLoad'], valueFromBackend=returnValue)

			else:
				return render_template(requestObj['htmlPathToLoad'], valueFromBackend=urlOfSheet)



	@flaskApp.route('/')
	def returnMainPage():
		return render_template('frontend/htmlTemplates/index.html')
		# return """	<p>Spreadsheet to reconcile:</p>
		# 			<button onclick="publicClickFunction()">Public</button>
		# 			<button onclick="privateClickFunction()">Private</button>
		# 			<p></p>
		# 			<img src="./frontend/assets/regal-cat.jpeg" alt="regal cat" />"""


	if __name__ == '__main__':
		
		flaskAppLoadProcess = ''
		flaskApp.run()


flaskApp = Flask(__name__, template_folder='./', static_folder='./frontend')
setupFlaskServer(flaskApp)