# ACM Computer Club
# This is our first successful attempt at multithreading driving and sensing functions.
# 

import RPi.GPIO as GPIO
import time
import thread
import os
from raspirobotboard import *

#Current version of working sensing script
from Sensing import *

# Creating an instance of objects RaspiRobot() and Distance()
print('Starting...')
rr = RaspiRobot()
wall = False
turn_right = False
turn_left = False
start = time.time()
stop = 0.0
dist = 0.0
ave = 0.0
# Use BCM GPIO references instead of physical pins and general GPIO pin designations
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
t1 = 14
t2 = 3
e1 = 15
e2 = 2
GPIO.setup(t1, GPIO.OUT) #Trigger 1
GPIO.setup(e1, GPIO.IN) #Echo 1
GPIO.setup(t2, GPIO.OUT) #Trigger 2
GPIO.setup(e2, GPIO.IN) #Echo 2

#look at pointer file in directory to label log then update pointer file
os.chmod("/home/pi/filenumber",0777)
filenumber = open("filenumber","r")
lognumber = filenumber.read()
timestamp = "robotlog"+lognumber+".csv"
lognumber = int(lognumber) + 1
filenumber.close()

filenumber = open("filenumber","w")
filenumber.write(str(lognumber)) 
filenumber.close()

#open up a new log file based on pointer
log = open(timestamp, "w")
log.write("time,direction,wall,side_distance\n") 
log.close()

# Set triggers to false
GPIO.output(t1, False)
GPIO.output(t2, False)

#Logging Function
def logging(timestamp,direction):
    global dist
    global ave
    log = open(timestamp, "a")
    log.write(time.strftime("%H:%M:%S,",time.localtime(),))
    log.write(direction + ",",)
    log.write(str(ave)+",",)
    log.write(str(dist),)
    log.write("\n")
    log.close()

print "Initializing..."

#Driving thread

def driving(threadName):
    global wall
    global turn_left
    global turn_right
    global dist
    global start
    global stop
    global rr
    print(threadName)
    while True:
        if wall == False:
            if turn_left == True:
                rr.left()
                print "left"
               
                logging(timestamp,'forward_left')         
            elif turn_right == True:
                rr.right()
                print "right"
                logging(timestamp,'forward_right')    
            elif turn_right == False and turn_left == False:
                rr.forward()
                print "forward"
                logging(timestamp,'forward')    
        if wall == True:
            rr.stop()
            stop = time.time()
            print "stop"
            logging(timestamp,'stop')
            print str(stop)
            print str(start)
            elapsed = stop - start
            print str(elapsed)
            time.sleep(1)
            if elapsed > 10:
                backitup()
                start = time.time()
        time.sleep(.1)     

def backitup():
    global dist
    rr.stop()
    time.sleep(2)
    if abs(dist - 150) > 30:
        #Direction to turn based on distance
        if dist > 150:
            print "reverse right"
            logging(timestamp,'reverse_right')
            rr.rev_right(1.5)
        elif dist < 150:
            print "reverse left"
            logging(timestamp,'reverse_left') 
            rr.rev_left(1.5)
    else:
        print "reverse"
        logging(timestamp,'reverse')
        rr.reverse(.75)
    rr.stop()
    time.sleep(1)

#Front mounted sensor for stopping

def sensing_forward(threadName):
    global wall
    global ave
    print(threadName)
    print "Sensing... "
    while True:
        #Start up sesnsing and stop if wall is within 5' roughly
        while wall == False:
            ave = average(t1, e1)
            if ave < 150:
                wall = True
            #print "Distance: %.1f" %ave
            time.sleep(.1)
        time.sleep(1)
        #Wait for 2 seconds then check again to see if obstruction within 5' has moved away
        while wall == True:
            ave = average(t1, e1)
            if ave > 150:
                time.sleep(2)
                wall = False
                #print 'restarting'

#Turning sensor mounted at 45 degree angle

def sensing_turn(threadName):
    global turn_right
    global turn_left
    global dist
    print(threadName)
    print "Sensing..."
    while True:
        #Start sensing to see if the car is more or less than 4' from the left wall (or obstructions)
        #10 cm of slippage included currently
        dist = measure(t2, e2)
        if abs(dist - 135) > 20:
            #Direction to turn based on distance
            if dist > 135:
                turn_left = True
                turn_right = False
                #print "left: %.1f" %ave
            elif dist < 135:
                turn_left = False
                turn_right = True
                #print "right: %.1f" %ave
        else:
            turn_left = False
            turn_right = False  
        time.sleep(.1)
           
try:
    thread.start_new_thread(driving, ('Starting driving...',) )
    thread.start_new_thread(sensing_forward, ('Starting sensing_forward...',) )
    thread.start_new_thread(sensing_turn, ('Starting sensing_turn...',) )
except KeyboardInterrupt:
    # User pressed CTRL-C
    # Reset GPIO settings
    rr.stop()
    GPIO.cleanup()
    print('Ending...')

while True:
    pass
