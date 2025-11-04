from ibapi.client import *
from ibapi.wrapper import *
from ibapi.contract import Contract

from datetime import datetime
from time import sleep
from threading import Thread
import math

from config import host, port, client_id, ib_account

# EClient sends requests to TWS
# EWrapper handles incoming messages
class TradeApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

        # custom attributes
        self.account_balance = math.nan
        self.account_equity = math.nan
        self.portfolio = {}


    # EWrapper Functions
    def updateAccountValue(self, key: str, val: str, currency: str, accountName: str): #retrieves account data
        # print("UpdateAccountValue. Key:", key, "Value:", val, "Currency:", currency, "AccountName:", accountName)


        if key == 'TotalCashBalance' and currency =='BASE':
            self.account_balance = val

        if key == 'NetLiquidationByCurrency' and currency =='BASE':
            self.account_equity = val

    def updatePortfolio(self, contract: Contract, position: Decimal, marketPrice: float, marketValue: float,
                        averageCost: float, unrealizedPNL: float, realizedPNL: float, accountName: str):
        """"
        print("UpdatePortfolio", end=": ")
        print(f"symbol={getattr(contract, 'symbol', None)}, secType={getattr(contract, 'secType', None)}, exchange={getattr(contract, 'exchange', None)} | position={position}, marketPrice={marketPrice}, marketValue={marketValue}, averageCost={averageCost}, unrealizedPNL={unrealizedPNL}, realizedPNL={realizedPNL}, accountName={accountName}")
        """


        self.portfolio[contract.localSymbol] = {
            'position': decimalMaxString(position),
            'marketPrice': floatMaxString(marketPrice),
            'marketValue': floatMaxString(marketValue),
            'averageCost': floatMaxString(averageCost),
            'unrealizedPNL': floatMaxString(unrealizedPNL),
            'realizedPNL': floatMaxString(realizedPNL)
        }
if __name__ == '__main__':
    app = TradeApp()

    app.connect(host, port, client_id)
    sleep(1)

    app_thread = Thread(target=app.run, daemon=True)
    app_thread.start()

    # requesting Account Updates which is then updated in the updateAccountValue
    app.reqAccountUpdates(True, ib_account)

    sleep(1)
    while True:
        current_time = datetime.now()
        print('--- Account Summary ---')
        print(f"{current_time:%Y-%m-%d %H:%M:%S}  Cash Balance: {app.account_balance}  Equity: {app.account_equity}")
        print('--- Portfolio ---')
        portfolio = app.portfolio or {}
        if not portfolio:
            print('No positions')
        else:
            headers = ['Symbol', 'Pos', 'MktPx', 'MktVal', 'AvgCost', 'UPnL', 'RPnL']
            rows = []
            for sym in sorted(portfolio):
                p = portfolio[sym]
                rows.append([
                    str(sym),
                    str(p.get('position', '')),
                    str(p.get('marketPrice', '')),
                    str(p.get('marketValue', '')),
                    str(p.get('averageCost', '')),
                    str(p.get('unrealizedPNL', '')),
                    str(p.get('realizedPNL', '')),
                ])
            # Calculate widths and format after all rows are built
            widths = [max(len(headers[i]), *(len(r[i]) for r in rows)) for i in range(len(headers))]
            fmt = '  '.join(('{:' + str(widths[0]) + '}') if i == 0 else ('{:>' + str(widths[i]) + '}') for i in range(len(widths)))
            print(fmt.format(*headers))
            print('-' * (sum(widths) + 2 * (len(widths) - 1)))
            for r in rows:
                print(fmt.format(*r))
        print('---')
        sleep(5)