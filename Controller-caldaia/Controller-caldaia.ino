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

  bool VERBOSE = false;                          // attiva disattiva il verbose mode
  
  //TEMPERATURA
  float tmax = 80.0f,
        tmin = 20.0f,
        t1 = .0f,
        t2 = .0f;                             // temperature (cambiare nome)
  bool pompa1, pompa2;
  
  //segatura
  bool stepper_run = false;   //stato dello stepper
  byte livello_segatura = 0;    //livello segatura silos
  int segatura_aggiunta = 0;    //segatura aggiunta 
  bool aggiungi_segatura = false;   //flag di controllo per l'aggiunta di segatura
  int payload = 120;                 //grammi di segatura da aggiungere
  int payload_mantenimento = 40;    //grammi di segatura da aggiungere una volta raggiunta la temperatura
  bool coclea_silos = false;        //stato coclea silos
  bool coclea_segatura = false;     //stato coclea segatura

  void invio() {
      /**
       * legenda:
       * 
       */
      Serial.print("DATA ");
      Serial.print("T1=");
      Serial.print(t1);
      Serial.print(" T2=");
      Serial.print(t2);
      Serial.print(" SegAgg=");
      Serial.print(segatura_aggiunta);
      Serial.print(" ControlSeg=");
      Serial.print(aggiungi_segatura);
      Serial.print(" Step=");
      Serial.print(stepper_run);
      Serial.print(" CclSilos=");
      Serial.print(coclea_silos);
      Serial.println();
  }
  
} DATA;

/****************************** dati del controller ***************************/
DATA data;                                    // dati importanti

//TIMER
Timer t;

//TEMPISTICHE
int ATTESA_SCARICO_SEGATURA = 2500;
int ATTESA_RITORNO_BILANCIA = 2000;

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

void verbose(String s, bool newline = true) {
  if(data.VERBOSE) Serial.print(s);
  if(newline) Serial.println();
}

/**
 * legge la temperatura dei sensori
 */
void leggoTemperature() {
  // molto pesante computazionalmente! da problemi con il motore
  if(data.stepper_run == false) {
    verbose("read temp"); //debug
    sensors.requestTemperatures();          // invio il comando di richiesta temperatura
    data.t1 = sensors.getTempCByIndex(CALDAIA);
    data.t2 = sensors.getTempCByIndex(BOILER);
    //stato();
  } else {
    verbose("not read temp");  //debug
  }
}

/*
 * legge il peso della segatura dalla bilancia
 * 
 * @return peso in grammi
 */
int pesoSegatura() {
  return bilancia.get_units();
}

/**
 * formatta e invia i dati al computer centrale
 */
void stato() {
  data.invio();
}

/**
 * gestisce il motorino per il ribaltamento della segatura
 */
void riposiziona() {
  verbose("riposiziono bilancia");
  stepper.moveTo(0);
  //data.stepper_run = false;          // aggiorno lo stato di azionamento dello stepper
  //stato();
}
void svuotaSegatura() {
  verbose("svuoto segatura");
  //data.stepper_run = true;            // aggiorno lo stato di azionamento dello stepper
  //stato();
  stepper.moveTo(5000);
  t.after(ATTESA_RITORNO_BILANCIA, riposiziona);
}

/**
 * 
 */
void addSegatura() {
  data.aggiungi_segatura = true;
}

/**
 * gestisce l'invio di segatura alla caldaia
 * 
 * @return segatura inviata alla caldaia in grammi 
 */
int controllerSegatura() {
  if (data.aggiungi_segatura) {
    if (pesoSegatura() >= data.payload ) {
        verbose("fermo coclea silos");
        data.coclea_silos = false;
        data.segatura_aggiunta = pesoSegatura();
        data.aggiungi_segatura = false;
        t.after(ATTESA_SCARICO_SEGATURA, svuotaSegatura);
        //ricalco il prossimo carico
        //e imposto il timer che lo richiamerà
        //TODO impostare payload di mantenimento quando la temperatura è arrivata a regime
        verbose("calcolo temporizzazione prossimo carico");
        t.after(10000, addSegatura);
    } else {
      if(data.coclea_silos == false) {
        //avvio coclea chiama segatura (set pin to high)
        data.coclea_silos = true;
        verbose("avvio coclea silos");
      }
    }
  } else {
    data.segatura_aggiunta = 0;
  }

  //controllo se lo stepper è in fase di movimento
  if (stepper.currentPosition() == 0) {
    data.stepper_run = false;
  } else {
    data.stepper_run = true;
  }
}

/**
 * debug
 */
void test() {
  int start = millis();
  data.invio();
  int fine = millis() - start;
  Serial.print("Tempo invio(ms): ");
  Serial.println(fine);  //debug

  start = millis();
  leggoTemperature();
  fine = millis() - start;
  Serial.print("Tempo letture temp(ms): ");
  Serial.println(fine);  //debug
}
/************************************** main **********************************/

void setup(void)
{
  Serial.begin(9600);
  Serial.println("handshake");    // invio "handshake" per la connessione automatica a python

  //TERMOMETRI
  Serial.print("Inizializzazione Termometri...");
  sensors.begin();
  Serial.println("OK");

  //STEPPER SEGATURA
  Serial.print("Settaggio motore stepper...");
  //stepper.setSpeed(5000);
  stepper.setMaxSpeed(5000);
  stepper.setAcceleration(100000);
  //stepper.setCurrentPosition(0);
  Serial.println("OK");

  //TIMER
  t.every(1000, stato);
  t.every(2000, leggoTemperature);

  //TESTING
  t.after(1000, test);
  t.after(3000, addSegatura);

  //BILANCIA
  Serial.print("Calibrazione e tara della bilancia...");
  bilancia.set_scale(calibration_factor); // imposto il fattore di calibrazione
  bilancia.tare();                      // imposto la tara mettendo a 0 la bilancia
  Serial.println("OK");
}

void loop(void)
{ 
  /**
 * varie funzioni di aggiornamento
 */
  controllerSegatura();
  t.update();
  stepper.run();
}
