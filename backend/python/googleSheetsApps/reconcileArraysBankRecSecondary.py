from google_auth_oauthlib.flow import InstalledAppFlow
import os
from pathlib import Path
from pprint import pprint as p
import sys

pathToThisPythonFile = Path(__file__).resolve()

if os.environ.get('runningOnProductionServer') == 'true':
    from ..myPythonLibrary import myPyFunc
    from ..googleSheets.myGoogleSheetsLibrary import myGspreadFunc
else:
    sys.path.append(str(pathToThisPythonFile.parents[1]))
    from myPythonLibrary import myPyFunc
    from googleSheets.myGoogleSheetsLibrary import myGspreadFunc


# def dailyDepositsColumnDataMatches(gpArrayCurrentRow, bankArrayCurrentRow):

#     if gpArrayCurrentRow[12][2:7] != bankArrayCurrentRow[8]:
#         return False
    
#     return True


# def getMatchedDailyDepositsRows(bankArray, gpArrayCurrentRow):

#     rowsThatMatch = []

#     for bankArrayRowIndex, bankArrayCurrentRow in enumerate(bankArray):
            
#             if dailyDepositsColumnDataMatches(gpArrayCurrentRow, bankArrayCurrentRow):
                
#                 rowsThatMatch.append({
#                     'secondArrayRowIndex': bankArrayRowIndex,
#                     'secondArrayRow': bankArrayCurrentRow
#                 })

#     return rowsThatMatch





