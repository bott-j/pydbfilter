import pandas as pd
import numpy as np
from dbfilterTree import DeadbandFilterTree

# If run from command line
if __name__ =="__main__":

    # Parse arguments

    # Setup initial filter structure
    measurements = {"my_measurement" : {"temperature" : DeadbandFilterTree(0.1, 60)}}
    allowedTags = ["location"]
    # Load CSV data
    df = pd.read_csv("query.csv", header=3)
    time = pd.to_datetime(df['_time']).astype(np.int64)

    # filter each point in list
    for index, row in df.iterrows():
        # Apply filter
        if(row['_measurement'] in measurements.keys()
            and row['_field'] in measurements[row['_measurement']].keys()):
            
            # Create list of tags associated with this data
            tags = [(tag, row[tag]) for tag in allowedTags if tag in df.columns]

            # Retrieve filter from tree datastructure by tag                                
            #filter = findfilter(row['_measurement'], row['_field'], tags)
            #filter.filter(row['_value'])

    # Force the last point to be stored for each fitler

    # Save to output CSV file
