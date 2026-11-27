import yfinance as yf

ticker= yf.Ticker('AAPL')

history=ticker.history(period='5d')
print(history)
last_price=history['Close'].iloc[-1]
print('Цена AAPL', last_price)

tickers=yf.Tickers('AAPL GOOG TSLA')

