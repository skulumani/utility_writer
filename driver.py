import matplotlib.pyplot as plt
import numpy as np
import pytz
from scipy import integrate
import pandas
import argparse
from datetime import datetime, timedelta
from time import sleep

import config
import influxdb_util
from enphase import enlighten


def get_daily_solar_data(eclient, date):
    print("Starting {}".format(date.strftime("%Y-%m-%d")),flush=True, end=' ')
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
    daily_panel_energy = np.trapz(powers, hours_of_day) # Watt Hours for entire day for each panel
    cum_panel_energy = integrate.cumtrapz(powers, hours_of_day, initial=0) # Watt Hour cumulative over the day

    # get total system energy for a day by summing up panel
    sys_power = np.sum(powers, axis=0)
    sys_daily_energy = np.sum(daily_panel_energy) # Watt  Hours
    sys_cum_energy = np.sum(cum_panel_energy, axis=0) 

    eastern = pytz.timezone("America/New_York")
    utc = pytz.utc
    # dt = np.arange(date, date+timedelta(days=1), timedelta(hours=0.25)).astype(datetime)
    dt = [eastern.localize(d).astimezone(utc) for d in times]

    # write panel data (15 min interval)
    for p, cpe, sn in zip(powers, cum_panel_energy, serial_num):
        influxdb_util.ingest_panel_data(dt, panel_list=p,
                                        serial_num=sn,
                                        measurement_name="panel_power",
                                        source="enphase",
                                        units="W")

        influxdb_util.ingest_panel_data(dt, panel_list=cpe,
                                        serial_num=sn,
                                        measurement_name="panel_energy",
                                        source="enphase",
                                        units="Wh")


    # write system data (1 per day interval)
    for p, sn in zip(daily_panel_energy, serial_num):

        influxdb_util.write_point(dt[0], measurement=p, measurement_name="daily_panel_energy",
                                tag_dict={"source": "enphase", "units": "Wh", "serial_num": sn})


    # write total system power 
    influxdb_util.ingest_system_data(dt, system_list=sys_power,
                                    measurement_name="system_power",
                                    source="enphase",
                                    units="W")
    influxdb_util.ingest_system_data(dt, system_list=sys_cum_energy,
                                    measurement_name="system_energy",
                                    source="enphase",
                                    units="Wh")
    influxdb_util.write_point(dt[0], measurement=sys_daily_energy, 
                            measurement_name="total_system_energy", 
                            tag_dict={"source": "enphase", "units": "Wh"})

    print("Total Energy: {:9.3f} Wh".format(sys_daily_energy), flush=True)

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

if __name__=="__main__":
    # check if session/config file exists
    eclient = enlighten.Client(time_step=15)
    eclient.login(config.username, config.password)
    
    parser = argparse.ArgumentParser(description="Download and write solar data to influxdb")
    
    parser.add_argument("start", metavar="s", type=str, help="Start date YYYYMMDD")
    parser.add_argument("end", metavar="e", type=str, help="End date YYYYMMDD")

    args = parser.parse_args()
    
    start = datetime.strptime(args.start, "%Y%m%d")
    end = datetime.strptime(args.end, "%Y%m%d")
    delta = timedelta(days=1)

    while start <= end:

        get_daily_solar_data(eclient, start)
        # get_daily_solar_data(eclient, datetime(2021,6,17))

        # sleep a little bit
        sleep(np.random.uniform(1,4))
        start += delta
