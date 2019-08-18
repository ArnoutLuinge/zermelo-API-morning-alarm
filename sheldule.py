import requests
import json
import os

save=False
if save and os.path.exists("token.json"):
    with open('token.json') as token_file:
        token_data = json.load(token_file)
        school = token_data['school']
        endpoint = "https://" + school + ".zportal.nl/api/v3/"

"""else:
    if school == "":
        raise TypeError("__init__() missing 1 required positional argument: \'school\'")
    if school == "":
        raise TypeError("__init__() missing 1 required positional argument: \'koppelcode\'")
"""

if not os.path.exists("token.json"):
    save = True
    user = input("Enter your username: ")
    school = input("Enter your school: ")
    koppelcode = input("Enter your koppelcode: ")
    koppelcode = koppelcode.replace(" ", "")
    endpoint = "https://" + school + ".zportal.nl/api/v3/"

    token_response = requests.Session().post(url=endpoint + 'oauth/token', data={
        "grant_type": "authorization_code",
        "code": koppelcode
    })
    if token_response.status_code == 200:
        token_data = json.loads(token_response.text)
    elif token_response.status_code == 400:
        raise Exception("error 400: koppelcode is ongeldig")
    else:
        raise Exception("error " + str(token_response.status_code))


if save and not os.path.exists("token.json"):
    token_data['school'] = school
    token_data['user'] = user
    with open('token.json', 'w') as token_file:
        json.dump(token_data, token_file)
    access_token = token_data['access_token']

with open('token.json') as token_file:
    token_data = json.load(token_file)
    access_token = token_data['access_token']
    school = token_data['school']
    user = token_data['user']
    print("Logged in as user: " + str(user))
    endpoint = "https://" + school + ".zportal.nl/api/v3/"

# Retrieve the portal status message
status = requests.get(endpoint + "status/status_message").text
print("Portal status: " + status)

import time
import datetime
from datetime import date

today = date.today()
tomorrow = today + datetime.timedelta(days=1)
# dd/mm/YY
fromDate = today.strftime("%d/%m/%Y")
toDate = tomorrow.strftime("%d/%m/%Y")
print(fromDate)
print(toDate)

datum_start = fromDate
datum_stop = toDate
timestamp_start = time.mktime(datetime.datetime.strptime(datum_start, "%d/%m/%Y").timetuple())
timestamp_end = time.mktime(datetime.datetime.strptime(datum_stop, "%d/%m/%Y").timetuple())

json_response = requests.get(endpoint + "appointments?user=" + user + "&access_token=" + access_token + "&start=" + str(
    int(timestamp_start)) + "&end=" + str(int(timestamp_end)) + "&valid=true").json()
print(json_response)
appointments = json_response['response']['data']


# we need to sort them
def start_field(appointment):
    return int(appointment['start'])

appointments.sort(key=start_field)

# now print them
def time_string(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')


for appointment in appointments:
    print(time_string(appointment['start']) + " Cancelled:" + str(appointment['cancelled']) + " " + str(appointment['startTimeSlot']) + " " + ",".join(
        appointment['teachers']) + " " + ','.join(appointment['subjects']) + " " + ','.join(appointment['locations']))

print(appointments)
if appointments == []:
    print("No appointments found for this day, seems like you'r free!")
    print("Setting WakeHour for lazy boy's, 8:30")
    OHwakeHour = 8

else:
    # looking for the first appointment and storing its time.
    for appointment in appointments:
        if appointment['cancelled'] == 0:
            firstAppointmentTime = appointment['start']
            wakeTime = firstAppointmentTime - 3600
            wakeHour = int(datetime.datetime.fromtimestamp(wakeTime).strftime('%H'))
            wakeMinute = int(datetime.datetime.fromtimestamp(wakeTime).strftime('%M'))

            print("First lesson at:", time_string(firstAppointmentTime))
            print("Waking up at:", time_string(wakeTime))
            print("wakeHour:", wakeHour)
            print("wakeMinute:", wakeMinute)
            break

    if wakeHour <= 7 or wakeHour == 8 and wakeMinute < 30 :
        OHwakeHour = 7
    elif wakeHour == 8 and wakeMinute >= 30 or wakeHour == 9 and wakeMinute < 30:
        OHwakeHour = 8
    elif wakeHour == 9 and wakeMinute >= 30 or wakeHour == 10:
        OHwakeHour = 9

print("OpenHAB WakeHour:", OHwakeHour)

# sending the wakehour to OpenHAB via MQTT
import paho.mqtt.client as paho
broker="192.168.1.***"		# MQTT broker's ip-addess
port=1883
def on_publish(client,userdata,result):             #create function for callback
    print("data published \n")
    pass
client1= paho.Client("zermeloWakehour")                           #create client object
client1.on_publish = on_publish                          #assign function to callback
client1.username_pw_set(username="<username>",password="<password>")   #hardcoded MQTT credentials <3
client1.connect(broker,port)                                 #establish connection
ret= client1.publish("wakehour/state", (OHwakeHour))                   #publish