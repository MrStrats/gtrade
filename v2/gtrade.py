import gdax, time, math, sys

################################################################################################
## API

publicClient = gdax.PublicClient()

# USER API / ACCOUNTS
# key, b64secret, passphrase
authClient = gdax.AuthenticatedClient('x', 'x', 'x')


################################################################################################
## FUNCTIONS

# Defining buy function
def gtrade_buy(inmarket, inprice, insize): #'ETH-USD'
    authClient.buy(price=inprice, size=insize, product_id=inmarket)

# Defining sell function
def gtrade_sell(inmarket, inprice, insize): #'ETH-USD'
    authClient.sell(price=inprice, size=insize, product_id=inmarket)

################################################################################################
## FUNCTIONS

def gtrade_printMenu():
        print("--------------------------------------------------------------------------")
        print("""
    * MENU *

    1a |  Place order (NOT READY)
    1b |  Show open orders
    1c |  Cancel all orders

    2a  |  Spread Sell Orders
    2b  |  Spread Buy Orders

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
            market = input("Market (BTC-USD):  ")
            quantity = input("Input quantity:  ")       
            order = input("limit or market order?  ")

            # ask if you want to designate specific rate
            if order == "limit":
                rate = input("Rate? (leave blank for auto)  ")
            
            # place orders
            try:
                ticker = bittrex.get_market_summaries()["result"]

                # function to find bid or ask
                def findBidAsk(mkt, BidorAsk):
                    for c in ticker: # for coin
                        if c["MarketName"] == mkt: # if market matches
                            if BidorAsk == "Bid":
                                rate = c['Bid'] + 0.00000001 # take bid and add incremental  
                            elif BidorAsk == "Ask":
                                rate = c['Ask'] - 0.00000001 # take ask and remove incremental   
                            return rate

                if order == "limit":                 
                    if side == "buy":
                        # change rate to auto if necessary
                        if rate == "":
                            rate = findBidAsk(market, "Bid")
                        bittrex.buy_limit(market, quantity, rate) # limit buy
                        print("\nOrder placed")
                    else:
                        # change rate to auto if necessary
                        if rate == "":
                            rate = findBidAsk(market, "Ask")
                        bittrex.sell_limit(market, quantity, rate) # limit sell
                        print("\nOrder placed")
                elif order == "market":
                    if side == "buy":
                        bittrex.buy_market(market, quantity) # market buy
                        print("\nOrder placed")
                    else:
                        bittrex.sell_market(market, quantity) # market sell
                        print("\nOrder placed")
                else:
                    print("\nCancelled")
            except:
                print("API ERROR")
        else:
            print("\nCancelled")

    ###############################################################################################
    # OPEN ORDERS
    elif choice == "1b":
        print("\n* OPEN ORDERS *\n")
        orders = authClient.get_orders()
        try:
            if orders[0]:
                if 'id' in orders[0][0]:
                    for o in orders[0]:
                        print("created: " + o["created_at"])
                        print("side: " + o["side"])
                        print("price: " + o["price"] + o['product_id'])
                        print("size: " + o["size"])
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
                orders = authClient.get_orders()
                for o in orders[0]:
                    authClient.cancel_order(o['id'])
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
            accounts = authClient.get_accounts()
            for a in accounts:
                if a['currency'] == currency:
                    return float(a['available'])

        low = float(input("Low:  "))
        high = float(input("High:  "))
        min_currency = float(input("Minimum " + currency + " to sell:  "))
        sleep_sec = float(input("Sleep between orders (sec):  "))

        try:
            '''
            orders = authClient.get_orders()
            if orders[0]:
                if 'id' in orders[0][0]:
                    print("\nCancelling existing orders...")
                    authClient.cancel_all(product=currency+'-USD')
                    time.sleep(5)
                    authClient.cancel_all(product=currency+'-USD')
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
                    gtrade_sell(currency+'-USD', round(p, 2), round(amount, 8))
                    print("#" + str(n) + " - " + str(round(amount, 8)) + " sold at " + str(round(p, 2)))
                    time.sleep(sleep_sec)
                    n += 1

            else:
                print("\nNot enough coin to sell...")
        except:
            e = sys.exc_info()[0]
            print("\nAPI ERROR: " + e)

    ###############################################################################################
    # SPREAD BUY ORDERS
    elif choice == "2b":
        print("\n* SPREAD BUY ORDERS *\n")
        currency = input("Currency? (e.g. 'BTC')  ")

        def available_USD():
            accounts = authClient.get_accounts()
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
                    gtrade_buy(currency+'-USD', p, coinPerTx_real)
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
    # TESTING
    elif choice == "z.":
        try:
            gtrade_sell('ETH-USD', '400.12', '.51231234')
            time.sleep(1)
            gtrade_sell('ETH-USD', '401.12', '.51251234')
        except:
            e = sys.exc_info()[0]
            print("\nAPI ERROR: " + e)

    ###############################################################################################
    # SHOW MENU
    elif choice == "?":
        gtrade_printMenu()

    ###############################################################################################
    # SHOW MARKET SUMMARY
    elif choice == "~":
        try:
            accounts = authClient.get_accounts()
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

# repeat the inputs
while True:
    keeprunning()