import GDAX, datetime, time, gtrade_api
import numpy as np
from gtrade_api import *

### SET THESE VARIABLES
trade = 'ON'
buyat = 211.52
sellat = 210.56

buyfee = .003
requestrate = 1 # seconds, how often GDAX is pinged for data    THIS IS THE SPEED OF PULLS
terminalupdates = 0 # minutes, how often you want a terminal update
###

### CODE STARTS HERE ###############################################################################################################

# setting variables
publicClient = GDAX.PublicClient()

# starting counters
numtrades = 0 # trade counter
runseconds = 0 # program run counter (seconds)

# Defining buy function
def gtradebuy(price, size):
        buyParams = {
        'price': price, #USD
        'size': size,
        'product_id': 'ETH-USD'  #CHANGE!!
        }
        gtrade_api.authClient.buy(buyParams)

# Defining sell function
def gtradesell(price, size):
        sellParams = {
        'price': price, #USD
        'size': size,
        'product_id': 'ETH-USD'   #CHANGE!!
        }
        gtrade_api.authClient.sell(sellParams)

# function to check if time for terminal update
def timeforterminalupdate():
        if terminalupdates == 0:
                return True
        elif (runseconds*10)%(terminalupdates*60*10) == 0:
                return True

# function to pull current time
def now():
        now = datetime.datetime.now()
        return str(now.strftime("%a")) + " " + str(now.hour) + ":" + str(now.minute).zfill(2) + ":" + str(now.second).zfill(2) 

# initial terminal comments
for i in range(100):
    print ("")
print ("""
          __                 __    
   ____ _/ /__________ _____/ /__  
  / __ `/ __/ ___/ __ `/ __  / _ \ 
 / /_/ / /_/ /  / /_/ / /_/ /  __/ 
 \__, /\__/_/   \__,_/\__,_/\___/  
/____/                             

""")
print ("Initial Settings:")
print ("- Buy at " + str (round(buyat,2)))  # This makes sure every "buyat" is rounded off so we have the same number of precision in decimal points
print ("- Sell at " + str (round(sellat,2))) # This makes sure every "sellat" is rounded off so we have the same number of precision in decimal points
print ("- Trading rate of " + str (requestrate) + " seconds") # Pick the speed of all requests
print ("- Terminal updates every " + str (terminalupdates) + " minutes")  #
print ("_" * 40)
print ("")

#gtrade_api.authClient.cancelOrders(product_id="ETH-USD") # cancel all orders






print ("""
# core trading engine
if trade == 'ON':
        while True: # runs in continuous loop
                bid = publicClient.getProductTicker(product="ETH-USD").get('bid') #pulls highest bid
                ask = publicClient.getProductTicker(product="ETH-USD").get('ask') #pulls lowest ask
                try:
                        orders = gtrade_api.authClient.getOrders() #attempts to pull open orders
                        orderside = orders[0][0].get('side') #attempts to pull order "side", i.e. buy/sell
                except: # if try fails, do this...
                        fills = gtrade_api.authClient.getFills(productId="ETH-USD")
                        fillside = fills[0][0].get('side') #get the 'side' of the last order filled
                        if fillside == 'buy': # if the last order filled was a buy, execute sell order
                                ethquantity = gtrade_api.authClient.getAccount(gtrade_api.ethaccount).get('available') # pull ETH available in account
                                ethquantity = float(ethquantity) * (1-buyfee)
                                ethquantity = round(ethquantity,8)
                                gtradesell(round(sellat,2),ethquantity) # post sell order
                                print (now() + " - BOUGHT " + str (round(float(fills[0][0].get("size")),2)) + " at " + str (round(float(fills[0][0].get("price")),2)) + " - Now selling " + str (round(ethquantity,2)) + " at " + str (sellat))
                                numtrades = numtrades + 1
                        elif fillside == 'sell': # if the last order filled was a sell, execute buy order
                                usdquantity = gtrade_api.authClient.getAccount(gtrade_api.usdaccount).get('available') # pull USD available in account
                                buyquantity = (float(usdquantity)*(1-buyfee)) / round(buyat,2)
                                buyquantity = round(buyquantity,8)
                                gtradebuy(round(buyat,2),buyquantity) # post buy order
                                print (now() + " - SOLD " + str (round(float(fills[0][0].get("size")),2)) + " at " + str (round(float(fills[0][0].get("price")),2)) + " - Now buying " + str (round(buyquantity,2)) + " at " + str (buyat))
                                numtrades = numtrades + 1
                        else:
                                print ("ERROR")
                else: # if try succeeds, do this...
                        if orderside == 'buy' and timeforterminalupdate() == True: # if it's a buy order and time for a terminal update
                                print (now() + " - " + str (numtrades) + " trades - Buying at " + str (float(orders[0][0].get("price"))) + " vs " + bid)
                        elif orderside == 'sell' and timeforterminalupdate() == True: # if it's a sell order and time for a terminal update
                                print (now() + " - " + str (numtrades) + " trades - Selling at " + str (float(orders[0][0].get("price"))) + " vs " + ask)
                time.sleep(requestrate) # pause program for given time
                runseconds += requestrate # add run seconds to counter


                """)