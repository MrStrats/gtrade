import gdax # GDAX API
import time # for sleep
import math # for math functions
import sys # for printing errors
import os # for checking paths
import bcrypt # hashing
import pickle # file saving/loading
from cryptography.fernet import Fernet # encrypting


####################################################################
####################################################################
## USER CREDENTIAL CHECK AND ENCRYPTION

# function to generate repeating string from password to use as key
def stringRepeat(string, length):
    if len(string) < length - 1: # check if repeating is necessary
        while len(string) < length - 1: # continue while length is needed
            for c in string: # iterate through character
                string += c # add character
                if len(string) >= length - 1: # break when length is met
                    break
    string += "="
    return string

# Ask for user
user_name = input("\nEnter Login Name:  ")

# Try opening pickle file and pulling variables
new_user = False
try:   
    # gets you a path that works across operating systems
    dirpath = os.path.dirname(__file__)
    filename = os.path.join(dirpath, 'data/' + user_name + '.pckl')
    with open(filename, 'rb') as f: 
        hashed_password, api_key_encrypted, api_secret_encrypted, api_pass_encrypted = pickle.load(f)
except:
    new_user = True

# if can open, ask for pass
# if can't open, create new key, secret, pass
# pass is hashed, key/secret is encrypted
if new_user == True:
    # get user inputs
    print("\n*NEW USER*")
    api_key = input("Enter API Key:  ")
    if not api_key:
        exit()
    api_secret = input("Enter API Secret:  ")
    if not api_secret:
        exit()
    api_pass = input("Enter API Passphrase:  ")
    if not api_pass:
        exit()

    # get password <= 44 - 1 characters (length of fernet key)
    while True:
        password_store = input("\nEnter Login Password:  ")
        if len(password_store) <= 44 - 1:
            break

    # Hash password
    hashed_password = bcrypt.hashpw(str.encode(password_store), bcrypt.gensalt()) # Hash password with a randomly-generated salt

    # encode api key, secret
    key = str.encode(stringRepeat(password_store, 44)) # length of fernet key
    api_key_encrypted = Fernet(key).encrypt(str.encode(api_key))
    api_secret_encrypted = Fernet(key).encrypt(str.encode(api_secret))
    api_pass_encrypted = Fernet(key).encrypt(str.encode(api_pass))

    # check if save directory exists
    if not os.path.exists("data"):
        os.makedirs("data")

    # Save the objects:
    # Gets you a path that works across operating systems
    dirpath = os.path.dirname(__file__)
    filename = os.path.join(dirpath, 'data/' + user_name + '.pckl')
    with open(filename, 'wb') as f:
        pickle.dump([hashed_password, api_key_encrypted, api_secret_encrypted, api_pass_encrypted], f)

    access = True # allow access
else:
    # Existing user, check password
    password_attempt = input("Enter Login Password:  ")

    # Check that an unhashed password matches one that has previously been hashed
    if bcrypt.checkpw(str.encode(password_attempt), hashed_password):
        # decrypt api data
        key = str.encode(stringRepeat(password_attempt, 44)) # fernet key
        api_key = Fernet(key).decrypt(api_key_encrypted).decode()
        api_secret = Fernet(key).decrypt(api_secret_encrypted).decode()
        api_pass = Fernet(key).decrypt(api_pass_encrypted).decode()

        access = True
    else:
        print("\n* Invalid Password *")
        access = False


####################################################################
####################################################################
## ACCESS GRANTED / INITIAL SCREEN & MENU

