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



def mapGPArray(currentRowIndex, currentRow):

    newAmtColName = 'New Amount'
    dteStrColNme = 'Date Str'
    gpDteColIdx = 1
    gpAmtColIdx = 5
    gpTypColIdx = 11
    gpPdToColIdx = 14

    if currentRowIndex:

        currentType = currentRow[gpTypColIdx]
        currentPaidTo = currentRow[gpPdToColIdx]

        currentAmount = myPyFunc.strToFloat(currentRow[gpAmtColIdx])
        if currentType in ['Decrease Adjustment', 'Check', 'Withdrawl'] or 'Transfer To' in currentPaidTo: currentAmount = -currentAmount

        currentTransfer = ''

        if currentRow[gpPdToColIdx]:
            if currentRow[gpPdToColIdx][0:11] == 'Transfer To':
                currentTransfer = 'Out'
            elif currentRow[gpPdToColIdx][0:13] == "Transfer From":
                currentTransfer = 'In'


        currentRow.append(currentAmount)
        currentRow.append(myPyFunc.dateStrToStr(currentRow[gpDteColIdx]))
        currentRow.append(currentTransfer)

    else:

        currentRow.append(newAmtColName)
        currentRow.append(dteStrColNme)
        currentRow.append('Transfer')



def getGPArray(spreadsheetLevelObj):

    def removeBlankDates(currentRowIndex, currentRow):

        gpDteColIdx = 1

        if currentRow[gpDteColIdx] == '':
            return False
        else:
            return True

    gpArray = spreadsheetLevelObj.worksheet('GP').get_all_values()
    gpArray = myPyFunc.filterArray(removeBlankDates, gpArray)
    return myPyFunc.mapArray(mapGPArray, gpArray)



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


