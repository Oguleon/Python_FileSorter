import os
import shutil
#test: endlos schleife 
import time
import logging
#paths sauber halten
from pathlib import Path
#sheduler test
#import sched

# Basis-Ordner (macros)
USER_FOLDER = Path.home() 
DOWNLOADS_FOLDER = USER_FOLDER / "Downloads"

#logging
LOG_FILE = DOWNLOADS_FOLDER / "background.log"
logging.basicConfig(
    filename=str(LOG_FILE),
     level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# Move File
def moveFile(full_filename: str, dst_folder_name: str) -> None:
    
    src = DOWNLOADS_FOLDER / full_filename
    dst_folder = DOWNLOADS_FOLDER / dst_folder_name
    dst = dst_folder / full_filename
    try:
        if not src.exists():
            logging.warning(f"Source does no longer exist (race?): {src}")
            return
        if src.is_dir():
            return
        dst_folder.mkdir(exist_ok=True)
    #src = os.path.join(downloads_folder, fullFilename)
    #dst = os.path.join(downloads_folder, dst_folder, fullFilename)
        shutil.move(str(src), str(dst))
        logging.info(f"moved {src.name} -> {dst_folder.name}/")
    except Exception as e:
        logging.error(f"error while moving '{src}' -> '{dst}':{e}")


# Iterate Filename-List to create and sort into Folders
def createSortIntoFolders(file_list: list[str]) -> None:
    for fullFilename in file_list:
        src = DOWNLOADS_FOLDER / fullFilename 
        
        if not src.exists() or not src.is_file():
            continue

        #filename, filetype = os.path.splitext(fullFilename)
        #filetype = filetype.replace(".", "")

        # Erweiterung ermitteln (ohne Punkt), z.B. ".pdf" -> "pdf"
        filetype = src.suffix.lower().lstrip(".")
        
        # If folder -> skip
        if filetype == "":
            continue

        
        # Zielordnername = Endung (z.B. "pdf")
        moveFile(fullFilename, filetype)

        
       

        #if os.path.exists(dst_path):
           # moveFile(fullFilename, filetype) 
        #else:
            #os.makedirs(dst_path)
            #moveFile(fullFilename, filetype)    

def mainloop():
    logging.info("FileSorter started")
    while True:
        try:
            logging.info("Skript läuft noch...")
            if (DOWNLOADS_FOLDER / "STOP.txt").exists(): #early escape
                logging.info("STOP-Datei erkannt. Script beendet sich.")
                break
            current_entries = os.listdir(DOWNLOADS_FOLDER)
            createSortIntoFolders(current_entries)

            print("-====+====-")
            print("Files: ", current_entries)
            print("-====+====-")
            time.sleep(5)
        except KeyboardInterrupt:
            logging.info("Skript ended manually (Keyboard Interrupt)")
            break
        except Exception as e:
            logging.error(f"unhandled error: {e}")
            time.sleep(5)  

if __name__ == "__main__":
    mainloop()
