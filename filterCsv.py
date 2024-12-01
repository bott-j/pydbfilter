#!/usr/bin/env python
"""filterCsv.py: Applies deadband fitlering to exported CSV files from\
 influxdb v2."""
 
 # Import built-in modules
import argparse

# Import third-party modules
import pandas as pd
import numpy as np

# Import custom modules
from dbfilterTree import DeadbandFilterTree

# Authorship information
__author__ = "James Bott"
__copyright__ = "Copyright 2024, James Bott"
__credits__ = ["James Bott"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "James Bott"
__email__ = "https://github.com/bott-j"
__status__ = "Development"

# If run from command line
if __name__ =="__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Applies deadband filtering to influxdb CSV exports.")
    parser.add_argument('infile',
        type=str,
        help="Filename of input CSV file")
    parser.add_argument('outfile', 
        type=str,
        help="Filename of output CSV file")
    parser.add_argument('--lastvalue', 
        action="store_true",
        help="Always save the last value in the input data to the output file")
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
    
    # Allowed tags
    allowedTags = args.tags
    
    # Load CSV data
    dfInput = pd.read_csv(args.infile, header=3)
    output = list()

    # filter each point in list
    for index, row in dfInput.iterrows():

        # Apply filter
        if(row['_measurement'] in measurements.keys()
            and row['_field'] in measurements[row['_measurement']].keys()):
            
            # Create list of tags associated with this data
            tags = [(tag, row[tag]) for tag in allowedTags if tag in dfInput.columns]

            # Retrieve filter from tree datastructure by tag   
            filter = measurements[row['_measurement']][row['_field']].walk(sorted(tags))

            # Apply filter to data
            newData = filter.filter(pd.to_datetime(row['_time']).to_numpy(np.int64), row['_value'])
            if(newData):
                newRow = row.to_dict()
                newRow["_time"] = newData[0]
                newRow["_value"] = newData[1]
                output += [newRow]

    # Force the last point to be stored for each fitler
    for measurement, fields in measurements.items():
        for field, filter in fields.items():
            if(args.lastvalue):
                for (tags, filter) in [([], filter)] + filter.getAllChildren():
                    newData = filter.flush()
                    if(newData):
                        newRow = dict()
                        newRow["_start"] = newData[0]
                        newRow["_stop"] = newData[0]
                        newRow["_time"] = newData[0]
                        newRow["table"] = 0
                        newRow["_value"] = newData[1]
                        newRow["_measurement"] = measurement
                        newRow["_field"] = field
                        for (tagName, tagValue) in tags:
                            newRow[tagName] = tagValue
                        output += [newRow]

    # Convert to pandas dataframe    
    dfOutput = pd.DataFrame(data=output)

    # Save to output CSV file
    dfOutput.to_csv(args.outfile, index=False)