# Utility Writer

Write utility data from

* Pepco
* Enphase Solar
* DCWater

to the influxdb 

# Usage

1. Download power usage and water usage
2. Get solar production data

~~~
conda activate utilities
python driver.py <start YYYYMMDD> <end YYYYMMDD>
~~~

3. Get power and water usage

~~~
conda activate utilities
python write_influxdb.py <path to power.csv> <path to water.csv>
~~~

# Installation

~~~
conda env create -f environment.yml
~~~

Rename `config_example.py` to `config.py`

Fill in config information with enphase contractor account and influxdb credentials

# TODO

* [ ] Add [enphase API](https://github.com/chrisroedig/py-enphase-enlighten) library
* [ ] Add pvoutput API library - write Pepco data to pvoutput
* [x] Add conda enviornment file
* [x] Move secrets to a seperate file

# Libraries

* [Enlighten API](https://github.com/danielpatenaude/python_enlighten_api) - standard version
* [Contractor enlighten](https://github.com/chrisroedig/py-enphase-enlighten) - better version for panel data
