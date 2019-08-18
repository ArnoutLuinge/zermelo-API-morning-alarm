# zermelo-API-morning-alarm
Morning alarm based on your first lesson, using the zermelo API.

## Description
Little python script that looks at your first lesson on your sheldule for the day to determine the time you should wake up.

### My implementation
I currently have this running on my OpenHAB (home auytomation) server as a cronjob (every morning at 06:00). It sends the "WakeHour" via MQTT to the OpenHAB system. I have OpenHAB connected trough serial to an arduino. One of the arduino's functions is to open and close the curtains and rollerblinds at the right time. I know, its a mess


Many thanks to https://github.com/coollorenzo for the great code I have taken many parts from, and the zermelo-API documentation.
