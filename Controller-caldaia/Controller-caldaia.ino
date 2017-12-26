/** 
 *  Arduino DS18B20 temp sensor tutorial http://www.ardumotive.com/how-to-use-the-ds18b20-temperature-sensor-en.html
 *  
 *  rosso = gnd
 *  nero = gnd
 *  giallo = collegato a vcc tramite resistenza (tot) e ad arduino su pin digitale di lettura
 *  
 *  è possibile collegare più termometri in serie
 */
#include <OneWire.h>
#include <DallasTemperature.h>

/**
 * bilancia chip HX711 libreria: https://github.com/bogde/HX711
 * 
 * connessioni del modulo H711 ad arduino:
 *  DT = analog A1
 *  SCK = analog A0
 * connessioni del sensore di peso al modulo HX711:
 *  rosso = E+
 *  nero= E-
 *  verde = A-
 *  bianco = A+
 */
#include <HX711.h>

/**
 * libreria timer github: https://github.com/JChristensen/Timer
 */
#include <Event.h>
#include <Timer.h>

/**
 * accel stepper per il motore passo passo: https://github.com/adafruit/AccelStepper
 * 
 * dir = 
 * 
 */
#include <AccelStepper.h>

typedef struct {
  float tmax = 80.0f,
        tmin = 20.0f,
        t1 = .0f,
        t2 = .0f;                             // temperature (cambiare nome)
  int segatura_aggiunta = 0;
  byte livello_segatura = 0;
  bool pompa1, pompa2;

  void invio() {
      /**
       * legenda:
       * 
       */
      Serial.print("Temp1=");
      Serial.print(t1);
      Serial.print(" Temp2=");
      Serial.print(t2);
      Serial.print(" Peso=");
      Serial.print(segatura_aggiunta);
      Serial.println();
  }
  
} DATA;

/****************************** dati del controller ***************************/
DATA data;                                    // dati importanti

//TIMER
Timer t;

//TERMOMETRI
#define ONE_WIRE_BUS 2                        // il pin 2 viene usato per il bus Onewire
OneWire oneWire(ONE_WIRE_BUS);                // Inizializzo istanza Onewire per comunicare con i dispositivi
DallasTemperature sensors(&oneWire);          // passo oneWire a Dallas Temperature
enum Termometri {CALDAIA, BOILER, ESTERNO};   // enum con i nomi dei sensori di temperatura

//BILANCIA
#define DOUT A1
#define CLK A0
const float calibration_factor = 391.76f;     // valore di calibrazione della bilancia, valore fisso NON MODIFICARE
HX711 bilancia(DOUT, CLK);

//STEPPER SEGATURA
#define STEP 3                                // pin di step
#define DIR 4                                 // pin di direzione
AccelStepper stepper(AccelStepper::DRIVER, STEP, DIR);

/************************************ funzioni ********************************/

/**
 * formatta e invia i dati al computer centrale
 */
void invioDati(){
  data.invio();
}

/**
 * legge la temperatura dei sensori
 */
void leggoTemperature() {
  sensors.requestTemperatures();          // invio il comando di richiesta temperatura
  data.t1 = sensors.getTempCByIndex(CALDAIA);
  data.t2 = sensors.getTempCByIndex(BOILER);
}

/*
 * legge il peso della segatura dalla bilancia
 * 
 * @return peso in grammi
 */
int leggoPesoSegatura() {
  return bilancia.get_units(), 0;
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
  Serial.println("handshake");    // invio "handshake" per la connessione automatica a python

  //TERMOMETRI
  sensors.begin();

  //BILANCIA
  bilancia.set_scale(calibration_factor); // imposto il fattore di calibrazione
  bilancia.tare(20);                      // imposto la tara mettendo a 0 la bilancia

  //STEPPER SEGATURA
  stepper.setSpeed(500);
  stepper.setMaxSpeed(2000);
  stepper.setAcceleration(300);
  stepper.setCurrentPosition(0);
  stepper.moveTo(10000);    //debug

  //TIMER
  //t.every(1000, invioDati);
  //t.every(200, leggoTemperature);

  //TESTING
  //pinMode(11, OUTPUT);
  //digitalWrite(11, HIGH);
  //pinMode(12, INPUT);
}

void loop(void)
{ 
  //leggoTemperature();
  //invioDati();
  
  // If at the end of travel go to the other end DEBUG
  if (stepper.distanceToGo() == 0)
    stepper.moveTo(-stepper.currentPosition());

  //Serial.println(digitalRead(12));  //debug
    
  t.update();
  stepper.run();
}
