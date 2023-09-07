#!/usr/bin/env python
# coding: utf-8

# In[1]:


from __future__ import print_function
from tornado.web import StaticFileHandler, Application as TornadoApplication
from tornado.websocket import WebSocketHandler
from tornado.ioloop import IOLoop
import tornado.gen
import requests
from os.path import dirname, join as join_path
from datetime import datetime, timedelta 
import logging
import json
import time

logging.basicConfig(
    format='%(asctime)s: [%(levelname)s] - %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S',
    level=logging.DEBUG)

stats = {}
data_out = {}
lastheard = {}
actual_date = datetime.strftime(datetime.now(),"%Y-%m-%d")

is_changed = False

class Senzor:
    def __init__(self, name, avgT, maxT, minT, actT, onl):
        self.name = name
        self.minT = minT
        self.maxT = maxT
        self.avgT = avgT
        self.actT = actT
        self.onl = onl
        
class Aimtec:
    def __init__(self, stav_aimtec):
        self.stav_aimtec = stav_aimtec
        
class Hodnoty:
    def __init__(self, name, temp, alert, time, date):
        self.name = name
        self.temp = temp
        self.alert = alert
        self.time = time
        self.date = date

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, log):
        self.log = log

    def get(self):
        #date = datetime.strptime(data_out['created_on'], '%Y-%m-%dT%H:%M:%S.%f')
        #with open('2020-05-08.json', "r") as read_file:
        #    developer = json.load(read_file)
        developer = stats
        
        try:
            if(data_out['stav_aimtec']==True):
                stav_aimtec1 = Aimtec('online')
            else:
                stav_aimtec1 = Aimtec('offline')
        
            Senzor1 = Senzor('red', developer['red']['avg'],  developer['red']['max'],  developer['red']['min'], developer['red']['akt'], 'Online')
            Senzor2 = Senzor('green', developer['green']['avg'],  developer['green']['max'],  developer['green']['min'], developer['green']['akt'], 'Online')
            Senzor3 = Senzor('blue', developer['blue']['avg'],  developer['blue']['max'],  developer['blue']['min'], developer['blue']['akt'],'Online')
            Senzor4 = Senzor('pink', developer['pink']['avg'],  developer['pink']['max'],  developer['pink']['min'], developer['pink']['akt'],'Online')
            Senzor5 = Senzor('yellow', developer['yellow']['avg'],  developer['yellow']['max'],  developer['yellow']['min'], developer['yellow']['akt'],'Online')
            Senzor6 = Senzor('black', developer['black']['avg'],  developer['black']['max'],  developer['black']['min'], developer['black']['akt'],'Online')
            Senzor7 = Senzor('orange', developer['orange']['avg'],  developer['orange']['max'],  developer['orange']['min'], developer['orange']['akt'], 'Online')
            senzors = [Senzor1, Senzor2, Senzor3, Senzor4, Senzor5, Senzor6, Senzor7]
            for item in senzors:
                if(time.time()-lastheard[item.name] > 120):
                    item.onl = 'Offline'
                    
            senzors = [stav_aimtec1, Senzor1, Senzor2, Senzor3, Senzor4, Senzor5, Senzor6, Senzor7]
            self.render('./sablona2.html', title="Home page", senzors=senzors)
        except KeyError:
            self.render('./sablona_krize.html', title="Jejda!")

