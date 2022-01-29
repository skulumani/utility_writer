from datetime import datetime, time
import pytz
import argparse

from influxdb_client import InfluxDBClient, Point, Dialect
from influxdb_client.client.write_api import SYNCHRONOUS

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

url = "http://192.168.88.12:8086"
token = "pc5XzRSoA7b_CKgpl6yiyxCiLmEo-Y36l8jRMKXTkNxDNPU3jiQIgBk5ZtIXU3WUPYhzqMgNaPW8tif02O0OfA=="
org = "wolverines"

bucket = "utilities" # "investments"


def daily_energy_usage(year=2021):
    """Daily energy usage
    
    Get energy usage for each day of the year
    """

    # read from influx db
    client = InfluxDBClient(url=url, token=token, org=org)
    query_api = client.query_api()

    p = {"_start": datetime(year, 1, 1),
         "_stop": datetime(year, 12, 31),
         "_measurement": "energy_consumption"
         }

    # read into dataframe
    data_frame = query_api.query_data_frame('''
            from(bucket: "utilities")
                |> range(start: _start, stop: _stop)
                |> filter(fn: (r) => r["_measurement"] == _measurement)
                |> timeShift(duration: -4h, columns: ["_start", "_stop", "_time"])
                |> aggregateWindow(every: 24h, fn: sum, createEmpty: false)
                ''', params=p)

    # loop over the dataframe and plot a point for each hour of day
    time = data_frame["_time"]
    hour = [t.hour for t in time]
    month = [t.month for t in time]
    day = [(t.toordinal() - datetime(t.year, 1, 1).toordinal() +1) for t in time]
    energy = data_frame["_value"]/1000
    
    fig, ax = plt.subplots()
    cmap = plt.get_cmap('hsv')

    scatter = ax.scatter(day, energy, c=month, cmap=cmap, s=5)
    ax.set_xlim([0, 364])
    
    # legend
    # legend = ax.legend(*scatter.legend_elements(), title="Month", loc="upper right",
    #                 mode="expand", ncol=12)
    print("{} Total Energy used: {}".format(year, sum(energy)))

    plt.xlabel("Day of Year")
    plt.ylabel("Energy (kWh)")
    plt.title("{:g} Energy Usage - Total {:.3} kWh".format(year, sum(energy)))
    plt.grid(axis='both', alpha=0.5)
    plt.show()

    client.close()

def hourly_energy_usage(year=2021):
    """Hourly energy usage
    
    Get energy usage for each hour of the year and plot as a point

    Shows energy usage for each hour of the day over entire year
    """

    # read from influx db
    client = InfluxDBClient(url=url, token=token, org=org)
    query_api = client.query_api()

    p = {"_start": datetime(year, 1, 1),
         "_stop": datetime(year, 12, 31),
         "_measurement": "energy_consumption"
         }

    # read into dataframe
    data_frame = query_api.query_data_frame('''
            from(bucket: "utilities")
                |> range(start: _start, stop: _stop)
                |> filter(fn: (r) => r["_measurement"] == _measurement)
                |> timeShift(duration: -4h, columns: ["_start", "_stop", "_time"])
                ''', params=p)

    # loop over the dataframe and plot a point for each hour of day
    time = data_frame["_time"]
    hour = [t.hour for t in time]
    month = [t.month for t in time]
    energy = data_frame["_value"]/1000
   
    # find average energy used for each hour
    energy_mean = np.zeros(24)
    for (e, h) in zip(energy, hour):
        energy_mean[h] += e

    energy_mean = energy_mean / 365

    # import pdb; pdb.set_trace()

    fig, ax = plt.subplots()
    cmap = plt.get_cmap('hsv')

    scatter = ax.scatter(hour, energy, c=month, cmap=cmap, s=5)
    ax.plot(np.arange(0, 24), energy_mean, "k-x")

    ax.set_xlim([0, 23])
    
    # legend
    # legend = ax.legend(*scatter.legend_elements(), title="Month", loc="upper right",
    #                 mode="expand", ncol=12)

    plt.xlabel("Hour")
    plt.ylabel("Energy (kWh)")
    plt.title("{:g} Hourly Energy Usage".format(year))
    plt.grid(axis='both', alpha=0.5)
    plt.show()

    client.close()

