


###############################
##### SET THESE VARIABLES #####
###############################

# Use on /off
# Ex: 
# bitcoinTrading = "on"
# bitcoinTrading = "off"

bitcoinTrading = "OFF"
ethereumTrading = "OFF"
litecoinTrading = "OFF"

coinusd = "COIN-USD"

###############################
######## STOP SETTING #########
###############################


# If coins are on, find prices and store info... Ready to send to main program for processing...

if bitcoinTrading == "ON":
    coinusd = "BTC-USD"

if ethereumTrading == "ON":
    coinusd = "ETH-USD"

if litecoinTrading == "ON":
    coinusd = "LTC-USD"


print (coinusd)