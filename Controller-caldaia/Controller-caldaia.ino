/* Arduino DS18B20 temp sensor tutorial
   More info: http://www.ardumotive.com/how-to-use-the-ds18b20-temperature-sensor-en.html
   Date: 19/6/2015 // www.ardumotive.com */


//Include libraries
#include <OneWire.h>
#include <DallasTemperature.h>

// Data wire is plugged into pin 2 on the Arduino
#define ONE_WIRE_BUS 2
// Setup a oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);
// Pass our oneWire reference to Dallas Temperature. 
DallasTemperature sensors(&oneWire);

float t1 = 0, t2 = 0; //temperature dei sensori
int interval = 1000;  //tempo di intervallo invio dati

void setup(void)
{
  Serial.begin(9600); //Begin serial communication
  Serial.println("handshake");
  sensors.begin();
}

void loop(void)
{ 
  // Send the command to get temperatures
  sensors.requestTemperatures();
  // Why "byIndex"? You can have more than one IC on the same bus. 0 refers to the first IC on the wire
  t1 = sensors.getTempCByIndex(0);
  t2 = sensors.getTempCByIndex(1);
  Serial.print("Temp1:");
  Serial.print(t1);
  Serial.print(" ");
  Serial.print("Temp2:");
  Serial.print(t2);
  delay(interval);
}