def annual_solar_power(year=2021):
    """Solar power for entire year

    Get power for each hour over the entire year

    """
    # read from influx db
    client = InfluxDBClient(url=url, token=token, org=org)
    query_api = client.query_api()

    p = {"_start": datetime(year, 1, 1),
         "_stop": datetime(year, 12, 31),
         "_measurement": "system_power"
         }

    # read into dataframe
    data_frame = query_api.query_data_frame('''
            from(bucket: "utilities")
                |> range(start: _start, stop: _stop)
                |> filter(fn: (r) => r["_measurement"] == _measurement)
                |> timeShift(duration: -4h, columns: ["_start", "_stop", "_time"])
                ''', params=p)

    # loop over the dataframe and plot a point for each hour of day
    time = data_frame["_time"]
    hour = [t.hour for t in time]
    month = [t.month for t in time]
    tod = [t.time() for t in time]
    power = data_frame["_value"]/1000
    
    fig, ax = plt.subplots()
    cmap = plt.get_cmap('hsv')

    scatter = ax.scatter(time, power, c=month, cmap=cmap, s=5)
    # ax.set_xlim([0, 23])

    plt.xlabel("Time of Day")
    plt.ylabel("Power (kW)")
    plt.title("{:g} Solar Power".format(year))
    plt.grid(axis='both', alpha=0.5)
    plt.show()

    client.close()

def daily_solar_energy(year=2021):
    """Daily solar energy

    Energy generated each day over the entire year
    """

    # read from influx db
    client = InfluxDBClient(url=url, token=token, org=org)
    query_api = client.query_api()

    p = {"_start": datetime(year, 1, 1),
         "_stop": datetime(year, 12, 31),
         "_measurement": "total_system_energy"
         }

    # read into dataframe
    data_frame = query_api.query_data_frame('''
            from(bucket: "utilities")
                |> range(start: _start, stop: _stop)
                |> filter(fn: (r) => r["_measurement"] == _measurement)
                |> timeShift(duration: -4h, columns: ["_start", "_stop", "_time"])
                ''', params=p)

    # loop over the dataframe and plot a point for each hour of day
    time = data_frame["_time"]
    hour = [t.hour for t in time]
    month = [t.month for t in time]
    day = [(t.toordinal() - datetime(t.year, 1, 1).toordinal() +1) for t in time]
    energy = data_frame["_value"]/1000
    
    fig, ax = plt.subplots()
    cmap = plt.get_cmap('hsv')

    scatter = ax.scatter(day, energy, c=month, cmap=cmap, s=5)
    ax.set_xlim([0,364])
    
    # legend
    # legend = ax.legend(*scatter.legend_elements(), title="Month", loc="upper right",
    #                 mode="expand", ncol=12)

    plt.xlabel("Day of year")
    plt.ylabel("Energy (kWh)")
    plt.title("{:g} Solar Energy".format(year))
    plt.grid(axis='both', alpha=0.5)
    plt.show()

    client.close()

def daily_water_usage(year=2021):
    """Daily water usage"""

    # read from influx db
    client = InfluxDBClient(url=url, token=token, org=org)
    query_api = client.query_api()

    p = {"_start": datetime(year, 1, 1),
         "_stop": datetime(year, 12, 31),
         "_measurement": "water_consumption",
         "_field": "water_consumption"
         }

    # read into dataframe
    data_frame = query_api.query_data_frame('''
            from(bucket: "utilities")
                |> range(start: _start, stop: _stop)
                |> filter(fn: (r) => r["_measurement"] == _measurement)
                |> filter(fn: (r) => r["_field"] == _field)
                |> aggregateWindow(every: 24h, fn: sum, createEmpty: false)
                ''', params=p)

    # loop over the dataframe and plot a point for each hour of day
    time = data_frame["_time"]
    hour = [t.hour for t in time]
    month = [t.month for t in time]
    day = [(t.toordinal() - datetime(t.year, 1, 1).toordinal() +1) for t in time]
    water_usage = data_frame["_value"] * 28.3168

    fig, ax = plt.subplots()
    cmap = plt.get_cmap('hsv')

    scatter = ax.scatter(day, water_usage, c=month, cmap=cmap, s=5)
    # ax.plot(day, water_usage)
    ax.set_xlim([0, 364])

    plt.xlabel("Day of year")
    plt.ylabel("Water Usage (liters)")
    plt.title("{:g} Water Usage".format(year))
    plt.grid(axis='both', alpha=0.5)
    plt.show()

    client.close()


if __name__ == "__main__":
    annual_power_usage()
