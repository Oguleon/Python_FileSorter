import os
import shutil

# Move File
def moveFile(fullFilename, dst_folder):
    src = "./Sandbox/" + fullFilename
    dst = "./Sandbox/" + dst_folder + "/" + fullFilename
    shutil.move(src, dst)

# Iterate Filename-List to create and sort into Folders
def createSortIntoFolders():
    i = 0
    for fullFilename in fileList:
        filename, filetype = os.path.splitext(fullFilename)
        filetype = filetype.replace(".", "")
        if os.path.exists("./Sandbox/" + filetype):
            moveFile(fullFilename, filetype) 
        else:
            os.makedirs("./Sandbox/" + filetype)
            moveFile(fullFilename, filetype)    
     
# Main
print("-====+====-")

# Get Filenames and print them
fileList = os.listdir("./Sandbox")
print("Files: ", fileList)
createSortIntoFolders()

print("-====+====-")