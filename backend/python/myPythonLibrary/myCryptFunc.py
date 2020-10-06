from cryptography.fernet import Fernet
from pathlib import Path


def generateKey(pathToKeyFile):
    """
    Generates a key and save it into a file
    """
    
    generatedKey = Fernet.generate_key()

    with open(pathToKeyFile, 'wb') as keyFileObj:
        keyFileObj.write(generatedKey)



def openSavedKey(pathToKeyFile):
    """
    Loads the key from the current directory named `keyFile.key`
    """

    return open(pathToKeyFile, 'rb').read()



def encryptFile(pathOfFileToProcess, loadedKey, pathToSaveEncryptedFile=None):
    """
    Given a pathOfFileToProcess (str) and key (bytes), it encrypts the file and write it
    """

    fernetObjUsingKey = Fernet(loadedKey)

    with open(pathOfFileToProcess, "rb") as fileObj:
        # read all file data
        fileData = fileObj.read()


    # encrypt data
    encryptedFileData = fernetObjUsingKey.encrypt(fileData)

    # write the encrypted file
    with open(pathToSaveEncryptedFile, "wb") as fileObj:
        fileObj.write(encryptedFileData)



def decryptFile(pathOfEncryptedFile, loadedKey, pathToSaveDecryptedFile=None):
    """
    Given a pathOfEncryptedFile (str) and key (bytes), it decrypts the file and write it
    """

    fernetObjUsingKey = Fernet(loadedKey)

    with open(pathOfEncryptedFile, "rb") as fileObj:
        # read the encrypted data
        encryptedFileData = fileObj.read()

    # decrypt data
    decryptedFileData = fernetObjUsingKey.decrypt(encryptedFileData)


    # write the original file
    with open(pathToSaveDecryptedFile, "wb") as fileObj:
        fileObj.write(decryptedFileData)




def decryptIntoSameFolder(pathToFolder, fileName, encryptionKey):

	pathToDecryptedFile = Path(pathToFolder, 'decrypted' + fileName)

	decryptFile(Path(pathToFolder, 'encrypted' + fileName), encryptionKey, pathToSaveDecryptedFile=pathToDecryptedFile)
	return pathToDecryptedFile



def clearDecryptedFiles(decryptedFilesToClear):
	for decryptedFileToClear in decryptedFilesToClear:
			with open(decryptedFileToClear, "w") as fileObj:
				fileObj.write('')
