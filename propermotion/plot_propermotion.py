#!/usr/bin/env python
from datetime import datetime
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import pandas as pd
from astropy.time import Time
from sklearn.metrics import mean_squared_error
import sys

# Define your color palette as a list of RGB tuples or hexadecimal codes
nature_colors = ['#DC000099', '#4DBBD599', '#00A08799', '#F39B7F99', '#8491B499', '#DC0000FF', '#3C5488FF']
# red, blue, green, organge, grey, dark red, dark blue

# Load the data
kk = 0
bb = 0

data_path = sys.argv[1]
data = pd.read_csv(data_path)

# name is pm-J1234-X-errorbar.txt
# id is J1234
id = data_path.split('-')[1]

#band default is 'X' otherwise give by sys.argv[2]
band = 'X'
if len(sys.argv) > 2:
    band = sys.argv[2]


# Convert dates to datetime objects for analysis
data['date'] = pd.to_datetime(data['date'])

# Convert dates to a numeric format (days since the start) for fitting
data['days_since_start'] = (data['date'] - data['date'].min()).dt.days

# Prepare data for linear regression
X = data[['days_since_start']]  # Predictor variable for fitting

plt.figure(figsize=(12, 8))

# Fit the model and prepare predictions for R1, R2, R3
if 'R1' in data.columns:
    Y_pred_R1 = LinearRegression().fit(X, data[['R1']]).predict(X)
    model = LinearRegression()
    model.fit(X, data[['R1']])
    slope = model.coef_
    m1,b1 = np.polyfit(data['days_since_start'], data['R1'], 1 , full=False, cov=True)
    print('m1 : ',m1) 
    [kk, bb] = m1
    bb -= 1
    print('b1 : ',b1)
    print('kk : ',kk)
    print('bb : ',bb)

if 'R2' in data.columns:
    Y_pred_R2 = LinearRegression().fit(X, data[['R2']]).predict(X)
if 'R3' in data.columns:
    Y_pred_R3 = LinearRegression().fit(X, data[['R3']]).predict(X)


# Plot original data and linear fit with dates as x-axis for R1
if 'R1' in data.columns:
    #plt.ylim([0,5])
    #plt.scatter(data['date'], data['R1'], label='J2', alpha=0.5,  color=nature_colors[0], s=120)
    plt.plot(data['date'], Y_pred_R1, label='', color=nature_colors[4])
    plt.errorbar(data['date'], data['R1'], yerr=data['R1_err'], fmt='o', label='Jet', alpha=0.5,  color=nature_colors[0], markersize=12)
    plt.text(data['date'].iloc[-1], data['R1'].iloc[-1], 'm = {:.2f} $\pm$  mas/y'.format(slope[0][0]*365))

# Plot original data and linear fit with dates as x-axis for R2
if 'R2' in data.columns:
    plt.scatter(data['date'], data['R2'], label='J2 Original Data', alpha=0.5, color='green')
    #plt.plot(data['date'], Y_pred_R2, label='J2 Linear Fit', color='green')

# Plot original data and linear fit with dates as x-axis for R3
if 'R3' in data.columns:
    plt.scatter(data['date'], data['R3'], label='J3 Original Data', alpha=0.5, color='red')
    #plt.plot(data['date'], Y_pred_R3, label='J3 Linear Fit', color='red')

# Title, labels, and legend

plt.gcf().autofmt_xdate()  # Rotate date labels to make them readable
#plt.xlim(pd.to_datetime('1995-01-01'), pd.to_datetime('2024-01-01'))
# get the biggest date
date_max = data['date'].max()
print(date_max)
date_min = data['date'].min()
print(date_min)
#plt.xlim(pd.to_datetime('1995-01-01'), pd.to_datetime('2024-01-01'))
plt.ylim([-0.05,4])
#plt.title('Propermotion of J0646+4451', fontsize=24 )
plt.xlabel('Epoch (year)', fontsize=20)
plt.xticks(rotation=0,fontsize=18)
plt.ylabel('Relative separation from core (mas)', fontsize=20)
plt.yticks(rotation=0,fontsize=18)
plt.legend(fontsize=16)

plt.tight_layout()
plt.savefig('propermotion-{}-{}.png'.format(id,band), dpi=600)
plt.show()
