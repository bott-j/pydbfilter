#!/usr/bin/env python
"""influxFilterProxy.py: Influx DB proxy server with deadband filtering."""

# Import built-in modules
import argparse
import re
import socketserver
import threading
import urllib.parse as urlparse

# Import third-party modules
import http.server
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import numpy as np
import pandas as pd

# Import custom modules
from pydbfilter import DeadbandFilterTree

# Authorship information
__author__ = "James Bott"
__copyright__ = "Copyright 2024, James Bott"
__credits__ = ["James Bott"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "James Bott"
__email__ = "https://github.com/bott-j"
__status__ = "Development"

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass
    
class InfluxProxyHttpHandler(http.server.SimpleHTTPRequestHandler):
    _client : InfluxDBClient = None
    _linePattern : re.Pattern = re.compile('^([^,]+)(,([^ ]*))? ([^ ]+) ([0-9]+)$')
    _url : str = None 
    _lastvalue : bool = None
    _measurements : dict = None
    _tags : list = None

    def __init__(self, url, lastvalue, measurements, tags):
        """ Class constructor. """
        self._url = url
        self._lastvalue = lastvalue
        self._measurements = measurements
        self._tags = tags 
        return

    def __call__(self, *args, **kwargs):
        """ Call SimpleHTTPRequestHandler method. """
        super().__init__(*args, **kwargs)
        return

    def handle_line(self, line):
        """ Handles a line of influx line protocol from the request. """
        points = list()

        # Attempt to match the line
        m = re.match(self._linePattern, line)

        # If a measurement has been detected
        if(m):
            measurement = m.group(1) 
            tag_set = m.group(3)
            field_set = m.group(4)
            timestamp = m.group(5)

            # Parse tag set to dictionary
            if(tag_set):
                tags = {tag.split("=")[0] : tag.split("=")[1] for tag in tag_set.split(",")}
            else:
                tags = {}

            # Parse field set to dictionary
            fields = {field.split("=")[0] : field.split("=")[1] for field in field_set.split(",")}

            # Apply filter
            for field in fields.keys():
                if(measurement in self._measurements.keys()
                    and field in self._measurements[measurement].keys()):

                    # Retrieve filter from tree datastructure by tag   
                    filter = self._measurements[measurement][field].walk(sorted(tags.items()))

                    # Apply filter to data
                    newData = filter.filter(pd.to_datetime(int(timestamp)).to_numpy(np.int64), fields[field])
                    for data in newData:
                        # Add the data to the queue to be forwarded to the real influxdb server
                        points += [{
                            "measurement" : measurement, 
                            "tags" : tags, 
                            "fields" : {field : data[1]}, 
                            "time" : data[0]
                            }]

        return points

    def do_POST(self):
        """ Handles the HTTP post request from the client. """
        points = list()

        # Create the client
        if(self._client is None):
            # Parse the query string
            uri, queryString = self.path.split("?")
            query = urlparse.parse_qs(queryString)

            # Create the influxdb client connection
            self._client = InfluxDBClient(
                url=self._url, 
                token=self.headers["Authorization"].split(" ")[1], 
                org=query['org']
                )
            self._writeApi = client.write_api(write_options=SYNCHRONOUS)
            
        # Get the content length
        nContent = int(self.headers['Content-Length'])
        
        # Read the content
        content = self.rfile.read(nContent).decode("UTF-8")

        # Split by lines and handle each line
        for line in content.split("\n"):
            points += self.handle_line(line)

        # Send response headers to client
        self.send_response(200)
        self.end_headers()

        # Forward cached data to the real influxdb server
        self._writeApi.write(
            query['bucket'], 
            query['org'], 
            points
            )

        # Close influxdb client connection
        client.close()

        return

# main script 
if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Influx Database proxy server with deadband filtering.")
    parser.add_argument('host',
        type=str,
        help="IP address to bind server to.")
    parser.add_argument('port',
        type=int,
        help="TCP port to listen on.")
    parser.add_argument('server_url', 
        type=str,
        help="URL of Influx server in format http://host:port")
    parser.add_argument('--lastvalue', 
        action="store_true",
        help="Always forward the last value on close of input stream")
    parser.add_argument('--fields',
        nargs=4,
        metavar=("measurement", "field", "deadband", "minimum interval"),
        action="append",
        default=[],
        help="Measurement/field values for which filtering will be applied")
    parser.add_argument('--tags',
        nargs="+",
        default=[],
        help="Allowed tags")
    args = parser.parse_args()

    # Setup initial filter structure
    measurements = dict()
    for measurement, field, deadband, mininterval in args.fields:
        measurements[measurement] = {field : DeadbandFilterTree(float(deadband), float(mininterval))}

    try:
        # Create the server, binding to HOST on PORT
        handler = InfluxProxyHttpHandler(args.server_url, args.lastvalue, measurements, args.tags)
        server = ThreadedTCPServer((args.host, args.port), handler)
        server.allow_reuse_address = True 
        
        # create a thread for the server and start
        serverthread = threading.Thread(target = server.serve_forever)
        serverthread.daemon = True
        serverthread.start()
            
        # wait for user input
        input("Press enter or CTRL-C to exit\n")
        
    except KeyboardInterrupt:
        pass

    finally:
        print("Exiting...")
        # Shutdown HTTP server
        server.shutdown()
        server.server_close()
        serverthread.join()