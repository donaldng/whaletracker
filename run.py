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
        print("We are currently following %s coin, priced at %s%s." % (coin, currency, global_price))
    print("")

    cur = db.find( { 'ts' : { '$gt' : 60 }, 'pair': coin } )
    tps = round(cur.count()/60, 4)
    print("TPS: %s" % tps)

    min_amount = 99
    top = 5

    top_buy = db.aggregate([
                            { "$match": { 'ts' : { '$gt' : t }, 'amount': { '$gt' : min_amount }, 'pair': coin } },
                            { "$group": {"_id": "$amount", "count": { "$sum": 1 }, "avgPrice": { "$avg": "$price" } }},
                            { "$sort": { "count": -1 } },
                            { "$limit": top }
                        ])

    top_sell = db.aggregate([
                            { "$match": { 'ts' : { '$gt' : t }, 'amount': { '$lt' : (min_amount * -1) }, 'pair': coin } },
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
        print("\nTotal: %s%s" % (currency, abs(round(total,2))))

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
        print("\nTotal: %s%s" % (currency, abs(round(total,2))))


def spawn_tracker():
    pid=os.fork()
    if pid==0: # new process
        #print(x)
        ppid = os.getpid()
        os.system("nohup python3 tracker.py %s %s >/dev/null 2>&1 &" % (ppid, coin))
        exit()


def get_market_price(coin):
    if len(coin)==6:
        fsym = coin[:3]
        tsym = coin[-3:]
        url = "https://min-api.cryptocompare.com/data/price?fsym=%s&tsyms=%s" % (fsym, tsym)

        try:
            return float(requests.get(url).json()[tsym])
        except:
            print("Can't find %s from coinmarketcap!" % coin)

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


def main():

    global global_price
    global coin
    global currency

    coin = str(sys.argv[1])

    # Default lookback timeframe will be set to 1 hour.
    lookback_seconds = 3600
    
    if len(sys.argv) == 3:
        lookback_seconds = int(sys.argv[2])

    global_price = get_market_price(coin)

    if global_price:

        spawn_tracker()        
        
        currency = '$' if coin[:-3] == 'USD' else '฿'        
        
        while True:
            os.system("clear")
            lookback(lookback_seconds)
            print("\nprocessing... %s" % str(time.time())[-3:])
            time.sleep(1)
    else:
        print("Error: cannot find %s pair." % coin)
        sys.exit()


if __name__== "__main__":
    if len(sys.argv) > 1:
        main()

    print("Error: 'crypto pair' parameter required! E.g. BTCUSD or ETHBTC")

