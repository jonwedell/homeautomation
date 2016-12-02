#!/usr/bin/env python2

import RPi.GPIO as GPIO
import time
import sys

# Set pin mode to broadcom numbering
GPIO.setmode(GPIO.BCM)

# Define which pins we will be reading from and set them up
pir_living = 23
pir_kitchen = 24

# If ran directly print both states
if len(sys.argv) == 1:
    try:
        GPIO.setup(pir_living, GPIO.IN)
        GPIO.setup(pir_kitchen, GPIO.IN)
        while True:
            print "Living: %s Kitchen %s" % (GPIO.input(pir_living), GPIO.input(pir_kitchen))
            time.sleep(.5)
    finally:
        GPIO.cleanup()
    
elif sys.argv[1] == "kitchen":
    GPIO.setup(pir_kitchen, GPIO.IN)
    print GPIO.input(pir_kitchen)
    
elif sys.argv[1] == "living":
    GPIO.setup(pir_living, GPIO.IN)
    print GPIO.input(pir_living)
    
GPIO.cleanup()

