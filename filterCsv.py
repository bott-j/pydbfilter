import argparse
import pandas as pd
import numpy as np
from dbfilterTree import DeadbandFilterTree

# If run from command line
if __name__ =="__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS,
        description="Applies deadband filtering to influxdb CSV exports.")
    parser.add_argument('infile',
        type=str,
        help="Filename of input CSV file")
    parser.add_argument('outfile', 
        type=str,
        help="Filename of output CSV file")
    args = parser.parse_args()

    # Setup initial filter structure
    globalFilter = DeadbandFilterTree(0.1, 60)
    measurements = {"my_measurement" : {"temperature" : globalFilter}}
    allowedTags = ["location"]
    
    # Load CSV data
    df = pd.read_csv(args.infile, header=3)
    output = list()

    # filter each point in list
    for index, row in df.iterrows():

        # Apply filter
        if(row['_measurement'] in measurements.keys()
            and row['_field'] in measurements[row['_measurement']].keys()):
            
            # Create list of tags associated with this data
            tags = [(tag, row[tag]) for tag in allowedTags if tag in df.columns]

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
    for (tags, filter) in [([], globalFilter)] + globalFilter.getAllChildren():
        newData = filter.flush()
        if(newData):
            newRow = dict()
            newRow["_start"] = newData[0]
            newRow["_stop"] = newData[0]
            newRow["_time"] = newData[0]
            newRow["table"] = 0
            newRow["_value"] = newData[1]
            newRow["_measurement"] = "my_measurement"
            newRow["_field"] = "temperature"
            for (tagName, tagValue) in tags:
                newRow[tagName] = tagValue
            output += [newRow]

    # Convert to pandas dataframe    
    dfOutput = pd.DataFrame(data=output)

    # Save to output CSV file
    dfOutput.to_csv(args.outfile, index=False)