#include<ESP8266WiFi.h>
#include <WiFiClient.h> 
#include <ESP8266WebServer.h>
#include <ESP8266HTTPClient.h>
#include <Adafruit_Sensor.h>
#include "DHT.h"

#define TEMPER_PIN 2

const char* ssid     = "EBANIY_ROT_ETOGO_KAZINO";
const char* password = "San987873";

//Web/Server address to read/write from 
const char *host = "192.168.42.36:8086";   // website or IP address of server ??????????????

DHT dht(TEMPER_PIN,DHT22);

void WiFiInit()
{
 WiFi.mode(WIFI_STA); // Задаем режим работы: клиент
 WiFi.begin(ssid, password);
 byte Connect = 15; //попытки подключения к WiFi
 while (--Connect && WiFi.status() != WL_CONNECTED) // Ждем пока статус не станет WL_CONNECTED
 {
  Serial.print(".");
  delay(500);
 }
 if (WiFi.status() == WL_CONNECTED)// если подключился к основному вифи, то норм, в противном случае делаем точкой доступа есп 
 {
   Serial.println("");
   Serial.println("WiFi connected");
   Serial.print("IP address: ");
   Serial.println(WiFi.localIP()); // показывает наше IP
 }
}

void setup() {
    Serial.begin(115200); 
    dht.begin();

    Serial.println("Connecting to WiFi");
    WiFiInit();
}


int noise[] = {0,0,0,0,0};
int resNoise = 0;
int i = 0;
String DataArray[3] = {};
String id = "-1";
String x= "59.995913";
String y= "30.288869";

void loop() {

  float hum = dht.readHumidity();
  float tem = dht.readTemperature();

  HTTPClient http;    //Declare object of class HTTPClient

  String DataString, getData, Link;

  if (i < 5){
    noise[i] = analogRead(A0);// for micro
    resNoise = noise[i];
    i++;
  }
  else {
    for (int j=0; j<5; j++) {
      resNoise = resNoise + noise[j];
    }
     resNoise = resNoise / 5;
    for (int k=0; k<4; k++) {
     noise[k] = noise[k+1];
    }
     noise[4] = analogRead(A0);
  }
  
  if (isnan(hum)|| isnan(tem)){
    Serial.println("Failed read");
  }
  else {
    /*Serial.print("Humidity: ");//for temperature
    Serial.print(hum);
    Serial.print(" %\t");
    Serial.print("Temperature: ");
    Serial.print(tem);
    Serial.print(" *C\t");
    Serial.print("Noise: ");
    Serial.print(resNoise);
    Serial.print(" n.p.");
    Serial.println("");*/
  }


  DataArray[0] = String(resNoise); 
  DataArray[1] = String(tem); //Temperature sensor
  DataArray[2] = String(hum); //Humidity sensor

// String DataSend = "{" + "t:" + DataArray[1] + "," + "h:" + DataArray[2] + "," + "id:" + id + "," + "y:" + y + "," + "x:" + x + "}" ;
String DataSend =   "{\"t\":" + DataArray[1] + "," + "\"h\":" + DataArray[2] + "," + "\"id\":" + id + "," + "\"y\":" + y + "," + "\"x\":" + x+"}" ;

 
Serial.println(DataSend);

 DataString = String(DataSend); //String to interger conversion
  
  //GET Data
  getData = "data/" + DataString ;  //Note "?" added at front
  Link = "http://192.168.42.36:8086/" + getData; //?????????????????????

  http.begin(Link);     //Specify request destination

  int httpCode = http.GET();            //Send the request
  String payload = http.getString();    //Get the response payload
 
  Serial.println(httpCode);   //Print HTTP return code
  Serial.println(payload);    //Print request response payload
 
  http.end();  //Close connection
  
  delay(1000);
}
