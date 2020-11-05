from google_auth_oauthlib.flow import InstalledAppFlow
import os
from pathlib import Path
from pprint import pprint as p
import sys

from pkg_resources import parse_requirements

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

    gpTableName = 'GP'
    bankTableName = 'Bank'
    matchedTableName = 'Matched'
    didNotMatchTableName = 'Did Not Match'
    dailyDepositsTableName = 'Daily Deposits'

    amountColumnName = 'Amount+-'
    dateStrColumnName = 'Date String'

    def mapGPArray(currentRowIndex, currentRow):
        if currentRowIndex == 0:
            currentRow.append(amountColumnName)
            currentRow.append('Bank Amount')
            currentRow.append(dateStrColumnName)
        else:
            currentAmount = currentRow[5]
            currentType = currentRow[11]
            currentPaidTo = currentRow[14]
            currentDate = currentRow[1]

            amount = myPyFunc.strToFloat(currentAmount)

            if 'Decrease Adjustment' == currentType or 'Transfer To' in currentPaidTo: amount = -amount

            currentRow.append(amount)
            currentRow.append(amount)
            currentRow.append(myPyFunc.dateStrToStr(currentDate))


    gpArray = spreadsheetLevelObj.worksheet(gpTableName).get_all_values()
    gpArray = myPyFunc.mapArray(mapGPArray, gpArray)
    
    

    def mapBankArray(currentRowIndex, currentRow):
        if currentRowIndex == 0:
            currentRow.append(amountColumnName)
            currentRow.append(dateStrColumnName)
        else:
            currentDebitAmount = currentRow[5]
            currentCreditAmount = currentRow[6]
            currentDate = currentRow[0]

            currentRow.append(myPyFunc.strToFloat(currentCreditAmount) - myPyFunc.strToFloat(currentDebitAmount))
            currentRow.append(myPyFunc.dateStrToStr(currentDate))

    bankArray = spreadsheetLevelObj.worksheet(bankTableName).get_all_values()
    bankArray = myPyFunc.mapArray(mapBankArray, bankArray)
        

    def mapDailyDepositsArray(currentRowIndex, currentRow):

        if currentRowIndex == 0:
            currentRow.append('BisTrack Amount')
            currentRow.append('Bank Amount')
        else:
            currentType = currentRow[2]
            
            def getBistrackAmount():
                currentBistrackAmount = currentRow[6]
                return myPyFunc.ifConditionFlipSign(myPyFunc.strToFloat(currentBistrackAmount), currentType, 'Debit')

            def getBankAmount():
                currentBankAmount = currentRow[4]
                return myPyFunc.ifConditionFlipSign(myPyFunc.strToFloat(currentBankAmount), currentType, 'Debit')

            currentDate = currentRow[0]
            dateToAppend = None

            if currentDate != '':
                dateToAppend = currentDate
            currentRow.append(dateToAppend)

            currentRow.append(getBistrackAmount())
            currentRow.append(getBankAmount())

    dailyDepositsArray = spreadsheetLevelObj.worksheet(dailyDepositsTableName).get_all_values()
    dailyDepositsArray = myPyFunc.mapArray(mapDailyDepositsArray, dailyDepositsArray)

    gpArrayFirstRow = gpArray.pop(0)
    bankArrayFirstRow = bankArray.pop(0)

    matchedArray = [[gpTableName] + [''] * (len(gpArrayFirstRow) - 1) + [''] + [bankTableName] + [''] * (len(bankArrayFirstRow) - 1)]
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
        'sheetObj': spreadsheetLevelObj.worksheet(matchedTableName),
        'resizeRows': 3,
        'startingRowIndexToClear': 0,
        'resizeColumns': 1
    },
    {
        'sheetObj': spreadsheetLevelObj.worksheet(didNotMatchTableName),
        'resizeRows': 2,
        'startingRowIndexToClear': 0,
        'resizeColumns': 1
    }]


    myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)
    myGspreadFunc.displayArray(spreadsheetLevelObj.worksheet(matchedTableName), matchedArray)

    bankArray.insert(0, bankArrayFirstRow)
    myGspreadFunc.displayArray(spreadsheetLevelObj.worksheet(didNotMatchTableName), bankArray)

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