class nacti:
    def load_json(self,file_name):
        fh = open(file_name, 'r')
        data_out = fh.read()
        fh.close()
        return data_out
    def load_json_colour(self,file_name):
        fh = open(file_name, 'r')
        data_out = fh.readlines()
        fh.close()
        return data_out
    def uprav_cas(casovy_udaj):
        cas = casovy_udaj.split('T')
        datum = (cas[0][8] + cas[0][9] + '.' +cas[0][5]+cas[0][6]+'.'+cas[0][0]+cas[0][1]+cas[0][2]+cas[0][3])
        cas2 = cas[1][0:8]
        return cas2, datum
    
    def priprav(self, data):
        avg = round(data['pink']['avg'], 2)
        maxT = round(data['pink']['max'], 2)
        minT = round(data['pink']['min'], 2)
        akt = round(data['pink']['akt'], 2)
        pink = Senzor('pink', avg,  maxT,  minT, akt, True)
        
        avg = round(data['red']['avg'], 2)
        maxT = round(data['red']['max'], 2)
        minT = round(data['red']['min'], 2)
        akt = round(data['red']['akt'], 2)
        red = Senzor('red', avg,  maxT,  minT, akt, True)
        
        avg = round(data['blue']['avg'], 2)
        maxT = round(data['blue']['max'], 2)
        minT = round(data['blue']['min'], 2)
        akt = round(data['blue']['akt'], 2)
        blue = Senzor('blue', avg,  maxT,  minT, akt, True)
        
        avg = round(data['green']['avg'], 2)
        maxT = round(data['green']['max'], 2)
        minT = round(data['green']['min'], 2)
        akt = round(data['green']['akt'], 2)
        green = Senzor('green', avg,  maxT,  minT, akt, True)
        
        avg = round(data['yellow']['avg'], 2)
        maxT = round(data['yellow']['max'], 2)
        minT = round(data['yellow']['min'], 2)
        akt = round(data['yellow']['akt'], 2)
        yellow = Senzor('yellow', avg,  maxT,  minT, akt, True)
        
        avg = round(data['black']['avg'], 2)
        maxT = round(data['black']['max'], 2)
        minT = round(data['black']['min'], 2)
        akt = round(data['black']['akt'], 2)
        black = Senzor('black', avg,  maxT,  minT, akt, True)
        
        avg = round(data['orange']['avg'], 2)
        maxT = round(data['orange']['max'], 2)
        minT = round(data['orange']['min'], 2)
        akt = round(data['orange']['akt'], 2)
        orange = Senzor('orange', avg,  maxT,  minT, akt, True)
        
        senzors = [pink, red, blue, green, yellow, black, orange]
        
        return senzors
    
class pink(tornado.web.RequestHandler):
    
    def get(self):
        try:
            data_out = nacti.load_json_colour(self,'pink.json')
            poradi = 0;
            hodnoty = []
            for item in data_out[len(data_out):1:-1]:
                item = json.loads(item)
                item['cas'],item['datum'] = nacti.uprav_cas(item['created_on'])
                alert = 'black'
                if(item['temperature']>30 or item['temperature']<0):
                    alert = 'red'
                teplota = round(item['temperature'], 2)
                hodnota = Hodnoty('pink', teplota, alert, item['cas'], item['datum'])
                hodnoty.append(hodnota)
            self.render('./pink.html',title="Pink sensor",hodnoty=hodnoty)
        except FileNotFoundError:
            self.render('./sablona_krize.html', title="Jejda!")
            
class blue(tornado.web.RequestHandler):
    
    def get(self):
        try:
            data_out = nacti.load_json_colour(self,'blue.json')
            poradi = 0;
            hodnoty = []
            for item in data_out[len(data_out):1:-1]:
                item = json.loads(item)
                item['cas'],item['datum'] = nacti.uprav_cas(item['created_on'])
                alert = 'black'
                if(item['temperature']>30 or item['temperature']<0):
                    alert = 'red'
                teplota = round(item['temperature'], 2)
                hodnota = Hodnoty('blue', teplota, alert, item['cas'], item['datum'])
                hodnoty.append(hodnota)
            self.render('./blue.html',title="Blue sensor",hodnoty=hodnoty)
        except FileNotFoundError:
            self.render('./sablona_krize.html', title="Jejda!")
            
