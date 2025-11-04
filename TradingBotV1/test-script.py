from ibapi.client import EClient # send messagest to TWS
from ibapi.wrapper import EWrapper # handles incoming messages
from time import sleep
from threading import Thread # required since can't access app after app.run() therefore need to run app on one thread and run commands on other threads


from config import host, port, client_id

class TradeApp(EWrapper, EClient): 
    def __init__(self): 
        EClient.__init__(self, self)


if __name__ == '__main__':
    app = TradeApp()

    app.connect(host, port, client_id)
    sleep(1)
    
    app_thread = Thread(target=app.run, daemon=True) #daemon kills all threads once app.run is exited
    app_thread.start()

    print("yay")