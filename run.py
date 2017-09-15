#!/usr/bin/env python3
from pymongo import MongoClient
import time, json, os, sys, requests

db = MongoClient().wtracker.trades

def lookback(sec):
    t = int(time.time())-sec

    print("")
    print("[ Whaletracker ]")
    print("")
    print("Tracking trades over past %s." % convert_to_time(sec))
    if global_price:
        print("We are currently following %s coin, priced at $%s." % (coin, global_price))
    print("")

    cur = db.find( { 'ts' : { '$gt' : 60 } } )
    tps = round(cur.count()/60, 4)
    print("TPS: %s" % tps)

    min_amount = 99
    top = 10

    top_buy = db.aggregate([
                            { "$match": { 'ts' : { '$gt' : t }, 'amount': { '$gt' : min_amount } } },
                            { "$group": {"_id": "$amount", "count": { "$sum": 1 }, "avgPrice": { "$avg": "$price" } }},
                            { "$sort": { "count": -1 } },
                            { "$limit": top }
                        ])

    top_sell = db.aggregate([
                            { "$match": { 'ts' : { '$gt' : t }, 'amount': { '$lt' : (min_amount * -1) } } },
                            { "$group": {"_id": "$amount", "count": { "$sum": 1 }, "avgPrice": { "$avg": "$price" } }},                            
                            { "$sort": { "count": -1 } },
                            { "$limit": top }
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
        amount = x["_id"]
        count = x["count"]     
        avgPrice = round(float(x["avgPrice"]), 6)

        if global_price:
            amount_sum = global_price * float(amount) * int(count)
            total += amount_sum

        print("%s. %s x %s (%s)" % (c, avgPrice, amount, count))


    if global_price:
        print("\nTotal: $%s" % abs(round(total,2)))

    print("")
    print("=================")
    print("=== Top SELL  ===")
    print("=================")
    print("")
    
    c=0
    total = 0
    for x in top_sell:
        c+=1
        amount = x["_id"]
        count = x["count"]
        avgPrice = round(float(x["avgPrice"]), 6)  

        if global_price:
            amount_sum = global_price * float(amount) * int(count)
            total += amount_sum

        print("%s. %s x %s (%s)" % (c, avgPrice, amount, count))


    if global_price:
        print("\nTotal: $%s" % abs(round(total,2)))


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

def convert_to_time(seconds):
    d = 0

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    
    str = "%s minutes" % m

    if h:
        str = "%s hours" % h

    elif h >= 24:
        d = divmod(h, 24)
        str = "%s days" % d
    
    return str


def main(coin):

    spawn_tracker()

    global global_price
    global_price = get_market_price(coin)

    while True:
        os.system("clear")
        lookback(60*60)
        print("\nprocessing... %s" % str(time.time())[-3:])
        time.sleep(1)


if __name__== "__main__":
    coin = ""
    if len(sys.argv) != 1:
        coin = sys.argv[1]

    main(coin)

