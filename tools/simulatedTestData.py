#!/usr/bin/env python
"""simulatedTestData.py: Generates test time-series data and sends to an influx\
 DB, CSV file or console (default)."""

# Import built-in modules
import argparse
from datetime import datetime, timedelta

# Import third-party modules
from matplotlib import pyplot as plt
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import numpy as np
import pandas as pd

# Authorship information
__author__ = "James Bott"
__copyright__ = "Copyright 2024, James Bott"
__credits__ = ["James Bott"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "James Bott"
__email__ = "https://github.com/bott-j"
__status__ = "Development"

# Create random walk samples
def createDataRandomWalk(n = 1000):
	""" Creates a random walk dataset."""
	# Time indecies
	x = [i for i in range(0, n)]

	# Creae random walk
	y = np.zeros(n)
	for i in range(1, n):
		y[i] = y[i-1] + np.random.random()*2-1
	
	return x, y

# Create cloud samples using a Markov decision process (MDP)
def createDataClouds(n = 1000, 
		r = 1, 
		pCloud = 0.025,
		pNoCloud = 0.026, 
		minAtt = 0.3, 
		maxAtt = 0.6):
	""" Creates cloud profile using MDP. """
	# Time indecies
	x = [i for i in range(0, n)]
	
	# Approximate irradiance as half of sine wave
	y = np.sin([np.pi*(y-n*0.05)/(n*0.9) if y > 0.05*n 
		and y < 0.95*n else 0 for y in x])

	# Apply moving average function to smooth edges by convolution
	y = np.convolve(y, np.ones(int(n*0.1))/int(n*0.1), 'same')

	# Apply MDP to create scaling for clouds
	scaling = np.ones(n)
	for i in range(1, n):
		if((scaling[i-1] == 1 and np.random.random() <= pCloud)
			or (scaling[i-1] != 1 and np.random.random() > pNoCloud)):
			scaling[i] = minAtt + np.random.random() * (maxAtt - minAtt)
	
	# Apply scaling to time series irradiance values
	y = np.multiply(y, scaling)

	return x, y

# If run from command line
if __name__ =="__main__":

	# Handle arguments
	parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS, 
		description="Generates test time-series data and sends to an influx\
 DB, CSV file or display (default).")
	outputGroup = parser.add_mutually_exclusive_group()
	outputGroup.add_argument('--influx2', 
		nargs=6, 
		type=str,
		help="Send data to influxdb v2",
		metavar=("url", "org", "bucket", "token", "measurement", "field"),
		default=None)
	outputGroup.add_argument('--file', 
		nargs=3, 
		type=str,
		help="Save data to influxdb style CSV file",
		metavar=("filename", "measurement", "field"),
		default=None)
	outputGroup.add_argument('--display',
						action="store_true",
						help="Display profile data using Matplotlib") 
	parser.add_argument('--profile', 
						nargs=1, 
						type=str,
						help="Type of profile",
						metavar=("profile"),
						choices=("randomwalk", "clouds"),
						default=None)
	args = parser.parse_args()

	# Generate the profile data
	if(args.profile is None
		or args.profile[0] == "randomwalk"):
		nPoints = 1000
		x, y = createDataRandomWalk(n = nPoints)
	elif(args.profile[0] == "clouds"):
		nPoints = 6*60*60
		x, y = createDataClouds(n = nPoints)
	
	# Handle sending to influxdb
	if(args.influx2):
		print("Writing to influxdb v2...")

		# Connection parameters		
		url = args.influx2[0]
		org = args.influx2[1]
		bucket = args.influx2[2]
		token = args.influx2[3]
		measurement = args.influx2[4]
		field = args.influx2[5]

		# Create client and write api object		
		client = InfluxDBClient(url=url, token=token, org=org)
		write_api = client.write_api(write_options=SYNCHRONOUS)

		# Write the points
		t = list(map(lambda x: datetime.utcnow() 
			+ timedelta(seconds = float(x-nPoints)),x))
		df = pd.DataFrame(data = y, index = t, columns=[field])
		write_api.write(bucket=bucket, 
			org=org, 
			record=df, 
			data_frame_measurement_name=measurement)

		print("done.")

	# Handle save to CSV file
	elif(args.file):
		print("Writing to CSV file...")

		# Parameters for file operation
		filename = args.file[0]
		measurement = args.file[1]
		field = args.file[2]

		# Create pandas dataframe		
		t = map(lambda x: (datetime.utcnow() 
			+ timedelta(seconds = float(x-1000)))
			.isoformat(timespec='microseconds')+'000Z',x)
		df = pd.DataFrame(
			data = [["","",0,row[0],row[0],row[0],row[1],field,measurement] \
				for row in zip(t, y)], 
				index = x, 
				columns=["", 
						 "result", 
						 "table", 
						 "_start", 
						 "_stop", 
						 "_time", 
						 "_value", 
						 "_field", 
						 "_measurement"])
		
		# Write to CSV file
		with open(filename, "w") as file:
			file.write("#group,false,false,true,true,false,false,true,true\n")
			file.write("#datatype,string,long,dateTime:RFC3339,dateTime:"
					 + "RFC3339,dateTime:RFC3339,double,string,string\n")
			file.write("#default,mean,,,,,,,\n")
			df.to_csv(file, index=False, line_terminator='\n')

		print("done.")

	# Display the data using Matplotlib (default)
	else:
		plt.plot(list(map(lambda x: datetime.utcnow() 
			+ timedelta(seconds=float(x-1000)), x)), y)
		plt.title("Simulated Data")
		plt.xlabel("Time")
		plt.ylabel("Magnitude")
		plt.grid()
		plt.tight_layout()
		plt.show()