def reconcileArraysBankRec(oAuthMode, bank, googleSheetTitle, googleAccountUsername=None):

    pathBelowRepos = pathToThisPythonFile
    spreadsheetLevelObj = myGspreadFunc.getSpreadsheetLevelObj(oAuthMode, pathBelowRepos, googleAccountUsername=googleAccountUsername).open(googleSheetTitle)

    newAmtColName = 'New Amount'
    dteStrColNme = 'Date Str'
    
    gpTypColIdx = 11
    gpNumColIdx = 12
    gpNewAmtColIdx = 17
    gpDateStrColIdx = 18
    gpTrsfrColIdx = 19
    

    mtchdNme = 'Matched'
    notMtchdNme = 'Did Not Match'
    
    bnkNme = 'Bank'

    gpArray = getGPArray(spreadsheetLevelObj)
    gpArrayFirstRow = gpArray.pop(0)

    def getPrimaryBankArray():

        bnkStatusColIdx = 0
        bnkDteColIdx = 1
        bnkDrCrColIdx = 8
        bnkAmtColIdx = 9

        bankArray = spreadsheetLevelObj.worksheet(bnkNme).get_all_values()

        def filterBankArray(currentRowIndex, currentRow):

            # p(currentRow)
            # p(currentRow[bnkStatusColIdx])
            # p(currentRow[bnkTypColIdx])

            if currentRow[bnkStatusColIdx] not in ['H', 'B', 'T'] and currentRow[bnkTypColIdx] not in ['Data', 'Ledger Balance', 'Collected + 1 Day', 'Opening Collected', 'One Day Float', '2 Day Float', '3 Day + Float', 'MTD Avg Collected', 'MTD Avg Neg Collected', 'Total Credits', 'Number of Credits', 'Total Debits', 'Number of Debits', 'Float Adjustment(s)']:
                return True
            else:
                return False

        bankArray = myPyFunc.filterArray(filterBankArray, bankArray)

        def mapBankArray(currentRowIndex, currentRow):

            if currentRowIndex:

                currentAmount = myPyFunc.strToFloat(currentRow[bnkAmtColIdx])
                currentDate = currentRow[bnkDteColIdx]

                if len(currentDate) < 8:
                    currentDate = '0' + currentDate

                currentDate = currentDate[4:8] + currentDate[0:4]

                if currentRow[bnkDrCrColIdx] == 'Debit':
                    currentAmount = -currentAmount

                currentRow.append(currentAmount)
                currentRow.append(currentDate)

            else:

                currentRow.append(newAmtColName)
                currentRow.append(dteStrColNme)


        return myPyFunc.mapArray(mapBankArray, bankArray)


    def getPrimaryDailyDepositsArray():
        
        dlyDepNme = 'Daily Deposits'
        dlyDepAmtColIdx = 5
        dlyDepTrxIdColIdx = 7
        dailyDepositsArray = spreadsheetLevelObj.worksheet(dlyDepNme).get_all_values()

        def mapDailyDeposits(currentRowIndex, currentRow):

            if currentRowIndex:
                currentRow[dlyDepAmtColIdx] = myPyFunc.strToFloat(currentRow[dlyDepAmtColIdx])

            return currentRow

        return myPyFunc.mapArray(mapDailyDeposits, dailyDepositsArray)



    def getSecondaryBankArray():

        bnkDteColIdx = 0
        bnkDrColIdx = 5
        bnkCrColIdx = 6

        def mapBankArray(currentRowIndex, currentRow):

            if currentRowIndex:

                currentDebitAmount = currentRow[bnkDrColIdx]
                currentCreditAmount = currentRow[bnkCrColIdx]
                currentDate = currentRow[bnkDteColIdx]

                currentRow.append(myPyFunc.strToFloat(currentCreditAmount) - myPyFunc.strToFloat(currentDebitAmount))
                currentRow.append(myPyFunc.dateStrToStr(currentDate))
            
            else:

                currentRow.append(newAmtColName)
                currentRow.append(dteStrColNme)

        bankArray = spreadsheetLevelObj.worksheet(bnkNme).get_all_values()
        return myPyFunc.mapArray(mapBankArray, bankArray)



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


    if bank == 'Primary':
        bnkTypColIdx = 7
        bankArray = getPrimaryBankArray()
        dailyDepositsArray = getPrimaryDailyDepositsArray()
        
    elif bank == 'Secondary':
        bnkNewAmtColIdx = 7
        bnkDteStrColIdx = 8
        bankArray = getSecondaryBankArray()

        
    bankArrayFirstRow = bankArray.pop(0)

    matchedArray = [['GP'] + [''] * (len(gpArrayFirstRow) - 1) + [''] + [bnkNme] + [''] * (len(bankArrayFirstRow) - 1)]
    matchedArray.append(gpArrayFirstRow + [''] + bankArrayFirstRow)


    def getPrimaryCompletedMatchedArray():

        amountComparisonFunction = myPyFunc.getColumnComparisonFunction(gpNewAmtColIdx, bnkNewAmtColIdx)
        dateComparisonFunction = myPyFunc.getColumnComparisonFunction(gpDateStrColIdx, bnkDteStrColIdx)

        def rowForMatchedArrayOnAmountTrxNumType(gpArrayCurrentRow):

            rowToReturn = gpArrayCurrentRow

            trxNumComparisonFunction = myPyFunc.getColumnComparisonFunction(gpNumColIdx, bnkScndDescColIdx)

            def typeComparisonFunction(gpArrayCurrentRow, bankArrayCurrentRow):

                if gpArrayCurrentRow[gpTypColIdx] == bankArrayCurrentRow[bnkTypColIdx][0:6]:
                    return True
                return True

            rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([amountComparisonFunction, trxNumComparisonFunction, typeComparisonFunction], gpArrayCurrentRow, bankArray)

            if len(rowIndicesThatMatch) == 1:
                filterOnCheckAmountTypeFunction = myPyFunc.getFilterByIndexFunction([gpNewAmtColIdx, gpDateStrColIdx, gpTypColIdx])
                rowToReturn.extend([myPyFunc.getMatchStatus(myPyFunc.filterArray(filterOnCheckAmountTypeFunction, gpArrayFirstRow))] + bankArray.pop(rowIndicesThatMatch[0]))
            elif len(rowIndicesThatMatch) > 1:
                p('More than one row matches on the first pass')

            return rowToReturn


        myPyFunc.transferToArray(gpArray, matchedArray, rowForMatchedArrayOnAmountTrxNumType)

        def notCheckFunction(gpArrayCurrentRow, bankArrayCurrentRow):

                    if gpArrayCurrentRow[gpTypColIdx] != 'Check' or (gpArrayCurrentRow[gpTypColIdx] == 'Check' and len(gpArrayCurrentRow[gpNumColIdx]) != 5):
                        return True
                    return False

        def rowForMatchedArrayOnAmountDateNotCheck(gpArrayCurrentRowIndex, gpArrayCurrentRow):

            if len(gpArrayCurrentRow) == len(gpArrayFirstRow):

                rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([amountComparisonFunction, dateComparisonFunction, notCheckFunction], gpArrayCurrentRow, bankArray)

                def filterOnUnmatchedRowsByAmountFunction(matchedArrayCurrentRowIndex, matchedArrayCurrentRow):

                    if len(matchedArrayCurrentRow) == len(gpArrayFirstRow) and matchedArrayCurrentRow[gpNewAmtColIdx] == gpArrayCurrentRow[gpNewAmtColIdx]:

                        return True

                    return False

                if len(rowIndicesThatMatch) == 1 or len(rowIndicesThatMatch) == len(myPyFunc.filterArray(filterOnUnmatchedRowsByAmountFunction, matchedArray)):
                    filterOnAmountDateFunction = myPyFunc.getFilterByIndexFunction([gpNewAmtColIdx, gpDateStrColIdx])
                    gpArrayCurrentRow.extend([myPyFunc.getMatchStatus(myPyFunc.filterArray(filterOnAmountDateFunction, gpArrayFirstRow))] + bankArray.pop(rowIndicesThatMatch[0]))

        arrayToReturn = myPyFunc.mapArray(rowForMatchedArrayOnAmountDateNotCheck, matchedArray)

        def rowForMatchedArrayOnAmountNotCheck(gpArrayCurrentRowIndex, gpArrayCurrentRow):

            if len(gpArrayCurrentRow) == len(gpArrayFirstRow):

                rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([amountComparisonFunction, notCheckFunction], gpArrayCurrentRow, bankArray)

                def filterOnUnmatchedRowsByAmountFunction(matchedArrayCurrentRowIndex, matchedArrayCurrentRow):

                    if len(matchedArrayCurrentRow) == len(gpArrayFirstRow) and matchedArrayCurrentRow[gpNewAmtColIdx] == gpArrayCurrentRow[gpNewAmtColIdx]:

                        return True

                    return False

                if len(rowIndicesThatMatch) == 1 or len(rowIndicesThatMatch) == len(myPyFunc.filterArray(filterOnUnmatchedRowsByAmountFunction, matchedArray)):
                    filterOnAmountFunction = myPyFunc.getFilterByIndexFunction([gpNewAmtColIdx])
                    gpArrayCurrentRow.extend([myPyFunc.getMatchStatus(myPyFunc.filterArray(filterOnAmountFunction, gpArrayFirstRow))] + bankArray.pop(rowIndicesThatMatch[0]))

        arrayToReturn = myPyFunc.mapArray(rowForMatchedArrayOnAmountNotCheck, matchedArray)

        def rowForMatchedArrayOnAmountDate(gpArrayCurrentRowIndex, gpArrayCurrentRow):

            if len(gpArrayCurrentRow) == len(gpArrayFirstRow):

                rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([amountComparisonFunction, dateComparisonFunction], gpArrayCurrentRow, bankArray)

                def filterOnUnmatchedRowsByAmountFunction(matchedArrayCurrentRowIndex, matchedArrayCurrentRow):

                    if len(matchedArrayCurrentRow) == len(gpArrayFirstRow) and matchedArrayCurrentRow[gpNewAmtColIdx] == gpArrayCurrentRow[gpNewAmtColIdx]:

                        return True

                    return False

                if len(rowIndicesThatMatch) == 1 or len(rowIndicesThatMatch) == len(myPyFunc.filterArray(filterOnUnmatchedRowsByAmountFunction, matchedArray)):
                    gpArrayCurrentRow.extend(['Matched On New Amount and Date Str, ignoring transaction type'] + bankArray.pop(rowIndicesThatMatch[0]))

        arrayToReturn = myPyFunc.mapArray(rowForMatchedArrayOnAmountDate, matchedArray)

        def rowForMatchedArrayAmount(gpArrayCurrentRowIndex, gpArrayCurrentRow):

            if len(gpArrayCurrentRow) == len(gpArrayFirstRow):

                rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([amountComparisonFunction], gpArrayCurrentRow, bankArray)

                def filterOnUnmatchedRowsByAmountFunction(matchedArrayCurrentRowIndex, matchedArrayCurrentRow):

                    if len(matchedArrayCurrentRow) == len(gpArrayFirstRow) and matchedArrayCurrentRow[gpNewAmtColIdx] == gpArrayCurrentRow[gpNewAmtColIdx]:

                        return True

                    return False

                if len(rowIndicesThatMatch) == 1 or len(rowIndicesThatMatch) == len(myPyFunc.filterArray(filterOnUnmatchedRowsByAmountFunction, matchedArray)):
                    gpArrayCurrentRow.extend(['Matched On New Amount, ignoring transaction type'] + bankArray.pop(rowIndicesThatMatch[0]))

        arrayToReturn = myPyFunc.mapArray(rowForMatchedArrayAmount, matchedArray)


        # def rowForMatchedArrayDailyDeposits(gpArrayCurrentRowIndex, gpArrayCurrentRow):

        #     if len(gpArrayCurrentRow) == len(gpArrayFirstRow):

        #         rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([amountComparisonFunction], gpArrayCurrentRow, bankArray)

        #         def filterOnUnmatchedRowsByAmountFunction(matchedArrayCurrentRowIndex, matchedArrayCurrentRow):

        #             if len(matchedArrayCurrentRow) == len(gpArrayFirstRow) and matchedArrayCurrentRow[gpNewAmtColIdx] == gpArrayCurrentRow[gpNewAmtColIdx]:

        #                 return True

        #             return False

        #         if len(rowIndicesThatMatch) == 1 or len(rowIndicesThatMatch) == len(myPyFunc.filterArray(filterOnUnmatchedRowsByAmountFunction, matchedArray)):
        #             gpArrayCurrentRow.extend(['Matched On New Amount, ignoring transaction type'] + bankArray.pop(rowIndicesThatMatch[0]))

        # arrayToReturn = myPyFunc.mapArray(rowForMatchedArrayDailyDeposits, matchedArray)

        return arrayToReturn



    def getSecondaryCompletedMatchedArray():

        amountComparisonFunction = myPyFunc.getColumnComparisonFunction(gpNewAmtColIdx, bnkNewAmtColIdx)

        def rowForMatchedArrayOnAmountDateNotCheck(gpArrayCurrentRow):

            rowToReturn = gpArrayCurrentRow

            dateComparisonFunction = myPyFunc.getColumnComparisonFunction(gpDateStrColIdx, bnkDteStrColIdx)
            rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([amountComparisonFunction, dateComparisonFunction], gpArrayCurrentRow, bankArray)

            if len(rowIndicesThatMatch) == 1:
                filterOnAmountDateFunction = myPyFunc.getFilterByIndexFunction([gpNewAmtColIdx, gpDateStrColIdx])
                rowToReturn.extend([myPyFunc.getMatchStatus(myPyFunc.filterArray(filterOnAmountDateFunction, gpArrayFirstRow))] + bankArray.pop(rowIndicesThatMatch[0]))
            elif len(rowIndicesThatMatch) > 1:
                p('More than one row matches on the first pass')

            return rowToReturn


        myPyFunc.transferToArray(gpArray, matchedArray, rowForMatchedArrayOnAmountDateNotCheck)


        def rowForMatchedArrayOnAmountDateNotCheck(gpArrayCurrentRowIndex, gpArrayCurrentRow):

            if len(gpArrayCurrentRow) == len(gpArrayFirstRow):

                rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([amountComparisonFunction], gpArrayCurrentRow, bankArray)

                def filterOnUnmatchedRowsByAmountFunction(matchedArrayCurrentRowIndex, matchedArrayCurrentRow):
                    
                    if len(matchedArrayCurrentRow) == len(gpArrayFirstRow) and matchedArrayCurrentRow[gpNewAmtColIdx] == gpArrayCurrentRow[gpNewAmtColIdx]:
                    
                        return True
                    
                    return False


                if len(rowIndicesThatMatch) == 1 or len(rowIndicesThatMatch) == len(myPyFunc.filterArray(filterOnUnmatchedRowsByAmountFunction, matchedArray)):

                    filterOnAmountFunction = myPyFunc.getFilterByIndexFunction([gpNewAmtColIdx])
                    gpArrayCurrentRow.extend([myPyFunc.getMatchStatus(myPyFunc.filterArray(filterOnAmountFunction, gpArrayFirstRow))] + bankArray.pop(rowIndicesThatMatch[0]))

        return myPyFunc.mapArray(rowForMatchedArrayOnAmountDateNotCheck, matchedArray)

        # def addMatchesFromDailyDepositsArray(currentRowIndex, currentRow):

        #     if len(currentRow) == len(gpArrayFirstRow):

        #         rowsThatMatch = getMatchedDailyDepositsRows(dailyDepositsArray, currentRow)

        #         if len(rowsThatMatch) == 1:
        #             pass
        
        # matchedArray = myPyFunc.mapArray(addMatchesFromDailyDepositsArray, matchedArray)

    if bank == 'Primary':
        bnkScndDescColIdx = 11
        bnkNewAmtColIdx = 14
        bnkDteStrColIdx = 15
        matchedArray = getPrimaryCompletedMatchedArray()

    elif bank == 'Secondary':
        matchedArray = getSecondaryCompletedMatchedArray()



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



def mainFunction(arrayOfArguments):
    reconcileArraysBankRec(True, arrayOfArguments[1], 'Bank Rec ' + arrayOfArguments[1], googleAccountUsername=arrayOfArguments[2])


if __name__ == '__main__':
    p(str(pathToThisPythonFile.name) + ' is not being imported. It is being run directly...')
    mainFunction(sys.argv)
else:
    p(str(pathToThisPythonFile.name) + ' is being imported. It is not being run directly...')