import os
import shutil
import time
import threading
import pystray
from PIL import Image

user_folder = os.path.expanduser("~")
downloads_folder = os.path.join(user_folder, "Downloads")
automaticSortMode_status = False

# Move File
def moveFile(fullFilename, dst_folder):
    src = os.path.join(downloads_folder, fullFilename)
    dst = os.path.join(downloads_folder, dst_folder, fullFilename)
    shutil.move(src, dst)

# Iterate Filename-List to create and sort into Folders
def createSortIntoFolders():
    fileList = os.listdir(downloads_folder)
    for fullFilename in fileList:
        filename, filetype = os.path.splitext(fullFilename)
        filetype = filetype.replace(".", "")

        # If folder -> skip
        if filetype == "":
            continue

        dst_path = os.path.join(downloads_folder, filetype)

        if os.path.exists(dst_path):
            moveFile(fullFilename, filetype) 
        else:
            os.makedirs(dst_path)
            moveFile(fullFilename, filetype)    

def automaticSortMode():
    while automaticSortMode_status:
        createSortIntoFolders()
        time.sleep(10)

automaticMode = threading.Thread(target=automaticSortMode, daemon=True)

# Main
print("-====+====-")

# Get Filenames and print them
fileList = os.listdir(downloads_folder)
print("Files: ", fileList)
createSortIntoFolders()

automaticSortMode_status = True
automaticMode.start()

input("Program is currently active. Press [ENTER] to quit...\n")

print("-====+====-")