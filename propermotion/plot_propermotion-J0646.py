#!/usr/bin/env python
from datetime import datetime
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import mean_squared_error

# Load the data
import sys
data_path = sys.argv[1] 
data = pd.read_csv(data_path)

# Convert dates to datetime objects for analysis
data['date'] = pd.to_datetime(data['date'])

# Convert dates to a numeric format (days since the start) for fitting
data['days_since_start'] = (data['date'] - data['date'].min()).dt.days

# Prepare data for linear regression
X = data[['days_since_start']]  # Predictor variable for fitting

xxx = np.arange(0, 1000, 1)
yyy = []

# Fit the model and prepare predictions for R1, R2, R3
if 'R1' in data.columns:
    Y_pred_R1 = LinearRegression().fit(X, data[['R1']]).predict(X)
    m1,b1 = np.polyfit(data['days_since_start'], data['R1'], 1 , full=False, cov=True)
    print('m1 : ',m1) 
    [kk, bb] = m1
    print('b1 : ',b1)

    print('kk : ',kk)
    print('bb : ',bb)
    xx = -bb/kk
    print('xx : ',xx)


    model = LinearRegression()
    model.fit(X, data[['R1']])
    m = model.coef_
    print('m : ',m)
    b = model.intercept_
    mse = mean_squared_error(data[['R1']], Y_pred_R1)
    rmse = np.sqrt(mse)
    print('rmse : ',rmse)
    #xxx = -b/m
    for i in xxx:
        yyy.append(m*i + b)
    #yyy = m*xxx + b
    #yyy = np.array(yyy)
    #print('xxxxx : ',xxx, pd.to_datetime(xxx))
if 'R2' in data.columns:
    Y_pred_R2 = LinearRegression().fit(X, data[['R2']]).predict(X)
if 'R3' in data.columns:
    Y_pred_R3 = LinearRegression().fit(X, data[['R3']]).predict(X)

# Plot all measurements on a single plot with time (date) as the x-axis
plt.figure(figsize=(12, 8))

# Plot original data and linear fit with dates as x-axis for R1
if 'R1' in data.columns:
    #plt.ylim([0,5])
    plt.scatter(data['date'], data['R1'], label='Real ', alpha=0.5, color='purple')
    plt.plot(data['date'], Y_pred_R1, label='Fit', color='blue')
    #plt.plot(xxx,yyy, label='m = ' + str(m[0][0]), color='red')
    plt.text(data['date'].iloc[-1], data['R1'].iloc[-1], 'm = {:.2f} $\pm$  mas/y'.format(m[0][0]*365))

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

#plt.title('Propermotion of J0646+4451 using ' +  data_path.split('/')[-1], fontsize=24  )
plt.xlabel('Time', fontsize=20)
plt.ylim([-1,5])
plt.ylabel('Relative projected distance (mas)', fontsize=20)
plt.legend()

plt.tight_layout()
plt.savefig('propermotion-'+  data_path.split('/')[-1] + '.png' , dpi=600)
plt.show()