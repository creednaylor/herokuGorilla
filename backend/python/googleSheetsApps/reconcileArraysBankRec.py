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



def reconcileArraysBankRec(bankAccount, googleSheetTitle, googleAccountUsername, copyNotes):

    pathBelowRepos = pathToThisPythonFile
    spreadsheetLevelObj = myGspreadFunc.getSpreadsheetLevelObj(True, pathBelowRepos, googleAccountUsername=googleAccountUsername).open(googleSheetTitle)

    dteStrColNme = 'New Date'
    newAmtColName = 'New Amount'

    gpAmtColIdx = 5
    gpTypColIdx = 11
    gpNumColIdx = 12
    gpDateStrColIdx = 19
    gpNewAmtColIdx = 20

    gpNme = 'GP'
    bankNme = 'Bank'
    dlyDepNme = 'Daily Deposits'
    mtchdNme = 'Matched'
    notMtchdNme = 'Did Not Match'


    def getGPArray(spreadsheetLevelObj):

        gpArray = spreadsheetLevelObj.worksheet(gpNme).get_all_values()
        
        def filterOutBlankDates(currentRow):

            gpDteColIdx = 1

            if currentRow[gpDteColIdx] != '':
                return True
            return False

        gpArray = list(filter(filterOutBlankDates, gpArray))

        def mapGPArray(currentRowIndex, currentRow):

            gpDteColIdx = 1
            gpTypColIdx = 11
            gpPdToColIdx = 14

            if currentRowIndex:

                currentType = currentRow[gpTypColIdx]
                currentPaidTo = currentRow[gpPdToColIdx]

                currentAmount = myPyFunc.strToFloat(currentRow[gpAmtColIdx])
                if currentType in ['Decrease Adjustment', 'Check', 'Withdrawl'] or 'Transfer To' in currentPaidTo: currentAmount = -currentAmount

                gpTypObj = {
                    'Check': 2,
                    'Decrease Adjustment': 5,
                    'Deposit': 1,
                    'Increase Adjustment': 4,
                    'Withdrawl': 3,
                    'Interest Income': 8
                }

                newGPTyp = str(gpTypObj[currentRow[gpTypColIdx]]) + ' - ' + currentRow[gpTypColIdx]

                if currentRow[gpPdToColIdx]:
                    if currentRow[gpPdToColIdx][:11] == 'Transfer To':
                        newGPTyp = '6 - Transfer Out'
                    elif currentRow[gpPdToColIdx][:13] == "Transfer From":
                        newGPTyp = '7 - Transfer In'
    
                for columnToAppend in [newGPTyp, currentRow[gpNumColIdx], myPyFunc.dateStrToStr(currentRow[gpDteColIdx]), currentAmount]:
                    currentRow.append(columnToAppend)

            else:

                for columnToAppend in ['New CM Trx Type', 'New CM Trx Number', dteStrColNme, newAmtColName]:
                    currentRow.append(columnToAppend)
            
            return currentRow

        return myPyFunc.mapArray(mapGPArray, gpArray)


    gpArray = getGPArray(spreadsheetLevelObj)
    gpArrayFirstRow = gpArray.pop(0)
    bankArray = spreadsheetLevelObj.worksheet(bankNme).get_all_values()

    def transformPrimaryBankArray(bankArray):

        bankStatusColIdx = 0
        bankDteColIdx = 1
        bankDrCrColIdx = 8
        bankNotesColIdx = 13

        if copyNotes:

            def rowsMatch(notMtchdArrayRow, bankArrayRow):

                for columnIndex in range(0, bankNotesColIdx):

                    if notMtchdArrayRow[columnIndex] != bankArrayRow[columnIndex]:

                        return False

                return True

            def removeCarriageReturn(currentRow):

                currentRow[bankThrdDescColIdx] = currentRow[bankThrdDescColIdx].replace('\n', '')
                return currentRow

            bankArray = list(map(removeCarriageReturn, bankArray))

            notMtchdArray = spreadsheetLevelObj.worksheet(notMtchdNme).get_all_values()
            
            for notMtchdArrayRow in notMtchdArray:

                for bankArrayRow in bankArray:

                    if rowsMatch(notMtchdArrayRow, bankArrayRow):
                        
                        bankArrayRow[bankNotesColIdx] = notMtchdArrayRow[bankNotesColIdx]

            clearAndResizeParameters = [
                {
                    'sheetObj': spreadsheetLevelObj.worksheet(bankNme),
                    'resizeRows': 2,
                    'startingRowIndexToClear': 0,
                    'resizeColumns': 2
                }
            ]

            myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)
            myGspreadFunc.displayArray(spreadsheetLevelObj.worksheet(bankNme), bankArray)


        def filterBankArray(currentRow):

            if currentRow[bankStatusColIdx] not in ['H', 'B', 'T'] and currentRow[bankTypColIdx] not in ['Data', 'Ledger Balance', 'Collected + 1 Day', 'Opening Collected', 'One Day Float', '2 Day Float', '3 Day + Float', 'MTD Avg Collected', 'MTD Avg Neg Collected', 'Total Credits', 'Number of Credits', 'Total Debits', 'Number of Debits', 'Float Adjustment(s)']:
                return True
            return False

        bankArray = list(filter(filterBankArray, bankArray))

        def mapBankArray(currentRowIndex, currentRow):

            if currentRowIndex:

                currentAmount = myPyFunc.strToFloat(currentRow[bankAmtColIdx])

                currentDate = currentRow[bankDteColIdx]

                lengthOfDateStr = 8
                lengthOfMonthAndDay = 4

                if len(currentDate) < lengthOfDateStr:
                    currentDate = '0' + currentDate

                currentDate = currentDate[lengthOfMonthAndDay:lengthOfDateStr] + currentDate[:lengthOfMonthAndDay]

                if currentRow[bankDrCrColIdx] == 'Debit': currentAmount = -currentAmount

                currentRow[bankThrdDescColIdx] = currentRow[bankThrdDescColIdx].replace('\n', '')

                for columnToAppend in [currentAmount, currentDate]:
                    currentRow.append(columnToAppend)

            else:

                for columnToAppend in [newAmtColName, dteStrColNme]:
                    currentRow.append(columnToAppend)

        return myPyFunc.mapArray(mapBankArray, bankArray)



    def getPrimaryDailyDepositsArray():


        dailyDepositsArray = spreadsheetLevelObj.worksheet(dlyDepNme).get_all_values()

        def mapDailyDeposits(currentRowIndex, currentRow):

            if currentRowIndex:
                currentRow[dlyDepNetAmtColIdx] = myPyFunc.strToFloat(currentRow[dlyDepNetAmtColIdx])

            return currentRow

        return myPyFunc.mapArray(mapDailyDeposits, dailyDepositsArray)



    def getSecondaryBankArray(bankArray):

        bankDteColIdx = 0
        bankDrColIdx = 5
        bankCrColIdx = 6

        def mapBankArray(currentRowIndex, currentRow):

            if currentRowIndex:

                currentDebitAmount = currentRow[bankDrColIdx]
                currentCreditAmount = currentRow[bankCrColIdx]
                currentDate = currentRow[bankDteColIdx]

                for columnToAppend in [myPyFunc.strToFloat(currentCreditAmount) - myPyFunc.strToFloat(currentDebitAmount), myPyFunc.dateStrToStr(currentDate)]:
                    currentRow.append(columnToAppend)

            else:

                for columnToAppend in [newAmtColName, dteStrColNme]:
                    currentRow.append(columnToAppend)
                
                return currentRow

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


    if bankAccount == 'Primary':
        bankTypColIdx = 7
        bankAmtColIdx = 9
        bankThrdDescColIdx = 12

        dlyDepNetAmtColIdx = 5
        
        bankArray = transformPrimaryBankArray(bankArray)
        dailyDepositsArray = getPrimaryDailyDepositsArray()


    elif bankAccount == 'Secondary':
        bankNewAmtColIdx = 7
        bankDteStrColIdx = 8
        bankArray = getSecondaryBankArray(bankArray)


    bankArrayFirstRow = bankArray.pop(0)

    matchedArray = [[gpNme] + [''] * (len(gpArrayFirstRow) - 1) + [''] + [bankNme] + [''] * (len(bankArrayFirstRow) - 1)]
    matchedArray.append(gpArrayFirstRow + [''] + bankArrayFirstRow)



    def createFilterOnUnmatchedRows(matchedArrayCurrentRow):
            
            def filterOnUnmatchedRows(arrayToFilterCurrentRow):
                
                if len(arrayToFilterCurrentRow) == len(gpArrayFirstRow) and arrayToFilterCurrentRow[gpNewAmtColIdx] == matchedArrayCurrentRow[gpNewAmtColIdx]:

                    return True

                return False

            return filterOnUnmatchedRows


    def getCompletedMatchedArrayPrimary(matchedArray):

        amountComparisonFunction = myPyFunc.getColumnComparisonFunction(gpNewAmtColIdx, bankNewAmtColIdx)
        dateComparisonFunction = myPyFunc.getColumnComparisonFunction(gpDateStrColIdx, bankDteStrColIdx)
        trxNumComparisonFunction = myPyFunc.getColumnComparisonFunction(gpNumColIdx, bankScndDescColIdx)
        lengthOfCheckNumber = 5

        def typeComparisonFunction(firstArrayCurrentRow, bankArrayCurrentRow):

            if firstArrayCurrentRow[gpTypColIdx] == bankArrayCurrentRow[bankTypColIdx][:lengthOfCheckNumber]:
                return True
            return False

        def rowForMatchedArrayOnAmountTrxNumType(gpArrayCurrentRow):

            rowToReturn = gpArrayCurrentRow

            rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([amountComparisonFunction, trxNumComparisonFunction, typeComparisonFunction], gpArrayCurrentRow, bankArray)

            if len(rowIndicesThatMatch) == 1:
                filterFieldsForMatchStatus = myPyFunc.getFilterByIndexFunction([gpNewAmtColIdx, gpDateStrColIdx, gpTypColIdx])
                rowToReturn.extend([myPyFunc.getMatchStatus(myPyFunc.filterArray(filterFieldsForMatchStatus, gpArrayFirstRow))] + bankArray.pop(rowIndicesThatMatch[0]))
            elif len(rowIndicesThatMatch) > 1:
                p('More than one row matches on the first pass')

            return rowToReturn


        myPyFunc.transferToArray(gpArray, matchedArray, rowForMatchedArrayOnAmountTrxNumType)

        def checkComparisonFunction(firstArrayCurrentRow, bankArrayCurrentRow):

            if firstArrayCurrentRow[gpTypColIdx] != 'Check' or (firstArrayCurrentRow[gpTypColIdx] == 'Check' and len(firstArrayCurrentRow[gpNumColIdx]) != lengthOfCheckNumber):
                return True
            return False


        def rowForMatchedArrayOnAmountDateNotCheck(matchedArrayCurrentRow):

            if len(matchedArrayCurrentRow) == len(gpArrayFirstRow):

                rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([amountComparisonFunction, dateComparisonFunction, checkComparisonFunction], matchedArrayCurrentRow, bankArray)
                filterByCurrentAmount = createFilterOnUnmatchedRows(matchedArrayCurrentRow)

                if len(rowIndicesThatMatch) == 1 or len(rowIndicesThatMatch) == len(list(filter(filterByCurrentAmount, matchedArray))):
                    filterFieldsForMatchStatus = myPyFunc.getFilterByIndexFunction([gpNewAmtColIdx, gpDateStrColIdx])
                    return matchedArrayCurrentRow + [myPyFunc.getMatchStatus(myPyFunc.filterArray(filterFieldsForMatchStatus, gpArrayFirstRow))] + bankArray.pop(rowIndicesThatMatch[0])

            return matchedArrayCurrentRow

        matchedArray = list(map(rowForMatchedArrayOnAmountDateNotCheck, matchedArray))

        def rowForMatchedArrayOnAmountNotCheck(matchedArrayCurrentRow):

            if len(matchedArrayCurrentRow) == len(gpArrayFirstRow):

                rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([amountComparisonFunction, checkComparisonFunction], matchedArrayCurrentRow, bankArray)
                filterByCurrentAmount = createFilterOnUnmatchedRows(matchedArrayCurrentRow)

                if len(rowIndicesThatMatch) == 1 or len(rowIndicesThatMatch) == len(list(filter(filterByCurrentAmount, matchedArray))):
                    filterFieldsForMatchStatus = myPyFunc.getFilterByIndexFunction([gpNewAmtColIdx])
                    return matchedArrayCurrentRow + [myPyFunc.getMatchStatus(myPyFunc.filterArray(filterFieldsForMatchStatus, gpArrayFirstRow))] + bankArray.pop(rowIndicesThatMatch[0])

            return matchedArrayCurrentRow

        matchedArray = list(map(rowForMatchedArrayOnAmountNotCheck, matchedArray))

        def rowForMatchedArrayOnAmountDate(matchedArrayCurrentRow):

            if len(matchedArrayCurrentRow) == len(gpArrayFirstRow):

                rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([amountComparisonFunction, dateComparisonFunction], matchedArrayCurrentRow, bankArray)
                filterByCurrentAmount = createFilterOnUnmatchedRows(matchedArrayCurrentRow)

                if len(rowIndicesThatMatch) == 1 or len(rowIndicesThatMatch) == len(list(filter(filterByCurrentAmount, matchedArray))):
                    return matchedArrayCurrentRow + ['Matched On New Amount and Date Str, ignoring transaction type'] + bankArray.pop(rowIndicesThatMatch[0])

            return matchedArrayCurrentRow

        matchedArray = list(map(rowForMatchedArrayOnAmountDate, matchedArray))

        def rowForMatchedArrayAmount(matchedArrayCurrentRow):

            if len(matchedArrayCurrentRow) == len(gpArrayFirstRow):

                rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([amountComparisonFunction], matchedArrayCurrentRow, bankArray)
                filterByCurrentAmount = createFilterOnUnmatchedRows(matchedArrayCurrentRow)

                if len(rowIndicesThatMatch) == 1 or len(rowIndicesThatMatch) == len(list(filter(filterByCurrentAmount, matchedArray))):
                    return matchedArrayCurrentRow + ['Matched On New Amount, ignoring transaction type'] + bankArray.pop(rowIndicesThatMatch[0])

            return matchedArrayCurrentRow

        matchedArray = list(map(rowForMatchedArrayAmount, matchedArray))

        def rowForMatchedArrayOnTrxNumTypeNotAmount(matchedArrayCurrentRow):

            if len(matchedArrayCurrentRow) == len(gpArrayFirstRow):

                rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([trxNumComparisonFunction, typeComparisonFunction], matchedArrayCurrentRow, bankArray)
                filterByCurrentAmount = createFilterOnUnmatchedRows(matchedArrayCurrentRow)

                if len(rowIndicesThatMatch) == 1 or len(rowIndicesThatMatch) == len(list(filter(filterByCurrentAmount, matchedArray))):
                    return matchedArrayCurrentRow + ['AMOUNT DOESN\'T MATCH! Matched trx number and type, but not amount'] + bankArray.pop(rowIndicesThatMatch[0])

            return matchedArrayCurrentRow

        matchedArray = list(map(rowForMatchedArrayOnTrxNumTypeNotAmount, matchedArray))

        def rowForMatchedArrayOnDlyDepBistrackID(matchedArrayCurrentRow):

            if len(matchedArrayCurrentRow) == len(gpArrayFirstRow):

                def dailyDepBistrackIDComparisonFunction(matchedArrayCurrentRow, dailyDepositsArrayCurrentRow):

                    lengthOfBistrackID = 5
                    lengthOfBistrackPrefix = 2
                    dlyDepTrxIdColIdx = 7

                    if matchedArrayCurrentRow[gpNumColIdx][lengthOfBistrackPrefix:lengthOfBistrackID + lengthOfBistrackPrefix] == dailyDepositsArrayCurrentRow[dlyDepTrxIdColIdx]:
                        return True
                    return False

                rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([dailyDepBistrackIDComparisonFunction], matchedArrayCurrentRow, dailyDepositsArray)
                filterByCurrentAmount = createFilterOnUnmatchedRows(matchedArrayCurrentRow)
                
                if len(rowIndicesThatMatch) == 1 or len(rowIndicesThatMatch) == len(list(filter(filterByCurrentAmount, matchedArray))):
                    return matchedArrayCurrentRow + ['AMOUNT DOESN\'T MATCH! Matched to Daily Deposits on Bistrack ID'] + dailyDepositsArray.pop(rowIndicesThatMatch[0])

            return matchedArrayCurrentRow

        matchedArray = list(map(rowForMatchedArrayOnDlyDepBistrackID, matchedArray))


        # def rowForMatchedArrayOnDlyDepFirstAmount(matchedArrayCurrentRow):

        #     if len(matchedArrayCurrentRow) == len(gpArrayFirstRow):

        #         def dailyDepFirstAmountComparisonFunction(matchedArrayCurrentRow, dailyDepositsArrayCurrentRow):

        #             if matchedArrayCurrentRow[gpAmtColIdx] == dailyDepositsArrayCurrentRow[dlyDepNetAmtColIdx]:
        #                 return True
        #             return False

        #         rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([dailyDepFirstAmountComparisonFunction], matchedArrayCurrentRow, dailyDepositsArray)
        #         filterByCurrentAmount = createFilterOnUnmatchedRows(matchedArrayCurrentRow)
            
        #         if len(rowIndicesThatMatch) == 1 or len(rowIndicesThatMatch) == len(list(filter(filterByCurrentAmount, matchedArray))):
                    
        #             def filterBankArrayOnAmount(currentRow):
                        
        #                 if currentRow[bankAmtColIdx] == matchedArrayCurrentRow[gpAmtColIdx]
        #                 #get row from bankarray

        #             return matchedArrayCurrentRow + ['AMOUNT DOESN\'T MATCH! Matched to Daily Deposits on net amount'] + dailyDepositsArray.pop(rowIndicesThatMatch[0])

        #     return matchedArrayCurrentRow

        # matchedArray = list(map(rowForMatchedArrayOnDlyDepFirstAmount, matchedArray))


        # def rowForMatchedArrayOnDlyDepGrossAmount(matchedArrayCurrentRow):

        #     if len(matchedArrayCurrentRow) == len(gpArrayFirstRow):

        #         def dailyDepGrossAmountComparisonFunction(matchedArrayCurrentRow, dailyDepositsArrayCurrentRow):

        #             dlyDepGrossAmtColIdx = 6

        #             if matchedArrayCurrentRow[gpAmtColIdx] == dailyDepositsArrayCurrentRow[dlyDepGrossAmtColIdx]:
        #                 return True
        #             return False

        #         rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([dailyDepGrossAmountComparisonFunction], matchedArrayCurrentRow, dailyDepositsArray)
        #         filterByCurrentAmount = createFilterOnUnmatchedRows(matchedArrayCurrentRow)
            
        #         if len(rowIndicesThatMatch) == 1 or len(rowIndicesThatMatch) == len(list(filter(filterByCurrentAmount, matchedArray))):
        #             return matchedArrayCurrentRow + ['AMOUNT DOESN\'T MATCH! Matched to Daily Deposits on gross amount'] + dailyDepositsArray.pop(rowIndicesThatMatch[0])

        #     return matchedArrayCurrentRow

        # matchedArray = list(map(rowForMatchedArrayOnDlyDepGrossAmount, matchedArray))

        return matchedArray



    def getCompletedMatchedArraySecondary():

        amountComparisonFunction = myPyFunc.getColumnComparisonFunction(gpNewAmtColIdx, bankNewAmtColIdx)

        def rowForMatchedArrayOnAmountDateNotCheck(gpArrayCurrentRow):

            rowToReturn = gpArrayCurrentRow

            dateComparisonFunction = myPyFunc.getColumnComparisonFunction(gpDateStrColIdx, bankDteStrColIdx)
            rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([amountComparisonFunction, dateComparisonFunction], gpArrayCurrentRow, bankArray)

            if len(rowIndicesThatMatch) == 1:
                filterFieldsForMatchStatus = myPyFunc.getFilterByIndexFunction([gpNewAmtColIdx, gpDateStrColIdx])
                rowToReturn.extend([myPyFunc.getMatchStatus(myPyFunc.filterArray(filterFieldsForMatchStatus, gpArrayFirstRow))] + bankArray.pop(rowIndicesThatMatch[0]))
            elif len(rowIndicesThatMatch) > 1:
                p('More than one row matches on the first pass')

            return rowToReturn


        myPyFunc.transferToArray(gpArray, matchedArray, rowForMatchedArrayOnAmountDateNotCheck)


        def rowForMatchedArrayOnAmountDateNotCheck(matchedArrayCurrentRow):

            if len(matchedArrayCurrentRow) == len(gpArrayFirstRow):

                rowIndicesThatMatch = myPyFunc.rowIndicesInSecondFromTestsOnFirst([amountComparisonFunction], matchedArrayCurrentRow, bankArray)

                filterByCurrentAmount = createFilterOnUnmatchedRows(matchedArrayCurrentRow)

                if len(rowIndicesThatMatch) == 1 or len(rowIndicesThatMatch) == len(list(filter(filterByCurrentAmount, matchedArray))):

                    filterFieldsForMatchStatus = myPyFunc.getFilterByIndexFunction([gpNewAmtColIdx])
                    return matchedArrayCurrentRow + [myPyFunc.getMatchStatus(myPyFunc.filterArray(filterFieldsForMatchStatus, gpArrayFirstRow))] + bankArray.pop(rowIndicesThatMatch[0])

            return matchedArrayCurrentRow

        matchedArray = list(map(rowForMatchedArrayOnAmountDateNotCheck, matchedArray))





        # def addMatchesFromDailyDepositsArray(currentRowIndex, currentRow):

        #     if len(currentRow) == len(gpArrayFirstRow):

        #         rowsThatMatch = getMatchedDailyDepositsRows(dailyDepositsArray, currentRow)

        #         if len(rowsThatMatch) == 1:
        #             pass

        # matchedArray = myPyFunc.mapArray(addMatchesFromDailyDepositsArray, matchedArray)

    if bankAccount == 'Primary':
        bankScndDescColIdx = 11
        bankNewAmtColIdx = 14
        bankDteStrColIdx = 15
        matchedArray = getCompletedMatchedArrayPrimary(matchedArray)

    elif bankAccount == 'Secondary':
        matchedArray = getCompletedMatchedArraySecondary()


    clearAndResizeParameters = [
        {
            'sheetObj': spreadsheetLevelObj.worksheet(mtchdNme),
            'resizeRows': 3,
            'startingRowIndexToClear': 0,
            'resizeColumns': 3
        },
        {
            'sheetObj': spreadsheetLevelObj.worksheet(notMtchdNme),
            'resizeRows': 2,
            'startingRowIndexToClear': 0,
            'resizeColumns': 3
        }
    ]


    for row in matchedArray:
        pass
        # row.insert()

    myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)
    myGspreadFunc.displayArray(spreadsheetLevelObj.worksheet(mtchdNme), matchedArray)

    bankArray.insert(0, bankArrayFirstRow)
    myGspreadFunc.displayArray(spreadsheetLevelObj.worksheet(notMtchdNme), bankArray)

    topRowsParameters = {mtchdNme: 2}
    myGspreadFunc.setFiltersOnSpreadsheet(spreadsheetLevelObj, topRowsParameters)

    gpFormatParameters = {
        gpNme: [
            {
                'range': ['F:F', 'G:G'],
                'format': 'currencyWithoutSymbol'
            }
        ]
    }


    myGspreadFunc.setFormattingOnSpreadsheet(spreadsheetLevelObj, gpFormatParameters)

    if bankAccount == 'Primary':

        bankFormatParameters = [
            {
                'range': ['J:J'],
                'format': 'currencyWithoutSymbol'
            }
        ]

        allFormatParameters = {
            bankNme: bankFormatParameters,
            dlyDepNme: [
                {
                    'range': ['F:F'],
                    'format': 'currencyWithoutSymbol'
                }
            ],
            mtchdNme: gpFormatParameters[gpNme] + [
                {
                    'range': ['U:U', 'AF:AF', 'AK:AK'],
                    'format': 'currencyWithoutSymbol'
                }
            ],
            notMtchdNme: bankFormatParameters + [
                {
                    'range': ['O:O'],
                    'format': 'currencyWithoutSymbol'
                }
            ]
        }

        myGspreadFunc.setFormattingOnSpreadsheet(spreadsheetLevelObj, allFormatParameters)
        
    myGspreadFunc.autoAlignColumnsInSpreadsheet(spreadsheetLevelObj)


    if bankAccount == 'Primary':

        columnWidthParameters = [
            {
                'sheetName': mtchdNme,
                'columnToAdjust': len(gpArrayFirstRow) + 1 + bankThrdDescColIdx
            },
            {
                'sheetName': notMtchdNme,
                'columnToAdjust': bankThrdDescColIdx
            }
        ]

        columnWidthRequest = {
            "requests": []
        }
        

        for sheetInfo in columnWidthParameters:
            columnWidthRequest['requests'].append(
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": spreadsheetLevelObj.worksheet(sheetInfo['sheetName'])._properties['sheetId'],
                            "dimension": "COLUMNS",
                            "startIndex": sheetInfo['columnToAdjust'],
                            "endIndex": sheetInfo['columnToAdjust'] + 1
                        },
                        "properties": {
                            "pixelSize": 400
                        },
                        "fields": "pixelSize"
                    }
                }
            )

            columnWidthRequest['requests'].append(
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": spreadsheetLevelObj.worksheet(sheetInfo['sheetName'])._properties['sheetId'],
                            "startColumnIndex": sheetInfo['columnToAdjust'],
                            "endColumnIndex": sheetInfo['columnToAdjust'] + 1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "wrapStrategy" : "CLIP",
                            }
                        },
                        "fields": "userEnteredFormat(wrapStrategy)"
                    }
                }
            )

        spreadsheetLevelObj.batch_update(columnWidthRequest)



def mainFunction(arrayOfArguments):

    copyNotes = False

    if len(arrayOfArguments) == 4 and arrayOfArguments[3] == 'copyNotes': copyNotes = True
    reconcileArraysBankRec(arrayOfArguments[1], 'Bank Rec ' + arrayOfArguments[1], googleAccountUsername=arrayOfArguments[2], copyNotes=copyNotes)


if __name__ == '__main__':
    p(str(pathToThisPythonFile.name) + ' is not being imported. It is being run directly...')
    mainFunction(sys.argv)
else:
    p(str(pathToThisPythonFile.name) + ' is being imported. It is not being run directly...')