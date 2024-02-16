from datetime import datetime
import apache_beam as beam


class ConvertDateToDatetime(beam.DoFn):
    def __init__(self, columnname, desired_format):
        self.columnname = columnname
        self.desired_format = desired_format

    def process(self, element):

        element[self.columnname] = element[self.columnname].strftime(
            self.desired_format
        )
        yield element
