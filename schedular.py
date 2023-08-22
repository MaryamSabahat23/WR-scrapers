import schedule
import time
import subprocess

def run_script(script_path):
    print(f"Running script: {script_path}")
    subprocess.run(["python", script_path])
    print(f"Script {script_path} executed.")

#  Schedule the scripts to run every 1 **minute"
schedule.every(7).days.do(run_script, script_path="Glassdoor.py")
schedule.every(7).days.do(run_script, script_path="seek.py")
schedule.every(7).days.do(run_script, script_path="indeed.py")
while True:
    schedule.run_pending()
    time.sleep(1)