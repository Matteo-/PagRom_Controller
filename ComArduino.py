##################################### Arduino ##################################
import serial
import serial.tools.list_ports
import time
import datetime

from utils import *

class ComArduino:
    
    def __init__(self, coonfig):
        
        self.ser = serial.Serial()
        self.baudrate = config['ino_boudrate']
        #dati prrovenienti da arduino
        self.lettura = {}
        
        self.connect()
        #TODO controllare connessione attraverso pyserial
        print("[SERIALE] arduino connesso")
    
    #ritorna la lettura completa di tutti i valori    
    def get_all_data(self):
        return self.lettura
    
    #ritorna la il valore del campo di lettura
    def get_by_name(self, name):
        return self.lettura[name]
    
    #chiude la connessione con arduino
    def close(self):
        self.ser.close()
    
    
    #scrive sulla seriale    
    def write(self, text):
        self.ser.write(str.encode(text))

    #leggo i valori provenienti da arduino
    def read(self, raw=False):
        out = b""
        try:
            while(self.ser.inWaiting() > 0):
                out += self.ser.read(1)
        except:
            print("[SERIALE] errore nella connessione con arduino")
            #pulisco i dati
            self.lettura = {}
            #tento riconnessione
            self.close()
            self.connect()
            raise Exception('Reading error')
        
        if not raw: 
            try:
                if out.decode() != "":
                    self.lettura = dataParser(out.decode())
                    self.lettura['date'] = '{:%d-%b-%Y %H:%M:%S}'.format(datetime.datetime.now())
            except Exception as ex:
                print(ex)  
            return self.lettura
        else:
            return out.decode()

    
    """
    ####### connessione tramite handshake #######
    #   python----connect---->Arduino           #
    #   python<---"handshake"----Arduino        #
    #   connection DONE!                        #
    #############################################
    """
    def connect(self):
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            try:
                self.ser = serial.Serial(p.device, self.baudrate)
                time.sleep(1) #evito che arduino vada in reset
                if self.read(raw=True).strip() == "handshake":
                    break
                else:
                    self.close()
            except serial.SerialException as ex:
                print(ex)
        #return self.ser.state()

