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
    from googleSheets.googleSheetsApps import reconcileArraysBankRec


# def sortArrayOfArrays(array, subArrayIndexToSortBy): 
#     # reverse = None (Sorts in Ascending order) 
#     # key is set to sort using second element of  
#     # sublist lambda has been used

#     return(sorted(array, key = lambda x: x[subArrayIndexToSortBy])) 


def reconcileArrays(oAuthMode, googleSheetTitle, googleAccountUsername=None):

    # pathBelowRepos = pathToThisPythonFile
    # spreadsheetLevelObj = myGspreadFunc.getSpreadsheetLevelObj(oAuthMode, pathBelowRepos, googleAccountUsername=googleAccountUsername).open(googleSheetTitle)

    # newAmtColName = 'New Amount'
    # dteStrColNme = 'Date Str'
    
    # gpNumColIdx = 12
    # gpNewAmtColIdx = 17
    # gpDateStrColIdx = 18
    # gpTypColIdx = 11
    # gpTrsfrColIdx = 19
    
    # bnkNme = 'Bank'
    # bnkStatusColIdx = 0
    # bnkDteColIdx = 1
    # bnkTypColIdx = 7
    # bnkDrCrColIdx = 8
    # bnkAmtColIdx = 9
    # bnkScndDescColIdx = 11
    # bnkNewAmtColIdx = 14
    # bnkDteStrColIdx = 15
    
    # dlyDepNme = 'Daily Deposits'
    # dlyDepAmtColIdx = 5
    # dlyDepTrxIdColIdx = 7
    
    # mtchdNme = 'Matched'
    # notMtchdNme = 'Did Not Match'

    # gpArray = reconcileArraysBankRec.getGPArray(spreadsheetLevelObj)
    # bankArray = spreadsheetLevelObj.worksheet(bnkNme).get_all_values()

    # def filterBankArray(currentRowIndex, currentRow):

    #     if currentRow[bnkStatusColIdx] not in ['H', 'B', 'T'] and currentRow[bnkTypColIdx] not in ['Data', 'Ledger Balance', 'Collected + 1 Day', 'Opening Collected', 'One Day Float', '2 Day Float', '3 Day + Float', 'MTD Avg Collected', 'MTD Avg Neg Collected', 'Total Credits', 'Number of Credits', 'Total Debits', 'Number of Debits', 'Float Adjustment(s)']:
    #         return True
    #     else:
    #         return False

    # bankArray = myPyFunc.filterArray(filterBankArray, bankArray)

    # def mapBankArray(currentRowIndex, currentRow):

    #     if currentRowIndex:

    #         currentAmount = myPyFunc.strToFloat(currentRow[bnkAmtColIdx])
    #         currentDate = currentRow[bnkDteColIdx]

    #         if len(currentDate) < 8:
    #             currentDate = '0' + currentDate

    #         currentDate = currentDate[4:8] + currentDate[0:4]

    #         if currentRow[bnkDrCrColIdx] == 'Debit':
    #             currentAmount = -currentAmount

    #         currentRow.append(currentAmount)
    #         currentRow.append(currentDate)

    #     else:

    #         currentRow.append(newAmtColName)
    #         currentRow.append(dteStrColNme)


    # bankArray = myPyFunc.mapArray(mapBankArray, bankArray)



    # bankArray = sortArrayOfArrays(bankArray, bnkDteColIdx)


    # def filterGPArray(currentRowIndex, currentRow):
    #     if datetime.strptime(currentRow[gpDteColIdx], '%Y-%m-%d %H:%M:%S') <= datetime(2020, 9, 30):
    #         return True
    #     else:
    #         return False

    # gpArray = myPyFunc.filterArray(filterGPArray, gpArray)
    # gpArray = sortArrayOfArrays(gpArray, gpDteColIdx)


    # dailyDepositsArray = spreadsheetLevelObj.worksheet(dlyDepNme).get_all_values()

    # def mapDailyDeposits(currentRowIndex, currentRow):

    #     if currentRowIndex:
    #         currentRow[dlyDepAmtColIdx] = myPyFunc.strToFloat(currentRow[dlyDepAmtColIdx])

    #     return currentRow

    # dailyDepositsArray = myPyFunc.mapArray(mapDailyDeposits, dailyDepositsArray)


    # gpArrayFirstRow = gpArray.pop(0)
    # bankArrayFirstRow = bankArray.pop(0)

    # for rowIndex, row in enumerate(bankArray):
    #     if row[bnkScndDescColIdx] == '88076':
    #         p(rowIndex)

    matchedArray = [['GP'] + [''] * (len(gpArrayFirstRow) - 1) + [''] + [bnkNme] + [''] * (len(bankArrayFirstRow) - 1)]
    matchedArray.append(gpArrayFirstRow + [''] + bankArrayFirstRow)

    # spacingColumnIndex = 14

    # amountComparisonFunction = myPyFunc.getColumnComparisonFunction(gpNewAmtColIdx, bnkNewAmtColIdx)


    # def rowForMatchedArrayOn(gpArrayCurrentRow):

    #     rowToReturn = gpArrayCurrentRow

    #     trxNumComparisonFunction = myPyFunc.getColumnComparisonFunction(gpNumColIdx, bnkScndDescColIdx)

    #     def typeComparisonFunction(gpArrayCurrentRow, bankArrayCurrentRow):

    #         if gpArrayCurrentRow[gpTypColIdx] == bankArrayCurrentRow[bnkTypColIdx][0:6]:
    #             return True
    #         return True

    #     rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([amountComparisonFunction, trxNumComparisonFunction, typeComparisonFunction], gpArrayCurrentRow, bankArray)

    #     if len(rowIndicesThatMatch) == 1:
    #         filterOnCheckAmountTypeFunction = myPyFunc.getFilterByIndexFunction([gpNewAmtColIdx, gpDateStrColIdx, gpTypColIdx])
    #         rowToReturn.extend([myPyFunc.getMatchStatus(myPyFunc.filterArray(filterOnCheckAmountTypeFunction, gpArrayFirstRow))] + bankArray.pop(rowIndicesThatMatch[0]))
    #     elif len(rowIndicesThatMatch) > 1:
    #         p('More than one row matches on the first pass')

    #     return rowToReturn


    # myPyFunc.transferToArray(gpArray, matchedArray, rowForMatchedArrayOn)



    # def rowForMatchedArrayOnAmount(gpArrayCurrentRowIndex, gpArrayCurrentRow):

    #     if len(gpArrayCurrentRow) == len(gpArrayFirstRow):

    #         dateComparisonFunction = myPyFunc.getColumnComparisonFunction(gpDateStrColIdx, bnkDteStrColIdx)
            
    #         def notCheckFunction(gpArrayCurrentRow, bankArrayCurrentRow):

    #             if gpArrayCurrentRow[gpTypColIdx] != 'Check' or (gpArrayCurrentRow[gpTypColIdx] == 'Check' and len(gpArrayCurrentRow[gpNumColIdx]) != 5):
    #                 return True
    #             return False

    #         rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([amountComparisonFunction, dateComparisonFunction, notCheckFunction], gpArrayCurrentRow, bankArray)

    #         def filterOnUnmatchedRowsByAmountFunction(matchedArrayCurrentRowIndex, matchedArrayCurrentRow):
                
    #             if len(matchedArrayCurrentRow) == len(gpArrayFirstRow) and matchedArrayCurrentRow[gpNewAmtColIdx] == gpArrayCurrentRow[gpNewAmtColIdx]:
                
    #                 return True
                
    #             return False

    #         if len(rowIndicesThatMatch) == 1 or len(rowIndicesThatMatch) == len(myPyFunc.filterArray(filterOnUnmatchedRowsByAmountFunction, matchedArray)):

    #             filterOnAmountDateFunction = myPyFunc.getFilterByIndexFunction([gpNewAmtColIdx, gpDateStrColIdx])
    #             gpArrayCurrentRow.extend([myPyFunc.getMatchStatus(myPyFunc.filterArray(filterOnAmountDateFunction, gpArrayFirstRow))] + bankArray.pop(rowIndicesThatMatch[0]))

    # myPyFunc.mapArray(rowForMatchedArrayOnAmount, matchedArray)




    # for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(matchedArray):

    #     if len(comparisonCurrentRow) == len(bankArrayFirstRow) + 1 and comparisonCurrentRow[bnkTypColIdx] != 'Check(s) Paid':

    #         gpRowsThatMatchComparisonCurrentRow = []

    #         # if comparisonCurrentRow[bnkAmtColIdx] == -1100.48:
    #         #     p(1)
            
    #         for gpArrayCurrentRowIndex in reversed(range(0, len(gpArray))):

    #             if comparisonCurrentRow[bnkAmtColIdx] == gpArray[gpArrayCurrentRowIndex][shts['gp']['colIdx']['amt']]:

    #                 if gpArray[gpArrayCurrentRowIndex][gpTypColIdx] != 'Check' or (gpArray[gpArrayCurrentRowIndex][gpTypColIdx] == 'Check' and len(gpArray[gpArrayCurrentRowIndex][gpNumColIdx])!= 5):

    #                     gpRowsThatMatchComparisonCurrentRow.append({
    #                         'gpArrayRowIndex': gpArrayCurrentRowIndex,
    #                         'gpArrayRow': gpArray[gpArrayCurrentRowIndex]})

    #         if len(gpRowsThatMatchComparisonCurrentRow) == 1:
    #             matchedArray[comparisonCurrentRowIndex] = matchedArray[comparisonCurrentRowIndex] + gpArray.pop(gpRowsThatMatchComparisonCurrentRow[0]['gpArrayRowIndex'])
    #             matchedArray[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched on amount, 1 bank row with 1 GP row'

    #         if len(gpRowsThatMatchComparisonCurrentRow) > 1:

    #             comparisonRowsThatMatchComparisonCurrentRow = []
    
    #             for comparisonDuplicateRowIndex, comparisonDuplicateRow in enumerate(matchedArray):
        
    #                 if comparisonDuplicateRow[bnkAmtColIdx] == comparisonCurrentRow[bnkAmtColIdx] and len(comparisonDuplicateRow) == len(bankArrayFirstRow) + 1:
                        
    #                     comparisonRowsThatMatchComparisonCurrentRow.insert(0, {
    #                         'comparisonDuplicateRowIndex': comparisonDuplicateRowIndex,
    #                         'comparisonDuplicateRow': comparisonDuplicateRow
    #                     })

    #             gpRowsThatMatchLength = len(gpRowsThatMatchComparisonCurrentRow)            
    
    #             if gpRowsThatMatchLength == len(comparisonRowsThatMatchComparisonCurrentRow):
                    
    #                 for comparisonDuplicateMatchedRowIndex in range(0, len(comparisonRowsThatMatchComparisonCurrentRow)):
                        
    #                     matchedArray[comparisonRowsThatMatchComparisonCurrentRow[comparisonDuplicateMatchedRowIndex]['comparisonDuplicateRowIndex']] = matchedArray[comparisonRowsThatMatchComparisonCurrentRow[comparisonDuplicateMatchedRowIndex]['comparisonDuplicateRowIndex']] + gpArray.pop(gpRowsThatMatchComparisonCurrentRow[comparisonDuplicateMatchedRowIndex]['gpArrayRowIndex'])
    #                     matchedArray[comparisonRowsThatMatchComparisonCurrentRow[comparisonDuplicateMatchedRowIndex]['comparisonDuplicateRowIndex']][spacingColumnIndex] = f'Matched on amount, {gpRowsThatMatchLength} bank rows with {gpRowsThatMatchLength} GP rows'
        


    # for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(matchedArray):

    #     if len(comparisonCurrentRow) == len(bankArrayFirstRow) + 1 and comparisonCurrentRow[bnkTypColIdx] != 'Check(s) Paid':
    #         # p(comparisonCurrentRow)

    #         for dailyDepositsCurrentRow in dailyDepositsArray:
                
    #             if comparisonCurrentRow[bnkAmtColIdx] == dailyDepositsCurrentRow[dlyDepAmtColIdx]:
                    
    #                 gpRowsThatMatchComparisonCurrentRow = []

    #                 for gpArrayCurrentRowIndex in reversed(range(0, len(gpArray))):

    #                     if gpArray[gpArrayCurrentRowIndex][gpNumColIdx][2:7] == dailyDepositsCurrentRow[dlyDepTrxIdColIdx]:
    #                         matchedArray[comparisonCurrentRowIndex] = matchedArray[comparisonCurrentRowIndex] + gpArray[gpArrayCurrentRowIndex]
    #                         matchedArray[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched from Daily Deposits file'


    # for comparisonCurrentRowIndex, comparisonCurrentRow in enumerate(matchedArray):

    #     if len(comparisonCurrentRow) == len(bankArrayFirstRow) + 1 and comparisonCurrentRow[bnkTypColIdx] == 'Check(s) Paid':
    
    #         gpRowsThatMatchComparisonCurrentRow = []
            
    #         for gpArrayCurrentRowIndex, gpArrayCurrentRow in enumerate(gpArray):

    #             if comparisonCurrentRow[bnkAmtColIdx] == gpArrayCurrentRow[shts['gp']['colIdx']['amt']] and comparisonCurrentRow[bnkDteColIdx] == gpArrayCurrentRow[gpDteColIdx]: 

    #                 gpRowsThatMatchComparisonCurrentRow.append({
    #                     'gpArrayRowIndex': gpArrayCurrentRowIndex,
    #                     'gpArrayRow': gpArrayCurrentRow})

    #         if len(gpRowsThatMatchComparisonCurrentRow) == 1:

    #             matchedArray[comparisonCurrentRowIndex] = matchedArray[comparisonCurrentRowIndex] + gpArray.pop(gpRowsThatMatchComparisonCurrentRow[0]['gpArrayRowIndex'])
    #             matchedArray[comparisonCurrentRowIndex][spacingColumnIndex] = 'Matched on amount and date, bank transaction is a check, GP transaction does not have the same check number'


    clearAndResizeParameters = [{
        'sheetObj': spreadsheetLevelObj.worksheet(mtchdNme),
        'resizeRows': 3,
        'startingRowIndexToClear': 0,
        'resizeColumns': 1
    },
    {
        'sheetObj': spreadsheetLevelObj.worksheet(notMtchdNme),
        'resizeRows': 2,
        'startingRowIndexToClear': 0,
        'resizeColumns': 1
    }]


    myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)
    myGspreadFunc.displayArray(spreadsheetLevelObj.worksheet(mtchdNme), matchedArray)

    bankArray.insert(0, bankArrayFirstRow)
    myGspreadFunc.displayArray(spreadsheetLevelObj.worksheet(notMtchdNme), bankArray)

    customTopRows = {'Matched': 2}
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