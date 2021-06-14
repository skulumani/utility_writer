from enphase import enlighten
from datetime import datetime

import config

# inverter level data
eclient = enlighten.Client()

eclient.login(config.username, config.password)

# check on timezone
date = datetime(2021, 1, 1, 0, 0, 0)
times, powers = eclient.system_data(date)


# get panel level power data for a date
# get total system energy for a day
# write to influxdb
# loop to next day
