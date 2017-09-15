#!/usr/bin/env python3
from pymongo import MongoClient
from websocket import create_connection
import time, json, os, sys

pid = int(sys.argv[1]) if len(sys.argv) != 1 else 0

db = MongoClient().wtracker

ws = create_connection('wss://api.bitfinex.com/ws/')
sub = json.dumps({'event': 'subscribe', 'channel': 'trades', 'pair':'IOTBTC'})
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
        
        data = {'ts':ts, 'price': price,'amount':amount}
        res = db.trades.insert_one(data)

ws.close()