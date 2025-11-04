# TradingBot V1 - Technical Exploration

This version focused on understanding how to connect to and interact with Interactive Brokers' trading platform through their API. The goal was to build a foundation for pulling real-time financial data and see what's possible.

## What I Built

Connected to Interactive Brokers TWS (Trader Workstation) and built a system that:
- Pulls live account balance and equity data
- Retrieves current portfolio positions with P&L calculations
- Displays everything in a formatted table that updates every 5 seconds
- Handles the connection properly without blocking the interface

## Technical Details

### API Connection Setup
The Interactive Brokers API uses a pattern where you inherit from both EWrapper (handles incoming data) and EClient (sends requests). You connect to TWS running locally and authenticate with a client ID.

```python
class TradeApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        # Custom attributes for storing data
        self.account_balance = math.nan
        self.account_equity = math.nan
        self.portfolio = {}
```

The tricky part is that all communication is asynchronous - you send a request and wait for the response to come back through callback methods.

### Real-Time Data Handling
TWS pushes account updates through specific callback methods. I implemented two key ones:

`updateAccountValue()` - Gets called whenever account data changes (balance, equity, etc.)
`updatePortfolio()` - Gets called for each position with current market prices and P&L

The data comes in as strings that need to be parsed and stored properly. Financial data requires precision, so I used proper decimal handling where needed.

### Threading Architecture
The API connection runs in a background thread so the main program can continue displaying data without freezing. Used Python's threading module:

```python
app_thread = Thread(target=app.run, daemon=True)
app_thread.start()
```

Main thread runs a loop that displays the current portfolio data every 5 seconds.

### Data Presentation
Built a dynamic table formatter that calculates column widths based on the actual data:

```python
widths = [max(len(headers[i]), *(len(r[i]) for r in rows)) for i in range(len(headers))]
fmt = '  '.join(('{:' + str(widths[0]) + '}') if i == 0 else ('{:>' + str(widths[i]) + '}') for i in range(len(widths)))
```

This creates properly aligned columns regardless of symbol names or dollar amounts.

## What I Learned

**API Patterns**: Financial APIs work differently than typical REST APIs. Everything is event-driven and asynchronous. You can't just make a request and get an immediate response.

**Threading in Python**: Had to learn about daemon threads and how to share data safely between threads. The main insight is keeping the API communication separate from the user interface.

**Financial Data Precision**: Regular floating point math isn't suitable for financial calculations. The API provides helper functions like `decimalMaxString()` and `floatMaxString()` for proper handling.

**Real-Time Systems**: Building something that continuously updates taught me about the challenges of keeping connections alive and handling network issues gracefully.

## Key Code Components

The core logic is in the callback methods:

```python
def updateAccountValue(self, key: str, val: str, currency: str, accountName: str):
    if key == 'TotalCashBalance' and currency =='BASE':
        self.account_balance = val
    if key == 'NetLiquidationByCurrency' and currency =='BASE':
        self.account_equity = val

def updatePortfolio(self, contract: Contract, position: Decimal, marketPrice: float, 
                   marketValue: float, averageCost: float, unrealizedPNL: float, 
                   realizedPNL: float, accountName: str):
    self.portfolio[contract.localSymbol] = {
        'position': decimalMaxString(position),
        'marketPrice': floatMaxString(marketPrice),
        'marketValue': floatMaxString(marketValue),
        'averageCost': floatMaxString(averageCost),
        'unrealizedPNL': floatMaxString(unrealizedPNL),
        'realizedPNL': floatMaxString(realizedPNL)
    }
```

## What Works Well

The system connects reliably and pulls data consistently. The table formatting adapts to different portfolio sizes automatically. Threading keeps everything responsive.

## Current Limitations

Only pulls current snapshot data - no historical information yet. No data persistence between runs. Error handling could be more comprehensive. Only works with one account at a time.

## Interesting Observations

The IB API is quite powerful but has a steep learning curve. The documentation assumes you already understand trading concepts. The event-driven nature makes it well-suited for real-time applications but harder to debug than synchronous code.

Portfolio data includes both realized and unrealized P&L, which is useful for understanding actual vs. paper gains. The market value calculations update in real-time as prices change.

## Technical Stack Used

- Python 3.12
- Interactive Brokers API (ibapi package)
- Threading for concurrency
- Decimal module for financial precision
- Standard string formatting for display
