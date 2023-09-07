#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import nest_asyncio
nest_asyncio.apply()

import paho.mqtt.client as mqtt
import json
import requests
from datetime import datetime
import asyncio
import websockets
from time import sleep

SERVER = '147.228.124.230'  # RPi
TOPIC = 'ite/#'
teamUUID = '18e75f4e-daea-4c95-bf12-4a7b6936ad45'
sensorUUID = "d7755342-65cc-4cd3-a6b4-ae0a495c3885"
url_store_measurements = 'https://uvb1bb4153.execute-api.eu-central-1.amazonaws.com/Prod/measurements'
url_create_alerts = 'https://uvb1bb4153.execute-api.eu-central-1.amazonaws.com/Prod/alerts'
stav = True
stats = {}
stav_aimtec = True

async def test(data_out):
    print('jsem v Testu')
    async with websockets.connect('ws://localhost:8881/websocket') as websocket:
        await websocket.send(json.dumps(data_out))
        response = await websocket.recv()
        #print(data_out)

      




    # The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, mid, qos):
    print('Connected with result code qos:', str(qos))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(TOPIC)
    


def sort_it(data_out):
    dictionary_teams = {'yellow': "yellow.json", 'green':"green.json",'red':"red.json",'blue':"blue.json",'black':"black.json",'pink':"pink.json",'orange':"orange.json"}
    color = data_out['team_name']
    file_name = dictionary_teams[color]
    print(file_name)
    return file_name

        
def write_to_json(data_out,file_name,mode):    
    fh = open(file_name, mode)
    fh.write(json.dumps(data_out)+'\n')
    
    fh.close()
    
def get_stats(teamName, date):
    if stats == {} or teamName not in stats:
        return False
    else:
        return stats[teamName]
    
    
def send_alert(data_out):
    date = datetime.strptime(data_out['created_on'], '%Y-%m-%dT%H:%M:%S.%f')
    output_data = { 
        "createdOn": date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"+02:00",
        "sensorUUID": sensorUUID,
        "temperature": data_out['temperature'], 
        "highTemperature": 30,
        "lowTemperature": 0,
    }
    Headers = {'teamUUID': teamUUID, 'Content-Type': 'application/json'}
    
    response = requests.post(url = url_create_alerts, data = json.dumps(output_data), headers=Headers)
            
    print("Status code: ", response.status_code)
    response_Json = response.json()
    print("Printing Post JSON data")
    print(response_Json )

    
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global stav
    global stav_aimtec
    if (msg.payload == 'Q'):
        client.disconnect()
    print(msg.payload)  
    try:
        data_out=json.loads(msg.payload)
    except ValueError:
        print('chyba, necitelny senzor')
        return
    try:
        data_out['stav_aimtec'] = stav_aimtec
        asyncio.get_event_loop().run_until_complete(test(data_out))
    except OSError:
        print('nepodarilo se odeslat data!')
        
    
    file_name = sort_it(data_out)
    write_to_json(data_out,file_name,"a")
    
    if get_stats(data_out['team_name'], data_out['created_on']) == False:
        stats[data_out['team_name']] = {'avg': data_out['temperature'], 'min' : data_out['temperature'], 'max': data_out['temperature'], 'akt' : data_out['temperature'], 'cnt': 1}
        # pokud neni denni zaznam vytvori se novy a udela se sablona z prvnich dat co soubor dostane
    else:
        if (stats[data_out['team_name']]['max']) < data_out['temperature']:
            (stats[data_out['team_name']]['max']) = data_out['temperature']
            # porovnavani nove hodnoty v konkretnim tymu, pokud je v souboru mensi nez nove prichozi
            # prepise se v souboru nova maximalni hodnota u dane prichozi barvy
        if (stats[data_out['team_name']]['min']) > data_out['temperature']:
            (stats[data_out['team_name']]['min']) = data_out['temperature']
            # porovnavani nove hodnoty v konkretnim tymu, pokud je v souboru vetsi nez nove prichozi
            # prepise se v souboru nova minimalni hodnota u dane prichozi barvy
        (stats[data_out['team_name']]['avg']) = ((stats[data_out['team_name']]['avg']*stats[data_out['team_name']]['cnt'])+data_out['temperature'])/(stats[data_out['team_name']]['cnt']+1)
        (stats[data_out['team_name']]['cnt']) += 1
        # spocteni prumeru ((prumer(avg)*celkovy pocet(cnt))+(nova prijata teplota(temperature)))/(celkovy pocet(cnt)+1)
        # pricte count +1 do souboru - pro pocitani prumeru
    date = datetime.strptime(data_out['created_on'], '%Y-%m-%dT%H:%M:%S.%f')
    
    file_name = date.strftime("%Y-%m-%d")+".json"
    # vytvoreni souboru podle konkretniho data v danem formatu .json
    write_to_json(stats,file_name,"w")
    # zapsani do souboru
            
    if(data_out['team_name']) == 'pink':   # odesilani nasich dat
            output_data = {
            "createdOn": date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"+02:00",
            "sensorUUID": sensorUUID,
            "temperature": "{:.{}f}".format(data_out['temperature'], 1), 
            "status": "TEST"
            }
            # data dle specifikace API
            
            Headers = {'teamUUID': teamUUID, 'Content-Type': 'application/json'}
            # Headers dle specifikace API
            response = requests.post(url = url_store_measurements, data = json.dumps(output_data), headers=Headers)
            stav_aimtec = True
            if(response.status_code is not 200):
                stav_aimtec = False
            print("Status code: ", response.status_code)
            response_Json = response.json()
            print("Printing Post JSON data")
            print(response_Json )
            # vypis odpovedi na pozadavek do konzole
            if(data_out['temperature']<30 and data_out['temperature']>0):
                stav = True
                #print(stav)
        
            if((data_out['temperature']>30 or data_out['temperature']<0) and stav == True):
                send_alert(data_out)
                #print("mel bys poslat alert!!")
                stav = False
                #print(stav)
    
    
    '''print(msg.topic, msg.qos, msg.payload)'''

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.username_pw_set('mqtt_student', password='pivo')

    client.connect(SERVER, 1883, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and
    # a manual interface.
    client.loop_forever()


if __name__ == '__main__':
    main()


# In[ ]:





# In[ ]:




