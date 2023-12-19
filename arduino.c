#include <BH1750_WE.h>
#include <DFRobot_DHT20.h>
#include <stdio.h>
#include <string.h>

#define LED_RED_PIN 9
#define LED_GREEN_PIN 7
#define PUMP_PIN 5
#define RAINDROP_SENSOR_ANALOG_PIN 3
#define RAINDROP_SENSOR_DIGITAL_PIN 2

#define INIT 1 
#define WAIT 2 
#define SEND 3

double temp = 0;
double humid = 0;
DFRobot_DHT20 dht20;
BH1750_WE GY30; 
uint8_t isRain;
int state = INIT;
uint32_t checksum;
int len;
String outString;
String inString;
float lux; 

uint32_t checksumCalc(String str){
  uint32_t res=0;
  for(int i=0; i<str.length();i++){
    res += (int)str[i];
  }
  return res;
}

void setup() {
  // put your setup code here, to run once:
  pinMode(LED_RED_PIN,OUTPUT);
  pinMode(LED_GREEN_PIN,OUTPUT);
  pinMode(PUMP_PIN,OUTPUT);
  pinMode(RAINDROP_SENSOR_DIGITAL_PIN,INPUT);
  GY30.powerOn();
  GY30.init();
  Serial.begin(9600);
  //Initialize sensor
  while(dht20.begin()){
    delay(1000);
  }
}

void loop() {
  if(Serial.available()){
    inString = Serial.readString();
    if(inString == "!RST#"){
      state = SEND;
    } else if(inString == "!OK#"){
      state = WAIT;
    } else if(inString == "!ON1#"){
      digitalWrite(LED_RED_PIN, HIGH);
    } else if(inString == "!ON2#"){
      digitalWrite(LED_GREEN_PIN, HIGH);
    } else if(inString == "!ON3#"){
      digitalWrite(PUMP_PIN, HIGH);
    } else if(inString == "!OFF1#"){
      digitalWrite(LED_RED_PIN, LOW);
    } else if(inString == "!OFF2#"){
      digitalWrite(LED_GREEN_PIN, LOW);
    } else if(inString == "!OFF3#"){
      digitalWrite(PUMP_PIN, LOW);
    }
  }

  if(state == SEND){
    //Get Data
    humid = dht20.getHumidity();
    temp = dht20.getTemperature();
    lux = GY30.getLux();
    isRain = digitalRead(RAINDROP_SENSOR_DIGITAL_PIN);
    //Concatenate String
    outString = "OK:" + String(temp) + ":" + String(humid*100) + ":" + String(lux) + ":" + String(isRain);
    //Get checksum
    outString = "!" + outString + ":" + String(checksumCalc(outString)) + "#\n";
    Serial.println(outString);
  }
  delay(100);
}
