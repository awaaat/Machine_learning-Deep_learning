from parameter_dictionary import ConfigParameters
import logging
from raw_data_processor import RawDataProcessor
import pandas as pd

class DataCleanerAndTransformer(RawDataProcessor):
      """
      This module defines the `DataCleanerAndTransformer` class, which extends the functionality 
      of `RawDataProcessor` to perform advanced data cleaning and transformation operations 
      on a DataFrame.

      Classes:
      - DataCleanerAndTransformer: Inherits from `RawDataProcessor` and provides methods to:
            - Transform DataFrame columns (drop, retain, rename).
            - Remove duplicate rows and reset the index.
            - Update a 'rating' column based on specific conditions.

      Methods:
      - __init__: Initializes the class with logging and configuration parameters.
      - initialize_logging: Sets up a logger for tracking operations.
      - transform_columns: Applies transformations like column dropping, retaining, and renaming.
      - drop_duplicates: Removes duplicate rows and resets the DataFrame index.
      - update_rating_col: Updates the 'rating' column based on conditions in other columns.
      - clean_and_transform: Executes all cleaning and transformation steps sequentially.

      Dependencies:
      - `ConfigParameters` (from `parameter_dictionary`): Supplies configuration parameters.
      - `RawDataProcessor` (from `raw_data_processor`): Provides base data processing functionalities.
      - `pandas` (as `pd`): Handles DataFrame manipulations.
      - `logging`: Enables logging of operations and errors.

      Usage:
      Import this module, create an instance of `DataCleanerAndTransformer`, and call its 
      `clean_and_transform` method to perform comprehensive data cleaning and transformation.

      Example:
      ```python
      from parameter_dictionary import ConfigParameters
      from data_cleaner_and_transformer import DataCleanerAndTransformer

      parameter_dict = ConfigParameters()
      cleaner = DataCleanerAndTransformer(parameter_dict, logging_level='INFO')
      cleaned_data = cleaner.clean_and_transform()
      ```

      Notes:
      - Ensure that the parameter dictionary (`parameter_dict`) contains all required keys 
            such as 'columns_to_drop', 'columns_to_swap', 'columns_to_rename_2', and 'CSV_URL'.
      - The `RawDataProcessor` class must provide a `process` method that initializes the DataFrame.
      """

      
      def __init__(self, parameter_dict, logging_level = 'INFO'):
            parameter_dict = ConfigParameters()
            
            super().__init__(parameter_dict)
            self.columns_to_drop = parameter_dict['columns_to_drop']
            self.columns_to_swap = parameter_dict['columns_to_swap']
            self.columns_to_rename_2 = parameter_dict['columns_to_rename_2']
            self.csv_file_path = parameter_dict['CSV_URL']

            self.initialize_logging(logging_level)
            self.rd_processor = RawDataProcessor(parameter_dict=parameter_dict)
            self.df = self.rd_processor.process()
      def initialize_logging(self, logging_level):
            """
            Sets up logging for the class instance.
            Inputs: None
            Args:
                  logging_level : str
                  The logging level for the logger ("DEBUG" or "INFO").
            """
            logger_name = __name__+ ".DataCleaningAndTransformation"
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

      def transform_columns(self):
            """
            Perform column transformations on the DataFrame.
            
            - Drops specified columns.
            - Retains only specified columns.
            - Renames specified columns.
            Args: 
                  None
            Returns:
                  pd.DataFrame: The transformed DataFrame.

            Raises:
                  ValueError: If specified columns are not found in the DataFrame.
                  KeyError: If there are issues with column renaming.
            """
            try:
                  self.df = self.df.drop(columns = self.columns_to_drop)
                  self.df = self.df[self.columns_to_swap]
                  self.df = self.df.rename(columns = self.columns_to_rename_2)
                  self.logger.info('Successfully Transformed Columns')
                  return self.df
            except KeyError as e:
                  self.logger.error(f"One or more columns specified in `columns_to_rename_2` do not exist: {e}")
                  raise e
            except ValueError as e:
                  self.logger.error(f"One or more columns specified in `columns_to_drop` or `columns_to_swap` are missing: {e}")
                  raise e
            except Exception as e:
                  self.logger.error(f"Unexpected error during transformation: {e}")
                  raise e 
      def drop_duplicates(self):
            """
            Removes duplicate rows from the DataFrame and resets the index.

            - Keeps the first occurrence of each duplicate.
            - Resets the DataFrame index after dropping duplicates.

            Returns:
                  pd.DataFrame: The DataFrame with duplicates removed.

            Raises:
                  AttributeError: If `self.df` is not a valid DataFrame.
                  Exception: For any unexpected errors during the operation.
            """
            try:
                  self.df = self.df.drop_duplicates(keep='first').reset_index(drop=True)
                  self.logger.info("Successfully removed duplicate rows and reset the index.")
                  return self.df
            except AttributeError as e:
                  self.logger.error(f"DataFrame object is not valid or missing: {e}")
                  raise e
            except Exception as e:
                  self.logger.error(f"An unexpected error occurred while removing duplicates: {e}")
                  raise e

      def update_rating_col(self):
            """
            Updates the 'rating' column in the DataFrame based on specified conditions.

            - Sets the 'rating' to 5.0 if the 'orders_done' column equals 0 or the 'condition' column is 'new'.
            - Otherwise, retains the original 'rating' value.

            Returns:
                  pd.DataFrame: The DataFrame with the updated 'rating' column.

            Raises:
                  AttributeError: If `self.df` is not a valid DataFrame.
                  Exception: For any unexpected errors during the operation.
            """
            try:
                  if self.df is None or self.df.empty:
                        self.logger.error("The input DataFrame is None or empty.")
                        raise ValueError("The input DataFrame is None or empty.")

                  self.df['rating'] = self.df.apply(
                        lambda row: 5.0 if (row['orders_done'] == 0 or row['condition'] == 'new') else row['rating'], 
                        axis=1
                  )
                  self.logger.info("Successfully updated the 'rating' column based on specified conditions.")
                  return self.df
            except KeyError as e:
                  self.logger.error(f"Required columns ('orders_done', 'condition', or 'rating') are missing from the DataFrame: {e}")
                  raise e
            except Exception as e:
                  self.logger.error(f"An unexpected error occurred while updating the 'rating' column: {e}")
                  raise e
      def impute_price(self):
            """
            Replace zeros in the specified column with the column's median value.

            Parameters:
                  df (pd.DataFrame): The input DataFrame.
                  col (str): The name of the column to process.

            Returns:
                  pd.DataFrame: The DataFrame with zeros replaced by the column's median.
            """
            try:
                  self.col = 'price'
                  if self.col not in self.df.columns:
                        raise ValueError(f"Column '{self.col}' does not exist in the DataFrame.")
                  
                  # Calculate the median of the column (excluding zeros)
                  median_value = self.df.loc[self.df[self.col] != 0, self.col].median()
                  
                  # Replace zeros with the median value
                  self.df[self.col] = self.df[self.col].apply(lambda x: median_value if x <= 500 else x)
                  
                  self.logger.info(f"Successfully replaced zeros in column '{self.col}' with the median.")
                  return self.df
            except Exception as e:
                  self.logger.error(f"Error in impute_zero_with_median: {e}")
                  raise e
      def clean_name_col(self):
            """
            Clean the 'name' column by removing rows with missing values.

            This method checks if the column specified in `self.col_name` exists in the DataFrame (`self.df`).
            If the column does not exist, it raises a `ValueError`. Otherwise, it drops rows where the 'name'
            column has missing (NaN) values and logs the operation.

            Returns:
                  pd.DataFrame: The updated DataFrame with rows containing missing values in the 'name' column removed.

            Raises:
                  ValueError: If the specified column does not exist in the DataFrame.
                  Exception: If any other error occurs during the operation.

            """
            self.col_name = 'name'
            try:
                  if self.col_name not in self.df.columns:
                        raise ValueError(f"Column '{self.col_name}' does not exist in the DataFrame.")
                  # Drop rows where the specified column has NaN values
                  self.df = self.df.dropna(subset=[self.col_name])

                  self.logger.info(f"Successfully dropped rows with missing values in '{self.col_name}' column.")
                  return self.df
            
            except Exception as e:
                  self.logger.error(f"Error in drop_rows_with_missing_in_column: {e}")
                  raise e
      def _dropna_(self):
            self.df = self.df.dropna(axis=0)
            return self.df

      def clean_and_transform(self):
            """
            Executes a series of data cleaning and transformation steps on the DataFrame.

            - Applies column transformations, including dropping, retaining, and renaming specified columns.
            - Removes duplicate rows and resets the index.
            - Updates the 'rating' column based on specified conditions.

            Returns:
                  pd.DataFrame: The cleaned and transformed DataFrame.

            Raises:
                  Exception: Any errors encountered during the cleaning and transformation steps are propagated.
            """
      
            self.transform_columns()
            self.drop_duplicates()
            self.update_rating_col()
            self.impute_price()
            self.clean_name_col()
            self. _dropna_()
            return self.df