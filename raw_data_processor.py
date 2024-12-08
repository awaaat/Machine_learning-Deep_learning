import pandas as pd
import re
import logging
from data_ingestion import load_csv_file
import numpy as np
from parameter_dictionary import ConfigParameters


class RawDataProcessor:
      """
      This module provides functionality to process and transform raw data into a structured format
      suitable for analysis. It includes the `RawDataProcessor` class, which handles loading CSV data,
      renaming columns, extracting specific patterns, and creating additional computed columns.

      Classes:
      - RawDataProcessor: Main class for handling raw data processing tasks.

      Functions:
      - initialize_logging: Sets up logging for debugging and monitoring.
      - get_data: Loads data from a CSV file into a DataFrame.
      - rename_columns: Renames DataFrame columns using a provided mapping.
      - drop_null_cols: Removes rows with null values.
      - get_account_names: Extracts account names from descriptions using predefined patterns.
      - drop_null_account_names: Filters rows with 'None' in the 'account_name' column.
      - get_orders_done: Extracts completed order counts from descriptions.
      - create_col_account_condition: Creates a column indicating whether accounts are 'new' or 'used'.
      - create_col_account_rating: Computes account ratings from raw text and converts them to a uniform scale.

      Attributes:
      - parameter_dict: Configuration dictionary with details such as CSV paths, column mappings, and regex patterns.
      - logging_level: Logging verbosity level (default: "INFO").
      """

      def __init__(self, parameter_dict, logging_level = 'INFO'):
            """
            Args:
                  parameter dictionary : dict
                        Dictionary containing configuration parameters, such as database path,
                        columns to rename.
            logging_level : str, optional
                Level of logging, either "DEBUG" or "INFO" (default is "INFO").
            """
            parameter_dict = ConfigParameters()
            self.csv_path = parameter_dict['CSV_URL']
            self.columns_to_rename = parameter_dict['columns_to_rename']
            self.account_name_patterns = parameter_dict['account_name_patterns']
            self.order_patterns = parameter_dict['order_patterns']
            self.condition_pattern = parameter_dict['condition_pattern']
            self. rating_patterns = parameter_dict['rating_patterns']
            self.bid_take_group = parameter_dict['bid_take_group']
            self.initialize_logging(logging_level)
            self.df = None
            
      def initialize_logging(self, logging_level):
            """
            Sets up logging for the class instance.
            Inputs: None
            Args:
                  logging_level : str
                  The logging level for the logger ("DEBUG" or "INFO").
            """
            logger_name = __name__+ ".RawDataProcessor"
            self.logger = logging.getLogger(logger_name)
            self.logger.propagate = False

            levels = {'DEBUG':logging.DEBUG, 'INFO': logging.INFO}
            log_level = levels.get(logging_level.upper(), logging.INFO)
            self.logger.setLevel(log_level)

            if not self.logger.handlers:
                  console_handler = logging.StreamHandler()
                  formatter = logging.Formatter('%(asctime)s : %(name)s - %(levelname)s - %(message)s')
                  console_handler.setFormatter(formatter)
                  self.logger.addHandler(console_handler)
      def get_data(self):
            """
            Load data from a CSV file into a DataFrame.

            This method loads data from a CSV file at the specified path and stores it in `self.df`.
            It logs a message indicating that the data has been loaded successfully.

            Attributes:
                  self.csv_path (str): The path to the CSV file containing the data.

            Returns:
                  pd.DataFrame: The data retrieved from the CSV file and stored in `self.df`.

            Raises:
                  FileNotFoundError: If the specified CSV file path does not exist.
                  pd.errors.EmptyDataError: If the CSV file is empty.
                  Exception: For other errors during the data loading process.
            """
            self.df = load_csv_file(self.csv_path)
            self.logger.info('Successfully Loaded Data ')
            return self.df

      def rename_columns(self):
            """
            Rename columns in the DataFrame according to a specified mapping.

            This method renames columns in `self.df` based on the dictionary `self.columns_to_rename`.
            It is useful for standardizing column names to match a specific format.

            Attributes:
                  self.columns_to_rename (dict): A dictionary mapping current column names to new names.

            Returns:
                  pd.DataFrame: The DataFrame with columns renamed according to the specified mapping.

            Raises:
                  KeyError: If any columns specified in `self.columns_to_rename` are not found in the DataFrame.
                  Exception: For other errors encountered during column renaming.
            """
            try:
                  self.df = self.df.rename(columns=self.columns_to_rename)
                  self.logger.info('Successfully Renamed Specified Columns ')
                  return self.df
            except KeyError as e:
                  self.logger.erro('Key Error. No Culumns Found. Error {e}')
                  raise e
            except Exception as e:
                  self.logger.error('Error While Renaming the Columns Specified')
                  raise e
      def drop_null_cols(self):
            """
                  Drop rows with null values from the DataFrame.

                  This method removes rows in `self.df` that contain any null values.
                  A log message is recorded upon successful removal.

                  Args:
                        self.df (pd.DataFrame): The DataFrame from which null value rows will be removed.

                  Returns:
                        pd.DataFrame: The DataFrame after dropping rows with null values.

                  Raises:
                        Exception: Logs an error and raises the exception if an error occurs during the row removal process.
            """
            try:
                  self.df = self.df.dropna(axis = 0)
                  self.logger.info("Successfully Dropped Rows with Null Values")
                  return self.df
            except Exception as e:
                  self.logger.error("Error While Dropping Null Values")
                  raise e


      def get_account_names(self):
            """ Extract account names from the 'description' column based on predefined patterns.
            This method iterates over each row in `self.df`, searching for matching account name patterns
            within the 'description' column. If a match is found, the corresponding account name is assigned
            to the 'account_name' column. If no match is found, 'None' is assigned. A log message is recorded
            upon successful extraction.

            Args:
                  None

            Returns:
                  pd.DataFrame: The DataFrame with an additional 'account_name' column containing extracted names.

            Raises:
                  Exception: Logs an error and raises the exception if an error occurs during the extraction process.
            """
            self.df['account_name'] = None
            try:
                  for idx, row in self.df.iterrows():
                        cell = row['description']
                        matched = False
                        for key, (pattern, flags) in self.account_name_patterns.items():
                              match = re.search(pattern, cell, flags=flags)
                              if match:
                                    self.df.at[idx, 'account_name'] = key
                                    matched = True
                                    break
                  if not matched:
                        self.df.at[idx, 'account_name'] = 'None'
                  self.df = self.df[self.df['account_name'] != 'None']
                  self.logger.info("Successfully Extracted and created 'account_name' column")
                  return self.df
            except Exception as e:
                  self.logger.error('Failed to Extract Account Names')
                  raise e
      #def drop_null_account_names(self):
      #     """
      #     Remove rows where the 'account_name' column contains 'None'.
      #
      #     This method filters `self.df` to exclude rows where the 'account_name' column has the value 'None'.
      #     Logs a success message if the operation completes, or logs an error message if an exception occurs.
      #
      #           Args:
      #                None
      #
      #           Returns:
      #                pd.DataFrame: The DataFrame after removing rows with 'None' in the 'account_name' column.
      #
      #           Raises:
      #                Exception: Logs an error and raises the exception if an error occurs during the row filtering process.
      #         """
      #        try:
      #             self.df = self.df[self.df['account_name'] != 'None']
      #      self.logger.info("Successfully removed Rows with 'None' in 'account_name' .")
      #            return self.df
      #    except KeyError as e:
      #         raise e
      #   except Exception as e:
       #        self.logger.error("An error occurred while removing rows with 'None' in 'account_name'.")
       #       raise e
      def create_col_account_condition(self):
            """
            Create a new column 'account_condition' in the DataFrame based on the 'condition' column.

            This function iterates through each row in `df` and checks if the 'condition' column contains
            the word 'new'. If found, 'account_condition' is set to 'new'; otherwise, it is set to 'used'.

            Args:
                  df (pd.DataFrame): The input DataFrame with a 'condition' column.

            Returns:
                  pd.DataFrame: The DataFrame with an added 'account_condition' column.
            """
            try:
                  self.df['account_condition'] = None
                  for idx, row in self.df.iterrows():
                        self.cell = row['condition']
                        match = re.search(self.condition_pattern[0], self.cell, flags=self.condition_pattern[1])  # Using both regex and flags correctly
                        if match:
                              self.df.at[idx, 'account_condition'] = 'new'
                        else:
                              self.df.at[idx, 'account_condition'] = 'used'
                  self.df['account_condition'] = self.df['account_condition'].astype(str)
                  self.df = self.df.drop(columns= 'condition', axis=1)
                  self.logger.info(" Successfully Created Column 'account_condition'")
                  return self.df
            except TypeError as t:
                  self.logger.error('Error; Please Check that your Positional Arguments are Correct')
                  raise t
            except Exception as e:
                  self.logger.error(f"Error While Creating the Column account_conditio. Error {e}")
                  raise e 
      def get_orders_done(self):
            """
            Extract and populate the 'orders_done' column based on patterns in the 'description' column.

            This method iterates through the 'description' column in `self.df`, searching for matching patterns
            that indicate completed orders. If a pattern matching 'zero_orders' is found, the 'orders_done' column
            is set to 0. For other patterns, a numeric order count is extracted and populated in the 'orders_done' column.
            Any unmatched rows are set to NaN. After processing, missing values in 'orders_done' are filled with the
            column's median. Logs messages for successful completion and any errors encountered.

            Args:
                  None

            Returns:
                  pd.DataFrame: The DataFrame with an added or updated 'orders_done' column, filled based on the extracted order data.

            Raises:
                  KeyError: Logs an error and raises the exception if the 'description' column is missing.
                  Exception: Logs a generic error message and raises the exception for any other processing issues.
            """
            try:
                  self.df['orders_done'] = np.nan
                  for idx, row in self.df.iterrows():
                        self.cell = row['description']
                        matched = False
                        for key, (pattern, flags) in self.order_patterns.items():
                              match = re.search(pattern, self.cell, flags=flags)
                              if match:
                                    if key == 'zero_orders':
                                          self.df.at[idx, 'orders_done'] = 0
                                    else:
                                          if self.df.at[idx, 'orders_done'] is np.nan or pd.isna(self.df.at[idx, 'orders_done']):
                                                # Handle "2k" as 200 and remove "+" if present, convert to integer
                                                value = match.group(1).replace('k', '00').replace('K', '00').replace('+', '')
                                                try:
                                                      self.df.at[idx, 'orders_done'] = int(value)
                                                except ValueError:
                                                      self.df.at[idx, 'orders_done'] = np.nan  # If conversion fails, set as NaN
                                    matched = True
                                    break
                              if not matched:
                                    self.df.at[idx, 'orders_done']=np.nan
                  self.df.loc[self.df['account_condition'] == 'new', 'orders_done'] = self.df.loc[self.df['account_condition'] == 'new', 'orders_done'].fillna(0)
                  self.logger.info("Successfully Extracted and Created Column 'orders done'. ")
                  return self.df
            except KeyError as e:
                  self.logger.error("Error while Processing the Column 'orders_done' ")
                  raise e
            except Exception as e:
                  self.logger.error(f"An error occurred while processing your Action. Error {e}")
                  raise e
     

      

      def create_col_account_rating(self):
            """
            Create and populate the 'account_rating' column by extracting rating information from the 'rating' column.

            This method applies predefined rating patterns to parse and convert the 'rating' column data, assigning 
            corresponding values to a new column 'account_rating'. The method handles different formats such as 
            percentages, fractions, and standalone ratings.

            Args:
                  self (object): The instance of the class containing 'df', a DataFrame with a 'rating' column and an 
                  attribute 'rating_patterns', which includes patterns for rating extraction. Also requires a logging 
                  attribute 'logger' to capture errors.

            Returns:
                  DataFrame: The modified DataFrame with a new 'account_rating' column containing the extracted ratings 
                  converted to a numeric scale.

            Raises:
                  Exception: Raises any exception encountered during the process and logs an error message.
            """
            try:
                  self.df['rating'] = self.df['rating'].apply(lambda x: x.split(":")[1].strip() if ":" in x and len(x.split(":")) > 1 else x.strip())
                  self.df['account_rating'] = np.nan
                  for idx, row in self.df.iterrows():
                        raw_string = str(row['rating']).strip()
                        self.extracted_rating = None
                        for key, (pattern, flags) in self.rating_patterns.items():
                              match = re.search(pattern, raw_string, flags  = flags)
                              if match:
                                    if key=='new_unranked':
                                          self.extracted_rating = 10.0
                                    elif key== 'percentage':
                                          self.extracted_rating = float(match.group(1))
                                    elif key== 'fraction':
                                          self.numerator = float(match.group(1))
                                          self.denominator = float(match.group(3))
                                          if float(self.denominator)!= 0:
                                                self.extracted_rating = float(self.numerator)
                                    elif key == 'stand_alone':
                                          self.extracted_rating = float(match.group(1))
                                    break
                        self.df.at[idx, 'account_rating'] = self.extracted_rating
                  self.df['account_rating'] = self.df['account_rating'].apply(
                        lambda value: value if value<=5.0
                        else (value / 10) * 5 if value <= 10.0
                        else (value / 100) * 5)
                  self.df['account_rating'] = self.df['account_rating'].apply(lambda value: value if value <= 5.0 else 4.9)
                  self.logger.info("Successfully Created Column 'account_rating'. ")
                  return self.df
            except Exception as e:
                  self.logger.error(f"Failed to extract and Create Column 'account_rating'. Error: {e} ")
                  raise e
      def classify_accounts(self):
            """
            Classifies accounts in a DataFrame by mapping each account name to a category 
            ('take' or 'bid') based on predefined groups, and assigns the result to a new column 
            'take_or_bid'.

            Args:
                  df (pd.DataFrame): The DataFrame containing the 'account_name' column, which includes 
                                    account names to be classified.

            Returns:
                  pd.DataFrame: The DataFrame with an additional 'take_or_bid' column, where each entry 
                              is either 'take' or 'bid' (or None if no match is found) based on the 
                              `bid_take_group` mapping.

            Logs:
                  Logs an error if the 'account_name' column is not found or if other exceptions arise.
            """
            try:
                  self.df['take_or_bid'] = None 
                  for idx, row in self.df.iterrows():
                        if row['account_name'] in self.bid_take_group:
                              self.df.at[idx, 'take_or_bid'] = self.bid_take_group[row['account_name']]
                  self.logger.info('Successfully Classified Accounts as Bid/Take')
                  return self.df
            except KeyError as e:
                  self.logger.error("The 'account_name' column is missing from the DataFrame.")
                  raise e
            except Exception as e:
                  self.logger.error(f"An error occurred in classify_accounts: {e}")
                  raise e
      def transform_price_col(self):
            """
            Extracts numeric price values from a 'price' column in a DataFrame by removing any commas 
            in the string, converting the price to a numeric format, and assigns the result to a new 
            column 'account_price'.

            Args:
                  df (pd.DataFrame): The DataFrame containing the 'price' column with prices in string 
                                    format prefixed by a currency symbol.

            Returns:
                  pd.DataFrame: The DataFrame with an additional 'account_price' column with numeric values.

            Logs:
                  Logs an error if the 'price' column is not found or if other exceptions arise.
            """
            try:
                  self.df['account_price'] = self.df['price'].apply(lambda x: float(x.split('S')[1].replace(',', '')))
                  self.logger.info('Successfully Transformed Price Column')
                  self.df = self.df.drop(columns='price')
                  return self.df
            except KeyError:
                  self.logger.error("The 'price' column is missing from the DataFrame.")
                  raise
            except ValueError as e:
                  self.logger.error(f"Data conversion error in extract_price: {e}")
                  raise
            except Exception as e:
                  self.logger.error(f"An error occurred in extract_price: {e}")
                  raise e
                                    


      def process(self):
            """
            Execute the main data processing workflow.

            This method sequentially performs data processing steps.

            Args:
                  None

            Returns:
                  pd.DataFrame: The fully processed DataFrame after applying all transformations.

            Raises:
                  Exception: Propagates any exceptions raised by individual processing steps.
            """
            self.get_data()
            self.rename_columns()
            self.drop_null_cols()
            self.get_account_names()
            self.create_col_account_condition()
            self.get_orders_done()
            self.create_col_account_rating()
            self.classify_accounts()
            self.transform_price_col()

            return self.df
      
