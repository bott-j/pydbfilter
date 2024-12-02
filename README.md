# pydbfilter
A dead-band filter Python module together with tools for processing of influxdb TCP/IP line protocol streams and CSV data files.

GETTING STARTED

To process CSV file exports from InfluxDB:

  $python filterCsv.py query-input.csv query-output.csv --fields MEASUREMENT_NAME FIELD_NAME DEADBAND MAX_INTERVAL

Where MEASUREMENT_NAME is the measurement name to be processed, and FIELD_NAME is the FIELD_NAME to be processed. The values DEADBAND and MAX_INTERVAL specify the deadband to be applied to the raw field value and maximum time gap between field updates. 

The filename query-input.csv is the export from InfluxDB and query-output.csv is the saved output CSV file.

Multiple --fields options can be passed to the script to apply the deadband to different measurements and fields.