if access == True:

    # GDAX USD/BTC TICKER
    gdax_public = gdax.PublicClient()
    usdperbtc = float(gdax_public.get_product_ticker(product_id="BTC-USD")["price"])

    # USER API / ACCOUNTS
    # key, b64secret, passphrase
    gdax_authClient = gdax.AuthenticatedClient(api_key, api_secret, api_pass)


    ################################################################################################
    ## FUNCTIONS


    ################################################################################################
    ## FUNCTIONS

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

    def gtrade_printMenu():
            print("--------------------------------------------------------------------------")
            print("""
        * MENU *

        1a |  Place order (needs to be tested)
        1b |  Show open orders
        1c |  Cancel all orders

        2a |  Spread Sell Orders
        2b |  Spread Buy Orders (evenly by size, uneven by value)
        2c |  Spread Buy Orders (evenly by value, uneven by size)

        3a |  Auto Trade (Ping Method)
        3b |  Auto Trade (Range Bound) *Not Working*

        z. |  TESTING
               
        ?  |  Menu
        ~  |  Market Summary

        exit
            """)

    gtrade_printMenu()

    ######################################################################################################################
    ## CHECK INPUTS

    def keeprunning():
        print("--------------------------------------------------------------------------")
        choice = input("#:  ")

        ###############################################################################################
        # PLACE ORDER
        if choice == "1a":
            print("\n* PLACE ORDER *\n")
            side = input("buy or sell?  ")
            if side == "buy" or side == "sell":
                market = input("Market (e.g. 'BTC-USD'):  ")
                volume = input("Input volume:  ")       
                order = input("limit or market order?  ")

                # ask if you want to designate specific rate
                if order == "limit":
                    rate = input("Rate? (leave blank for auto)  ")
                
                # place orders
                try:
                    # grab tickers
                    ticker = gdax_public.get_product_ticker(market)

                    # Limit orders
                    if order == "limit":                 
                        if side == "buy":
                            # If rate = auto, find bid
                            if rate == "":
                                rate = ticker['bid']
                            gdax_authClient.buy(price=round(rate, 2), size=round(volume, 8), product_id=market, post_only=True)
                            print("\nOrder placed")
                        else:
                            # If rate = auto, find ask
                            if rate == "":
                                rate = ticker['ask']
                            gdax_authClient.sell(price=round(rate, 2), size=round(volume, 8), product_id=market, post_only=True)
                            print("\nOrder placed")
                    # Market order
                    elif order == "market":
                        if side == "buy":
                            rate = ticker['ask'] * 1.1 # high ask to ensure execution
                            gdax_authClient.buy(price=round(rate, 2), size=round(volume, 8), product_id=market)
                            print("\nOrder placed")
                        else:
                            rate = ticker['bid'] * .9 # low bid to ensure execution
                            gdax_authClient.sell(price=round(rate, 2), size=round(volume, 8), product_id=market)
                            print("\nOrder placed")
                    else:
                        print("\nCancelled")
                # Error
                except:
                    e = sys.exc_info()[0]
                    print("\nAPI ERROR: " + e)
            # If not buy or sell, cancel
            else:
                print("\nCancelled")

        ###############################################################################################
        # OPEN ORDERS
        elif choice == "1b":
            print("\n* OPEN ORDERS *\n")
            orders = gdax_authClient.get_orders()
            try:
                if orders[0]:
                    if 'id' in orders[0][0]:
                        for o in orders[0]:
                            print("created: " + o["created_at"])
                            print("side: " + o["side"])
                            print("price: " + o["price"] + o['product_id'])
                            print("size: " + o["size"])
                            print("type: " + o["type"])
                            print("time in force: " + o["time_in_force"])
                            print("post only: " + str(o["post_only"]))
                            print()
                else:
                    print("No orders")
            except:
                e = sys.exc_info()[0]
                print("\nAPI ERROR: " + e)

        ###############################################################################################
        # CANCEL ORDERS
        elif choice == "1c":
            print("\n* CANCEL ALL ORDERS *\n")
            if input("Are you sure you want to cancel all orders (Y/N):  ") == "Y":
                try:
                    print("\nCancelling any existing orders...")
                    orders = gdax_authClient.get_orders()
                    for o in orders[0]:
                        gdax_authClient.cancel_order(o['id'])
                        print(o['product_id'] + " cancelled")
                    print("All orders cancelled or none to cancel")
                except:
                    print("\nAPI ERROR")
            else:
                print("\nNo action taken")    

        ###############################################################################################
        # SPREAD SELL ORDERS
        elif choice == "2a":
            print("\n* SPREAD SELL ORDERS *\n")
            currency = input("Currency? (e.g. 'BTC')  ")

            def available_currency():
                accounts = gdax_authClient.get_accounts()
                for a in accounts:
                    if a['currency'] == currency:
                        return float(a['available'])

            low = float(input("Low:  "))
            high = float(input("High:  "))
            min_currency = float(input("Minimum " + currency + " to sell:  "))
            sleep_sec = float(input("Sleep between orders (sec):  "))

            try:
                '''
                orders = gdax_authClient.get_orders()
                if orders[0]:
                    if 'id' in orders[0][0]:
                        print("\nCancelling existing orders...")
                        gdax_authClient.cancel_all(product=currency+'-USD')
                        time.sleep(5)
                        gdax_authClient.cancel_all(product=currency+'-USD')
                        print("Done.")
                '''

                available_currency = available_currency()

                if available_currency >= min_currency:
                    print("\nPlacing orders...")
                    transactions = math.floor(available_currency / min_currency) # round down to integer so amount is always greater than min
                    amount = available_currency / transactions
                    increment = (high - low) / (transactions - 1) # subtract 1 to get right amount of transactions
                    
                    # make price list
                    prices = [low]
                    while transactions > 1:
                        prices.append(prices[len(prices) - 1] + increment)
                        transactions -= 1

                    # trade
                    n = 1
                    for p in prices:
                        gdax_authClient.sell(price=round(p, 2), size=round(amount, 8), product_id=currency+'-USD', post_only=True)
                        print("#" + str(n) + " - " + str(round(amount, 8)) + " sold at " + str(round(p, 2)))
                        time.sleep(sleep_sec)
                        n += 1

                else:
                    print("\nNot enough coin to sell...")
            except:
                e = sys.exc_info()[0]
                print("\nAPI ERROR: " + e)

        ###############################################################################################
        # SPREAD BUY ORDERS #1
        elif choice == "2b":
            print("\n* SPREAD BUY ORDERS *\n")
            currency = input("Currency? (e.g. 'BTC')  ")

            def available_USD():
                accounts = gdax_authClient.get_accounts()
                for a in accounts:
                    if a['currency'] == "USD":
                        return round(float(a['available']),2)

            try:
                # Get and print available USD
                availableUSD = available_USD()
                print("Available to trade:  " + str(availableUSD))

                # Get inputs
                amountToTrade = float(input("\nAmount to trade:  "))
                low = float(input("Buy - Low:  "))
                high = float(input("Buy - High:  "))
                coinPerTx_user = float(input("Min " + currency + " per tx (estimate):  "))
                sleep_sec = float(input("Sleep between orders (sec):  "))

                # Cap amount to trade at amount available
                amountToTrade = availableUSD if amountToTrade > availableUSD else amountToTrade
                
                print ("\nTrading $" + str(amountToTrade) + " worth of BTC between " + str(low) + " - " + str(high))
                time.sleep(5)

                # GDAX fee
                GDAXfee = .0025 # held even for limit orders

                if availableUSD >= coinPerTx_user:
                    print("\nPlacing orders...")
                    avgBuyPrice = round(((high + low) / 2) * (1 + GDAXfee), 2) + .1 # round 2 for usd, average usd buy in, ADD $.1 AS FIX TO LEAVE A LITTLE REMAINING
                    maxCoinToBuy = round(amountToTrade / avgBuyPrice, 8) # round 8 for satoshi, max coin to buy
                    transactions = math.floor(maxCoinToBuy / coinPerTx_user) # total transactions - 1 (missing end point)
                    coinPerTx_real = round(maxCoinToBuy / (transactions + 1), 8) # round 8 for satoshi, real coin per tx
                    increment = (high - low) / transactions # step amount

                    # make price list
                    prices = []
                    for i in range(transactions + 1):
                        p = round(low + (increment * i), 2) # round 2 for usd
                        prices.append(p)
        
                    # trade
                    sumBought = 0
                    for i,p in enumerate(prices):  
                        gdax_authClient.buy(price=p, size=coinPerTx_real, product_id=currency+'-USD', post_only=True)
                        usdBought = round((p * coinPerTx_real) * (1 + GDAXfee), 2) # amount of usd bought
                        sumBought = round(sumBought + usdBought, 2) # total bought
                        print("#" + str(i+1) + " - " + str(coinPerTx_real) + " bought at " + str(p) + " for " + str(usdBought) + " - " + str(round(amountToTrade - sumBought, 2)))
                        time.sleep(sleep_sec)

                else:
                    print("\nNot enough coin to buy...")
            except:
                e = sys.exc_info()[0]
                print("\nAPI ERROR: " + e)

        ###############################################################################################
        # SPREAD BUY ORDERS #2
        elif choice == "2c":
            print("\n* SPREAD BUY ORDERS *\n")
            currency = input("Currency? (e.g. 'BTC')  ")

            def available_USD():
                accounts = gdax_authClient.get_accounts()
                for a in accounts:
                    if a['currency'] == "USD":
                        return round(float(a['available']),2)

            try:
                # Get and print available USD
                availableUSD = available_USD()
                print("Available to trade:  " + str(availableUSD))

                # Get inputs
                amountToTrade = float(input("\nAmount to trade:  "))
                low = float(input("Buy - Low:  "))
                high = float(input("Buy - High:  "))
                coinPerTx_user = float(input("Min " + currency + " per tx (estimate):  "))
                sleep_sec = 1

                # Cap amount to trade at amount available
                amountToTrade = availableUSD if amountToTrade > availableUSD else amountToTrade

                # GDAX fee
                GDAXfee = .0025 # held even for limit orders

                # Calculate       
                minBuyPrice = high * coinPerTx_user * (1 + GDAXfee) + .1 # minimum buyin, ADD $.1 AS FIX TO LEAVE A LITTLE REMAINING
                transactions = math.floor(amountToTrade / minBuyPrice)
                increment = round((high - low) / (transactions - 1), 2)

                # make price list
                prices = []
                for i in range(transactions):
                    p = round(low + (increment * i), 2) # round 2 for usd
                    prices.append(p)
                  
                # Trade
                print ("\nTrading $" + str(amountToTrade) + " worth of BTC between " + str(low) + " - " + str(high))
                time.sleep(5)
                print("\nPlacing", transactions, "orders...")

                sumBought = 0
                for i,p in enumerate(prices):  
                    size = round( (high * coinPerTx_user) / p, 8) # round 8 for satoshi
                    gdax_authClient.buy(price=p, size=size, product_id=currency+'-USD', post_only=True)
                    usdBought = round((p * size) * (1 + GDAXfee), 2) # amount of usd bought
                    sumBought = round(sumBought + usdBought, 2) # total bought
                    print("#" + str(i+1) + " - " + str(size) + " bought at " + str(p) + " for " + str(usdBought) + " - " + str(round(amountToTrade - sumBought, 2)))
                    time.sleep(sleep_sec)
                
            except:
                print("ERROR")


        ###############################################################################################
        # AUTO TRADE (Ping Method)
        elif choice == "3a":
            print("\n* AUTO TRADE (Ping Method) *\n")

            try:
                print ("_" * 30)
                print ("\n GDAX Trade Wallet")
                print ("_" * 30)
                try:
                    accounts = gdax_authClient.get_accounts()
                    for a in accounts:
                        print('Currency: ' + a['currency'])
                        print('Balance: ' + a['balance'])
                        print('Available: ' + a['available'])
                        print()
                except:
                    print("\nAPI ERROR")
                print ("_" * 30)
        

                currency = input("\nTrade which currency? (e.g. 'BTC'): ")


                def available_currency():
                    accounts = gdax_authClient.get_accounts()
                    for a in accounts:
                        if a['currency'] == currency:
                            return float(a['available'])

                def available_USD():
                    accounts = gdax_authClient.get_accounts()
                    for a in accounts:
                        if a['currency'] == "USD":
                            return round(float(a['available']),2)

                available_currency = available_currency()
                availableUSD = available_USD()
                

                print ("\nChoose the buy and sell points: \n")
                low = round(float(input("     Buy: ")),2)
                high = round(float(input("    Sell: ")),2)

                print ("\n What is that max amount of USD you wish to trade each buy/sell cycle? \n")
                maxCash = round(float(input("     (For Max Leave Blank): ")),2)


                #LOGIC TO FIND PREVIOUS BUY OR SELL AND THEN EXECUTE THE TRADE CYCLE!!!

                #gdax_authClient.buy(price='100', size='1', product_id="BTC-USD")

            except:
                e = sys.exc_info()[0]
                print("\TRADER ERROR: " + e)


            
        

        ###############################################################################################
        # AUTO TRADE (Range Method)
        elif choice == "3b":
            print("\n* AUTO TRADE (Bound Method) *\n")
            currency = input("Currency? (e.g. 'BTC')  ")

        ###############################################################################################
        # TESTING
        elif choice == "z.":
            orders = gdax_authClient.get_orders()
            print(orders)

        ###############################################################################################
        # SHOW MENU
        elif choice == "?":
            gtrade_printMenu()

        ###############################################################################################
        # SHOW MARKET SUMMARY
        elif choice == "~":
            try:
                accounts = gdax_authClient.get_accounts()
                for a in accounts:
                    print('Currency: ' + a['currency'])
                    print('Balance: ' + a['balance'])
                    print('Available: ' + a['available'])
                    print()
            except:
                print("\nAPI ERROR")


        ###############################################################################################
        # EXIT
        elif choice == "exit":
            exit()

    # Repeat the inputs / keep things running
    while True:
        keeprunning()