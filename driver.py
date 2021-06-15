from enphase import enlighten
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate

import config

# check if session/config file exists
eclient = enlighten.Client(time_step=5)
eclient.login(config.username, config.password)

# check on timezone
date = datetime(2021, 6, 13)

# 5 minute power levels for entire day
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


# write to influxdb

# convert Eastern to UTC time
# need to format the time in eastern

# Things to write to influx
# 1. Total system energy at 15 min intervals over the day
# 2. Total system power at 15 min intervals over the day
# 3. Power for each panel at 15 min interval
# 4. Panel energy over day at 15 min intervals
# 5. Temperature at same time as panel data
# 6. Cloud cover percentage at same time
# 7. Metric for weather (cloudy, sunny, etc)

# loop to next day