class green(tornado.web.RequestHandler):
    
    def get(self):
        try:
            data_out = nacti.load_json_colour(self,'green.json')
            poradi = 0;
            hodnoty = []
            for item in data_out[len(data_out):1:-1]:
                item = json.loads(item)
                item['cas'],item['datum'] = nacti.uprav_cas(item['created_on'])
                alert = 'black'
                if(item['temperature']>30 or item['temperature']<0):
                    alert = 'red'
                teplota = round(item['temperature'], 2)
                hodnota = Hodnoty('green', teplota, alert, item['cas'], item['datum'])
                hodnoty.append(hodnota)
            self.render('./green.html',title="Green sensor",hodnoty=hodnoty)
        except FileNotFoundError:
            self.render('./sablona_krize.html', title="Jejda!")
            
class orange(tornado.web.RequestHandler):
    
    def get(self):
        try:
            data_out = nacti.load_json_colour(self,'orange.json')
            poradi = 0;
            hodnoty = []
            for item in data_out[len(data_out):1:-1]:
                item = json.loads(item)
                item['cas'],item['datum'] = nacti.uprav_cas(item['created_on'])
                alert = 'black'
                if(item['temperature']>30 or item['temperature']<0):
                    alert = 'red'
                teplota = round(item['temperature'], 2)
                hodnota = Hodnoty('orange', teplota, alert, item['cas'], item['datum'])
                hodnoty.append(hodnota)
            self.render('./orange.html',title="Orange sensor",hodnoty=hodnoty)
        except FileNotFoundError:
            self.render('./sablona_krize.html', title="Jejda!") 
            
class yellow(tornado.web.RequestHandler):
    
    def get(self):
        try:
            data_out = nacti.load_json_colour(self,'yellow.json')
            poradi = 0;
            hodnoty = []
            for item in data_out[len(data_out):1:-1]:
                item = json.loads(item)
                item['cas'],item['datum'] = nacti.uprav_cas(item['created_on'])
                alert = 'black'
                if(item['temperature']>30 or item['temperature']<0):
                    alert = 'red'
                teplota = round(item['temperature'], 2)
                hodnota = Hodnoty('yellow', teplota, alert, item['cas'], item['datum'])
                hodnoty.append(hodnota)
            self.render('./yellow.html',title="Yellow sensor",hodnoty=hodnoty)
        except FileNotFoundError:
            self.render('./sablona_krize.html', title="Jejda!")
            
class black(tornado.web.RequestHandler):
    
    def get(self):
        try:
            data_out = nacti.load_json_colour(self,'black.json')
            poradi = 0;
            hodnoty = []
            for item in data_out[len(data_out):1:-1]:
                item = json.loads(item)
                item['cas'],item['datum'] = nacti.uprav_cas(item['created_on'])
                alert = 'black'
                if(item['temperature']>30 or item['temperature']<0):
                    alert = 'red'
                teplota = round(item['temperature'], 2)
                hodnota = Hodnoty('black', teplota, alert, item['cas'], item['datum'])
                hodnoty.append(hodnota)
            self.render('./black.html',title="Black sensor",hodnoty=hodnoty)
        except FileNotFoundError:
            self.render('./sablona_krize.html', title="Jejda!")
            
class red(tornado.web.RequestHandler):
    
    def get(self):
        try:
            data_out = nacti.load_json_colour(self,'red.json')
            poradi = 0;
            hodnoty = []
            for item in data_out[len(data_out):1:-1]:
                item = json.loads(item)
                item['cas'],item['datum'] = nacti.uprav_cas(item['created_on'])
                alert = 'black'
                if(item['temperature']>30 or item['temperature']<0):
                    alert = 'red'
                teplota = round(item['temperature'], 2)
                hodnota = Hodnoty('red', teplota, alert, item['cas'], item['datum'])
                hodnoty.append(hodnota)
            self.render('./red.html',title="Red sensor",hodnoty=hodnoty)
        except FileNotFoundError:
            self.render('./sablona_krize.html', title="Jejda!")

    
