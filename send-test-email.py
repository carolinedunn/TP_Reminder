#! /usr/bin/python

# Imports
import requests

def send_simple_message():
    print("I am sending an email.")
    return requests.post(
        "https://api.mailgun.net/v3/YOUR_DOMAIN_NAME/messages",
        auth=("api", "YOUR_API_KEY"),
        data={"from": 'hello@example.com',
            "to": ["YOUR_MAILGUN_EMAIL_ADDRESS"],
            "subject": "Tom's Hardware TP Project",
            "text": "Congratulations! You have completed the email send step."})
            
request = send_simple_message()
print ('Status: '+format(request.status_code))
print ('Body:'+ format(request.text))