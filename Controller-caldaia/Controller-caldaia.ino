/** 
 *  Arduino DS18B20 temp sensor tutorial http://www.ardumotive.com/how-to-use-the-ds18b20-temperature-sensor-en.html
 */
#include <OneWire.h>
#include <DallasTemperature.h>

/****************************** dati del controller ***************************/

#define ONE_WIRE_BUS 2                // il pin 2 viene usato per il bus Onewire
OneWire oneWire(ONE_WIRE_BUS);        // Inizializzo istanza Onewire per comunicare con i dispositivi
DallasTemperature sensors(&oneWire);  // passo oneWire a Dallas Temperature

enum Termometri {CALDAIA, BOILER, ESTERNO};   // enum con i nomi dei sensori di temperatura

float tmax = 80.0f, tmin = 20.0f, t1 = 0.0f, t2 = .0f; //temperature (cambiare nome)
int interval = 1000;  //tempo di intervallo invio dati in ms

/************************************ funzioni ********************************/

/**
 * formatta e invia i dati al computer centrale
 */
void invioDati(){
  /**
   * legenda:
   * 
   */
  Serial.print("Temp1=");
  Serial.print(t1);
  Serial.print(" ");
  Serial.print("Temp2=");
  Serial.print(t2);
  Serial.println();
}

/**
 * legge la temperatura dei sensori
 */
void leggoTemperature() {
  sensors.requestTemperatures();          // invio il comando di richiesta temperatura
  t1 = sensors.getTempCByIndex(CALDAIA);
  t2 = sensors.getTempCByIndex(BOILER);
}

/*
 * legge il peso della segatura dalla bilancia
 * 
 * @return peso in grammi
 */
int leggoPesoSegatura() {
  
}

/**
 * gestisce il motorino per il ribaltamento della segatura
 */
void rovescioSegatura() {
  
}

/**
 * gestisce l'invio di segatura alla caldaia
 * 
 * @return segatura inviata alla caldaia in grammi 
 */
int controllerSegatura() {
  
}

/************************************** main **********************************/

void setup(void)
{
  Serial.begin(9600);
  Serial.println("handshake");    //invio "handshake" per la connessione automatica a python 
  sensors.begin();
}

void loop(void)
{ 
  leggoTemperature();
  invioDati();
  delay(interval);
}
