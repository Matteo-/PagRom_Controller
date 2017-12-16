#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#TODO ogni sezione dovra diventare un oggetto
################################## Config utils ################################
def leggi_file(file):
    f = open(file, "r") 
    return f.read().strip()

'''
formatta i dati provenienti da arduino 
dividendoli in un dizionario
se i dati non sono formattabili 
ritorna dizionario vuoto
'''
def dataParser(datain):
    data = {}
    elements = []
    #splitto la stringa nei vari elementi
    try:
        row = datain.strip().split("\n")
        for el in row:
            try:
                #elimino i commenti
                if el[0] != '#':
                    elements.extend(el.strip().split())
            except:
                pass
    except:
        return data
    
    for el in elements:
        try:
            name,value = el.split("=")
            data[name] = value
        except:
            pass

    return data

'''
dizionario che contiene tutte le configurazioni del Controller
'''
config = dataParser(leggi_file("config.txt"))

##################################### DataBase #################################
''' serve python-mysqldb --> apt install python-mysqldb '''
import MySQLdb

class DataBase:
    
    def __init__(self, config):
        try:
            self.db_connection = MySQLdb.connect(host=config['db_host'],
                                 user=config['db_user'],
                                 passwd=config['db_passwd'],
                                 db=config['db_name'])
            print("[DATABASE] connesso")
        except:
            print("[DATABASE] non riesco a connettermi al database")
            quit()

        # creo il cursore per utilizzare il database
        self.db = self.db_connection.cursor()

    #eseguo la query e aggiorno il database
    #ritorno il risultato della query
    def execute(self, query):
        self.db.execute(query)
        self.db_connection.commit()
        return self.db.fetchall()

    #chiude la connessione con il database
    def closeDataBase():
        global db_connection
        db_connection.close()

# esempi di utilizzo
#db.execute("SHOW TABLES")
#for row in db.fetchall():
#    print(row[0])

#creo database
db = DataBase(config)

##################################### Arduino ##################################
import serial
import serial.tools.list_ports
import time

#TODO trrovarla automaticamente trramite haandshake coon arrduino
#porta di collegamento con arduino
ser = serial.Serial()
baudrate = 9600
connected = False;

#TODO mandare ad arduino il tempo di intervallo*2 e farglielo impostare
#tempo di intervallo in secondi
interval = 0.5

#dati prrovenienti da arduino
lettura = {}

def aggiorna_dati(new_data):
    #print("[ARDUINO] aggiorno dati")
    #print("new: "+str(new_data))
    try:
        global lettura
        lettura = new_data
    except Exception as ex:
        print(ex)
    #print("lettura: "+str(lettura))
    #print("[ARDUINO] fine aggiorno dati")

def get_all_data():
    global lettura
    return lettura
    
def getdata_byname(name):
    global lettura
    return lettura[name]

def closeSerial(connection):
    connection.close()

#leggo i valori provenienti da arduino
def readArduino(connection):
    out = b""
    try:
        while(connection.inWaiting() > 0):
            out += ser.read(1)
    except:
        print("[SERIALE] errore nella connessione con arduino")    

    return out.decode()

"""
####### connessione tramite handshake #######
#   python----connect---->Arduino           #
#   python<---"handshake"----Arduino        #
#   connection DONE!                        #
#############################################
"""
ports = list(serial.tools.list_ports.comports())
for p in ports:
    try:
        ser = serial.Serial(p.device, baudrate)
        time.sleep(1) #evito che arduino vada in reset
        if readArduino(ser).strip() == "handshake":
            connected = True
            break
        else:
            ser.close()
    except serial.SerialException:
        pass

#controllo il risultato
if connected:
    print("[SERIALE] arduino connesso")
else:
    print("[SERIALE] arduino non trovato")
    quit()

#appunti scrittura e lettura su seriale
#scrittura
#ser.write(b"H")
#lettura
#out = b""
#while(ser.inWaiting() > 0):
#    out += ser.read(1)
#oppure (bloccante)
#ser.readline()

#appunti per codifica e decodifica
#my_str = "hello world"
#my_str_as_bytes = str.encode(my_str)
#type(my_str_as_bytes) # ensure it is byte representation
#my_decoded_str = my_str_as_bytes.decode()
#type(my_decoded_str) # ensure it is string representation

##################################### Telegram bot #############################
#TODO agiungere comando status, imposta temp minima, massima, critica, ecc
from telegram.ext import Updater, CommandHandler
import logging

# Enable logging
logging.basicConfig(filename='Controller.log',
                    format='%(asctime)s|%(levelname)s| %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('ciao! usa /help per spawnare il manuale')
    
def help(bot, update):
    try:
        manuale = leggi_file("manuale.txt")
        update.message.reply_text(manuale)
    except Exception as ex:
        print(ex)

'''
#da mettere a posto
def status(bot, update):
    dim = {0:"KB", 1:"MB", 2:"GB"}
    i = 0
    update.message.reply_text("dimensione database: 100"+dim[1])
    query_dim = """
    SELECT SUM(data_length+index_length) AS dimensione
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE table_schema = '"""+config['db_name']+"'"
    try:
        res = db.execute(query_dim)
        print(res)
        for row in res:
            print(str(row))
            row = int(row)
            while row > 1024:
                row /= 1024
                i += 1
            update.message.reply_text("dimensione database: "+str(row)+dim[i])
            print("OK")
    except Exception as ex:
        print(ex)
'''
    
def leggi_temp(bot, self):
    raw_data = readArduino(ser)
    if raw_data != "":
        #print(raw_data.strip())
        tmp = dataParser(raw_data)
        #controllo se ho letto daati coorretti e aggiorno
        if tmp:
            #in caso i dati siano corrotti o inesistenti
            try:
                aggiorna_dati(tmp)
                db.execute("INSERT INTO temperatura (temp) VALUES ("+str(getdata_byname('Temp1'))+")")
            except Exception as ex:
                print(ex)
            
def temp(bot, update):
    print("invio temperatura")
    try:
        print(get_all_data())
        txt = "Temp pc: "+str(getdata_byname('Temp1'))+"°C\n"
        txt += "Temp ambiente: "+str(getdata_byname('Temp2'))+"°C"
        update.message.reply_text(txt)
    except Exception as ex:
        print(ex)

'''
def alarm(bot, job):
    """Send the alarm message."""
    bot.send_message(job.context, text='Beep!')

def set_timer(bot, update, args, job_queue, chat_data):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        # Add job to queue
        job = job_queue.run_once(alarm, due, context=chat_id)
        chat_data['job'] = job

        update.message.reply_text('Timer successfully set!')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def unset(bot, update, chat_data):
    """Remove the job if the user changed their mind."""
    if 'job' not in chat_data:
        update.message.reply_text('You have no active timer')
        return

    job = chat_data['job']
    job.schedule_removal()
    del chat_data['job']

    update.message.reply_text('Timer successfully unset!')
'''

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    """Run bot."""
    updater = Updater(config['bot_token'])
    
    #creo il job che legge da arduino
    j = updater.job_queue
    job_leggi_temp = j.run_repeating(leggi_temp, interval=1, first=0)
    #job_leggi_temp.enabled = True

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("temp", temp))
#    dp.add_handler(CommandHandler("status", status))
    
    '''
    dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    
    dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))
    '''
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    print("[TELEGRAM_BOT] avviato")

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
