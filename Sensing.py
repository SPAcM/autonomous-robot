
# ACM Computer Club
# This is our one hundredth...?  attempt at multithreading driving and sensing functions.
# Original concept thanks to Matt Hawkins at www.raspberrypi-spy.co.uk

import RPi.GPIO as GPIO
import time
import thread

def measure(t, e):
    stop = 0.0
    # Measurements
    GPIO.output(t, True)
    time.sleep(0.00001)
    GPIO.output(t, False)
    start = time.time()
    while GPIO.input(e)==0:
        start = time.time()
    while GPIO.input(e)==1:
        stop = time.time()
    elapsed = stop - start
    distance = (elapsed * 34300)/2
    return distance

def average(t, e):
    # Average
    dist = 0
    for i in range(5):
        distance = measure(t, e)
        dist += distance
        time.sleep(0.05)     
    distance = dist / 5                
    return distance
