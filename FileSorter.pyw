import os
import shutil
#test: endlos schleife 
import time
import logging
#paths sauber halten
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandle


#sheduler test
#import sched
#TO DO
#prüfen ob Datei stabil ist- wer noch wächst wird in ruhe gelassen 
#Namenskonflikte loesen 


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
TEMP_EXTENSIONS = {".crdownload", ".part", ".tmp"} #tmp dateien werden grundsätzlich ignoriert

def isStable(file: Path, wait_secs: float = 2.5, retries: int = 5) -> bool: #rueckgabewert true false 
    if not file.exists() or not file.is_file(): #early escape: kein file
        return False
    if file.suffix.lower() in TEMP_EXTENSIONS: #dateiendung ist tmp 
        return False
    
    try: 
        prev_size = file.stat().st_size #file size speichern
        for _ in range(retries):
            time.sleep(wait_secs)
            if not file.exists():
                return False
            curr_size = file.stat().st_size
            if curr_size == prev_size:
                return True     #innerhalb der tries stable geworden
            prev_size = curr_size
        return False
    except Exception as e:
        logging.warning(f"stability check failed for {file}: {e}")
        return False
    

# Move File OLD
#def moveFile(full_filename: str, dst_folder_name: str) -> None:
    
    #src = DOWNLOADS_FOLDER / full_filename
    #dst_folder = DOWNLOADS_FOLDER / dst_folder_name
    #dst = dst_folder / full_filename
    #try:
     #   if not src.exists():
      #      logging.warning(f"Source does no longer exist (race?): {src}")
      #      return
      #  if src.is_dir():
      #      return
      #  dst_folder.mkdir(exist_ok=True)
      #  shutil.move(str(src), str(dst))
       # logging.info(f"moved {src.name} -> {dst_folder.name}/")
    #except Exception as e:
     #   logging.error(f"error while moving '{src}' -> '{dst}':{e}")
#Move neu
def move_file(file: Path):
    if not file.exists() or not file.is_file():
        return  #early escape
    ext = file.suffix.lower().lstrip(".")
    if not ext:
        return  #keine file endung
    target_dir = DOWNLOADS_FOLDER / ext
    target_dir.mkdir(exist_ok=True)
    target = target_dir / file.name

    #namenskonflikte hier
    #here 

    #move here 
    try:
        shutil.move(str(file), str(target))
        logging.info(f"moved: '{file.name}'->'{target_dir.name}/")
    except Exception as e:
        logging.error(f"move failed '{file}'->'{target}': {e}")


# Iterate Filename-List to create and sort into Folders
def createSortIntoFolders(file_list: list[str]) -> None:
    for fullFilename in file_list:
        src = DOWNLOADS_FOLDER / fullFilename 
        
        if not src.exists() or not src.is_file():
            continue

        # Erweiterung ermitteln (ohne Punkt), z.B. ".pdf" -> "pdf"
        filetype = src.suffix.lower().lstrip(".")
        
        # If folder -> skip
        if filetype == "":
            continue

        # Zielordnername = Endung (z.B. "pdf")
        moveFile(fullFilename, filetype)   

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
