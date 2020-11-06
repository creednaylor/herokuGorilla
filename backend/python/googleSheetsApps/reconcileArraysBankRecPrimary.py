from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
import json
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


# def sortArrayOfArrays(array, subArrayIndexToSortBy): 
#     # reverse = None (Sorts in Ascending order) 
#     # key is set to sort using second element of  
#     # sublist lambda has been used

#     return(sorted(array, key = lambda x: x[subArrayIndexToSortBy])) 



def reconcileArrays(oAuthMode, googleSheetTitle, googleAccountUsername=None):

    pathBelowRepos = pathToThisPythonFile
    spreadsheetLevelObj = myGspreadFunc.getSpreadsheetLevelObj(oAuthMode, pathBelowRepos, googleAccountUsername=googleAccountUsername).open(googleSheetTitle)

    sheets = {
        'gp': {
            'name': 'GP',
            'colIndx': {
                'date': 1,
                'amount': 5,
                'type': 11,
                'paidTo': 14
            }
        },
        'bank': {
            'name': 'Bank',
            'colIndx': {
                'date': 0,
                'debit': 5,
                'credit': 6
            }
        },
        'dailyDeposits': {
            'name': 'Daily Deposits'
        },
        'matched': {
            'name': 'Matched'
        },
        'notMatched': {
            'name': 'Did Not Match'
        },
    }

    bankStatusCol = 0
    bankDateColumnIndex = 1
    bankTransactionTypeColumnIndex = 7
    bankDebitCreditColumnIndex = 8
    bankAmountColumnIndex = 9
    bankDescriptionTwoColumnIndex = 11

    bankArray = spreadsheetLevelObj.worksheet(sheets['bank']['name']).get_all_values()

    def filterBankArray(currentRowIndex, currentRow):

        if currentRow[bankStatusCol] not in ['H', 'B', 'T'] and currentRow[bankTransactionTypeColumnIndex] not in ['Data', 'Ledger Balance', 'Collected + 1 Day', 'Opening Collected', 'One Day Float', '2 Day Float', '3 Day + Float', 'MTD Avg Collected', 'MTD Avg Neg Collected', 'Total Credits', 'Number of Credits', 'Total Debits', 'Number of Debits', 'Float Adjustment(s)']:
            return True
        else:
            return False

    bankArray = myPyFunc.filterArray(filterBankArray, bankArray)

    def mapBankArray(currentRowIndex, currentRow):

        if currentRowIndex:

            currentRow[bankAmountColumnIndex] = float(currentRow[bankAmountColumnIndex].replace(',', ''))

            if len(currentRow[bankDateColumnIndex]) < 8:
                currentRow[bankDateColumnIndex] = '0' + currentRow[bankDateColumnIndex]

            currentRow[bankDateColumnIndex] = str(datetime.strptime(currentRow[bankDateColumnIndex], '%m%d%Y'))

            if currentRow[bankDebitCreditColumnIndex] == 'Debit':
                # p(currentRow[bankAmountColumnIndex])
                currentRow[bankAmountColumnIndex] = -currentRow[bankAmountColumnIndex]


    bankArray = myPyFunc.mapArray(mapBankArray, bankArray)
    bankArrayFirstRow = bankArray.pop(0)
    # bankArray = sortArrayOfArrays(bankArray, bankDateColumnIndex)


    gpTrxDateColumnIndex = 1
    gpAmountColumnIndex = 5
    gpTrxTypeColumnIndex = 11
    gpTrxNumberColumnIndex = 12
    gpPaidToReceivedFromColumnIndex = 14
    gpTransferColumnIndex = 17

    gpArray = spreadsheetLevelObj.worksheet(sheets['gp']['name']).get_all_values()
    gpArray = [currentRow for currentRow in gpArray if currentRow[gpTrxDateColumnIndex] not in ['']]


    def mapGPArray(currentRowIndex, currentRow):

        if currentRowIndex:

            currentRow[gpAmountColumnIndex] = float(currentRow[gpAmountColumnIndex].replace(',', ''))
            currentRow[gpTrxDateColumnIndex] = str(datetime.strptime(currentRow[gpTrxDateColumnIndex], '%m/%d/%Y'))

            if currentRow[gpPaidToReceivedFromColumnIndex]:
                if currentRow[gpPaidToReceivedFromColumnIndex][0:11] == 'Transfer To':
                    currentRow.append('Out')
                elif currentRow[gpPaidToReceivedFromColumnIndex][0:13] == "Transfer From":
                    currentRow.append('In')
            if len(currentRow) == gpTransferColumnIndex:
                currentRow.append('')

            if currentRow[gpTrxTypeColumnIndex]:
                if not currentRow[gpTransferColumnIndex]:
                    if currentRow[gpTrxTypeColumnIndex] in ['Increase Adjustment', 'Deposit']:
                        currentRow[gpTransferColumnIndex] = "In"
                    if currentRow[gpTrxTypeColumnIndex] in ['Decrease Adjustment', 'Withdrawl', 'Check']:
                        currentRow[gpTransferColumnIndex] = "Out"

        else:

            currentRow.append('Transfer')

        if currentRow[gpTransferColumnIndex] == 'Out': currentRow[gpAmountColumnIndex] = -currentRow[gpAmountColumnIndex]


    gpArray = myPyFunc.mapArray(mapGPArray, gpArray)
    gpArrayFirstRow = gpArray.pop(0)

    def filterGPArray(currentRowIndex, currentRow):
        if datetime.strptime(currentRow[gpTrxDateColumnIndex], '%Y-%m-%d %H:%M:%S') <= datetime(2020, 9, 30):
            return True
        else:
            return False

    gpArray = myPyFunc.filterArray(filterGPArray, gpArray)
    # gpArray = sortArrayOfArrays(gpArray, gpTrxDateColumnIndex)


    dailyDepositsAmountColumnIndex = 5
    dailyDepositsTransactionIDColumnIndex = 7

    dailyDepositsArray = spreadsheetLevelObj.worksheet(sheets['dailyDeposits']['name']).get_all_values()


    def mapDailyDeposits(currentRowIndex, currentRow):

        if currentRowIndex:
            currentRow[dailyDepositsAmountColumnIndex] = float(currentRow[dailyDepositsAmountColumnIndex].lstrip('$').replace(',', ''))

        return currentRow

    dailyDepositsArray = myPyFunc.mapArray(mapDailyDeposits, dailyDepositsArray)



    matchedArray = [[sheets['bank']['name']] + [''] * (len(bankArray[0]) - 1) + [''] + [sheets['gp']['name']] + [''] * (len(gpArray[0]) - 1)]
    matchedArray.append(bankArrayFirstRow + ['Match Status'] + gpArrayFirstRow)

    spacingColumnIndex = 14


    def rowForMatchedArrayOn(gpArrayCurrentRow):

        rowToReturn = gpArrayCurrentRow

        # comparison 
        # functions


        # dateComparisonFunction = getColumnComparisonFunction(19, 8)
        # rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([amountComparisonFunction, dateComparisonFunction], gpArrayCurrentRow, bankArray)

        # if len(rowIndicesThatMatch) == 1:
        #     filterOnAmountDateFunction = getFilterByIndexFunction([17, 19])
        #     rowToReturn.extend([myPyFunc.getMatchStatus(myPyFunc.filterArray(filterOnAmountDateFunction, gpArrayFirstRow))] + bankArray.pop(rowIndicesThatMatch[0]))
        # elif len(rowIndicesThatMatch) > 1:
        #     p('More than one row matches on the first pass')

        return rowToReturn


    myPyFunc.transferToArray(gpArray, matchedArray, rowForMatchedArrayOn)



    # while bankArray:

        # bankArrayCurrentRow = bankArray.pop(0)
    #     rowToAppend = bankArrayCurrentRow + ['']

    #     gpArrayCurrentRowIndex = 0

    #     while gpArrayCurrentRowIndex in range(0, len(gpArray) - 1) and len(rowToAppend) == len(bankArrayCurrentRow) + 1:

    #         gpArrayCurrentRow = gpArray[gpArrayCurrentRowIndex]

    #         if bankArrayCurrentRow[bankAmountColumnIndex] == gpArrayCurrentRow[gpAmountColumnIndex]:

    #             if bankArrayCurrentRow[bankTransactionTypeColumnIndex] == 'Check(s) Paid' and gpArrayCurrentRow[gpTrxTypeColumnIndex] == 'Check':

    #                 if bankArrayCurrentRow[bankDescriptionTwoColumnIndex] == gpArrayCurrentRow[gpTrxNumberColumnIndex]:

    #                     gpArrayRowToAppend = gpArray.pop(gpArrayCurrentRowIndex)
    #                     rowToAppend = rowToAppend + gpArrayRowToAppend
    #                     rowToAppend[spacingColumnIndex] = 'Matched on amount and check number'

    #         gpArrayCurrentRowIndex = gpArrayCurrentRowIndex + 1

    #     matchedArray.append(rowToAppend)


    # def getRowThatMatchesAmountAndCheckNumber(currentRow):
        
    #     rowToAppend = currentRow

    #     return rowToAppend
    
    


    # # myPyFunc.transferToArray(gpArray, matchedArray, getRowThatMatchesAmountAndDate)
    


    # # columnsToMatch = [
    # #     [17, 19],
    # #     [7, 8]
    # # ]

    # # def getRowThatMatchesAmountAndDate(currentRow):

    # #     rowToAppend = currentRow
    # #     rowsThatMatch = myPyFunc.secondArrayRowsMatchFirstArrayRow(currentRow, bankArray, columnsToMatch)

    # #     if len(rowsThatMatch) == 1:
    # #         rowToAppend = rowToAppend + [myPyFunc.getMatchStatus(myPyFunc.getColumnNamesFromFirstRow(columnsToMatch[0], firstArrayFirstRow))] + bankArray.pop(rowsThatMatch[0]['secondArrayRowIndex'])
    # #     elif len(rowsThatMatch) > 1:
    # #         p('More than one row match the first pass')

    # #     return rowToAppend


    # # myPyFunc.transferToArray(gpArray, matchedArray, getRowThatMatchesAmountAndDate)




    # # columnsToMatch = [
    # #     [17, 19],
    # #     [7, 8]
    # # ]

    # # def getMatchedRowToAppend(currentRow):

    # #     rowToAppend = currentRow
    # #     rowsThatMatch = secondArrayRowsMatchFirstArrayRow(secondArray, currentRow, columnsToMatch)

    # #     if len(rowsThatMatch) == 1:
    # #         rowToAppend = rowToAppend + [getMatchStatus(getColumnNames(columnsToMatch, firstArrayFirstRow))] + secondArray.pop(rowsThatMatch[0]['secondArrayRowIndex'])
    # #     elif len(rowsThatMatch) > 1:
    # #         p('More rows that match first pass')

    # #     return rowToAppend


    # # myPyFunc.transferToArray(bankArray, matchedArray, getMatchedRowToAppend)








    # # for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(matchedArray):

    # #     if len(comparisonCurrentRow) == len(bankArrayFirstRow) + 1 and comparisonCurrentRow[bankTransactionTypeColumnIndex] != 'Check(s) Paid':

    # #         gpRowsThatMatchComparisonCurrentRow = []
            
    # #         for gpArrayCurrentRowIndex, gpArrayCurrentRow in enumerate(gpArray):

    # #             if comparisonCurrentRow[bankAmountColumnIndex] == gpArrayCurrentRow[gpAmountColumnIndex] and comparisonCurrentRow[bankDateColumnIndex] == gpArrayCurrentRow[gpTrxDateColumnIndex]: 

    # #                 if gpArrayCurrentRow[gpTrxTypeColumnIndex] != 'Check' or (gpArrayCurrentRow[gpTrxTypeColumnIndex] == 'Check' and len(gpArrayCurrentRow[gpTrxNumberColumnIndex])!= 5):
    # #                     gpRowsThatMatchComparisonCurrentRow.append({
    # #                         'gpArrayRowIndex': gpArrayCurrentRowIndex,
    # #                         'gpArrayRow': gpArrayCurrentRow})

    # #         if len(gpRowsThatMatchComparisonCurrentRow) == 1:

    # #             matchedArray[comparisonCurrentRowIndex] = matchedArray[comparisonCurrentRowIndex] + gpArray.pop(gpRowsThatMatchComparisonCurrentRow[0]['gpArrayRowIndex'])
    # #             matchedArray[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched on amount and date'
            


    # # for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(matchedArray):

    # #     if len(comparisonCurrentRow) == len(bankArrayFirstRow) + 1 and comparisonCurrentRow[bankTransactionTypeColumnIndex] != 'Check(s) Paid':

    # #         gpRowsThatMatchComparisonCurrentRow = []

    # #         # if comparisonCurrentRow[bankAmountColumnIndex] == -1100.48:
    # #         #     p(1)
            
    # #         for gpArrayCurrentRowIndex in reversed(range(0, len(gpArray))):

    # #             if comparisonCurrentRow[bankAmountColumnIndex] == gpArray[gpArrayCurrentRowIndex][gpAmountColumnIndex]:

    # #                 if gpArray[gpArrayCurrentRowIndex][gpTrxTypeColumnIndex] != 'Check' or (gpArray[gpArrayCurrentRowIndex][gpTrxTypeColumnIndex] == 'Check' and len(gpArray[gpArrayCurrentRowIndex][gpTrxNumberColumnIndex])!= 5):

    # #                     gpRowsThatMatchComparisonCurrentRow.append({
    # #                         'gpArrayRowIndex': gpArrayCurrentRowIndex,
    # #                         'gpArrayRow': gpArray[gpArrayCurrentRowIndex]})

    # #         if len(gpRowsThatMatchComparisonCurrentRow) == 1:
    # #             matchedArray[comparisonCurrentRowIndex] = matchedArray[comparisonCurrentRowIndex] + gpArray.pop(gpRowsThatMatchComparisonCurrentRow[0]['gpArrayRowIndex'])
    # #             matchedArray[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched on amount, 1 bank row with 1 GP row'

    # #         if len(gpRowsThatMatchComparisonCurrentRow) > 1:

    # #             comparisonRowsThatMatchComparisonCurrentRow = []
    
    # #             for comparisonDuplicateRowIndex, comparisonDuplicateRow in enumerate(matchedArray):
        
    # #                 if comparisonDuplicateRow[bankAmountColumnIndex] == comparisonCurrentRow[bankAmountColumnIndex] and len(comparisonDuplicateRow) == len(bankArrayFirstRow) + 1:
                        
    # #                     comparisonRowsThatMatchComparisonCurrentRow.insert(0, {
    # #                         'comparisonDuplicateRowIndex': comparisonDuplicateRowIndex,
    # #                         'comparisonDuplicateRow': comparisonDuplicateRow
    # #                     })

    # #             gpRowsThatMatchLength = len(gpRowsThatMatchComparisonCurrentRow)            
    
    # #             if gpRowsThatMatchLength == len(comparisonRowsThatMatchComparisonCurrentRow):
                    
    # #                 for comparisonDuplicateMatchedRowIndex in range(0, len(comparisonRowsThatMatchComparisonCurrentRow)):
                        
    # #                     matchedArray[comparisonRowsThatMatchComparisonCurrentRow[comparisonDuplicateMatchedRowIndex]['comparisonDuplicateRowIndex']] = matchedArray[comparisonRowsThatMatchComparisonCurrentRow[comparisonDuplicateMatchedRowIndex]['comparisonDuplicateRowIndex']] + gpArray.pop(gpRowsThatMatchComparisonCurrentRow[comparisonDuplicateMatchedRowIndex]['gpArrayRowIndex'])
    # #                     matchedArray[comparisonRowsThatMatchComparisonCurrentRow[comparisonDuplicateMatchedRowIndex]['comparisonDuplicateRowIndex']][spacingColumnIndex] = f'Matched on amount, {gpRowsThatMatchLength} bank rows with {gpRowsThatMatchLength} GP rows'
        


    # # for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(matchedArray):

    # #     if len(comparisonCurrentRow) == len(bankArrayFirstRow) + 1 and comparisonCurrentRow[bankTransactionTypeColumnIndex] != 'Check(s) Paid':
    # #         # p(comparisonCurrentRow)

    # #         for dailyDepositsCurrentRow in dailyDepositsArray:
                
    # #             if comparisonCurrentRow[bankAmountColumnIndex] == dailyDepositsCurrentRow[dailyDepositsAmountColumnIndex]:
                    
    # #                 gpRowsThatMatchComparisonCurrentRow = []

    # #                 for gpArrayCurrentRowIndex in reversed(range(0, len(gpArray))):

    # #                     if gpArray[gpArrayCurrentRowIndex][gpTrxNumberColumnIndex][2:7] == dailyDepositsCurrentRow[dailyDepositsTransactionIDColumnIndex]:
    # #                         matchedArray[comparisonCurrentRowIndex] = matchedArray[comparisonCurrentRowIndex] + gpArray[gpArrayCurrentRowIndex]
    # #                         matchedArray[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched from Daily Deposits file'


    # # for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(matchedArray):

    # #     if len(comparisonCurrentRow) == len(bankArrayFirstRow) + 1 and comparisonCurrentRow[bankTransactionTypeColumnIndex] == 'Check(s) Paid':
    
    # #         gpRowsThatMatchComparisonCurrentRow = []
            
    # #         for gpArrayCurrentRowIndex, gpArrayCurrentRow in enumerate(gpArray):

    # #             if comparisonCurrentRow[bankAmountColumnIndex] == gpArrayCurrentRow[gpAmountColumnIndex] and comparisonCurrentRow[bankDateColumnIndex] == gpArrayCurrentRow[gpTrxDateColumnIndex]: 

    # #                 gpRowsThatMatchComparisonCurrentRow.append({
    # #                     'gpArrayRowIndex': gpArrayCurrentRowIndex,
    # #                     'gpArrayRow': gpArrayCurrentRow})

    # #         if len(gpRowsThatMatchComparisonCurrentRow) == 1:

    # #             matchedArray[comparisonCurrentRowIndex] = matchedArray[comparisonCurrentRowIndex] + gpArray.pop(gpRowsThatMatchComparisonCurrentRow[0]['gpArrayRowIndex'])
    # #             matchedArray[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched on amount and date, bank transaction is a check, GP transaction does not have the same check number'


    clearAndResizeParameters = [{
        'sheetObj': spreadsheetLevelObj.worksheet(sheets['matched']['name']),
        'resizeRows': 3,
        'startingRowIndexToClear': 0,
        'resizeColumns': 3
    },
    {
        'sheetObj': spreadsheetLevelObj.worksheet(sheets['notMatched']['name']),
        'resizeRows': 2,
        'startingRowIndexToClear': 0,
        'resizeColumns': 1
    }]



    myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)
    myGspreadFunc.displayArray(spreadsheetLevelObj.worksheet(sheets['matched']['name']), matchedArray)

    gpArray.insert(0, gpArrayFirstRow)
    myGspreadFunc.displayArray(spreadsheetLevelObj.worksheet(sheets['notMatched']['name']), gpArray)


    customTopRows = {'Comparison': 2}
    myGspreadFunc.setFiltersOnSpreadsheet(spreadsheetLevelObj, customTopRows)
    myGspreadFunc.autoAlignColumnsInSpreadsheet(spreadsheetLevelObj)



    # strToReturn = os.environ.get('urlOfKingGorillaGoogleSheetPublicStr')

    # if not strToReturn:

    #     pathToConfigDataJSON = Path(pathToRepos, 'privateData', 'herokuGorilla', 'configData.json')
    #     jsonFileObj = open(pathToConfigDataJSON)
    #     strToReturn = json.load(jsonFileObj)['urlOfKingGorillaGoogleSheetPublicStr']
    
    # strToReturn = strToReturn[:-1] + '871892682'

    # return strToReturn


def mainFunction(arrayOfArguments):
    reconcileArrays(True, arrayOfArguments[1], googleAccountUsername=arrayOfArguments[2])


if __name__ == '__main__':
    p(str(pathToThisPythonFile.name) + ' is not being imported. It is being run directly...')
    mainFunction(sys.argv)
else:
    p(str(pathToThisPythonFile.name) + ' is being imported. It is not being run directly...')