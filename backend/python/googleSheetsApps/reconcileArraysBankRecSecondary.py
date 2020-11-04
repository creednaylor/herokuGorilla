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


def dailyDepositsColumnDataMatches(firstArrayCurrentRow, secondArrayCurrentRow):

    if firstArrayCurrentRow[12][2:7] != secondArrayCurrentRow[8]:
        return False
    
    return True


def getMatchedDailyDepositsRows(bankArray, firstArrayCurrentRow):

    rowsThatMatch = []

    for secondArrayRowIndex, secondArrayCurrentRow in enumerate(bankArray):
            
            if dailyDepositsColumnDataMatches(firstArrayCurrentRow, secondArrayCurrentRow):
                
                rowsThatMatch.append({
                    'secondArrayRowIndex': secondArrayRowIndex,
                    'secondArrayRow': secondArrayCurrentRow
                })

    return rowsThatMatch



def elementCriteriaAreTrue(element, criteriaToCheck):

    if len(element) > criteriaToCheck['maxRowLength']:
        return False
    else:
        for criterion in criteriaToCheck['criteria']:
            if element[criterion['columnIndexToCheck']] != criterion['valueToCheckFor']:
                return False

    return True


def countNumberOfElements(arrayToCount, criteriaToCheck):

    numberOfRecords = 0

    for element in arrayToCount:
        if elementCriteriaAreTrue(element, criteriaToCheck):
            numberOfRecords = numberOfRecords + 1

    return numberOfRecords


def reconcileArrays(oAuthMode, googleSheetTitle, googleAccountUsername=None):

    # pathToRepos = myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
    pathBelowRepos = pathToThisPythonFile
    spreadsheetLevelObj = myGspreadFunc.getSpreadsheetLevelObj(oAuthMode, pathBelowRepos, googleAccountUsername=googleAccountUsername).open(googleSheetTitle)

    gpTableName = 'GP'
    bankTableName = 'Bank'
    matchedTableName = 'Matched'
    didNotMatchTableName = 'Did Not Match'
    dailyDepositsTableName = 'Daily Deposits'

    gpArray = spreadsheetLevelObj.worksheet(gpTableName).get_all_values()
    amountColumnName = 'Amount+-'
    dateStrColumnName = 'Date String'
    

    def transformGPArray(currentRowIndex, currentRow):
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

            if 'Decrease Adjustment' == currentType or 'Transfer To' in currentPaidTo:
                amount = -amount

            currentRow.append(amount)
            currentRow.append(amount)
            currentRow.append(myPyFunc.dateStrToStr(currentDate))


    gpArray = myPyFunc.transformArray(gpArray, transformGPArray)
    bankArray = spreadsheetLevelObj.worksheet(bankTableName).get_all_values()
    

    def transformBankArray(currentRowIndex, currentRow):
        if currentRowIndex == 0:
            currentRow.append(amountColumnName)
            currentRow.append(dateStrColumnName)
        else:
            currentDebitAmount = currentRow[5]
            currentCreditAmount = currentRow[6]
            currentDate = currentRow[0]

            currentRow.append(myPyFunc.strToFloat(currentCreditAmount) - myPyFunc.strToFloat(currentDebitAmount))
            currentRow.append(myPyFunc.dateStrToStr(currentDate))

    bankArray = myPyFunc.transformArray(bankArray, transformBankArray)
    dailyDepositsArray = spreadsheetLevelObj.worksheet(dailyDepositsTableName).get_all_values()
    

    def transformDailyDepositsArray(currentRowIndex, currentRow):

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

    dailyDepositsArray = myPyFunc.transformArray(dailyDepositsArray, transformDailyDepositsArray)

    firstArrayFirstRow = gpArray.pop(0)
    secondArrayFirstRow = bankArray.pop(0)

    matchedArray = [[gpTableName] + [''] * (len(firstArrayFirstRow) - 1) + [''] + [bankTableName] + [''] * (len(secondArrayFirstRow) - 1)]
    matchedArray.append(firstArrayFirstRow + [''] + secondArrayFirstRow)

    columnsToMatch = [
        [17, 19],
        [7, 8]
    ]

    def getRowThatMatchesAmountAndDate(currentRow):

        rowToAppend = currentRow
        rowsThatMatch = myPyFunc.getSecondArrayRowsThatMatchFirstArrayCurrentRow(currentRow, bankArray, columnsToMatch)

        if len(rowsThatMatch) == 1:
            rowToAppend = rowToAppend + [myPyFunc.getMatchStatus(myPyFunc.getColumnNamesFromFirstRow(columnsToMatch[0], firstArrayFirstRow))] + bankArray.pop(rowsThatMatch[0]['secondArrayRowIndex'])
        elif len(rowsThatMatch) > 1:
            p('More than one row match the first pass')

        return rowToAppend


    myPyFunc.transferToArray(gpArray, matchedArray, getRowThatMatchesAmountAndDate)


    columnsToMatch = [
        [17], 
        [7]
    ]


    def addMatchesFromSecondArray(currentRowIndex, currentRow):
    
        if len(currentRow) == len(firstArrayFirstRow):

            rowsThatMatch = myPyFunc.getSecondArrayRowsThatMatchFirstArrayCurrentRow(currentRow, bankArray, columnsToMatch)

            criteriaToCheck = {
                'maxRowLength': 20,
                'criteria': [
                    {
                        'columnIndexToCheck': 17,
                        'valueToCheckFor': currentRow[17]
                    }
                ]
            }

            if len(rowsThatMatch) == 1 or countNumberOfElements(matchedArray, criteriaToCheck) == len(rowsThatMatch):

                currentRow.extend([myPyFunc.getMatchStatus(myPyFunc.getColumnNamesFromFirstRow(columnsToMatch[0], firstArrayFirstRow))] + bankArray.pop(rowsThatMatch[0]['secondArrayRowIndex']))
        
    myPyFunc.transformArray(matchedArray, addMatchesFromSecondArray)


    def addMatchesFromDailyDepositsArray(currentRowIndex, currentRow):

        if len(currentRow) == len(firstArrayFirstRow):

            rowsThatMatch = getMatchedDailyDepositsRows(dailyDepositsArray, currentRow)

            if len(rowsThatMatch) == 1:
                pass
    
    myPyFunc.transformArray(matchedArray, addMatchesFromDailyDepositsArray)


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

    bankArray.insert(0, secondArrayFirstRow)
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