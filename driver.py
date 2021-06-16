from enphase import enlighten
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pytz
from scipy import integrate
import pandas

import config

# check if session/config file exists
eclient = enlighten.Client(time_step=15)
eclient.login(config.username, config.password)

date = datetime(2021, 5, 30)

# power levels for entire day
times, powers = eclient.system_data(date)
times = np.array(times) # UTC time
powers = np.array(powers) # panel level power for the day

# get list of panel serial numbers
system_id = eclient.system_id
modules = sorted(eclient.modules, key=lambda x: x['inverter']['inverter_id'])
id_index = eclient.device_index # same order as powers
serial_num = np.array([int(m['inverter']['serial_num']) for m in modules])

# convert times to hours of the day
epoch = times[0].timestamp()
hours_of_day = [(t.timestamp() - epoch)/3600 for t in times]

# panel energy over the day
daily_energy = np.trapz(powers, hours_of_day) # Watt Hours for entire day for each panel
cum_energy = integrate.cumtrapz(powers, hours_of_day, initial=0) # Watt Hour cumulative over the day

# get total system energy for a day by summing up panel
sys_power = np.sum(powers, axis=0)
sys_daily_energy = np.sum(daily_energy) # Watt  Hours
sys_cum_energy = np.sum(cum_energy, axis=0) 

# time array
eastern = pytz.timezone("America/New_York")
utc = pytz.utc
dt = np.arange(date, date+timedelta(days=1), timedelta(hours=0.25)).astype(datetime)
dt = [eastern.localize(d).astimezone(utc) for d in dt]

# form pandas df 

# write to influxdb

# Things to write to influx
# 1. Total system energy at 15 min intervals over the day (system_energy)
# 2. Total system power at 15 min intervals over the day (system_power)
# 2a. total system energy for each day (system_daily_energy)
# 3. Power for each panel at 15 min interval (panel_power)
# 4. Panel energy over day at 15 min intervals (panel_energy)

# tags - serial_num, units, source
# fields - (panel_production: power, energy) (system_production: power, energy) (system_production_daily: energy)
# measurements - panel_production, system_production, system_daily_production

# 5. Temperature at same time as panel data
# 6. Cloud cover percentage at same time
# 7. Metric for weather (cloudy, sunny, etc)

# loop to next day - random backoff for client calls to website
