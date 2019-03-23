#include<ESP8266WiFi.h>
#include <WiFiClient.h> 
#include <ESP8266WebServer.h>
#include <ESP8266HTTPClient.h>
#include <Adafruit_Sensor.h>
#include "DHT.h"

#define TEMPER_PIN 2

const char* ssid     = "Connectify-1";
const char* password = "12345678";

//Web/Server address to read/write from 
const char *host = "192.168.184.1:8056";   // website or IP address of server ??????????????

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
    pinMode(D2,INPUT);
    pinMode(D3,INPUT);

    Serial.println("Connecting to WiFi");
    WiFiInit();
}


int noise[] = {0,0,0,0,0};
int resNoise = 0;
int i = 0;
int GasSensor = 0;
int GasSensor2 = 0;
String DataArray[5] = {};
String id = "-1";
String x= "59.995913";
String y= "30.288869";

void loop() {

  float hum = dht.readHumidity();
  float tem = dht.readTemperature();

  GasSensor = digitalRead(D3); // получить значение
  if (GasSensor == 1 ){
    GasSensor = 0;
  }
  else{
    GasSensor = 1;
  }
  GasSensor2 = digitalRead(D2); // получить значение
    if (GasSensor2 == 1 ){
    GasSensor2 = 0;
  }
  else{
    GasSensor2 = 1;
  }

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
    Serial.print("Humidity: ");//for temperature
    Serial.print(hum);
    Serial.print(" %\t");
    Serial.print("Temperature: ");
    Serial.print(tem);
    Serial.print(" *C\t");
    Serial.print("Noise: ");
    Serial.print(resNoise);
    Serial.print(" n.p.\t");
    Serial.print("Gas = " );
    Serial.print(GasSensor);
    Serial.print(" g.p.\t");
    Serial.print("Gas2 = " );
    Serial.print(GasSensor2);
    Serial.print(" g.p.");
    Serial.println("");
  }


  DataArray[0] = String(resNoise); 
  DataArray[1] = String(tem); //Temperature sensor
  DataArray[2] = String(hum); //Humidity sensor
  DataArray[3] = String(GasSensor); 
  DataArray[4] = String(GasSensor2); 
  

String DataSend =   "{\"t\":" + DataArray[1] + "," + "\"h\":" + DataArray[2] + "," + "\"g1\":" + DataArray[3] + "," + "\"g2\":" + DataArray[4] + "," + "\"n\":" + DataArray[0] + "," + "\"id\":" + id + "," + "\"x\":" + y + "," + "\"y\":" + x+"}" ;

 
Serial.println(DataSend);

 DataString = String(DataSend); //String to interger conversion
  
  //GET Data
  getData = "data/" + DataString ;  
  Link = "http://192.168.184.1:8056/" + getData; 

  http.begin(Link);     //Specify request destination

  int httpCode = http.GET();            //Send the request
  String payload = http.getString();    //Get the response payload
 
  Serial.println(httpCode);   //Print HTTP return code
  Serial.println(payload);    //Print request response payload
 
  http.end();  //Close connection
  
  delay(500);
}
