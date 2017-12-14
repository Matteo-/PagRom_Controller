#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import logging

# Enable logging
logging.basicConfig(filename='PagRom_Bot.log',
					format='%(asctime)s|%(levelname)s|%(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(bot, update):
    update.message.reply_text(
        'Padre....\n'
        'scegli lo stile di pulsante che ti piace di più e che trovi piu comodo\n'
        'premi /inlinea per avere i pulsanti sulla chat\n'
        'premi /tastiera per avere i tasti sotto la chat')

def inlinea(bot, update):
    keyboard = [[InlineKeyboardButton("Opzione 1", callback_data='1'),
                 InlineKeyboardButton("Opzione 2", callback_data='2')],
                [InlineKeyboardButton("Opzione 3", callback_data='3')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('questi sono i pulsanti sulla chat:', reply_markup=reply_markup)
        
def button(bot, update):
    query = update.callback_query
    #print (query)	 #debug

    bot.answerCallbackQuery(text="hai selezionato l'opzione: {}".format(query.data),
                          callback_query_id=query.id)
    bot.edit_message_text(text="Selected option: {}".format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)

def tastiera(bot, update):
    reply_keyboard = [['Opzione 1', 'Opzione 2', 'Opzione 3']]

    update.message.reply_text(
        'questi sono i pulsanti sotto la tastiera.\n'
        'Test session',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("327964142:AAENWdsnS4WB0H1QJDv6nkTAfLKEHt2ML0w")

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('inlinea', inlinea))
    updater.dispatcher.add_handler(CommandHandler('tastiera', tastiera))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    #updater.dispatcher.add_handler(CommandHandler('help', help))
    #updater.dispatcher.add_error_handler(error)	

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
	main()
