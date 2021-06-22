
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
    point_settings.add_default_tag("units", "Wh")
    point_settings.add_default_tag("source", "enphase")

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
