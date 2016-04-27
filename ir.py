#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import sys

# Set pin mode to broadcom numbering
GPIO.setmode(GPIO.BCM)

# Define which pins we will be reading from and set them up
pir_living = 14
pir_kitchen = 15


# If ran directly print both states
if len(sys.argv) == 1:
    GPIO.setup(pir_living, GPIO.IN)
    GPIO.setup(pir_kitchen, GPIO.IN)
    print "Living: %d Kitchen %d" % (GPIO.input(pir_living), GPIO.input(pir_kitchen))
    
elif sys.argv[1] == "kitchen":
    GPIO.setup(pir_kitchen, GPIO.IN)
    print GPIO.input(pir_kitchen)
    
elif sys.argv[1] == "living":
    GPIO.setup(pir_living, GPIO.IN)
    print GPIO.input(pir_living)
    
GPIO.cleanup()

