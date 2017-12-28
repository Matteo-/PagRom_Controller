################################## utils #######################################
import logging

# abilito il log
logging.basicConfig(filename='Controller.log',
                    format='%(asctime)s|%(levelname)s| %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#funzioni di utilità
def leggi_file(file):
    f = open(file, "r") 
    return f.read().strip()

val = -1 
def auto():
    global val
    val += 1
    return val

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
    
    #carico il dizionario di valori
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

'''
whitelist per il controllo delle autorizzazioni
ci possono essere 2 livelli 
    -"r" privilegi di lettura:
        da accesso a tutte le funzioni che permettono di leggere i dati
    -"rw" privilegi di lettura e scrittura:
        da accesso ad ogni tipo di funzione quindi possibilita di leggere e scrivere
'''
whitelist = {}
def carica_whitelist():
    global whitelist
    lista = leggi_file("whitelist.txt").strip().split()
    for row in lista:
        try:
            if row[0] is not '#':
                chat_id,nome,lingua,privilegi = row.split(':')
                whitelist[int(chat_id)] = {'nome':nome, 'privilegi':privilegi, 'lingua':lingua}
        except:
            pass

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
