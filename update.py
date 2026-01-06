import os
import sys
from logging import getLogger, basicConfig, INFO

basicConfig(level=INFO)
log = getLogger(__name__)

def update_requirements():
    if os.path.exists("requirements.txt"):
        os.system("pip3 install -U -r requirements.txt")

def start_update():
    if os.path.exists(".git"):
        log.info("Checking for Updates...")
        os.system("git pull")
        update_requirements()
        log.info("Update Process Completed.")
    else:
        log.info("No .git folder found. Skipping Update.")

if __name__ == "__main__":
    start_update()
