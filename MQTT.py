#from Adafruit_IO import MQTTClient
import paho.mqtt.client as mqtt
import sys
from uart import *
from envParse import *

AIO_FEED_ID = ["feed-green", "feed-red", "feed-pump", "freq"]
AIO_USERNAME = getUsername()
AIO_KEY = getKey()

#CONSTANT
isConnectedSuccessfully = 0
sendPeriod = 10

for i in range(len(AIO_FEED_ID)):
    AIO_FEED_ID[i] = AIO_USERNAME + "/feeds/" + AIO_FEED_ID[i]

print(AIO_FEED_ID)

def isConnected():
    return isConnectedSuccessfully

def getSendPeriod():
    return sendPeriod

def connected(client, userdata, flags, rc):
    global isConnectedSuccessfully
    for topic in AIO_FEED_ID:
        client.subscribe(topic)
    print(flags)
    print(rc)
    print("Ket noi thanh cong ...")
    isConnectedSuccessfully = 1
    client.publish("banhbaochien/feeds/freq", str(sendPeriod))

def subscribe(client , userdata , mid , granted_qos):
    print("Subscribe thanh cong ...")

def disconnected(client, userdata, rc):
    print("Ngat ket noi ...")
    sys.exit (1)

def message(client , userdata, message):
    global sendPeriod
    decodedPayload = message.payload.decode()
    print("Nhan du lieu: " + decodedPayload + " type" + str(type(decodedPayload)))

    if "feed-green" in  message.topic:
        if  decodedPayload == '0':
            print("Tat led 1")
            writeData("!OFF1#")
        else: 
            print("Bat led 1")
            writeData("!ON1#")
    if "feed-red" in message.topic:
        if  decodedPayload == '0':
            print("Tat led 2")
            writeData("!OFF2#")
        else: 
            print("Bat led 2")
            writeData("!ON2#")
    if "feed-pump" in message.topic:
        if decodedPayload == '0':
            print("Tat may bom")
            writeData("!OFF3#")
        else:
            print("Bat may bom")
            writeData("!ON3#")

    if "freq" in message.topic:
        sendPeriod = int(decodedPayload)
        print("New send period: " + decodedPayload)

client = mqtt.Client()
client.username_pw_set(username=AIO_USERNAME, password=AIO_KEY)
client.will_set("banhbaochien/feeds/connectcheck", payload=0, qos=0, retain=True)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe

try:
    client.connect("io.adafruit.com", 1883, 10)
except:
    writelog("NO INTERNET CONNECTION")
    exit(1)

client.loop_start()
