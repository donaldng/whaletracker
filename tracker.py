#!/usr/bin/env python3
from pymongo import MongoClient
from websocket import create_connection
import time, json, os, sys

try:
    pid = int(sys.argv[2]) if len(sys.argv) == 3 else 0
    pair = sys.argv[1]
except:
    print('Please pass in correct parameter, crypto pair required! E.g. BTCUSD or ETHBTC')

    
db = MongoClient().wtracker

ws = create_connection('wss://api.bitfinex.com/ws/')
sub = json.dumps({'event': 'subscribe', 'channel': 'trades', 'pair':pair})
ws.send(sub)

while True:
    x = json.loads(ws.recv())

    try:
        os.kill(pid, 0)
    except:
        sys.exit()

    if len(x) == 6:
        ts = x[3]
        price = x[4]
        amount = x[5]

        ts = int(float(time.time()))
        
        data = {'ts':ts, 'price': price,'amount':amount, 'pair': pair}
        res = db.trades.insert_one(data)

ws.close()