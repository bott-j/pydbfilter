import re
import socketserver
import dbfilterTree

measurements = {"test" : {"temperature" : dbfilterTree(0.1, 60)}}

class DbFilterRequestHandler(socketserver.StreamRequestHandler):

        def findfilter(measurement, field, tags):
            result = None

            # If in predefined measurements
            if measurement in measurements.keys():
                # If in predefined fields
                if field in measurements[measurement].keys():
                    result = measurements[measurement][field].walk(sorted(tags.items()))

            return result

        def handle_line(self, line):
            
            # Extract data from the line protocol text 
            m = re.match('^([^,]+),([^ ]*) ([^ ]+) ([0-9]+)$',line)

            # If a measurement has been detected
            if(m):
                measurement = m.group(1) 
                tag_set = m.group(2)
                field_set = m.group(3)
                timestamp = m.group(4)

                # If allowed measurement
                if(measurement in allowedMeasurements):
                    tags = {tag.split("=")[0] : tag.split("=")[1] for tag in tag_set.split()}
                    fields = {field.split("=")[0] : field.split("=")[1] for field in field_set.split()}

                    # For each field
                    for field in fields.keys():
                        # If a filter applies to this field
                        if(field in allowedFields):
                            # Filter applies to field but is indexed on tags
                            filter = findfilter(measurement, field, tags)
                            newValue = filter.filter(float(fields[field]))
                            float(fields[field]) = str(newValue)

            return

        def writePoint(self, measurement, tags, fields, timestamp):
            
            # Compose the point description

            # Write points to the server

            return

        def handle(self):
                
            # reset the string data
            self.data_string = list()
            for i in range(len(string_bays)):
                self.data_string.append(dict())

            
            #print("{} wrote:".format(self.client_address[0]))    
            self.data = self.rfile.readline().strip()
            
            http_data = ""
            
            # set counter for start of battery group
            self.cBatteries = 0
            
            while 1:
                
                buffer = self.rfile.readline().decode("utf-8")

                if len(buffer) > 0:
                    if buffer[0] == '0':
                        http_data = http_data + buffer
                        break
                    else:
                        http_data = http_data + buffer
                        self.handle_line(buffer)
            
            return