import os
import shutil
#test: endlos schleife 
import time
import logging
from logging.handlers import RotatingFileHandler
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
LOG_FILE = DOWNLOADS_FOLDER / "FileSorterLogs" / "background.log"
LOG_FILE.parent.mkdir(exist_ok=True)

def setup_logger(log_path: Path,
                 level: int = logging.INFO,
                 max_bytes: int = 5 * 1024, #5kb TO DO: ÄNDERN AUF 5 * 1024 * 1024 (5mb) this is for test iteration
                 backup_count: int = 5,
                 also_console: bool = False) -> logging.Logger:
    
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("filesorter")
    logger.setLevel(level)
    logger.propagate = False  # verhindert Doppel-Logs über Root-Logger
    
 #Handler nicht doppelt hinzufügen
    if not logger.handlers:
        fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        file_handler = RotatingFileHandler(
            filename=str(log_path),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
        
        if also_console:
            console = logging.StreamHandler()
            console.setLevel(level)
            console.setFormatter(fmt)
            logger.addHandler(console)

    return logger

logger = setup_logger(LOG_FILE, level=logging.INFO, max_bytes=5*1024, backup_count=7)

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
        logger.warning(f"stability check failed for {file}: {e}")
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
        logger.info(f"moved: '{file.name}'->'{target_dir.name}/")
    except Exception as e:
        logger.error(f"move failed '{file}'->'{target}': {e}")

class SortHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        logger.info(f"Created event: {path.name}")
    #STOP case
        if path.name == "STOP.txt":
            logger.info("STOP.txt created (event). Main loop will stop")
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

def initial_scan():
    logger.info("Initial scan")
    try:
        entries = list(DOWNLOADS_FOLDER.iterdir())
    except Exception as e:
        logger.error(f"Initial scan failed: {e}")
        return
    for path in entries:
        if path.name == "STOP.txt": #STOP.txt ueberspringen
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() in TEMP_EXTENSIONS:
            continue
        if isStable(path):
            move_file(path)
        else:
            for _ in range(5):
                time.sleep(2)
                if isStable(path):
                    move_file(path)
                    break

    logger.info("Inital scan done")

def main():
    logger.info("FileSorter started (watchdog)")
    initial_scan()
    observer = Observer()
    handler = SortHandler()
    observer.schedule(handler, str(DOWNLOADS_FOLDER), recursive=False)
    observer.start()
    
    try: 
        while True:
            #Stop check here
            if (DOWNLOADS_FOLDER / "STOP.txt").exists():
                logger.info("STOP found, ending")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Skript ended manually (keyboard interrupt)")
    finally:
        observer.stop()
        observer.join()
        logger.info("Observer stopped. Bye.")


if __name__ == "__main__":
    main()
