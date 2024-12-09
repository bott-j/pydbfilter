# pydbfilter

An Python package implementing time series compression algorithms including swing door trending, deadband and hysteresis. Also included is an InfluxDB proxy server to compress and forward line data protocol to an Influx time-series database, and tools for CSV processing.  

* [Getting Started](#getting-started)
* [Program Arguments](#program-arguments)
* [Algorithms](#algorithms)
* [Running Unit Tests](#running-unit-tests)

## Getting Started

### Running the Proxy Server

The InfluxDB proxy server can be started by running the influxFilterProxy.py Python script. This runs a HTTP server on the specified port which will accept incomming InfluxDB line protocol data, apply the deadband compression to the data, then forward the data to the nominated InfluxDB server.

To run the server, use the format:

```
  $ python influxFilterProxy.py HOST PORT URL --fields MEASUREMENT_NAME FIELD_NAME DEADBAND MAX_INTERVAL --tags TAG_1 TAG_2 TAG_N
```

Where MEASUREMENT_NAME is the measurement name to be processed and FIELD_NAME is the name of the field to be processed. The values DEADBAND and MAX_INTERVAL specify the deadband to be applied to the raw field value and maximum time gap between field updates. Multiple "--fields" options can be passed to the script to apply the compression to different measurements and fields. The list of tags follow the "--tags" option specifies which tags should be used to differentiate between filtered measurements. For example, if a tag "location" is specified, compression will be applied independently between subsets of the data which differ by value of the "location" tag. 

Here "HOST" and "PORT" are the local IP address and port for the proxy server to listen on. "URL" should point to the final InfluxDB server which the data will be forwarded to. 

For example, to setup the proxy server to listen on address 127.0.0.1 and port 8087, then forward the data to port 8086 at the InfluxDB server at address 10.0.0.10, the following command could be used:

```
  $ python influxFilterProxy.py 127.0.0.1 8087 "http://10.0.0.10:8086" --fields my_measurement temperature 0.1 10000 --tags location
```

In this example the compression will be applied to the "temperature" field of the measurement named "my_measurement", with deadband of 0.1 and maximum interval between points of 10'000 ms. The "location" tag will be used to differentiate between subsets of data which should be compressed independantly of each other.

### Processing CSV Files

To process CSV file exports from InfluxDB:

```
  $ python filterCsv.py query-input.csv query-output.csv --fields MEASUREMENT_NAME FIELD_NAME DEADBAND MAX_INTERVAL --tags location
```

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
## Algorithms

### Swinging Door trending

Swinging door trending is an algorithm which attempts to reduce a time series signal into a linear trend consisting of points between parallelogram envelopes [1]. As points are presented, the algorithm extends the current envelope fit the points. When a data point is presented which would cause the height of the current envelope to exceed a defined limit the algorithm generates a point marking the boundary of a new envelope is which created. The parallelogram is limited in height by a parameter referred to as the compression deviation. The compression deviation is the maximum height of each vertical edge of a parallelogram, and it determines how far the input points within the envelope deviate from the trend lines in the output of the algorithm. The algorithms name comes from the effect of widening the top and bottom sides of the envelope until a parallelogram is formed with parallel sides, which can be likened to doors swinging open.

![Output points form a linear trend where each line segment is the longitudinal center line of a parallelogram envelope.](images/sdt1.png?raw=true)

At run-time, several states are retained by the algorithm in order to track the boundaries of the current envelope. The algorithm is initialised when the first value (FV1) is received. Referring to the figure below two points are calculated; the upper pivot (pu) and lower pivot (pl) which are a distance CD above and below p1. The line formed between these points is the left-hand-side of the first parallelogram. Two gradients, the sloping upper max (mu,max) and sloping upper min (ml,min) are initialised to infinity. These gradients, together with the upper and lower pivot, track the top and bottom edges of the envelope.

![First point determines the middle of the left-hand-side edge for the parallelogram envelope.](images/sdt2.png?raw=true)

Once a second point is received, gradients are calculated between the upper and lower pivots to the new point (p2). Using these gradients, the top and bottom sides of the envelope are widened to accommodate the new point.

![Top and bottom edges of parallelogram are widened to accomodae the new point.](images/sdt3.png?raw=true)

Referring to the figure below, the process continues as more points are received and the envelope defined by mu,max and ml,min is further widened as required.

![Top and bottom edges of parallelogram are continue to be widened to accomodae new points.](images/sdt4.png?raw=true)

At a certain point, a measurement may be presented which would cause the right-hand-side of the envelope to exceed the compression deviation limit. This occurs when the mu,max and ml,min gradients are diverging away from each other. Under this condition, a new output point will be generated by the algorithm. The output point is calculated by first setting the gradient which caused the divergence to be the same as the opposite gradient, resulting in parallel top and bottom edges for the parallelogram. 

![New point causes the top and bottom edges of the envelope to diverge.](images/sdt5.png?raw=true)

The point of intersection between this gradient and the line between the latest and previous input points is found, which is the upper right corner of the parallelogram. The centre of the right-hand side of the parallelogram is then calculated which is the value of the output point generated by the algorithm. 

![Remaining points forming corners of parallelogram are found.](images/sdt6.png?raw=true)

The first value is redefined as the output point of the algorithm and new upper and lower pivots calculated. The gradients mumax and mlmin will be recalculated as the gradients between the latest input point and the upper and lower pivots respectively. As new input points are received the envelope is expanded until the compression deviation limit and the process continues. 

![Process is repeated to build further parallelogram envelopes.](images/sdt6.png?raw=true)

### Deadband

In this algorithm a deadband value sets a range which must be exceeded for the algorithm to generate a new point. The first point that is received is the base value which future points are compared to. For each point, if the difference in value between the value of that point and the value of the base point is less than or equal to the deadband that point will be ignored. If the difference in value exceeds the deadband the algorithm will return that point and the value will be used as the future base value.

![Deadband algorithm.](images/db1.png?raw=true)

### Hysteresis

This algorithm applies hysteresis to the input data. A delta value is accumulated which is the difference between the minimum and maximum value for past points. When this delta exceeds the configured hysteresis value a new output point is generated by the algorithm. The delta value is reset and continues to be accumulated for future values as the process repeats.

![Hysteresis algorithm.](images/hyst1.png?raw=true)

## Running Unit Tests

Pytest unit tests are located in the "./test/" sub-directory. Unit tests and code coverage analysis may be run by starting the "run_all_tests.py" Python script without arguments. 

## References

[1] 	J. D. A. Correa, C. Montez, A. S. R. Pinto and E. M. Leao, “Swinging Door Trending Compression Algorithm for IoT Environments,” IX Simpósio Brasileiro de Engenharia de Sistemas Computacionais, 2019. 