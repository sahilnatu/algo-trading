# -*- coding: utf-8 -*-
"""
Created on Sat Sep  4 12:28:02 2021

@author: sahil
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz

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
strategy_1_df = pd.DataFrame()
strategy_1_df["timestamp"] = hist_tick.index
strategy_1_df.set_index("timestamp",inplace=True)
strategy_1_df["open"] = hist_tick["Open"]
strategy_1_df["high"] = hist_tick["High"]
strategy_1_df["low"] = hist_tick["Low"]
strategy_1_df["close"] = hist_tick["Close"]

# Calculating 5-SMA and 7-SMA at 1m interval
sma_5 = hist_tick["Close"].rolling(5,min_periods=1).mean()
strategy_1_df["sma_5"] = sma_5
sma_7 = hist_tick["Close"].rolling(7,min_periods=1).mean()
strategy_1_df["sma_7"] = sma_7

# Create an empty column for call at every row
strategy_1_df["call"] = np.nan
strategy_1_df["trigger"] = np.nan

# Remove first 7 entries as 7-SMA would be incorrectly calculated there
strategy_1_df_trunc = strategy_1_df.iloc[7:,:]

for i in range(len(strategy_1_df_trunc)):
    if i==0:
        strategy_1_df_trunc["call"].iloc[i] = "HOLD"
        continue
    else:
        buy_trigger = (strategy_1_df_trunc.iloc[i-1,4] <= strategy_1_df_trunc.iloc[i-1,5]) and (strategy_1_df_trunc.iloc[i,4] > strategy_1_df_trunc.iloc[i,5])
        sell_trigger_1 = (strategy_1_df_trunc.iloc[i-1,4] >= strategy_1_df_trunc.iloc[i-1,5]) and (strategy_1_df_trunc.iloc[i,4] < strategy_1_df_trunc.iloc[i,5])
        if len(portfolio) > 0:
            last_close = strategy_1_df_trunc.iloc[i,3]
            avg_portfolio_price = portfolio["Value"].values
            sell_trigger_2 = (last_close <= avg_portfolio_price*stop_loss)
            sell_trigger_3 = (last_close >= avg_portfolio_price*profit_booking)
            if sell_trigger_2==True:
                print("2 is true")
            if sell_trigger_3==True:
                print("3 is true")
        else:
            sell_trigger_2 = False
            sell_trigger_3 = False
            
        sell_trigger = sell_trigger_1 or sell_trigger_2 or sell_trigger_3
        
        if buy_trigger:
            strategy_1_df_trunc["call"].iloc[i] = "BUY"
            strategy_1_df_trunc["trigger"].iloc[i] = "SMA 5/7"
            row = pd.DataFrame([[stock,strategy_1_df_trunc["call"].iloc[i],share_size,strategy_1_df_trunc["close"].iloc[i],share_size*strategy_1_df_trunc["close"].iloc[i]]], columns=["Stock","Activity","Qty","Value","Total"])
            portfolio_log = portfolio_log.append(row)
            row1 = pd.DataFrame([[stock,share_size,strategy_1_df_trunc["close"].iloc[i],share_size*strategy_1_df_trunc["close"].iloc[i]]], columns=["Stock","Qty","Value","Total"])
            portfolio = portfolio.append(row1)
            portfolio = portfolio.groupby("Stock").agg(
                                Qty = pd.NamedAgg(column="Qty", aggfunc="sum"),
                                Value = pd.NamedAgg(column="Value", aggfunc="mean"),
                                Total = pd.NamedAgg(column="Total", aggfunc="sum")
                                )
            portfolio.reset_index(inplace=True)
        elif sell_trigger_1:
            strategy_1_df_trunc["call"].iloc[i] = "SELL"
            strategy_1_df_trunc["trigger"].iloc[i] = "SMA 5/7"
            row = pd.DataFrame([[stock,strategy_1_df_trunc["call"].iloc[i],share_size,strategy_1_df_trunc["close"].iloc[i],share_size*strategy_1_df_trunc["close"].iloc[i]]], columns=["Stock","Activity","Qty","Value","Total"])
            portfolio_log = portfolio_log.append(row)
            row1 = pd.DataFrame([[stock,-share_size,strategy_1_df_trunc["close"].iloc[i],-share_size*strategy_1_df_trunc["close"].iloc[i]]], columns=["Stock","Qty","Value","Total"])
            portfolio = portfolio.append(row1)
            portfolio = portfolio.groupby("Stock").agg(
                                Qty = pd.NamedAgg(column="Qty", aggfunc="sum"),
                                Value = pd.NamedAgg(column="Value", aggfunc="mean"),
                                Total = pd.NamedAgg(column="Total", aggfunc="sum")
                                )
            portfolio.reset_index(inplace=True)
        elif sell_trigger_2:
            strategy_1_df_trunc["call"].iloc[i] = "SELL"
            strategy_1_df_trunc["trigger"].iloc[i] = "STOP LOSS"
            row = pd.DataFrame([[stock,strategy_1_df_trunc["call"].iloc[i],share_size,strategy_1_df_trunc["close"].iloc[i],share_size*strategy_1_df_trunc["close"].iloc[i]]], columns=["Stock","Activity","Qty","Value","Total"])
            portfolio_log = portfolio_log.append(row)
            row1 = pd.DataFrame([[stock,-share_size,strategy_1_df_trunc["close"].iloc[i],-share_size*strategy_1_df_trunc["close"].iloc[i]]], columns=["Stock","Qty","Value","Total"])
            portfolio = portfolio.append(row1)
            portfolio = portfolio.groupby("Stock").agg(
                                Qty = pd.NamedAgg(column="Qty", aggfunc="sum"),
                                Value = pd.NamedAgg(column="Value", aggfunc="mean"),
                                Total = pd.NamedAgg(column="Total", aggfunc="sum")
                                )
            portfolio.reset_index(inplace=True)
        elif sell_trigger_3:
            strategy_1_df_trunc["call"].iloc[i] = "SELL"
            strategy_1_df_trunc["trigger"].iloc[i] = "PROFIT BOOK"
            row = pd.DataFrame([[stock,strategy_1_df_trunc["call"].iloc[i],share_size,strategy_1_df_trunc["close"].iloc[i],share_size*strategy_1_df_trunc["close"].iloc[i]]], columns=["Stock","Activity","Qty","Value","Total"])
            portfolio_log = portfolio_log.append(row)
            row1 = pd.DataFrame([[stock,-share_size,strategy_1_df_trunc["close"].iloc[i],-share_size*strategy_1_df_trunc["close"].iloc[i]]], columns=["Stock","Qty","Value","Total"])
            portfolio = portfolio.append(row1)
            portfolio = portfolio.groupby("Stock").agg(
                                Qty = pd.NamedAgg(column="Qty", aggfunc="sum"),
                                Value = pd.NamedAgg(column="Value", aggfunc="mean"),
                                Total = pd.NamedAgg(column="Total", aggfunc="sum")
                                )
            portfolio.reset_index(inplace=True)
        else:
           strategy_1_df_trunc["call"].iloc[i] = "HOLD"

if len(portfolio)!=0:
    if portfolio.iloc[0,1]>0:
        print("need to sell")
        row = pd.DataFrame([[stock,"SELL",-portfolio.iloc[0,1],strategy_1_df_trunc["close"].iloc[-1],-portfolio.iloc[0,1]*strategy_1_df_trunc["close"].iloc[-1]]], columns=["Stock","Activity","Qty","Value","Total"])
        portfolio_log = portfolio_log.append(row)
        row1 = pd.DataFrame([[stock,-portfolio.iloc[0,1],strategy_1_df_trunc["close"].iloc[-1],-portfolio.iloc[0,1]*strategy_1_df_trunc["close"].iloc[-1]]], columns=["Stock","Qty","Value","Total"])
        portfolio = portfolio.append(row1)
        portfolio = portfolio.groupby("Stock").agg(
            Qty = pd.NamedAgg(column="Qty", aggfunc="sum"),
            Value = pd.NamedAgg(column="Value", aggfunc="mean"),
            Total = pd.NamedAgg(column="Total", aggfunc="sum")
            )
        portfolio.reset_index(inplace=True)
    elif portfolio.iloc[0,1]<0:
        print("need to buy")
        row = pd.DataFrame([[stock,"BUY",-portfolio.iloc[0,1],strategy_1_df_trunc["close"].iloc[-1],-portfolio.iloc[0,1]*strategy_1_df_trunc["close"].iloc[-1]]], columns=["Stock","Activity","Qty","Value","Total"])
        portfolio_log = portfolio_log.append(row)
        row1 = pd.DataFrame([[stock,-portfolio.iloc[0,1],strategy_1_df_trunc["close"].iloc[-1],-portfolio.iloc[0,1]*strategy_1_df_trunc["close"].iloc[-1]]], columns=["Stock","Qty","Value","Total"])
        portfolio = portfolio.append(row1)
        portfolio = portfolio.groupby("Stock").agg(
            Qty = pd.NamedAgg(column="Qty", aggfunc="sum"),
            Value = pd.NamedAgg(column="Value", aggfunc="mean"),
            Total = pd.NamedAgg(column="Total", aggfunc="sum")
            )
        portfolio.reset_index(inplace=True)
returns = portfolio_log.groupby(["Stock","Activity"]).agg(
    Qty = pd.NamedAgg(column="Qty", aggfunc="sum"),
    Value = pd.NamedAgg(column="Value", aggfunc="mean"),
    Total = pd.NamedAgg(column="Total", aggfunc="sum")
    )
returns.reset_index(inplace=True)
net_pl = returns[returns["Activity"]=="SELL"]["Total"].values[0] - returns[returns["Activity"]=="BUY"]["Total"].values[0]
net_buy = returns[returns["Activity"]=="BUY"]["Qty"].values[0]
net_sell = returns[returns["Activity"]=="SELL"]["Qty"].values[0]
avg_buy = returns[returns["Activity"]=="BUY"]["Value"].values[0]
avg_sell = returns[returns["Activity"]=="SELL"]["Value"].values[0]
print("Net Profit / Loss is: INR {val:.2f}".format(val=net_pl))
print("Total Shares Bought: {0}".format(net_buy))
print("Total Shares Sold: {0}".format(net_sell))
print("Avg Buy Price: INR {val:.2f}".format(val=avg_buy))
print("Avg Sell Price: INR {val:.2f}".format(val=avg_sell))

    # colors for the line plot
    #colors = ['blue', 'green', 'orange', 'red']
    
    # line plot - simple moving avg
    #plt = avgs.iloc[-30:,:].plot(kind='line',color=colors, linewidth=3, figsize=(12,6),title='Simple Moving Averages for RIL',xlabel='Date',ylabel='Share Price in INR')