class day1(tornado.web.RequestHandler):
    
    def get(self):
        den = datetime.today()-timedelta(days=1)
        try:
            data_senzoru = nacti.load_json(self,den.strftime("%Y-%m-%d")+".json")
            data = json.loads(data_senzoru)
            senzors = nacti.priprav(self, data)
            
            self.render('./sablona_day1.html', title="1 day ago", senzors=senzors)
        except FileNotFoundError:
            self.render('./sablona_krize.html', title="Jejda!")
        
class day2(tornado.web.RequestHandler):
    
    def get(self):
        den = datetime.today()-timedelta(days=2)
        try:
            data_senzoru = nacti.load_json(self,den.strftime("%Y-%m-%d")+".json")
            data = json.loads(data_senzoru)
            senzors = nacti.priprav(self, data)
        
            self.render('./sablona_day2.html', title="2 days ago", senzors=senzors)
        except FileNotFoundError:
            self.render('./sablona_krize.html', title="Jejda!")
        
class day3(tornado.web.RequestHandler):
    
    def get(self):
        den = datetime.today()-timedelta(days=3)
        try:
            data_senzoru = nacti.load_json(self,den.strftime("%Y-%m-%d")+".json")
            data = json.loads(data_senzoru)
            senzors = nacti.priprav(self, data)

            self.render('./sablona_day3.html', title="3 days ago", senzors=senzors)
        
        except FileNotFoundError:
            self.render('./sablona_krize.html', title="Jejda!")
        
class day4(tornado.web.RequestHandler):
    
    def get(self):
        den = datetime.today()-timedelta(days=4)
        try:
            data_senzoru = nacti.load_json(self,den.strftime("%Y-%m-%d")+".json")
            data = json.loads(data_senzoru)
            senzors = nacti.priprav(self, data)
        

            self.render('./sablona_day4.html', title="4 days ago", senzors=senzors)
        
        except FileNotFoundError:
            self.render('./sablona_krize.html', title="Jejda!")
        
class day5(tornado.web.RequestHandler):
    
    def get(self):
        den = datetime.today()-timedelta(days=5)
        try:
            data_senzoru = nacti.load_json(self,den.strftime("%Y-%m-%d")+".json")
            data = json.loads(data_senzoru)
            senzors = nacti.priprav(self, data)

            self.render('./sablona_day5.html', title="5 days ago", senzors=senzors)
        
        except FileNotFoundError:
            self.render('./sablona_krize.html', title="Jejda!")
        
class day6(tornado.web.RequestHandler):
    
    def get(self):
        den = datetime.today()-timedelta(days=6)
        try:
            data_senzoru = nacti.load_json(self,den.strftime("%Y-%m-%d")+".json")
            data = json.loads(data_senzoru)
            senzors = nacti.priprav(self, data)
        
            self.render('./sablona_day6.html', title="6 days ago", senzors=senzors)
        
        except FileNotFoundError:
            self.render('./sablona_krize.html', title="Jejda!")
    
        
        
