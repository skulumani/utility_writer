
from datetime import datetime, time
import pytz
import argparse

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, PointSettings
from influxdb_client.client.write.dataframe_serializer import data_frame_to_list_of_points
 
import pandas

url = "http://192.168.88.12:8086"
token = "pc5XzRSoA7b_CKgpl6yiyxCiLmEo-Y36l8jRMKXTkNxDNPU3jiQIgBk5ZtIXU3WUPYhzqMgNaPW8tif02O0OfA=="
org = "wolverines"

bucket = "utilities" # "investments"

def ingest_dataframe(df, measurement_name, tag_columns):
    """Write data"""

    point_settings = PointSettings()
    # point_settings.add_default_tag("units", "Wh")
    # point_settings.add_default_tag("source", "enphase")

    points = data_frame_to_list_of_points(data_frame=df,
                                          point_settings=point_settings, 
                                          data_frame_measurement_name=measurement_name,
                                          data_frame_tag_columns=tag_columns)
    
    client = InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api()

    # line protocol: measurementName,tagKey=tagValue fieldKey="fieldValue" timestamp
    # write_api.write(bucket=bucket, org=org, record=df, 
    #                 data_frame_measurement_name=measurement_name,
    #                 data_frame_tag_columns=tag_columns)
    write_api.write(bucket=bucket, org=org, record=points)

    write_api.close()
    client.close()

def ingest_panel_data(time_list, panel_list, serial_num, measurement_name, source, units):
    """Ingest panel data"""

    data = {"time": time_list, measurement_name: panel_list}
    df = pandas.DataFrame(data)
    df = df.assign(serial_num=serial_num)
    df = df.assign(source=source)
    df = df.assign(units=units)
    df = df.set_index("time")

    ingest_dataframe(df, measurement_name=measurement_name, tag_columns=["serial_num", "source", "units"])


def ingest_system_data(time_list, system_list, measurement_name, source, units):
    """Ingest system panel data"""
        
    data = {"time": time_list, measurement_name: system_list}
    df = pandas.DataFrame(data)
    df = df.assign(source=source)
    df = df.assign(units=units)
    df = df.set_index("time")
    ingest_dataframe(df, measurement_name=measurement_name,
                     tag_columns=["source", "units"])

def write_point(time, measurement, measurement_name, tag_dict):
    """Write a single point to influxdb"""
    client = InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api()

    p = Point(measurement_name).field(measurement_name, measurement).time(time, WritePrecision.MS)
    for k,v in tag_dict.items():
        p = p.tag(k, v)


    write_api.write(bucket=bucket,org=org, record=p)

    write_api.close()
    client.close()
