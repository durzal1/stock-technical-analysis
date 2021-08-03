import requests
import numpy as np
import pandas as pd
import math
import xlsxwriter
from matplotlib import pyplot as plt
from matplotlib import colors
from matplotlib.ticker import PercentFormatter
import mplfinance as mpf
import csv

# token used
IEX_CLOUD_API_TOKEN = 'Tpk_059b97af715d417d9f49f50b51b1c448'

# key
API_KEY = 'YOUR_API_KEY'

# the stock being analysed
symbol = 'AAPL'

# getting the data
api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}'
data = requests.get(api_url).json()

r = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol='+symbol+'&apikey=' + API_KEY)
if r.status_code == 200:
    result = r.json()
# data for the last 100 days
dataForAllDays = result['Time Series (Daily)']

# prices at closing times
closingPrices = []

# gets prices at closing times for the last 100 days
for i in range(99,-1,-1):
    price = list(dataForAllDays.keys())[i]
    dataForSingleDate = dataForAllDays[price]
    p = dataForSingleDate['4. close']
    closingPrices.append(float(p))

# the current 12 EMA
EMA12 = []

# the multiplier being used
mult12 = (2 / (12 + 1))

# getting the first SMA value to be used for EMA
avg = 0
for i in range(12):
    # adds to the average
    avg += closingPrices[i]

avg /= 12

# adds the average to EMA
EMA12.append(avg)

#gets the rest of the EMA
for i in range(12,100):
    EMA12.append((closingPrices[i] - EMA12[len(EMA12)-1])*mult12+EMA12[len(EMA12)-1])

# the current 26 EMA
EMA26 = []

# the multiplier being used
mult26 = (2 / (26 + 1))

# getting the first SMA value to be used for EMA
avg = 0
for i in range(26):
    avg += closingPrices[i]

avg /= 26

# adds the average to EMA
EMA26.append(avg)

#gets the rest of the EMA
for i in range(26,100):
    EMA26.append((closingPrices[i] - EMA26[len(EMA26)-1])*mult26+EMA26[len(EMA26)-1])

#difference between EMA12 and EMA26
EMADiff = []
for i in range(len(EMA26)):
    EMADiff.append(EMA12[i+14] - EMA12[i])

# signal line (9-day EMA of MACD line)

# the current 9 EMA
EMA9 = []

# the multiplier being used
mult9 = (2 / (9 + 1))

# getting the first SMA value to be used for EMA
avg = 0
for i in range(9):
    avg += EMADiff[i]

avg /= 9

# adds the average to EMA
EMA9.append(avg)

#gets the rest of the EMA
for i in range(9, len(EMADiff)):
    EMA9.append((EMADiff[i] - EMA9[len(EMA9)-1])*mult9 + EMA9[len(EMA9)-1])

# historgram (difference between MACD line and signal line)
MacdHistogram = []
for i in range(len(EMA9)):
    MacdHistogram.append(EMADiff[i+8] - EMA9[i])

# create seperate lists of all the data so they are the same size of MacdHistogram

# iniatilizing the new lists
MACDLine = []
SignalLine = []
for i in range( (len(EMADiff) - len(MacdHistogram)) ,len(EMADiff)):
    MACDLine.append(EMADiff[i])
for i in range( (len(EMA9) - len(MacdHistogram)) ,len(EMA9)):
    SignalLine.append(EMA9[i])

nums = []
control = []

# gets numbers 1-len(MacdHistorgram) to organize on graph
for i in range(len(MacdHistogram)):
    nums.append(i)
    control.append(0)

# splits MacdHistogram into positive and negative numbers
posH = []
negH = []

for num in MacdHistogram:
    if num > 0:
        posH.append(num)
        negH.append(0)
    else:
        negH.append(num)
        posH.append(0)
# plots the MACD Lines
x1 = np.arange(len(posH))

width = 0.5
fig, ax = plt.subplots()
rects1 = ax.bar(x1, posH, width, color='g')
rects2 = ax.bar(x1, negH, width, color='r')
ax.plot(nums,MACDLine)
ax.plot(nums,SignalLine)
ax.plot(nums,control, color = 'k')

ax.legend(['MACD Line', 'Signal', 'control', 'MACD Histogram'])
ax.set_title('MACD Line')
ax.set_xlabel('Dates starting at day 0(about 2 months ago) with largest number being last day market closed')
ax.set_ylabel('range')


# gets the true price of the stock for the last 67 days;

# writes the data in csv file to be used later
header = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
data = []
for i in range(len(MacdHistogram) - 1, -1, -1):
    # for each index add the date,open,high,low,close, and volume
    price = list(dataForAllDays.keys())[i]
    dataForSingleDate = dataForAllDays[price]

    Open = dataForSingleDate['1. open']

    high = dataForSingleDate['2. high']

    low = dataForSingleDate['3. low']

    close = dataForSingleDate['4. close']

    volume = dataForSingleDate['5. volume']

    Data = [price, Open, high, low, close, volume]
    data.append(Data)


with open('ye.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(header)

    # write multiple rows
    writer.writerows(data)

# gets the data and puts makes it into a graph
daily = pd.read_csv('ye.csv',index_col=0,parse_dates=True)
daily.index.name = 'Date'
daily.shape
daily.head(3)
daily.tail(3)
kwargs = dict(type='candle',mav=(2,4,6),volume=True,figratio=(11,8),figscale=0.85)
mc = mpf.make_marketcolors(up='g',down='r')
s  = mpf.make_mpf_style(marketcolors=mc)

mpf.plot(daily,type='candle',style= s)