def reconcileArrays(oAuthMode, googleSheetTitle, googleAccountUsername=None):

    pathBelowRepos = pathToThisPythonFile
    spreadsheetLevelObj = myGspreadFunc.getSpreadsheetLevelObj(oAuthMode, pathBelowRepos, googleAccountUsername=googleAccountUsername).open(googleSheetTitle)


    # dailyDepositsSheetName = 'Daily Deposits'


    sheets = {
        'gp': {
            'name': 'GP',
            'colNms': {
                'amount+-': 'Amount+-',
                'dateStr': 'Date String'
            },
            'colIndx': {
                'date': 1,
                'amount': 5,
                'type': 11,
                'paidTo': 14
            }
        },
        'bank': {
            'name': 'Bank'
        },
        'matched': {
            'name': 'Matched'
        },
        'notMatched': {
            'name': 'Did Not Match'
        },
        
    }


    def mapGPArray(currentRowIndex, currentRow):

        if currentRowIndex:

            currentAmount = currentRow[sheets['gp']['colIndx']['amount']]
            currentType = currentRow[sheets['gp']['colIndx']['type']]
            currentPaidTo = currentRow[sheets['gp']['colIndx']['paidTo']]
            currentDate = currentRow[sheets['gp']['colIndx']['date']]

            amount = myPyFunc.strToFloat(currentAmount)

            if 'Decrease Adjustment' == currentType or 'Transfer To' in currentPaidTo: amount = -amount

            currentRow.append(amount)
            currentRow.append(amount)
            currentRow.append(myPyFunc.dateStrToStr(currentDate))
        
        else:

            currentRow.append(sheets['gp']['colNms']['amount+-'])
            currentRow.append('Bank Amount')
            currentRow.append(sheets['gp']['colNms']['dateStr'])


    gpArray = spreadsheetLevelObj.worksheet(sheets['gp']['name']).get_all_values()
    gpArray = myPyFunc.mapArray(mapGPArray, gpArray)


    def mapBankArray(currentRowIndex, currentRow):

        if currentRowIndex:

            currentDebitAmount = currentRow[5]
            currentCreditAmount = currentRow[6]
            currentDate = currentRow[0]

            currentRow.append(myPyFunc.strToFloat(currentCreditAmount) - myPyFunc.strToFloat(currentDebitAmount))
            currentRow.append(myPyFunc.dateStrToStr(currentDate))
        
        else:

            currentRow.append(sheets['gp']['colNms']['amount+-'])
            currentRow.append(sheets['gp']['colNms']['dateStr'])

    bankArray = spreadsheetLevelObj.worksheet(sheets['bank']['name']).get_all_values()
    bankArray = myPyFunc.mapArray(mapBankArray, bankArray)
        

    # def mapDailyDepositsArray(currentRowIndex, currentRow):

    #     if currentRowIndex == 0:
    #         currentRow.append('BisTrack Amount')
    #         currentRow.append('Bank Amount')
    #     else:
    #         currentType = currentRow[2]
            
    #         def getBistrackAmount():
    #             currentBistrackAmount = currentRow[6]
    #             return myPyFunc.ifConditionFlipSign(myPyFunc.strToFloat(currentBistrackAmount), currentType, 'Debit')

    #         def getBankAmount():
    #             currentBankAmount = currentRow[4]
    #             return myPyFunc.ifConditionFlipSign(myPyFunc.strToFloat(currentBankAmount), currentType, 'Debit')

    #         currentDate = currentRow[0]
    #         dateToAppend = None

    #         if currentDate != '':
    #             dateToAppend = currentDate
    #         currentRow.append(dateToAppend)

    #         currentRow.append(getBistrackAmount())
    #         currentRow.append(getBankAmount())

    # dailyDepositsArray = spreadsheetLevelObj.worksheet(dailyDepositsSheetName).get_all_values()
    # dailyDepositsArray = myPyFunc.mapArray(mapDailyDepositsArray, dailyDepositsArray)

    gpArrayFirstRow = gpArray.pop(0)
    bankArrayFirstRow = bankArray.pop(0)

    matchedArray = [[sheets['gp']['name']] + [''] * (len(gpArrayFirstRow) - 1) + [''] + [sheets['bank']['name']] + [''] * (len(bankArrayFirstRow) - 1)]
    matchedArray.append(gpArrayFirstRow + [''] + bankArrayFirstRow)

    def getFilterByIndexFunction(indicesToFilter):
        
        def filterFunction(gpArrayFirstRowElementIndex, gpArrayFirstRowElement):

            if gpArrayFirstRowElementIndex in indicesToFilter:

                return True

            return False

        return filterFunction


    def getColumnComparisonFunction(firstArrayColumnIndex, secondArrayColumnIndex):

        def comparisonFunction(firstArrayCurrentRow, secondArrayCurrentRow):

            if firstArrayCurrentRow[firstArrayColumnIndex] == secondArrayCurrentRow[secondArrayColumnIndex]:
                
                return True

            return False

        return comparisonFunction

    amountComparisonFunction = getColumnComparisonFunction(17, 7)




    def rowForMatchedArrayOnAmountDate(gpArrayCurrentRow):

        rowToReturn = gpArrayCurrentRow

        dateComparisonFunction = getColumnComparisonFunction(19, 8)
        rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([amountComparisonFunction, dateComparisonFunction], gpArrayCurrentRow, bankArray)

        if len(rowIndicesThatMatch) == 1:
            filterOnAmountDateFunction = getFilterByIndexFunction([17, 19])
            rowToReturn.extend([myPyFunc.getMatchStatus(myPyFunc.filterArray(filterOnAmountDateFunction, gpArrayFirstRow))] + bankArray.pop(rowIndicesThatMatch[0]))
        elif len(rowIndicesThatMatch) > 1:
            p('More than one row matches on the first pass')

        return rowToReturn


    myPyFunc.transferToArray(gpArray, matchedArray, rowForMatchedArrayOnAmountDate)


    def rowForMatchedArrayOnAmount(gpArrayCurrentRowIndex, gpArrayCurrentRow):

        if len(gpArrayCurrentRow) == len(gpArrayFirstRow):

            rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([amountComparisonFunction], gpArrayCurrentRow, bankArray)

            def filterOnAmountLengthFunction(matchedArrayCurrentRowIndex, matchedArrayCurrentRow):
                
                if len(matchedArrayCurrentRow) == len(gpArrayFirstRow) and matchedArrayCurrentRow[17] == gpArrayCurrentRow[17]:
                
                    return True
                
                return False

            filterOnAmountFunction = getFilterByIndexFunction([17])

            if len(rowIndicesThatMatch) == 1 or len(rowIndicesThatMatch) == len(myPyFunc.filterArray(filterOnAmountLengthFunction, matchedArray)):

                gpArrayCurrentRow.extend([myPyFunc.getMatchStatus(myPyFunc.filterArray(filterOnAmountFunction, gpArrayFirstRow))] + bankArray.pop(rowIndicesThatMatch[0]))

    myPyFunc.mapArray(rowForMatchedArrayOnAmount, matchedArray)






    # def addMatchesFromDailyDepositsArray(currentRowIndex, currentRow):

    #     if len(currentRow) == len(gpArrayFirstRow):

    #         rowsThatMatch = getMatchedDailyDepositsRows(dailyDepositsArray, currentRow)

    #         if len(rowsThatMatch) == 1:
    #             pass
    
    # matchedArray = myPyFunc.mapArray(addMatchesFromDailyDepositsArray, matchedArray)


    clearAndResizeParameters = [{
        'sheetObj': spreadsheetLevelObj.worksheet(sheets['matched']['name']),
        'resizeRows': 3,
        'startingRowIndexToClear': 0,
        'resizeColumns': 1
    },
    {
        'sheetObj': spreadsheetLevelObj.worksheet(sheets['notMatched']['name']),
        'resizeRows': 2,
        'startingRowIndexToClear': 0,
        'resizeColumns': 1
    }]


    myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)
    myGspreadFunc.displayArray(spreadsheetLevelObj.worksheet(sheets['matched']['name']), matchedArray)

    bankArray.insert(0, bankArrayFirstRow)
    myGspreadFunc.displayArray(spreadsheetLevelObj.worksheet(sheets['notMatched']['name']), bankArray)

    customTopRows = {'Matched': 2}
    myGspreadFunc.setFiltersOnSpreadsheet(spreadsheetLevelObj, customTopRows)
    myGspreadFunc.autoAlignColumnsInSpreadsheet(spreadsheetLevelObj)



def mainFunction(arrayOfArguments):
    reconcileArrays(True, arrayOfArguments[1], googleAccountUsername=arrayOfArguments[2])


if __name__ == '__main__':
    p(str(pathToThisPythonFile.name) + ' is not being imported. It is being run directly...')
    mainFunction(sys.argv)
else:
    p(str(pathToThisPythonFile.name) + ' is being imported. It is not being run directly...')