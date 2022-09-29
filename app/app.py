import json
import os
from apscheduler.schedulers.background import BackgroundScheduler

from _loghandler import logger
from _main import mainLoop

from datetime import datetime
import time

now = datetime.now()
dtNow = now.strftime("%d-%b-%Y")

kick_off_at = '06:00:00'
full_re_roll = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def hbLogic():
    today = datetime.now().strftime("%d-%b-%Y")
    timestampTrigger = today + ", " + kick_off_at
    dailyTriggerTime = datetime.strptime(timestampTrigger, "%d-%b-%Y, %H:%M:%S")
    proceedOverride = False
    proceed = False
    data = {}
    if not os.path.exists('heartbeat.json'):  # New Container
        logger('I', "No heartbeat file.  Will run capacity check")
        proceedOverride = True

    if (datetime.now() - dailyTriggerTime).total_seconds() > 0:
        if datetime.now().strftime("%a") in full_re_roll:
            # Check to see if already run today
            proceed = True
            if os.path.exists('heartbeat.json'):
                f = open('heartbeat.json')
                data = json.load(f)
                if data['lastDate'] == today:
                    proceed = False

    if proceed or proceedOverride:
        logger('I', "Running Capacity Coefficient Check")
        mainLoop()
        logger('I', kick_off_at + " checks Done")

        data['lastDate'] = today
        with open('heartbeat.json', 'w') as f:
            json.dump(data, f)


if os.path.exists('heartbeat.json'):
    os.remove('heartbeat.json')

logger('I', "Application is now awake.")
hbLogic()
heartBeat = BackgroundScheduler(daemon=True)
heartBeat.add_job(hbLogic, 'interval', minutes=5)
heartBeat.start()

while True:
    time.sleep(60)

