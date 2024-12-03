# pydbfilter
A dead-band filter Python module together with tools for processing of influxdb TCP/IP line protocol streams and CSV data files.

[Description](#description)

[Getting Started](#getting-started)

[Program Arguments](#program-arguments)

## Description

![Point will be accepted if it exceeds the linear boundary lines determined from last two accepted points.](image.jpg?raw=true)

## Getting Started

To process CSV file exports from InfluxDB:

  $python filterCsv.py query-input.csv query-output.csv --fields MEASUREMENT_NAME FIELD_NAME DEADBAND MAX_INTERVAL

Where MEASUREMENT_NAME is the measurement name to be processed, and FIELD_NAME is the FIELD_NAME to be processed. The values DEADBAND and MAX_INTERVAL specify the deadband to be applied to the raw field value and maximum time gap between field updates. 

The filename query-input.csv is the export from InfluxDB and query-output.csv is the saved output CSV file.

Multiple --fields options can be passed to the script to apply the deadband to different measurements and fields.

## Program Arguments

### influxFilterProxy.py

usage: influxFilterProxy.py [-h] [--lastvalue] [--fields measurement field deadband minimum interval]
                            [--tags TAGS [TAGS ...]]
                            host port server_url

Influx Database proxy server with deadband filtering.

positional arguments:
  host                  IP address to bind server to.
  port                  TCP port to listen on.
  server_url            URL of Influx server in format http://host:port

optional arguments:
  -h, --help            show this help message and exit
  --lastvalue           Always forward the last value on close of input stream
  --fields measurement field deadband minimum interval
                        Measurement/field values for which filtering will be applied
  --tags TAGS [TAGS ...]
                        Allowed tags

### filterCsv.py

usage: filterCsv.py [-h] [--lastvalue] [--fields measurement field deadband minimum interval] [--tags TAGS [TAGS ...]]
                    infile outfile

Applies deadband filtering to influxdb CSV exports.

positional arguments:
  infile                Filename of input CSV file
  outfile               Filename of output CSV file

optional arguments:
  -h, --help            show this help message and exit
  --lastvalue           Always save the last value in the input data to the output file
  --fields measurement field deadband minimum interval
                        Measurement/field values for which filtering will be applied
  --tags TAGS [TAGS ...]
                        Allowed tags