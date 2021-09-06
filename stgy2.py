# -*- coding: utf-8 -*-
"""
Created on Sat Sep  4 12:28:02 2021

@author: sahil
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#from datetime import datetime, timedelta
#import pytz

#timezone = pytz.timezone("Asia/Kolkata")

stocks = ["RELIANCE.NS"]#,"RELIANCE.NS","INFY.NS","MINDTREE.NS","SBIN.NS"]
stock = stocks[0]
portfolio_log = pd.DataFrame(columns=["Stock","Activity","Qty","Value","Total"])
portfolio = pd.DataFrame(columns=["Stock","Qty","Value","Total"])
share_size = 100
stop_loss = 0.995
profit_booking = 1.05
#start_time = 

#while datetime.now() < end_time:
    
#tick = yf.Ticker(stock)

# Read ticker and extract data at 1m interval for last 40d
tick = yf.Ticker(stock)
hist_tick = tick.history(period="7d",interval="1m",)


# Create a new dataframe for strategy 1 (refer appendix for more details on this strategy)
strategy_2_df = pd.DataFrame()
strategy_2_df["timestamp"] = hist_tick.index
strategy_2_df.set_index("timestamp",inplace=True)
strategy_2_df["open"] = hist_tick["Open"]
strategy_2_df["high"] = hist_tick["High"]
strategy_2_df["low"] = hist_tick["Low"]
strategy_2_df["close"] = hist_tick["Close"]


# Create an empty column for call at every row
strategy_2_df["call"] = np.nan
strategy_2_df["trigger"] = np.nan

strategy_2_df["rising_sar"] = np.nan
strategy_2_df["falling_sar"] = np.nan
strategy_2_df["psar"] = np.nan
strategy_2_df["up_ep"] = np.nan
strategy_2_df["dn_ep"] = np.nan
strategy_2_df["up_acc"] = np.nan
strategy_2_df["dn_acc"] = np.nan
strategy_2_df["trend"] = np.nan

rising_sar_init = min(strategy_2_df["close"].iloc[0],strategy_2_df["close"].iloc[1])
falling_sar_init = max(strategy_2_df["close"].iloc[0],strategy_2_df["close"].iloc[1])
acc_init = 0.03
acc_max = 0.3
acc_step = 0.03
up_acc_reset = False
dn_acc_reset = False
up_acc = acc_init + acc_step
dn_acc = acc_init + acc_step
low_lim = 0

strategy_2_df = strategy_2_df.iloc[:100]

for i in range(len(strategy_2_df)):
    if i<2:
        strategy_2_df_subset = strategy_2_df.iloc[0:2]
        strategy_2_df_agg = strategy_2_df_subset.agg(
            up_ep = pd.NamedAgg(column="close", aggfunc="max"),
            dn_ep = pd.NamedAgg(column="close", aggfunc="min")
            )
        strategy_2_df["up_ep"].iloc[i] = strategy_2_df_agg.iloc[0]
        strategy_2_df["dn_ep"].iloc[i] = strategy_2_df_agg.iloc[1]
    else:
        strategy_2_df_subset = strategy_2_df.iloc[low_lim:i+1]
        strategy_2_df_agg = strategy_2_df_subset.agg(
            up_ep = pd.NamedAgg(column="close", aggfunc="max"),
            dn_ep = pd.NamedAgg(column="close", aggfunc="min")
            )
        strategy_2_df["up_ep"].iloc[i] = strategy_2_df_agg.iloc[0]
        strategy_2_df["dn_ep"].iloc[i] = strategy_2_df_agg.iloc[1]
    if i==0:
        strategy_2_df["rising_sar"].iloc[i] = rising_sar_init + acc_init*(falling_sar_init - rising_sar_init)
        strategy_2_df["falling_sar"].iloc[i] = rising_sar_init - acc_init*(rising_sar_init - falling_sar_init)
    if i==1:
        acc = acc_init + acc_step
        strategy_2_df["rising_sar"].iloc[i] = strategy_2_df["rising_sar"].iloc[i-1] + acc*(falling_sar_init - strategy_2_df["rising_sar"].iloc[i-1])
        strategy_2_df["falling_sar"].iloc[i] = strategy_2_df["falling_sar"].iloc[i-1] - acc*(strategy_2_df["falling_sar"].iloc[i-1] - rising_sar_init)
    if up_acc_reset == True:
        up_acc = acc_init
    else:
        if up_acc < acc_max:
            up_acc = up_acc + acc_step
    if dn_acc_reset == True:
        dn_acc = acc_init
    else:
        if dn_acc < acc_max:
            dn_acc = dn_acc + acc_step
    if i>1:
        strategy_2_df["rising_sar"].iloc[i] = strategy_2_df["rising_sar"].iloc[i-1] + up_acc*(strategy_2_df["up_ep"].iloc[i] - strategy_2_df["rising_sar"].iloc[i-1])
        strategy_2_df["falling_sar"].iloc[i] = strategy_2_df["falling_sar"].iloc[i-1] - dn_acc*(strategy_2_df["falling_sar"].iloc[i-1] - strategy_2_df["dn_ep"].iloc[i])
        curr_close = strategy_2_df["close"].iloc[i]
        curr_rising_sar = strategy_2_df["rising_sar"].iloc[i]
        curr_falling_sar = strategy_2_df["falling_sar"].iloc[i]
        last_close = strategy_2_df["close"].iloc[i-1]
        last_rising_sar = strategy_2_df["rising_sar"].iloc[i-1]
        last_falling_sar = strategy_2_df["falling_sar"].iloc[i-1]
        if curr_close >= curr_falling_sar and last_close < last_falling_sar:
            strategy_2_df["trend"].iloc[i] = "up_start"
            up_acc_reset = True
            dn_acc_reset = True
            low_lim = i+1
            strategy_2_df["psar"].iloc[i] = strategy_2_df["rising_sar"].iloc[i]
        elif curr_close <= curr_rising_sar and last_close > last_rising_sar:
            strategy_2_df["trend"].iloc[i] = "dn_start"
            up_acc_reset = True
            dn_acc_reset = True
            low_lim = i+1
            strategy_2_df["psar"].iloc[i] = strategy_2_df["falling_sar"].iloc[i]
        elif (curr_close < curr_falling_sar and last_close < last_falling_sar) or strategy_2_df["trend"].iloc[i-1] == "dn_start":
            strategy_2_df["trend"].iloc[i] = "dn"
            up_acc_reset = False
            dn_acc_reset = False
            strategy_2_df["psar"].iloc[i] = strategy_2_df["falling_sar"].iloc[i]
        elif (curr_close > curr_rising_sar and last_close > last_rising_sar) or strategy_2_df["trend"].iloc[i-1] == "up_start":
            strategy_2_df["trend"].iloc[i] = "up"
            up_acc_reset = False
            dn_acc_reset = False
            strategy_2_df["psar"].iloc[i] = strategy_2_df["rising_sar"].iloc[i]
        else:
            up_acc_reset = False
            dn_acc_reset = False
        strategy_2_df["up_acc"].iloc[i] = up_acc
        strategy_2_df["dn_acc"].iloc[i] = dn_acc
        
plt.plot(strategy_2_df["psar"], linestyle = ':')
plt.plot(strategy_2_df["close"], linestyle = '-')
plt.show()