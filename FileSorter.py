import os
import shutil
import time
import threading
import pystray
from PIL import Image

user_folder = os.path.expanduser("~")
destination_folder = os.path.join(user_folder, "Downloads")
source_folder = os.path.join(user_folder, "Downloads")
automaticSortMode_status = False

# Move File
def moveFile(fullFilename, dst_folder):
    src = os.path.join(destination_folder, fullFilename)
    dst = os.path.join(destination_folder, dst_folder, fullFilename)
    shutil.move(src, dst)

# Iterate Filename-List to create and sort into Folders
def createSortIntoFolders():
    fileList = os.listdir(source_folder)
    for fullFilename in fileList:
        filename, filetype = os.path.splitext(fullFilename)
        filetype = filetype.replace(".", "")

        # If folder -> skip
        if filetype == "":
            continue

        dst_path = os.path.join(destination_folder, filetype)

        if os.path.exists(dst_path):
            moveFile(fullFilename, filetype) 
        else:
            os.makedirs(dst_path)
            moveFile(fullFilename, filetype)    

def manualSortMode(icon, item):
    print("Mode: [Manual]")

    fileList = os.listdir(source_folder)
    print("Files: ", fileList)
    
    createSortIntoFolders()
    print("Sort complete.")

def automaticSortMode():
    while True:
        if automaticSortMode_status:
            fileList = os.listdir(source_folder)
            print("Files: ", fileList)

            createSortIntoFolders()
            print("Sort complete.")
        time.sleep(10)
automaticMode = threading.Thread(target=automaticSortMode, daemon=True)

def toggleAutomaticSortMode(icon, item):
    global automaticSortMode_status
    automaticSortMode_status = not automaticSortMode_status
    print(f"Automatic Sort Mode: [{automaticSortMode_status}]")

def quitProgram(icon, item):
    print("Quitting FileSorter...")
    icon.stop()

# Main
print("-====+====-")
print("Program is now active. Use the System-Tray.")
print("-====+====-")

automaticMode.start()

# Tray
tray_image = Image.new('RGB', (64, 64), color='purple')
tray_menu = pystray.Menu(
    pystray.MenuItem("Manual Sort", manualSortMode),
    pystray.MenuItem("Automatic Sort", toggleAutomaticSortMode, checked=lambda item: automaticSortMode_status),
    pystray.MenuItem("Quit Program", quitProgram)
)
tray = pystray.Icon("FileSorter", tray_image, "FileSorter-Menu", tray_menu)
tray.run()