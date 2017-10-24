import time
from gtrade_api import *

####
####  ENTER YOUR GDAX ACCOUNT AND RUN THE SCRIPT
####    THE OUTPUT SHOULD BE THEN PASTED INTO THE gtrade_api.py file

# GET ACCOUNT IDS

account = 0
while True:
        try:
                if (authClient.getAccounts()[account].get('currency') == 'USD') or (authClient.getAccounts()[account].get('currency') == 'ETH'):
                        print authClient.getAccounts()[account].get('currency')
                        print authClient.getAccounts()[account].get('id')
                account = account + 1
        except:
                exit()

