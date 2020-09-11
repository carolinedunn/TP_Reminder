#! /usr/bin/python

# Imports
import RPi.GPIO as GPIO
import time
import requests
from datetime import datetime

emptyDist = 17 # Distance to trigger TP holder empty email
intervalTime = 1800 # Check TP level every 30 minutes 
#intervalTime = 5 # test every 5 seconds
endHour = 22 #don't send emails after 10 pm
startHour = 8 #don't send emails before 8 am

#function for setting up emails
def send_simple_message(TPempty, n):
    return requests.post(
        "https://api.mailgun.net/v3/YOUR_DOMAIN_NAME/messages",
        auth=("api", "YOUR_API_KEY"),
        data={"from": 'hello@example.com',
            "to": ["YOUR_MAILGUN_EMAIL_ADDRESS"],
            "subject": "Time to refill your toilet paper",
            "html": "<html>Your toilet paper holder is empty in your master bathroom as of " + TPempty + ".<br>Reminder: "+ n +"<br>Please refill your toilet paper holder or purchase more toilet paper at <a href='https://amzn.to/3k4RIob'>Amazon</a></html>"})

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24

#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = ((TimeElapsed * 34300) / 2) * 0.393701 # distance in inches

    return distance

#Iniialize Variables
TPempty = "full"
n = 0
currenttime = datetime.now()
hour = currenttime.hour

try:

    while True:
        olddist = distance() # Measure TP distance 
        print ("Measured Distance = %.1f in" % olddist) #print distance
        time.sleep(intervalTime) # Wait 30 minutes
        newdist = distance() # Measure TP distance Again
        print ("Measured Distance = %.1f in" % newdist) #print new distance
        currenttime = datetime.now() #get updated time
        hour = currenttime.hour #get current hour

        if hour > endHour or hour < startHour: #Check for Do Not Disturb hours.
            end = str(endHour) #Format endHour as a string for printing
            start = str(startHour) #Format startHour as a string for printing
            print ("Don't send emails after "+ end +":00 or before "+start+":00.") #If within Do Not Disturb hours, then do nothing.
        elif olddist > emptyDist and newdist > emptyDist and n == 0: # Check if both distances measured show TP holder as empty for the first time.
            print("Time to change the toilet paper. Round 1")
            n=1 #reminder counter  #This is the 1st time TP empty observed
            dateraw= datetime.now() #get date/time when we fist noticed TP was empty
            TPempty = dateraw.strftime("%-m/%-d at %-I:%M %p") # format and save the date/time when we first noticed the TP was empty
            print("Toilet paper empty as of " + TPempty)
            r = str(n)     #make n a string for printing purposes       
            request = send_simple_message(TPempty, r). #Send an email to let the user know TP Holder is Empty
            print ('Status Code: '+format(request.status_code)). #200 status code means email sent successfully
        elif olddist > emptyDist and newdist > emptyDist and n > 0:
            n +=1       #increment reminder counter
            print("Toilet paper empty as of " + TPempty) #print the original date/time when TP was first empty
            r = str(n) #make n a string for printing purposes
            print("round: " + r) #number of reminders sent
            request = send_simple_message(TPempty, r) #send an email with the original TP date/time empty and number of reminders
            print ('Status Code: '+format(request.status_code)) #200 status code means email sent successfully
        else:
            print("Toilet paper level ok.") #At least 1 distance measured olddist or newdist or both distances measured show that TP holder is not empty.
            n = 0 #reset counter to zero 
        time.sleep(intervalTime) # Wait 30 minutes before measuring again

except KeyboardInterrupt:
    print ("Quit")
    GPIO.cleanup()
        

