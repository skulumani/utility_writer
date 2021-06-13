# Utility Writer

Write utility data from

* Pepco
* Enphase Solar
* DCWater

to the influxdb 

# Installation

~~~
conda env create -f environment.yml
~~~

# TODO

* Add [enphase API](https://github.com/chrisroedig/py-enphase-enlighten) library
* Add pvoutput API library - write Pepco data to pvoutput
* Add conda enviornment file
* Move secrets to a seperate file

# Libraries

* [Enlighten API](https://github.com/danielpatenaude/python_enlighten_api) - standard version
* [Contractor enlighten](https://github.com/chrisroedig/py-enphase-enlighten) - better version for panel data
