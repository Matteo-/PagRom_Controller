#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#TODO ogni sezione dovra diventare un oggetto
################################## utils #######################################
import logging

# abilito il log
logging.basicConfig(filename='Controller.log',
                    format='%(asctime)s|%(levelname)s| %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

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

#creo database
db = DataBase(config)

##################################### Arduino ##################################
import serial
import serial.tools.list_ports
import time
import datetime

class ComArduino:
    
    def __init__(self, coonfig):
        
        self.ser = serial.Serial()
        self.baudrate = config['ino_boudrate']
        #dati prrovenienti da arduino
        self.lettura = {}
        
        self.connect()
        
    def get_all_data(self):
        return self.lettura
    
    def get_by_name(self, name):
        return self.lettura[name]

    def close():
        self.ser.close()

    #leggo i valori provenienti da arduino
    def read(self, raw=False):
        out = b""
        try:
            while(self.ser.inWaiting() > 0):
                out += self.ser.read(1)
        except:
            print("[SERIALE] errore nella connessione con arduino")  
        
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
                    ser.close()
            except serial.SerialException as ex:
                print(ex)
        print("[SERIALE] arduino connesso")
        '''
        #controllo il risultato usare ser per valutare la connesione
        if connected:
            print("[SERIALE] arduino connesso")
        else:
            print("[SERIALE] arduino non trovato")
            quit()
        '''

ino = ComArduino(config)

##################################### Telegram bot #############################
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
                 InlineKeyboardButton("Option 2", callback_data='2')],

                [InlineKeyboardButton("Option 3", callback_data='3')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text('ciao! usa /help per spawnare il manuale', reply_markup=reply_markup)
    
def menu(bot, update):
    query = update.callback_query

    bot.edit_message_text(text="Selected option: {}".format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
    
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

last_read = 0
def leggi_temp(bot, self):
    ino.read()
    try:
        if ino.get_by_name('date') != last_read:
            #in caso i dati siano corrotti o inesistenti
            last_read = ino.get_by_name('date')
            try:
                db.execute("INSERT INTO temperatura (temp) VALUES ("+str(ino.get_by_name('Temp1'))+")")
            except Exception as ex:
                print(ex)
    except:
        pass
        #print(ex)
            
def temp(bot, update):
    try:
        print("invio temperatura")
        print(ino.get_all_data())
        txt = "data ultima lettura: "+ino.get_by_name('date')+"\n\n"
        txt += "Temp pc: "+str(ino.get_by_name('Temp1'))+"°C\n"
        txt += "Temp ambiente: "+str(ino.get_by_name('Temp2'))+"°C"
        update.message.reply_text(txt)
    except Exception as ex:
        #print(ex)
        pass

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
    updater.dispatcher.add_handler(CallbackQueryHandler(menu))
    
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
