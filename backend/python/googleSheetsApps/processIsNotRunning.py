# Spec: 
# Output: Whether a process is running or not
# Input: Process will be input into the command line
# Input: Whether the data should be saved to Google Sheets or not will be input into the commandline



#local application imports
from pathlib import Path
import sys
pathToThisPythonFile = Path(__file__).resolve()
sys.path.append(str(pathToThisPythonFile.parents[2]))
import googleSheets.myGoogleSheetsLibrary.myGoogleSheetsFunc as myGoogleSheetsFunc
import googleSheets.myGoogleSheetsLibrary.myGspreadFunc as myGspreadFunc

#standard library imports
from pprint import pprint as p
import psutil


#third-party imports
import gspread




def getArrayOfProcesses(saveToGoogleSheetsBoolean):

    arrayOfRunningProcesses = [['Name', 'Process ID', 'Exe', 'Current Directory', 'Execution Module', 'Command Line (0)']]

    for runningProcess in psutil.process_iter():
        
        processToAppend = [runningProcess.name(), runningProcess.pid]

        try:
            processToAppend.append(runningProcess.exe())
        except psutil.AccessDenied:
            processToAppend.append('')


        try:
            processToAppend.append(runningProcess.cwd())
        except psutil.AccessDenied:
            processToAppend.append('')

        try:
            for cmdLineOfProcess in runningProcess.cmdline():
                processToAppend.append(cmdLineOfProcess)
        except psutil.AccessDenied:
            pass

        arrayOfRunningProcesses.append(processToAppend)


    numberOfTotalColumns = max([len(i) for i in arrayOfRunningProcesses])


    for rowIndex, row in enumerate(arrayOfRunningProcesses):

        if len(row) < numberOfTotalColumns:

            numberOfColumnsToAdd = numberOfTotalColumns - len(row)

            if rowIndex == 0:

                for columnNumberToAdd in range(1, numberOfColumnsToAdd + 1):
                    row.append('Command Line (' + str(columnNumberToAdd) + ')')
                    # p('Command Line (' + str(columnNumberToAdd) + ')')

            else:
                row.extend([''] * numberOfColumnsToAdd)


    # p(arrayOfRunningProcesses)
    if saveToGoogleSheetsBoolean:
        saveToGoogleSheets(arrayOfRunningProcesses)


    return arrayOfRunningProcesses



def processIsNotRunning(processFromInput, saveToGoogleSheetsBoolean):
    
    for runningProcess in getArrayOfProcesses(saveToGoogleSheetsBoolean):
        if processFromInput in runningProcess:
            return False
    
    return True


def saveToGoogleSheets(arrayToOutput):
    
    objOfSheets = myGspreadFunc.getObjOfSheets('Data For Apps')

    clearAndResizeParameters = [{
        'sheetObj': objOfSheets['currentlyRunningProcesses']['sheetObj'],
        'resizeRows': 2,
        'resizeColumns': 6,
        'startingRowIndexToClear': 1
    }]

    
    myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)

    myGspreadFunc.displayArray(objOfSheets['currentlyRunningProcesses']['sheetObj'], arrayToOutput)



def mainFunction(arrayOfArguments):

    processFromInput = arrayOfArguments[1].lstrip('explorer ')
    
    saveToGoogleSheetsFromInput = False
    
    if arrayOfArguments[2] == 'outputToGoogleSheets':
        saveToGoogleSheetsFromInput = True

    if processIsNotRunning(processFromInput, saveToGoogleSheetsFromInput):
        p("Process '{}' is not running".format(processFromInput))
        return True
    else:
        p("Process '{}' is already running".format(processFromInput))
        return False



if __name__ == '__main__':
    p(str(pathToThisPythonFile.name) + ' is not being imported. It is being run directly...')
    mainFunction(sys.argv)
else:
	p(str(pathToThisPythonFile.name) + ' is being imported. It is not being run directly...')
