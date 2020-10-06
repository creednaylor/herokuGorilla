import pyautogui as g


def typeCharactersOnRemoteDesktop(charactersToType, priorPyAutoGuiPause, pause=None):

    charactersNeedingShift = (list(range(123, 127)) + list(range(94, 96)) + list(range(62, 91)) + [60, 58] + list(range(40, 44)) + list(range(33, 39)))
    

    for characterToType in charactersToType:

        if ord(characterToType) in charactersNeedingShift:

            if pause == None:
                g.PAUSE = .0001
            else:
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


def clickImageAfterWaiting(pngFileName, confidence=.9):

    g.click(getCoordinatesAfterWaiting(pngFileName, confidence=confidence))


def getCoordinatesAfterWaiting(pngFileName, confidence=.9, center=True):

    coordinatesToReturn = None

    while not coordinatesToReturn:
        p(f'Looking for {pngFileName[:-4]}')

        if center:
            coordinatesToReturn = g.locateCenterOnScreen(pngFileName, confidence=confidence)
        else:
            coordinatesToReturn = g.locateOnScreen(pngFileName, confidence=confidence)

    return coordinatesToReturn


def waitUntilGone(pngFileName, confidence=.9, center=True):

    coordinatesToReturn = g.locateOnScreen(pngFileName, confidence=confidence)

    while coordinatesToReturn:
        p(f'Waiting for {pngFileName[:-4]} to disappear.')

        if center:
            coordinatesToReturn = g.locateCenterOnScreen(pngFileName, confidence=confidence)
        else:
            coordinatesToReturn = g.locateOnScreen(pngFileName, confidence=confidence)

    return coordinatesToReturn
