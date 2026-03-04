import os
import shutil
#test: endlos schleife 
import time
import logging
#paths sauber halten
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


#sheduler test
#import sched
#TO DO:
#inital scan

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
    

def move_file(file: Path):
    if not file.exists() or not file.is_file():
        return  #early escape
    ext = file.suffix.lower().lstrip(".")
    if not ext:
        return  #keine file endung
    target_dir = DOWNLOADS_FOLDER / ext
    target_dir.mkdir(exist_ok=True)
    target = target_dir / file.name

    #namenskonflikte 
    if target.exists():
        stem, suffix = file.stem, file.suffix
        i = 1
        while target.exists():
            target= target_dir / f"{stem} ({i}){suffix}" #hängt eine Nummer an filenamen (iterate)
            i += 1
    
    #move here 
    try:
        shutil.move(str(file), str(target))
        logging.info(f"moved: '{file.name}'->'{target_dir.name}/")
    except Exception as e:
        logging.error(f"move failed '{file}'->'{target}': {e}")

class SortHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        logging.info(f"Created event: {path.name}")
    #STOP case
        if path.name == "STOP.txt":
            logging.info("STOP.txt created (event). Main loop will stop")
            return
    
        if isStable(path):
            move_file(path)
        else:
            #fallback
            for _ in range (5):
                if isStable(path):
                    move_file(path)
                    break
                time.sleep(2)
    
    def on_modified(self, event):
        #optional wenn modification
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() in TEMP_EXTENSIONS:
            return


def main():
    logging.info("FileSorter started (watchdog)")

    observer = Observer()
    handler = SortHandler()
    observer.schedule(handler, str(DOWNLOADS_FOLDER), recursive=False)
    observer.start()
    
    try: 
        while True:
            #Stop check here
            if (DOWNLOADS_FOLDER / "STOP.txt").exists():
                logging.info("STOP found, ending")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Skript enden manually (keyboard interrupt)")
    finally:
        observer.stop()
        observer.join()
        logging.info("Observer stopped. Bye.")


if __name__ == "__main__":
    main()
