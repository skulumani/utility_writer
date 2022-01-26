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


def daily_power_usage(year=2021):
    """Read power usage
    
    Get power usage for each day of the year
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
    print("Sum: {}".format(sum(energy)))
    plt.xlabel("Day of Year")
    plt.ylabel("Energy (kWh)")
    plt.title("{:g} Energy Usage".format(year))
    plt.grid(axis='both', alpha=0.5)
    plt.show()

    client.close()
def hourly_power_usage(year=2021):
    """Read power usage
    
    Get power usage for each hour of each day
    Plot as point for entire year
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
    
    fig, ax = plt.subplots()
    cmap = plt.get_cmap('hsv')

    scatter = ax.scatter(hour, energy, c=month, cmap=cmap, s=5)
    ax.set_xlim([0, 23])
    
    # legend
    # legend = ax.legend(*scatter.legend_elements(), title="Month", loc="upper right",
    #                 mode="expand", ncol=12)

    plt.xlabel("Hour")
    plt.ylabel("Energy (kWh)")
    plt.title("{:g} Energy Usage".format(year))
    plt.grid(axis='both', alpha=0.5)
    plt.show()

    client.close()

def hourly_solar_power(year=2021):
    """Read and plot solar power from influxdb

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
    power = data_frame["_value"]/1000

    fig, ax = plt.subplots()
    cmap = plt.get_cmap('hsv')

    scatter = ax.scatter(hour, power, c=month, cmap=cmap, s=5)
    ax.set_xlim([0, 23])

    plt.xlabel("Hour")
    plt.ylabel("Power (kW)")
    plt.title("{:g} Solar Power".format(year))
    plt.grid(axis='both', alpha=0.5)
    plt.show()

    client.close()

def daily_solar_energy(year=2021):
    """Energy from each day of the year"""

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
