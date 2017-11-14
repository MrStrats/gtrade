# Use this file to start the trading program.
# If GDAX goes down for any reason, this code will restart the trading program.

import time
while True: # run in continuous loop
    try:
        import gtrade # try to start trading program
    except:
        time.sleep(60) # if error, sleep for 60 seconds and retry