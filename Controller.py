#!/usr/bin/env python
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

##################################### Emoji ####################################
from emoji import emojize
#url emoji http://www.unicode.org/emoji/charts/emoji-list.html

emojilist = {}
#emojilist['sviluppatore'] = emojize(":man technologist:", use_aliases=True)
emojilist['OK'] = emojize(":OK hand:", use_aliases=True)
emojilist['pollicesu'] = emojize(":thumbs up:", use_aliases=True)
emojilist['lucepericolo'] = emojize(":police car light:", use_aliases=True)
emojilist['timer'] = emojize(":timer clock:", use_aliases=True)
emojilist['avviso'] = emojize(":megaphone:", use_aliases=True)
emojilist['telescopio'] = emojize(":telescope:", use_aliases=True)
emojilist['chart'] = emojize(":chart increasing:", use_aliases=True)
emojilist['lucchetto'] = emojize(":locked:", use_aliases=True)
emojilist['avviso'] = emojize(":warning:", use_aliases=True)
emojilist['spunta_ok'] = emojize(":heavy check mark:", use_aliases=True)
emojilist['croce_non_ok'] = emojize(":cross mark:", use_aliases=True)
emojilist['romania'] = emojize(":Romania:", use_aliases=True)
emojilist['italia'] = emojize(":Italy:", use_aliases=True)
emojilist['inglese'] = emojize(":United Kingdom:", use_aliases=True)

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
    def close(self):
        self.db_connection.close()

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
        #TODO controllare connessione attraverso pyserial
        print("[SERIALE] arduino connesso")
        
    def get_all_data(self):
        return self.lettura
    
    def get_by_name(self, name):
        return self.lettura[name]

    def close(self):
        self.ser.close()

    #leggo i valori provenienti da arduino
    def read(self, raw=False):
        out = b""
        try:
            while(self.ser.inWaiting() > 0):
                out += self.ser.read(1)
        except:
            print("[SERIALE] errore nella connessione con arduino")
            self.lettura = {}
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
                    ser.close()
            except serial.SerialException as ex:
                print(ex)

ino = ComArduino(config)

##################################### Telegram bot #############################
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

menulist = {}
menulist['MENU'] = 0
menulist['LEGGI_TEMP'] = 1 #auto()

keyboard = [[InlineKeyboardButton("nop", callback_data=menulist['MENU']),
             InlineKeyboardButton("leggi temperatura", callback_data=menulist['LEGGI_TEMP'])],
            [InlineKeyboardButton("nop", callback_data='3')]]   

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    try:
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text('ciao! usa /help per spawnare il manuale', reply_markup=reply_markup)  
    except Exception as ex:
        print(ex)
    
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

letture_perse = 0
last_read = 0

def leggi_temp(bot, self):
    '''
    tento la lettura di arduino
    se non riesco a leggere avvio la procedura di avviso
    in caso di lettura corretta aggiorno il database
    '''
    global letture_perse
    try:
        ino.read()
        letture_perse = 0
    except Exception as ex:
        print(ex) #debug
        '''avviso quando il timout di comunicazione con arduino scade'''
        #TODO capire perche non esegue il codice
        letture_perse += 1
        if letture_perse * int(config['bot_timer']) >= int(config['bot_arduino_timeout']):
            txt = emojilist['avviso']+" c'è un problema di comunicazione "+emojilist['avviso']
            txt += "\n\nnon riesco a comunicare con la caldaia\n\n"
            txt += "controllare la connessione di arduino\n"
            txt += "oppure contattare il programmatore"
            
            #TODO creare lista utenti autorizzati e mettere il controllo su ogni funzione 
            #con un try (funzione controllo) funzione principale except mandare messaggio non autorizzato
            print("invio avviso disconnessione")
            try:
                bot.send_message(chat_id="74544302", text=txt)
                letture_perse = 0
            except Exception as ex:
                    print(ex)
    else:
        '''
        qui procedo a elaborare i dati provenienti da arduino
        '''
        if ino.get_by_name('date') != last_read:
            #in caso i dati siano corrotti o inesistenti
            last_read = ino.get_by_name('date')
            try:
                db.execute("INSERT INTO temperatura (temp) VALUES ("+str(ino.get_by_name('Temp1'))+")")
            except Exception as ex:
                print(ex)
        
          
def temp(bot, update, chat_id=-1):
    try:
        #TODO fare anche il logging
        print("invio temperatura")
        print(ino.get_all_data())
        
        txt = "data ultima lettura: "+ino.get_by_name('date')+"\n\n"
        txt += "Temp pc: "+str(ino.get_by_name('Temp1'))+"°C\n"
        txt += "Temp ambiente: "+str(ino.get_by_name('Temp2'))+"°C"
    except Exception as ex:
        print(ex)
        txt = emojilist['avviso']+" c'è un problema di comunicazione "+emojilist['avviso']
        txt += "\n\nnon ci sono dati da mostrare\n\n"
        txt += "controllare la connessione di arduino\n"
        txt += "oppure contattare il programmatore"
        
    print(chat_id) #debug
    try:
        if chat_id == -1:
            print("invio da /tmp")
            update.message.reply_text(txt)
        else:
            print("invio da inline botton")
            bot.send_message(chat_id=chat_id, text=txt)
    except Exception as ex:
        print("errore")
                                  

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
    
def menu_parser(bot, update):
    try:
        query = update.callback_query
        '''
        bot.edit_message_text(text="Selected option: {}".format(query.data),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        '''
        
        print("[MENU] query.data: "+query.data+" type: "+str(type(query.data)))
        # map the inputs to the function blocks
        options = {menulist['LEGGI_TEMP'] : temp,
                   #1 : sqr,
                   #4 : sqr,
                   #9 : sqr,
                   #2 : even,
                   #3 : prime,
                   #5 : prime,
                   #7 : prime,
        }
        
        options[int(query.data)](bot, update, chat_id=query.message.chat_id)
        
        #bot.send_message(chat_id=query.message.chat_id, text="Selected option: {}".format(query.data))
    except Exception as ex:
        print(ex)
    

def main():
    """Run bot."""
    updater = Updater(config['bot_token'])
    
    #creo il job che legge da arduino
    j = updater.job_queue
    job_leggi_temp = j.run_repeating(leggi_temp, interval=int(config['bot_timer']), first=0)
    #job_leggi_temp.enabled = True

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CallbackQueryHandler(menu_parser))
    
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
