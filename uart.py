import serial.tools.list_ports
from log import * 
from writecsv import writecsv
import time

MCUver = ''
MCUfirmwareVer = ''
curTime = time.process_time()

numOfConnectionTry = 0
INIT = 0
MCU_CONNECTED = 1
MCU_DISCONNECTED = 2
MCU_MAX_CONNECT_ATTEMP = 3
prevTemp = 0
prevHumid = 0
currentTemp = 0
currentHumid = 0
isCollectedData = 0

HOPELESS=99

errorList = ['SENSOR ISSUE']

def checkIntegrity(string):
    receivedList = string.split(":")

    if(len(receivedList) < 6):
        return 1
    receivedSum = int(receivedList[len(receivedList)-1])
    calcSum = 0
    numofDelimiter = 0

    for i in range(len(string)):
        if string[i] == ':':
            numofDelimiter+=1
        if numofDelimiter == 5:
            break
        calcSum += ord(string[i])

    if calcSum != receivedSum:
        return 0
    else:
        return 1
            
def connectAttemp(state, client):
    global curTime, numOfConnectionTry

    if state == MCU_DISCONNECTED:
        print("MCU DISCONNECTED")

    while numOfConnectionTry < MCU_MAX_CONNECT_ATTEMP and state != MCU_CONNECTED:
        if time.process_time()-curTime > 3: 
            print('MCU Connect Attempt Number: ' + str(numOfConnectionTry))
            state = connectSerial()
            if state == INIT or state == MCU_DISCONNECTED:
                numOfConnectionTry = numOfConnectionTry+1
            else: 
                numOfConnectionTry = 0
                writeData('!VER#')
                readSerial(client)
                return MCU_CONNECTED
            curTime = time.process_time()

    if numOfConnectionTry == MCU_MAX_CONNECT_ATTEMP:
        print("CAN NOT CONNECT TO MCU!")
        return HOPELESS
          
def getIsCollectedData():
    return isCollectedData

def getPort():
    # ports = serial.tools.list_ports.comports()
    # N = len(ports)
    # commPort = "None"
    # for i in range(0, N):
        # port = ports[i]
        # strPort = str(port)
        # if "ttyACM" in strPort:
        #     splitPort = strPort.split(" ")
            # commPort = (splitPort[0])
        # print("/dev/ttyACM0")
    return "/dev/ttyACM0" 

def connectSerial():
    global state, ser
    ttyPort = getPort()
    if ttyPort != "None":
        try:
            ser = serial.Serial(port=ttyPort, baudrate=9600)
        except:
            return MCU_DISCONNECTED
        writelog("MCU CONNECTED!")
        print(ser)
        return MCU_CONNECTED
    else:
        writelog("CONNECTION ISSUE!")
        return MCU_DISCONNECTED
        
mess = ""

def readSerial(client):
    try:
        bytesToRead = ser.inWaiting()
    except:
        return MCU_DISCONNECTED

    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(client, mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]

    return MCU_CONNECTED
                
def processData(client, data):
    global prevTemp, prevHumid, isCollectedData, currentTemp, currentHumid
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)

    if len(splitData) < 2:
        return

    if not checkIntegrity(data):
        print("Checksum Mismatch!")
        return

    if splitData[0] == 'OK':
        writecsv(currentTemp, currentHumid)
        writelog("TEMP: " + str(currentTemp) + " HUMID: " + str(currentHumid))
        client.publish("banhbaochien/feeds/feed-humidity",splitData[2])
        client.publish("banhbaochien/feeds/feed-temp", splitData[1])
        client.publish("banhbaochien/feeds/feed-light",splitData[3])
        client.publish("banhbaochien/feeds/feed-rain",splitData[4])
        writeData("!OK#")
    elif splitData[0] == 'ERR':
        writelog("SENSOR ISSUE!")
    elif splitData[0] == 'VER':
        MCUver = splitData[1]
        MCUfirmwareVer = splitData[2]
        writelog('MCU Version: ' + MCUver + ' MCU Firmware Version: ' + MCUfirmwareVer)

def writeData(data):
    ser.write(str(data).encode())
