import pandas as pd

def ema(prices, period=14):
    return pd.Series(prices).ewm(span=period, adjust=False).mean().iloc[-1]
