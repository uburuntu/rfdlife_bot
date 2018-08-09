import logging
import subprocess
import sys
import time
from datetime import datetime

logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('spam.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)


def log(text):
    curr_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    print('{}\n{}\n'.format(curr_time, text))


def check_before_run():
    # Check version
    if sys.version_info < (3, 6):
        log('[Error] Your Python version: {}, need 3.6 or later'.format(sys.version_info))
        quit(1)

    # Check and install modules
    ret = subprocess.call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt', '--quiet'])
    if ret != 0:
        quit(2)


def run_bot_loop():
    while True:
        try:
            subprocess.call([sys.executable, 'main.py'])
        except KeyboardInterrupt:
            log('Interrupt bot: restarting in 3 sec')
            time.sleep(3)


if __name__ == '__main__':
    check_before_run()

    try:
        run_bot_loop()
    except KeyboardInterrupt:
        log('Interrupt run script: bot stopped')
        quit(0)
