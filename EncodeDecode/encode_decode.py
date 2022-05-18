from optparse import OptionParser
import binascii
import os

DELIMITER = "//-_-_-//"
ENCODING = "utf-8"

# for added  files after EOF in pdf
def put(args):
    # get pdf file name
    targetFile = args[0]
    # get path pdf file
    targetFileName = os.path.basename(targetFile)
    # create patched (pdf + secret file) file name
    patchedFileName = targetFileName.split(".")[0] + "_patched." + targetFileName.split(".")[1]
    # create patched file
    with open(targetFile, "rb") as hostFile, open(patchedFileName, "wb+") as patchedFile:
        # read original pdf and wrie in new one
        patchedFile.write(hostFile.read())
        
        index = 1
        # join a loop we can hide multiple files
        while index < len(args):
            sourceFile = args[index]
            sourceFileName = os.path.basename(sourceFile)
            print("trying to hide", sourceFile, "...")
            # for each file for the secret
            with open(sourceFile, "rb") as fileToHide:
                # write source file name + our DELIMITER chracrters and write encding secret file read as binary write as asci
                patchedFile.write(binascii.hexlify(bytes(sourceFileName + DELIMITER, ENCODING)))
                patchedFile.write(binascii.hexlify(fileToHide.read()))
                patchedFile.write(binascii.hexlify(bytes(sourceFileName + DELIMITER, ENCODING)))
                print("!!! ", sourceFileName, "hidden! in ", targetFile )
            index += 1


    
# extract hidden file    
def get(args):
    # open pdf hidden contain secret files
    with open(args[0], "rb") as targetFile:
        fileContent = targetFile.read()
        # detect EOF
        fileContentSplit = fileContent.split(bytes("%%EOF", ENCODING))
        # detect hidden file lenght
        fileContent = fileContentSplit[len(fileContentSplit)-1]
        # extracrt hidden content
        fileContent = binascii.unhexlify(fileContent.strip())

    if fileContent is None:
        print("something went wrong ...")
        exit
    # split first part is file name second part is file content
    hiddenFiles = fileContent.split(bytes(DELIMITER, ENCODING))
    fileName = None
    fileContent = None
    # we can extracrt multiple files so we in loop
    for index, element in enumerate(hiddenFiles):
        if index % 2 != 0:
            print("extract", fileName, "...")
            with open(fileName, "wb") as hiddenFile:
                hiddenFile.write(element)
                print("...", fileName, "extracted!")            
        elif index % 2 == 0:
            fileName = bytes.decode(element)

if __name__ == "__main__":
    parser = OptionParser()  
    parser.add_option("-p", "--put", action="store_true", help="hide files in PDF")  
    parser.add_option("-g", "--get", action="store_true", help="extract hidden files")  
    (options, args) = parser.parse_args() 

    if options.put and options.get is None:
        put(args)
    elif options.put is None and options.get:
        get(args)
    
