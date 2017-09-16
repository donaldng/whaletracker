#!/usr/bin/env python3
from pymongo import MongoClient
import time, json, os, sys, requests

db = MongoClient().wtracker.trades

def lookback(sec):
    t = int(time.time())-sec

    print("\n[ Whaletracker ]\n")
    print("Tracking trades over past %s." % convert_to_time(sec))
    if global_price:
        print("We are currently following %s coin, priced at %s%s." % (pair, currency, global_price))

    cur = db.find( { 'ts' : { '$gt' : 60 }, 'pair': pair } )
    tps = round(cur.count()/60, 4)
    print("\nTPS: %s" % tps)

    min_amount = 99
    limit = 5

    top = {}

    for x in ["buy", "sell"]:
        op = "$gt"

        if x == "sell":
            op = "$lt"
            min_amount *= -1

        top_trades = db.aggregate([
                                { "$match": { 'ts' : { '$gt' : t }, 'amount': { op : min_amount }, 'pair': pair } },
                                { "$group": {"_id": "$amount", "count": { "$sum": 1 }, "avgPrice": { "$avg": "$price" } }},
                                { "$match": { 'count': {'$gt': 1}  }},
                                { "$sort": { "count": -1 } },
                                { "$limit": limit }
                            ])



        print("\n===========================")
        print("===\t  Top %s\t===" % x.upper())
        print("===========================\n")

        c=0
        total = 0    
        for x in top_trades:
            c+=1
            amount = x["_id"]
            count = x["count"]     
            avgPrice = round(float(x["avgPrice"]), 6)

            if global_price:
                amount_sum = global_price * float(amount) * int(count)
                total += amount_sum

            print("%s. %s x %s (%s)" % (c, avgPrice, amount, count))

        if global_price and abs(total):
            print("\nTotal: %s%s" % (currency, abs(round(total,2))))


def spawn_tracker():
    pid=os.fork()
    if pid==0:
        ppid = os.getpid()
        os.system("nohup python3 tracker.py %s %s >/dev/null 2>&1 &" % (pair, ppid))
        exit()


def get_market_price(pair):
    if len(pair)==6:
        fsym = pair[:3]
        tsym = pair[-3:]
        url = "https://min-api.cryptocompare.com/data/price?fsym=%s&tsyms=%s" % (fsym, tsym)

        try:
            return float(requests.get(url).json()[tsym])
        except:
            print("Can't find %s from coinmarketcap!" % pair)

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
    global pair
    global currency

    # Take 1st param as pair
    pair = str(sys.argv[1]).upper()

    # Default lookback value
    lookback_seconds = 3600

    # Take 2nd parameter as lookback value
    if len(sys.argv) == 3:
        lookback_seconds = int(sys.argv[2])

    global_price = get_market_price(pair)

    if global_price:

        spawn_tracker()        
        
        currency = '$' if pair[-3:] == 'USD' else '฿'
        
        while True:
            os.system("clear")
            lookback(lookback_seconds)
            print("\nprocessing... %s" % str(time.time())[-3:])
            time.sleep(1)
    else:
        print("Error: cannot find %s pair." % pair)
        sys.exit()


if __name__== "__main__":
    if len(sys.argv) > 1:
        main()

    print("Error: 'crypto pair' parameter required! E.g. BTCUSD or ETHBTC")

