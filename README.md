# pydbfilter
A Python implementing a swing door compression algorithm together with tools for processing of InfluxDB TCP/IP line protocol streams and CSV data files.

[Description](#description)

[Getting Started](#getting-started)

[Program Arguments](#program-arguments)

[Program Arguments](#running-unit-tests)

## Description

The program applies Swing Door Trending (SDT) to each field (data point) within the Influx time-series data.

![Point will be accepted if it exceeds the linear boundary lines determined from last two accepted points.](image.jpg?raw=true)

## Getting Started

### Running the Proxy Server

The InfluxDB proxy server can be started by running the influxFilterProxy.py Python script. This runs a HTTP server on the specified port which will accept incomming InfluxDB line protocol data, apply the deadband compression to the data, then forward the data to the nominated InfluxDB server.

To run the server, use the format:

  $ python influxFilterProxy.py HOST PORT URL --fields MEASUREMENT_NAME FIELD_NAME DEADBAND MAX_INTERVAL --tags TAG_1 TAG_2 TAG_N

Where MEASUREMENT_NAME is the measurement name to be processed and FIELD_NAME is the name of the field to be processed. The values DEADBAND and MAX_INTERVAL specify the deadband to be applied to the raw field value and maximum time gap between field updates. Multiple "--fields" options can be passed to the script to apply the compression to different measurements and fields. The list of tags follow the "--tags" option specifies which tags should be used to differentiate between filtered measurements. For example, if a tag "location" is specified, compression will be applied independently between subsets of the data which differ by value of the "location" tag. 

Here "HOST" and "PORT" are the local IP address and port for the proxy server to listen on. "URL" should point to the final InfluxDB server which the data will be forwarded to. 

For example, to setup the proxy server to listen on address 127.0.0.1 and port 8087, then forward the data to port 8086 at the InfluxDB server at address 10.0.0.10, the following command could be used:

  $ python influxFilterProxy.py 127.0.0.1 8087 "http://10.0.0.10:8086" --fields my_measurement temperature 0.1 10000 --tags location

In this example the compression will be applied to the "temperature" field of the measurement named "my_measurement", with deadband of 0.1 and maximum interval between points of 10'000 ms. The "location" tag will be used to differentiate between subsets of data which should be compressed independantly of each other.

### Processing CSV Files

To process CSV file exports from InfluxDB:

  $ python filterCsv.py query-input.csv query-output.csv --fields MEASUREMENT_NAME FIELD_NAME DEADBAND MAX_INTERVAL --tags location

The filename query-input.csv is the export from InfluxDB and query-output.csv is the resulting compressed CSV file. The "--fields" and "--tags" options are the same as for proxy server script described previously.

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

## Running Unit Tests

Pytest unit tests are located in the "./test/" sub-directory. Unit tests and code coverage analysis may be run by starting the "run_all_tests.py" Python script without arguments. 