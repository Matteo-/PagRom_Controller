#!/usr/bin/env python
# -*- coding: utf-8 -*-
#TODO creare funzione broadcast per invio messaggi alla white list
from utils import *
from DataBase import DataBase
from ComArduino import ComArduino


carica_whitelist()


#database
db = DataBase(config)

#arduino
ino = ComArduino(config)

##################################### Telegram bot #############################
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

#traduzioni
import gettext
#_ = lambda s: s
_ = gettext.gettext
try:
    en = gettext.translation('Controller', localedir='locale', languages=['en'])
    #en.install()
except Exception as ex:
    print(ex)
print(_("non hai i privilegi necessari per proseguire "))

def imposta_lingua(chat_id):
    try:
        if whitelist[chat_id]['lingua'] == 'en':
            en.install()
        if whitelist[chat_id]['lingua'] == 'it':
            it.install()
        if whitelist[chat_id]['lingua'] == 'ro':
            ro.install()
    except Exception as ex:
        #print(ex)
        _ = lambda s: s

def auth(bot, chat_id, auth_lvl):
    accesso = True
    lvl = {'r':0, 'rw':1}
    try:
        if lvl[whitelist[chat_id]['privilegi']] < lvl[auth_lvl]:
            accesso = False
    except Exception as ex:
        print(ex)
        accesso = False
    
    imposta_lingua(chat_id)
    
    if not accesso:
        txt = _("non hai i privilegi necessari per proseguire ")+emojilist['lucchetto']
        bot.send_message(chat_id=chat_id, text=txt)
    
    return accesso
    
#diziaonario per indicizzare le voci di menu
menulist = {}
menulist['MENU'] = auto()
menulist['LEGGI_TEMP'] = auto()
menulist['RECONFIG'] = auto()
menulist['HELP'] = auto()

keyboard = [[InlineKeyboardButton(_("help"), callback_data=menulist['HELP']),
             InlineKeyboardButton(_("leggi temperatura"), callback_data=menulist['LEGGI_TEMP'])],
            [InlineKeyboardButton(_("riconfigura"), callback_data=menulist['RECONFIG'])]]   

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update, chat_id=0):
    reply_markup = InlineKeyboardMarkup(keyboard)
    if chat_id == 0:
        chat_id = update.message.chat_id
        if auth(bot, chat_id, "r"):
            try:
                update.message.reply_text(_("menu principale:"), reply_markup=reply_markup)  
            except Exception as ex:
                print(ex)
        else:
            print("tentativo entrata da parte di "+chat_id)
    else:
        if auth(bot, chat_id, "r"):
            try:
                bot.send_message(chat_id=chat_id, text=_("menu principale:"), reply_markup=reply_markup)
            except Exception as ex:
                print(ex)
    
def help(bot, update, chat_id):
    if auth(bot, chat_id, "r"):
        try:
            manuale = leggi_file("manuale.txt")
            bot.send_message(chat_id=chat_id, text=manuale)
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
        #se timeout infinito
        if config['bot_arduino_timeout'] is not 'I':
            '''avviso quando il timout di comunicazione con arduino scade'''
            #TODO capire perche non esegue il codice
            letture_perse += 1
            if letture_perse * int(config['bot_timer']) >= int(config['bot_arduino_timeout']):
                print("invio avviso disconnessione")
                try:
                    #invio il problema a tutti gli utenti
                    for chat_id in whitelist.keys():
                        imposta_lingua(chat_id)
                        txt = emojilist['avviso']+_(" c'è un problema di comunicazione ")+emojilist['avviso']
                        txt += _("\n\nnon riesco a comunicare con la caldaia\n\n")
                        txt += _("controllare la connessione di arduino\n")
                        txt += _("oppure contattare il programmatore")
                        bot.send_message(chat_id=chat_id, text=txt)
                        
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
                db.execute("INSERT INTO temperatura (temp) VALUES ("+str(ino.get_by_name('T1'))+")")
            except Exception as ex:
                print(ex)
        
          
def temp(bot, update, chat_id=-1):
    if auth(bot, chat_id, "r"):
        try:
            #TODO fare anche il logging
            print("invio temperatura")
            print(ino.get_all_data())
            
            txt = _("data ultima lettura: ")+ino.get_by_name('date')+"\n\n"
            txt += _("Temp pc: ")+str(ino.get_by_name('T1'))+"°C\n"
            txt += _("Temp ambiente: ")+str(ino.get_by_name('T2'))+"°C"
        except Exception as ex:
            print(ex)
            txt = emojilist['avviso']+_(" c'è un problema di comunicazione ")+emojilist['avviso']
            txt += _("\n\nnon ci sono dati da mostrare\n\n")
            txt += _("controllare la connessione di arduino\n")
            txt += _("oppure contattare il programmatore")
            
        print(chat_id) #debug
        try:
            if chat_id == -1:
                update.message.reply_text(txt)
            else:
                bot.send_message(chat_id=chat_id, text=txt)
        except Exception as ex:
            print(ex)
                                  
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)
    
def reconfig(bot, update, chat_id):
    if auth(bot, chat_id, "rw"):
        try:
            global config
            config = dataParser(leggi_file("config.txt"))
            carica_whitelist()
            txt = _("Riconfigurato ")+emojilist['spunta_ok']
            bot.send_message(chat_id=chat_id, text=txt)
        except Exception as ex:
            print(ex)
    
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
                   menulist['RECONFIG'] : reconfig,
                   menulist['HELP'] : help,
                   #9 : sqr,
                   #2 : even,
                   #3 : prime,
                   #5 : prime,
                   #7 : prime,
        }
        
        options[int(query.data)](bot, update, chat_id=query.message.chat_id)
        start(bot, update, query.message.chat_id)
        
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
    
    #dp.add_handler(CommandHandler("help", help))
    #dp.add_handler(CommandHandler("temp", temp))
    #dp.add_handler(CommandHandler("status", status))
    
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

    updater.idle()


if __name__ == '__main__':
    main()
