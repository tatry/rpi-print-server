#!/usr/bin/python3

# sudo pip3 install --system pycups-notify

import cups
from cups_notify import Subscriber, event
from gi.repository import GLib
import RPi.GPIO as GPIO
import signal
import threading

#
# Config options
#

# Time between last finished job and power off
turn_off_delay = 12*60 # in seconds

# GPIO 0-8 defaults to HIGH; 9-27 defaults to LOW (desidered); 14,15 defaults to UART
# unused GPIOs by pi-parport: 5,7,12,14,15,16,27 => usable: 12,16,27
bcm_gpio_pin_id = 27

#
# End of config options
#

cups_connection = cups.Connection()
cups_subscriber = Subscriber(cups_connection)
loop = GLib.MainLoop()
timer = None

def printer_power_off():
    global bcm_gpio_pin_id
    GPIO.output(bcm_gpio_pin_id, GPIO.LOW)

def printer_power_on():
    global bcm_gpio_pin_id
    GPIO.output(bcm_gpio_pin_id, GPIO.HIGH)

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
    if evt.description == "Job created.":
        timer_stop()
        printer_power_on()
    elif title_split[-1] == "idle" and " ".join(description_split[-4:]) == "state changed to idle.":
        timer_stop()
        timer_start()

def signal_handler(signum, frame):
    global loop
    loop.quit()

GPIO.setmode(GPIO.BCM)
# Do not show warnings when cleanup method was not called - we want to preserve printer power off
GPIO.setwarnings(False)
GPIO.setup(bcm_gpio_pin_id, GPIO.OUT, initial=GPIO.LOW)

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
    # do not call GPIO.cleanup() because we want to preserve printer power state

