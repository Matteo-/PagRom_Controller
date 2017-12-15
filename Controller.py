#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#TODO ogni sezione dovra diventare un oggetto
##################################### DataBase #################################
''' serve python-mysqldb --> apt install python-mysqldb '''
import MySQLdb
import getpass

name = "PagRom"
pspw = getpass.getpass("[DATABASE] inserisci password per "+name+":")

try:
	db_connection = MySQLdb.connect(host="localhost",
		                 user=name,
		                 passwd=pspw,
		                 db="PagRom_Caldaia")
	print("[DATABASE] connesso")
except:
    print("[DATABASE] I am unable to connect to the database")
    quit()

# creo il cursore per utilizzare il database
db = db_connection.cursor()

# esempi di utilizzo
#db.execute("SHOW TABLES")
#for row in db.fetchall():
#    print(row[0])

#eseguo la query e aggiorno il database
def DBexecute(query):
	db.execute(query)
	db_connection.commit()

#chiude la connessione con il database
def closeDataBase():
	db_connection.close()

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

def dataParser(datain):
	data = {}
	#splitto la stringa nei vari elementi
	elements = datain.strip().split()
	for el in elements:
		name,value = el.split(":")
		data[name] = value
	return data

#connessione automatica ad arduino
ports = list(serial.tools.list_ports.comports())
for p in ports:
	try:
		ser = serial.Serial(p.device, baudrate)
		time.sleep(0.9) #evito che arduino vada in reset
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

#ciclo di lettura
''' verrà sostituito da un job del bot '''
while(True):
	raw_data = readArduino(ser)
	if raw_data != "":
		print(raw_data)
		lettura = dataParser(raw_data)
		print(lettura['Temp1'])
		DBexecute("INSERT INTO temperatura (temp) VALUES ("+str(lettura['Temp1'])+")")
	time.sleep(interval)

#appunti scrittura e lettura su seriale
#scrittura
#ser.write(b"H")
#lettura
#out = b""
#while(ser.inWaiting() > 0):
#	out += ser.read(1)
#oppure (bloccante)
#ser.readline()

#appunti per codifica e decodifica
#my_str = "hello world"
#my_str_as_bytes = str.encode(my_str)
#type(my_str_as_bytes) # ensure it is byte representation
#my_decoded_str = my_str_as_bytes.decode()
#type(my_decoded_str) # ensure it is string representation

##################################### Telegram bot #############################
"""Simple Bot to send timed Telegram messages.
# This program is dedicated to the public domain under the CC0 license.
This Bot uses the Updater class to handle the bot and the JobQueue to send
timed messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
'''
from telegram.ext import Updater, CommandHandler
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Hi! Use /set <seconds> to set a timer')


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


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Run bot."""
    updater = Updater("TOKEN")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
'''
