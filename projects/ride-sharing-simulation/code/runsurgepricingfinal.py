#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 16:44:59 2026

@author: michael
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 15:39:39 2026

@author: michael
"""

import pandas as pd 
df_drivers = pd.read_excel("drivers.xlsx")
df_riders = pd.read_excel("riders.xlsx")

import surgepricingfinal
import rv
import dat
import eval
import numpy as np
import matplotlib.gridspec as gridspec
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt

import seaborn as sns

N = 20


coef = {
    # Spatial distributions
    "driver_init_x_mean": 9.96,
    "driver_init_y_mean": 12,
    "rider_init_x_mean": 7.89,
    "rider_init_y_mean": 13.07,
    "rider_dest_x_mean": 11.76,
    "rider_dest_y_mean": 14.92,

    "init_std": 5,
    "dropoff_std": 5.5,

    # Shift timing
    "shift_time_lb": 8,
    "shift_time_ub": 8,

    # Trip time randomness
    "trip_time_lb": 0.7,
    "trip_time_ub": 1.3,

    # System rates
    "abandon": 5,
    "driver_arrival": 4.73,
    "rider_arrival": 34.58,
    "driver_arrival_surge": 8,

    # Pricing
    "base_fare": 3,
    "distance_rate": 1.8,
    "cost_rate": 0.2,

    # Surge pricing
    "surge_base": 5,
    "surge_rate": 2.5,
    
    "driver_cap": 100,
    
    "initial_drivers" : 10,       # drivers pre-populated at t=0 # 20 
    "driver_count_threshold": 30,  # once this many drivers in system... 30 
    "driver_arrival_high_count": 2
    
}
# initialise empty lists for storage of kpi values


abandon_rates = np.zeros(N)
mean_avg_hourly_earnings = np.zeros(N)
mean_resting_times = np.zeros(N)
mean_waiting_times = np.zeros(N)

# initialise empty list for gini coefficients of hourly earnings (measure of fairness among drivers)
gini_avg_hourly_earnings = np.zeros(N)

for i in range(N):
    # run simulation for 1000 hours
    kpi = surgewithsimv3.simulate_boxcar(1000, coef)
    
    
    # find abandon rate
    total_riders_sim = len(kpi["waiting_times"])
    abandon_rates[i] = kpi["abandon_count"] / kpi["total_number_riders"]

    # find mean and gini coefficient of avg hourly earnings
    mean_avg_hourly_earnings[i] = np.mean(kpi["avg_hourly_earnings"])
    gini_avg_hourly_earnings[i] = eval.gini(kpi["avg_hourly_earnings"])

    # find mean resting and waiting times
    mean_resting_times[i] = np.mean(kpi["prop_resting_times"])
    mean_waiting_times[i] = np.mean(kpi["waiting_times"])
    
    

# define all metrics in a list
all_metrics = [abandon_rates, mean_waiting_times, mean_resting_times, mean_avg_hourly_earnings, gini_avg_hourly_earnings]
all_metric_names = ["Abandon Rates", "Mean Waiting Times", "Mean Resting Times", "Mean Hourly Earnings", "Gini Hourly Earnings"]

# find means, confidence intervals of the estimates, and 95% prediction interval for each kpi
means = []
CI_95 = []
PI_95 = []

# for each metric
for i in range(len(all_metrics)):
    # i-th list of values in all_metrics
    vals = all_metrics[i]
    # find means (and gini coefficient estimate)
    mean_i = np.mean(vals)
    means.append(float(mean_i))
    # find confidence intervals of estimate
    std_i = float(np.std(vals, ddof=1)) 
    # append confidence interval of estimate and prediction interval
    CI_95.append(
        [float(mean_i - (1.96/np.sqrt(N))* std_i), float(mean_i + (1.96/np.sqrt(N))* std_i)]
    )
    PI_95.append(
        [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]
    )
    if all_metric_names[i] == "Gini Hourly Earnings":
        print(f"{all_metric_names[i]}"
              f"\nGini Coefficient: {np.round(mean_i, 5)}"
              f"\n95% Confidence Interval on Gini Coefficient Estimate: {np.round(CI_95[-1], 5)}"
              f"\n95% Prediction Interval: {np.round(PI_95[-1], 5)}"
              f"\n=====================================================================================")
    else:
        print(f"{all_metric_names[i]}"
              f"\nMean: {np.round(mean_i, 5)}" 
              f"\n95% Confidence Interval on Mean Estimator: {np.round(CI_95[-1], 5)}" 
              f"\n95% Prediction Interval: {np.round(PI_95[-1], 5)}"
              f"\n=====================================================================================")




