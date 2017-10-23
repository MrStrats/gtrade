import GDAX

# This file separates the user's private data from the trading code

# USER API / ACCOUNTS
authClient = GDAX.AuthenticatedClient('Unique 32 character account #', 'Account Key #', 'final account #')
ethaccount = 'GDAX ETH WALLET #'
usdaccount = 'GDAX USD WALLET #' 



# GET ACCOUNT IDS

"""
account = 0
while True:
        try:
                if (authClient.getAccounts()[account].get('currency') == 'USD') or (authClient.getAccounts()[account].get('currency') == 'ETH'):
                        print authClient.getAccounts()[account].get('currency')
                        print authClient.getAccounts()[account].get('id')
                account = account + 1
        except:
                exit()

"""