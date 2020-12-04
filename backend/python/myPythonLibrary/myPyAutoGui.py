import pyautogui as g
from pprint import pprint as p
from pathlib import Path


def typeCharactersOnRemoteDesktop(charactersToType, pause=None):

    charactersNeedingShift = (list(range(123, 127)) + list(range(94, 96)) + list(range(62, 91)) + [60, 58] + list(range(40, 44)) + list(range(33, 39)))
    

    for characterToType in charactersToType:

        if ord(characterToType) in charactersNeedingShift:

            priorPyAutoGuiPause = g.PAUSE
            if pause == None: pause = .0001
            g.PAUSE = pause

            # g.hotkey('shift', characterToType)
            g.keyDown('shift')
            g.press(characterToType)
            g.keyUp('shift')
            g.PAUSE = priorPyAutoGuiPause

        else:
            g.press(characterToType)


def repetitiveKeyPress(numberOfTabs, keyToPress):

    for i in range(0, numberOfTabs):
        g.press(keyToPress)


def clickImageWhenAppears(imageFileName, confidence=.9):

    g.click(getCoordinatesWhenImageAppears(imageFileName, confidence=confidence))


def clickWhenLocalPNGAppears(pngFileStem, pngFileDirectory, confidence=.9):

    pngFilePath = str(Path(pngFileDirectory, pngFileStem + '.png'))
    clickImageWhenAppears(pngFilePath, confidence=confidence)

def doubleClickWhenLocalPNGAppears(pngFileStem, pngFileDirectory, confidence=.9):

    pngFilePath = str(Path(pngFileDirectory, pngFileStem + '.png'))

    coordinates = getCoordinatesWhenLocalPNGAppears(pngFileStem, pngFileDirectory)
    
    g.click(x=coordinates.x, y=coordinates.y, clicks=2)


def getCoordinatesWhenLocalPNGAppears(pngFileStem, pngFileDirectory, confidence=.9, center=True):

    pngFilePath = str(Path(pngFileDirectory, pngFileStem + '.png'))
    return getCoordinatesWhenImageAppears(pngFilePath, confidence=.9, center=True)

def getCoordinatesWhenImageAppears(imageFileName, confidence=.9, center=True):

    coordinatesToReturn = None

    while not coordinatesToReturn:
        p(f'Looking for {imageFileName}')

        if center:
            coordinatesToReturn = g.locateCenterOnScreen(imageFileName, confidence=confidence)
        else:
            coordinatesToReturn = g.locateOnScreen(imageFileName, confidence=confidence)

    return coordinatesToReturn


def locateOnScreenLocal(pngFileStem, pngFileDirectory):

    pngFilePath = str(Path(pngFileDirectory, pngFileStem + '.png'))

    return g.locateOnScreen(pngFilePath, confidence=.9)



def getCoordinatesIfLocalPNGIsShowing(pngFileStem, pngFileDirectory, confidence=.96):

    pngFilePath = str(Path(pngFileDirectory, pngFileStem + '.png'))

    return g.locateOnScreen(pngFilePath, confidence=confidence)


def waitUntilLocalPNGDisappears(pngFileStem, pngFileDirectory):

    pngFilePath = str(Path(pngFileDirectory, pngFileStem + '.png'))

    waitUntilImageDisappears(pngFilePath)


def waitUntilLocalPNGAppears(pngFileStem, pngFileDirectory):

    pngFilePath = str(Path(pngFileDirectory, pngFileStem + '.png'))

    waitUntilImageAppears(pngFilePath)


def waitUntilImageDisappears(imageFileName, confidence=.9, center=True):

    coordinatesToReturn = g.locateOnScreen(imageFileName, confidence=confidence)

    while coordinatesToReturn:
        p(f'Waiting for {imageFileName} to disappear.')

        if center:
            coordinatesToReturn = g.locateCenterOnScreen(imageFileName, confidence=confidence)
        else:
            coordinatesToReturn = g.locateOnScreen(imageFileName, confidence=confidence)

    return coordinatesToReturn

def waitUntilImageAppears(imageFileName, confidence=.9, center=True):

    coordinatesToReturn = g.locateOnScreen(imageFileName, confidence=confidence)

    while not coordinatesToReturn:
        p(f'Waiting for {imageFileName} to appear.')

        if center:
            coordinatesToReturn = g.locateCenterOnScreen(imageFileName, confidence=confidence)
        else:
            coordinatesToReturn = g.locateOnScreen(imageFileName, confidence=confidence)

    return coordinatesToReturn

def typeStr(strToType):

    for characterToType in strToType:
        if characterToType == '_':
            g.keyDown('shift')
            g.press(characterToType)
            g.keyUp('shift')
        else:
            g.press(characterToType)

def clickLocalPNGWhenAppearsAndWaitUntilLocaPNGDisappears(imageFileNameToClick, imageFileNameToWaitUntilDisappears, parentDir):

    clickWhenLocalPNGAppears(imageFileNameToClick, parentDir)
    waitUntilLocalPNGDisappears(imageFileNameToWaitUntilDisappears, parentDir)


def typeAndWriteOnRemoteDesktop(charactersToType, pause=None):

    charactersNeedingShift = (list(range(123, 127)) + list(range(94, 96)) + list(range(62, 91)) + [60, 58] + list(range(40, 44)) + list(range(33, 39)))
    
    stringToWrite = ''

    for characterToType in charactersToType:

        if ord(characterToType) in charactersNeedingShift:

            if stringToWrite: 
                g.write(stringToWrite)
                stringToWrite = ''

            priorPyAutoGuiPause = g.PAUSE

            if pause == None: pause = .0001
            g.PAUSE = pause

            # g.hotkey('shift', characterToType)
            g.keyDown('shift')
            g.press(characterToType)
            g.keyUp('shift')
            g.PAUSE = priorPyAutoGuiPause

        else:
            stringToWrite = stringToWrite + characterToType
    
    if stringToWrite: g.write(stringToWrite)