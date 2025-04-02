import json
import logging
from pathlib import Path
import os
import time
import typer
import uuid

import duckdb
import ijson

app = typer.Typer()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.command()
def extract_anthem_data(file_location: str):
    """
    Anthem data is a long list of nested json blocks which can be streamed in order to retrieve the items.
    The json block contains values that can either be a list of json, a singular json, or a singular value.
    The approach is to stream the data and the keys will be separated by file and the values will be
    a json separated by a newline. This exploded extraction will then be loaded into duckdb.

    To ensure that all the keys & values can be traced back to a given json block; a primary key is generated
    to identify this.
    :param file_location: Location in which the Anthem raw json file exists.

    :return: NA -- json data will be written to the exploded_data directory.
    """
    start_time = time.time()
    logger.info("Starting Anthem extraction.")

    output_directory = Path("exploded_data")
    output_directory.mkdir(exist_ok=True)

    files_available = {}

    with open(file_location, 'r') as file:
        for item in ijson.items(file, 'reporting_structure.item'):
            primary_key = str(uuid.uuid4())

            for key, value in item.items():
                if key not in files_available:
                    open_file_to_append = open(f"{output_directory}/{key}.json", 'a')
                    files_available[key] = open_file_to_append

                file_to_save = files_available[key]
                if isinstance(value, list):
                    for idx, inner_dict in enumerate(value):
                        dict_to_write = {"primary_key": primary_key, **inner_dict}
                        file_to_save.write(json.dumps(dict_to_write) + '\n')
                elif isinstance(value, dict):
                    dict_to_write = {"primary_key": primary_key, **value}
                    file_to_save.write(json.dumps(dict_to_write) + '\n')
                else:
                    str_to_write = {"primary_key": primary_key, "data_point": value}
                    file_to_save.write(json.dumps(str_to_write) + '\n')

    for open_file in files_available.values():
        open_file.close()

    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"Completed Anthem extraction in {execution_time / 60.0} minutes.")


@app.command()
def query(query_string: str, max_rows: int = 25):
    """
    Entry point to quickly query any data and show selected amount of rows.

    :param query_string: query to execute.
    :param max_rows: rows to putput
    :return: NA -- data will be shown as print.
    """
    db_path = os.getenv('DUCKDB_PATH', 'healthcare_pricing.db')
    conn = duckdb.connect(db_path)
    data = conn.sql(query_string)
    data.show(max_rows=max_rows)
    conn.close()


@app.command()
def create_anthem_data_in_duckdb():
    """
    From extracted ad exploded json data, we will be loading these data points in duckdb.
    Given that the data contract states what each column can be: https://github.com/CMSgov/price-transparency-guide/tree/master/schemas/table-of-contents,
    it is safe to autoload the json records inferring from a small subset.

    Goal is to iterate through all the extracted json values part of the extraction step, load it into duckdb and
    the log the count of each table records for observability.

    :return: NA --  data will be stored into tables to the local duckdb database.
    """

    db_path = os.getenv('DUCKDB_PATH', 'healthcare_pricing.db')
    conn = duckdb.connect(db_path)
    exploded_data_dir = Path("exploded_data")

    json_files = {str(file_).replace("exploded_data/", "").replace(".json", ""): str(file_) for file_ in
                  exploded_data_dir.iterdir() if file_.is_file()}

    start_time = time.time()
    logger.info(f"Starting loading anthem data into local duckdb {db_path}.")

    try:
        for table_name, file_path in json_files.items():
            logger.info(f"loading {file_path}")

            # since the json values are the same across each row based on the data contract; no need to have a large
            # sample size.
            create_table_query = f"""
            CREATE OR REPLACE TABLE {table_name} AS
            SELECT * 
            FROM read_json_auto('{file_path}', sample_size=100);
            """

            logger.info(f"Creating table '{table_name}'")
            conn.execute(create_table_query)

            count_of_records_query = f"SELECT COUNT(*) FROM {table_name}"
            result = conn.execute(count_of_records_query).fetchone()
            logger.info(f"Table: '{table_name}' ---  {result[0]} records.")


    except Exception as e:
        logger.error(f"Database error --- {str(e)}")
    finally:
        conn.close()

    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"Completed Anthem loading in {execution_time / 60.0} minutes.")


def main():
    app()
