from enphase import enlighten
from datetime import datetime

# inverter level data
eclient = enlighten.Client()

username = "username"
password = "password"

eclient.login(username, password)

# check on timezone
date = datetime(2021, 01, 01, 0, 0, 0)
times, powers = eclient.system_data(date)
