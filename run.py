#!/usr/bin/env python3
from pymongo import MongoClient
import time, json, os, sys, requests

db = MongoClient().wtracker.trades

def lookback(sec):
    t = int(time.time())-sec
    print("[ Whaletracker ]")
    print("")
    print("Tracking trades over past 24 hours.")
    if global_price:
        print("We are currently following %s coin, priced at $%s." % (coin, global_price))
    print("")

    cur = db.find( { 'ts' : { '$gt' : 60 } } )
    tps = round(cur.count()/60, 4)
    print("TPS: %s" % tps)

    top_buy = db.aggregate([
                            { "$match": { 'ts' : { '$gt' : t }, 'amount': { '$gt' : 0 } } },
                            { "$group": {"_id": "$amount", "count": { "$sum": 1 }}},
                            { "$sort": { "count": -1 } },
                            { "$limit": 5 }
                        ])

    top_sell = db.aggregate([
                            { "$match": { 'ts' : { '$gt' : t }, 'amount': { '$lt' : 0 } } },
                            { "$group": {"_id": "$amount", "count": { "$sum": 1 }}},
                            { "$sort": { "count": -1 } },
                            { "$limit": 5 }
                        ])

    print("")
    print("=================")
    print("===  Top BUY  ===")
    print("=================")
    print("")

    c=0
    total = 0    
    for x in top_buy:
        c+=1
        print("%s. %s (%s)" % (c, x["_id"], x["count"]))
        if global_price:
            total += global_price * float(x["_id"]) * int(x["count"])

    if global_price:
        print("\nTotal: $%s" % abs(total))

    print("")
    print("=================")
    print("=== Top SELL  ===")
    print("=================")
    print("")
    
    c=0
    total = 0
    for x in top_sell:
        c+=1
        print("%s. %s (%s)" % (c, x["_id"], x["count"]))
        if global_price:
            total += global_price * float(x["_id"]) * int(x["count"])

    if global_price:
        print("\nTotal: $%s" % abs(total))


def spawn_tracker():
    pid=os.fork()
    if pid==0: # new process
        #print(x)
        ppid = os.getpid()
        os.system("nohup python3 tracker.py %s >/dev/null 2>&1 &" % ppid)
        exit()


def get_market_price(coin):
    if coin != "":
        url = "https://api.coinmarketcap.com/v1/ticker/%s/" % coin
        
        try:
            return float(requests.get(url).json()[0]["price_usd"])
        except:
            print("Can't find %s from coinmarketcap!" % coin.lower())

    return 0

def main(coin):

    spawn_tracker()

    global global_price
    global_price = get_market_price(coin)

    while True:
        os.system("clear")
        lookback(60*60*24)
        print("\nprocessing... %s" % str(time.time())[-3:])
        time.sleep(1)


if __name__== "__main__":
    coin = ""
    if len(sys.argv) != 1:
        coin = sys.argv[1]

    main(coin)

