#include<ESP8266WiFi.h>
#include <WiFiClient.h> 
#include <ESP8266WebServer.h>
#include <ESP8266HTTPClient.h>
#include <Adafruit_Sensor.h>
#include "DHT.h"

#define TEMPER_PIN 2

const char* ssid     = "WiFI";//?????????????????
const char* password = "password";//??????????????????

//Web/Server address to read/write from 
const char *host = "XXX.XXX.X.XX";   // website or IP address of server ??????????????

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
int DataArray[] = {0,0,0};

void loop() {

  float hum = dht.readHumidity();
  float tem = dht.readTemperature();

  HTTPClient http;    //Declare object of class HTTPClient

  String NoiseData, station, getData, Link;

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
// First of all check one value (resNoise) !!!!!!!!!!!!
  DataArray[0] = hum; //Humidity sensor
  DataArray[1] = tem; //Temperature sensor
  DataArray[2] = resNoise;
  
  NoiseData = String(resNoise); //String to interger conversion
  station = "B";
  
  //GET Data
  getData = "?status=" + NoiseData + "&station=" + station ;  //Note "?" added at front
  Link = "http://XXX.XXX.X.XX/ecobomb/getSmallData.php" + getData; //?????????????????????

  http.begin(Link);     //Specify request destination

  int httpCode = http.GET();            //Send the request
  String payload = http.getString();    //Get the response payload
 
  Serial.println(httpCode);   //Print HTTP return code
  Serial.println(payload);    //Print request response payload
 
  http.end();  //Close connection
  
  delay(1000);
}
