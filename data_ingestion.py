import pandas as pd
import logging
from sqlalchemy import create_engine, text

"""
Data Ingestion Module. 
This module sets up a connection to the data. 
Data coes from different sources. It contains SQL query templates to retrieve the data, 
and it also includes external URLS for additional data, with logging configurations
for debugging and tracking the process. 

Attributes:
    logger (logging.Logger): Logger instance to track events in the data_ingestion module.
    db_path (str): The path to the SQLite database file.
    sql_query (str): SQL query to retrieve joined data from multiple database tables.
    weather_data_URL (str): URL for the primary weather data CSV file.
    weather_mapping_data_URL (str): URL for mapping weather data to specific fields.
"""
logger= logging.getLogger('data_ingestion')
logging.basicConfig(level=logging.INFO, format='%(asctime)s : %(name)s - %(levelname)s - %(message)s')

#Option 1; If we will be fetching data from a SQL database, the below function will apply
def create_db_engine(db_path):
      """
      Creates and tests a database engine connection
      Args:
            db_path(str): The database connection string
      Returns:
            engine: The SQLAlchemy engine object if successfully created.
      Raises:
            import error: If SQLAlchemy is not installed
            exception error: For other errors encountered during engine creation.
      """
      try:
            engine = create_engine(db_path)
            with engine.connect() as conn:
                  pass
            logger.info('Database Engine Created Successfully')
      except ImportError as e:
            logger.error('Required Modules Missing. Install them first. ')
            raise e
      except Exception as e:
            logger.error(f"Failed to Create a Database Connection. Error {e}")
            raise e
def query_data(engine, sql_query):
      """
      Executes a SQL query on the provided database engine.

      Args:
            engine: The SQLAlchemy engine object for database connection.
            sql_query (str): The SQL query to execute.

      Returns:
            DataFrame: A pandas DataFrame containing the query results.

      Raises:
            ValueError: If the query returns an empty DataFrame.
            Exception: For other errors during query execution.
      """
      try:
            with engine.connect() as connection:
                  df = pd.read_sql_query(text(sql_query), connection)
                  if sql_query is None:
                        logger.error('No SQL Statement Provided.')
                  if df.empty:
                        logger.error('Empty Dataframe Returned. Check your SQL Statement')
                        
                  logger.info('Data Queried Successfuly')
                  return df
      except ValueError as e:
            logger.error(f"SQL Query Failed. Error {e}")
            raise e
      except Exception as e:
            logger.error(f"An Error Occured. {e}")
            raise e
def load_csv_file(URL):
      """
      Reads a CSV file from a given web URL.
      Args:
            URL (str): The web URL to the CSV file.
      Returns:
            DataFrame: A pandas DataFrame containing the CSV data.
      Raises:
            pd.errors.EmptyDataError: If the CSV at the URL is empty or invalid.
            Exception: For other errors encountered while reading the CSV.
      """
      try:
            df = pd.read_csv(URL)
            logger.info('CSV File Loaded Successfully')
            return df
      except pd.errors.EmptyDataError as e:
            logger.error('The URL Provided Points to Invalid Data')
            raise e
      except Exception as e:
            logger.error('CSV Data Not Read. Confirm the Provided Parameters')
            raise e
      


                
                
                

