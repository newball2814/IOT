#!/usr/bin/env python3

from uart import *
from MQTT import *

# from predictAI import *
# import threading
import sys
import time

sendPeriod = 10
INIT = 0
MCU_CONNECTED = 1
MCU_DISCONNECTED = 2
state = INIT
HOPELESS=99
curTime = time.process_time()
aiTime = time.process_time()
WAIT = 5      
predictTime = time.process_time()
time.sleep(WAIT)

# Make prediction run seperately cuz Adafruit throtlle :v
# predictAIevent = threading.Event()
# predictAIThread = threading.Thread(target=lambda:predictionMainloop(predictAIevent))
# predictAIThread.start()
        
while True:  
    if state == INIT or state == MCU_DISCONNECTED:
        state = connectAttemp(state, client)

    if state == MCU_CONNECTED:
        if time.process_time() - curTime >= sendPeriod :
            writeData('!RST#')
            curTime = time.process_time()

    if state == HOPELESS:
        sys.exit(1)

    sendPeriod = getSendPeriod()
    state=readSerial(client)
    pass
