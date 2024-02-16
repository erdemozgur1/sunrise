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
