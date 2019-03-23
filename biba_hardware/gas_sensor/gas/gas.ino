int sensorValue = 0; // переменная для хранения значения датчика
void setup()
{
Serial.begin(115200);
}
void loop()
{
sensorValue = analogRead(A1); // получить значение
Serial.print("sensor = " );
Serial.println(sensorValue); // пауза перед следующим измерением
delay(200);
}