class EchoWebSocket(WebSocketHandler):
    
    def check_origin(self, origin):
        return True
    
    def initialize(self, log):
        self.log = log

    @tornado.gen.coroutine
    def open(self):
        logging.info('Websocket opened')

        def run(*args):
            logging.info('Sending a message to the client...')
            self.write_message(u'Server ready.') 
            

                
    def on_message(self, message):
        global actual_date
        global stats
        global is_changed
        global data_out
        
        # JS se ptá na websocketu na data pomocí stringu JS_PROMPT
        # TODO: změnit na něco (enum?)
        if (str(message) == 'JS_PROMPT'):
            if (is_changed):
                self.write_message(json.dumps(stats))
                is_changed = False    
            else:
                self.write_message('False')
            return
                    
        
        #vynulovani stats, kvuli zmene data
        if actual_date != datetime.strftime(datetime.now(),"%Y-%m-%d"):
            stats = dict()
        
        actual_date = datetime.strftime(datetime.now(),"%Y-%m-%d") #nastaveni aktualniho data
        
        #reagovani na zpravy, vypis do logu
        logging.info('<- '+str(message))
        self.log.append('{:{dfmt} {tfmt}} - {}'.format(
            datetime.now(), message, dfmt='%d.%m.%Y', tfmt='%H:%M:%S'))
        logging.info('-> You said: '+str(message))
        self.write_message(u'You said: {}'.format(message))
        
        #priprava na zobrazeni dat ze senzoru, vypocty min a max hodnot a zaroven vypocet prumerne hodnoty
        data_out = json.loads(message)
        lastheard[data_out['team_name']] = time.time()
        temp = round(data_out['temperature'], 2)
        data_out['temperature'] = temp
        #print(data_out['temperature'])
        if stats == {} or data_out['team_name'] not in stats:
            stats[data_out['team_name']] = {'avg': data_out['temperature'], 'min' : data_out['temperature'], 'max': data_out['temperature'], 'akt' : data_out['temperature'], 'cnt': 1}
        # pokud neni denni zaznam vytvori se novy a udela se sablona z prvnich dat co soubor dostane
        else:
            #print('max', stats[data_out['team_name']]['max'])
            #print('min', stats[data_out['team_name']]['min'])
            #print('avg', stats[data_out['team_name']]['avg'])

            if (stats[data_out['team_name']]['max']) < data_out['temperature']:
                (stats[data_out['team_name']]['max']) = data_out['temperature']
            # porovnavani nove hodnoty v konkretnim tymu, pokud je v souboru mensi nez nove prichozi
            # prepise se v souboru nova maximalni hodnota u dane prichozi barvy
            if (stats[data_out['team_name']]['min']) > data_out['temperature']:
                (stats[data_out['team_name']]['min']) = data_out['temperature']
            # porovnavani nove hodnoty v konkretnim tymu, pokud je v souboru vetsi nez nove prichozi
            # prepise se v souboru nova minimalni hodnota u dane prichozi barvy
        
            (stats[data_out['team_name']]['avg']) = ((stats[data_out['team_name']]['avg']*stats[data_out['team_name']]['cnt'])+data_out['temperature'])/(stats[data_out['team_name']]['cnt']+1)
            temp = round(stats[data_out['team_name']]['avg'], 2)
            stats[data_out['team_name']]['avg'] = temp
            (stats[data_out['team_name']]['cnt']) += 1
            #print('max', stats[data_out['team_name']]['max'])
            #print('min', stats[data_out['team_name']]['min'])
            #print('avg', stats[data_out['team_name']]['avg'])
        # spocteni prumeru ((prumer(avg)*celkovy pocet(cnt))+(nova prijata teplota(temperature)))/(celkovy pocet(cnt)+1)
        # pricte count +1 do souboru - pro pocitani prumeru
        #date = datetime.strptime(data_out['created_on'], '%Y-%m-%dT%H:%M:%S.%f')
        (stats[data_out['team_name']]['akt']) = data_out['temperature']
        is_changed = True # TODO: možná změnit
        
        
        
    def on_close(self):
        logging.info('Websocket closed')
    



if __name__ == '__main__':
    #IOLoop.current().stop()
    log = []

    # Handlers (access points)
    app = TornadoApplication([
        (r'/', MainHandler, {'log': log}),
        ('/sablona_day1.html',day1),
        ('/sablona_day2.html',day2),
        ('/sablona_day3.html',day3),
        ('/sablona_day4.html',day4),
        ('/sablona_day5.html',day5),
        ('/sablona_day6.html',day6),
        ('/pink.html',pink),
        ('/orange.html',orange),
        ('/blue.html',blue),
        ('/black.html',black),
        ('/green.html',green),
        ('/yellow.html',yellow),
        ('/red.html',red),
        (r'/websocket', EchoWebSocket, {'log': log}),
        (r'/(.*)', StaticFileHandler, {
            'path': join_path(dirname(__name__), 'assets')}),
    ])
    
    # Port
    TORNADO_PORT = 8881
    app.listen(TORNADO_PORT)
    
    # Start the server
    IOLoop.current().start()
    

