# Sunrise Data Engineer Assessment

## Introduction

The objective of this assessment is to getting the data from Teradata and write it onto Bigquery table/or file.
## Getting Started

To run this project, you need to do the following:

- Firstly, build the docker image with command in below.

      docker build -t your_image_name

- After that, you can run the code with the following command.

      docker run --rm -it --entrypoint bash your_image_name

- Lastly you will be in /template inside of the docker container which is your workdir. so you can run your code with following command.

      python main.py --arg1 argvalue1 --arg2 argvalue2

      Example: python main.py --teradata_host value --teradata_database value --teradata_user value --teradata_password value --teradata_table value --output  "\template" --desired_format "%Y-%m-%d %H:%M:%S" --column value

## Project Files

The project is organized into the following files.
- app.py -> contains function to convert data column to the desired format
- main.py -> main file to run the program
- requirements.txt -> contains dependencies
- Dockerfile -> to make our code containerized. 

## main.py

```python
import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from google.cloud import secretmanager
from google.cloud import bigquery
import teradatasql
import logging
from apache_beam.io import WriteToText
from function import ConvertDateToDatetime


def read_teradata(query, connection_config):
    logging.info(f"Executing query: {query}")
    with teradatasql.connect(**connection_config) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                yield dict(zip(columns, row))

    logging.info("Query execution completed.")


def run(args):
    # Set up the Dataflow pipeline

    with beam.Pipeline(options=beam_options) as p:
        # Read data from Teradata
        teradata_data = p | "Read from Teradata" >> beam.Create(
            read_teradata(
                query=f"SELECT * FROM {args.teradata_table}",
                connection_config={
                    "host": args.teradata_host,
                    "user": args.teradata_user,
                    "password": args.teradata_password,
                    "database": args.teradata_database,
                },
            )
        )

        converter = ConvertDateToDatetime(
            columnname=args.column, desired_format=args.desired_format
        )

        transformed_data = teradata_data | "Column Mapping" >> beam.ParDo(converter)

        final_data = transformed_data | "Write to File" >> beam.io.WriteToText(
            args.output
        )


if __name__ == "__main__":
    all_information = [
        ("--teradata_host", "Teradata server information"),
        ("--teradata_database", "Teradata database information"),
        ("--teradata_user", "Teradata username information"),
        ("--teradata_password", "Teradata password information"),
        ("--teradata_table", "Name of the table that you get data from teradata"),
        ("--bigquery_project", "bigquery project information"),
        ("--bigquery_dataset", "bigquery dataset information"),
        ("--bigquery_table", "bigquery table information"),
        ("--bigquery_schema", "bigquery schema information"),
        ("--bigquery_credentials", "bigquery credentials path"),
        ("--secret_name", "secretname for teradata connection info"),
        ("--output", "output file path"),
        ("--column", "date column that you want to specify desired format"),
        ("--desired_format", "desired format for your date column"),
    ]

    parser = argparse.ArgumentParser()
    for arg_name, help_message in all_information:
        parser.add_argument(arg_name, help=help_message)
    args, beam_args = parser.parse_known_args()

    beam_options = PipelineOptions(beam_args)

    try:
        run(args)
    except Exception as e:
        print(f"Error running Dataflow pipeline: {e}")
        raise

```

In main.py we read the data from teradata and transforming the date column to the desired format and extract data into file. The steps are in below:

- Create `read_teradata(query, connection_config)` function in order to get the data as we specified in query from teradata server that we specify connection_config information. It turns us a generator.
- And then we create dataflow pipeline which has 3 steps.

      First step is `Read from Teradata` which get the data from teradata and create pcollection from it by using `beam.Create` function.
      Second step is `Column Mapping` which we transform the date column that we specified to the desired format with using ParDo.
      Last step is `Write to File` which we wrote the transformed data that we get from the second step onto the file that we specified the location of.

- We created parameters with argparse in order to run our dataflow pipeline dynamically. so you can change the parameters when you running the code with specifying --argname value in runtime.

## function.py
In function.py, we specify the columnname that we want to convert,and also specify desired format so it turns that column type to the desired format.
