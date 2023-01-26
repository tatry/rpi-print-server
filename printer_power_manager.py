#!/usr/bin/python3

# sudo pip3 install --system pycups-notify
# sudo pip3 install --system tinytuya

import cups
from cups_notify import Subscriber, event
from gi.repository import GLib
import signal
import threading
import tinytuya as tuya

#
# Config options
#
turn_off_delay = 12*60 # in seconds
tuya_dev_id = "xxxxxxxxxxxxxxxxxxxxxx"
tuya_dev_key = "xxxxxxxxxxxxxxxx"
tuya_dev_addr = "192.168.x.x"
#
# End of config options
#

cups_connection = cups.Connection()
cups_subscriber = Subscriber(cups_connection)
loop = GLib.MainLoop()
timer = None
tuya_dev = tuya.OutletDevice(
    dev_id=tuya_dev_id,
    address=tuya_dev_addr,
    local_key=tuya_dev_key,
    version=3.3)

def printer_power_off():
    global tuya_dev
    tuya_dev.turn_off()

def printer_power_on():
    global tuya_dev
    tuya_dev.turn_on()

def timer_stop():
    global timer
    if timer is not None:
        timer.cancel()

def timer_start():
    global timer
    timer_stop() # if already running
    timer = threading.Timer(turn_off_delay, printer_power_off)
    timer.start()

def cups_handler(evt):
    title_split = evt.title.split()
    description_split = evt.description.split()
    if title_split[-1] == "pending" and evt.description == "Job created.":
        timer_stop()
        printer_power_on()
    elif title_split[-1] == "idle" and " ".join(description_split[-4:]) == "state changed to idle.":
        timer_stop()
        timer_start()

def signal_handler(signum, frame):
    global loop
    loop.quit()

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

cups_subscriber.subscribe(cups_handler, [event.CUPS_EVT_JOB_CREATED, event.CUPS_EVT_PRINTER_STATE_CHANGED])

printer_power_off()

try:
    loop.run()
except KeyboardInterrupt:
    pass
finally:
    cups_subscriber.unsubscribe_all()
    printer_power_off()
