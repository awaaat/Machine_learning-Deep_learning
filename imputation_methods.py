import logging
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.linear_model import LinearRegression
from sklearn.impute import IterativeImputer

# Set up logging
logger = logging.getLogger('imputation')
logging.basicConfig(level=logging.INFO, format='%(asctime)s : %(name)s - %(levelname)s - %(message)s')


def drop_missing_values(df, axis=0, threshold=0.05):
      """
      Drop rows or columns based on a missing value threshold.

      Parameters:
            df (pd.DataFrame): The input DataFrame.
            axis (int): Axis to drop along, 0 for rows, 1 for columns.
            threshold (float): The maximum percentage of missing values allowed.

      Returns:
            pd.DataFrame: The modified DataFrame with rows or columns dropped.
      """
      try:
            if not (0 <= threshold <= 1):
                  raise ValueError("Threshold must be between 0 and 1.")
            if axis not in (0, 1):
                  raise ValueError("Axis must be 0 (rows) or 1 (columns).")

            if axis == 0:  # Drop rows
                  logger.info(f"Dropping rows with more than {threshold * 100}% missing values.")
                  return df.dropna(axis=0, thresh=int((1 - threshold) * df.shape[1]))
            else:  # Drop columns
                  logger.info(f"Dropping columns with more than {threshold * 100}% missing values.")
                  return df.dropna(axis=1, thresh=int((1 - threshold) * df.shape[0]))

      except Exception as e:
            logger.error(f"Error in drop_missing_values: {e}")
            raise e


def impute_mean(df, cols):
      """
      Impute missing values in specified columns with the mean.

      Parameters:
            df (pd.DataFrame): The input DataFrame.
            cols (list or str): The column(s) to impute.

      Returns:
            pd.DataFrame: The DataFrame with missing values imputed.
      """
      try:
            if isinstance(cols, str):
                  cols = [cols]

            for col in cols:
                  logger.info(f"Imputing missing values in column '{col}' with mean.")
                  df[col] = df[col].fillna(df[col].mean())

            logger.info("Successfully imputed missing values with mean.")
            return df
      except Exception as e:
            logger.error(f"Error in impute_mean: {e}")
            raise e


def impute_median(df, cols):
      """
      Impute missing values in specified columns with the median.

      Parameters:
            df (pd.DataFrame): The input DataFrame.
            cols (list or str): The column(s) to impute.

      Returns:
            pd.DataFrame: The DataFrame with missing values imputed.
      """
      try:
            if isinstance(cols, str):
                  cols = [cols]

            for col in cols:
                  logger.info(f"Imputing missing values in column '{col}' with median.")
                  df[col] = df[col].fillna(df[col].median())

            logger.info("Successfully imputed missing values with median.")
            return df
      except Exception as e:
            logger.error(f"Error in impute_median: {e}")
            raise e


def impute_mode(df, cols):
      """
      Impute missing values in specified columns with the mode.

      Parameters:
            df (pd.DataFrame): The input DataFrame.
            cols (list or str): The column(s) to impute.

      Returns:
            pd.DataFrame: The DataFrame with missing values imputed.
      """
      try:
            if isinstance(cols, str):
                  cols = [cols]

            for col in cols:
                  mode_value = df[col].mode()[0]
                  logger.info(f"Imputing missing values in column '{col}' with mode: {mode_value}")
                  df[col] = df[col].fillna(mode_value)

            logger.info("Successfully imputed missing values with mode.")
            return df
      except Exception as e:
            logger.error(f"Error in impute_mode: {e}")
            raise e


def impute_knn(df, cols, n_neighbors=5):
      """
      Impute missing values using k-NN.

      Parameters:
            df (pd.DataFrame): The input DataFrame.
            cols (list or str): The column(s) to impute.
            n_neighbors (int): Number of neighbors to use for k-NN.

      Returns:
            pd.DataFrame: The DataFrame with missing values imputed.
      """
      try:
            if isinstance(cols, str):
                  cols = [cols]

            logger.info(f"Imputing missing values using k-NN with {n_neighbors} neighbors.")
            imputer = KNNImputer(n_neighbors=n_neighbors)
            df[cols] = imputer.fit_transform(df[cols])

            logger.info("Successfully imputed missing values with k-NN.")
            return df
      except Exception as e:
            logger.error(f"Error in impute_knn: {e}")
            raise e


def impute_with_regression(df, target_col, feature_cols):
      """
      Impute missing values in a column using regression.

      Parameters:
            df (pd.DataFrame): The input DataFrame.
            target_col (str): The column with missing values to impute.
            feature_cols (list or str): The columns to use as predictors.

      Returns:
            pd.DataFrame: The DataFrame with missing values imputed.
      """
      try:
            if isinstance(feature_cols, str):
                  feature_cols = [feature_cols]

            # Drop rows where the target column is missing
            non_null_df = df.dropna(subset=[target_col])

            # Drop rows where the target column is missing and any of the feature columns are null
            null_df = df[df[target_col].isnull() & df[feature_cols].notnull().all(axis=1)]

            if not non_null_df.empty and not null_df.empty:
                  # Train the regression model
                  model = LinearRegression()
                  model.fit(non_null_df[feature_cols], non_null_df[target_col])

                  # Predict the missing target column values
                  predicted_values = model.predict(null_df[feature_cols])

                  # Replace the missing values with predicted values
                  df.loc[df[target_col].isnull(), target_col] = predicted_values

            logger.info(f"Successfully imputed missing values in '{target_col}' using regression.")
            return df
      except Exception as e:
            logger.error(f"Error in impute_with_regression: {e}")
            raise e

def impute_mice(df, cols):
      """
      Impute missing values using the MICE (Multiple Imputation by Chained Equations) method.

      Parameters:
            df (pd.DataFrame): The input DataFrame.
            cols (list or str): The column(s) to impute.

      Returns:
            pd.DataFrame: The DataFrame with missing values imputed.
      """
      try:
            if isinstance(cols, str):
                  cols = [cols]

            logger.info(f"Imputing missing values in columns {cols} using MICE.")
            imputer = IterativeImputer(max_iter=10, random_state=0)
            df[cols] = imputer.fit_transform(df[cols])

            logger.info("Successfully imputed missing values using MICE.")
            return df
      except Exception as e:
            logger.error(f"Error in impute_mice: {e}")
            raise e


def impute_interpolation(df, cols, method='linear', order=2):
      """
      Impute missing values in specified columns using interpolation.

      Parameters:
            df (pd.DataFrame): The input DataFrame.
            cols (list or str): The column(s) to impute.
            method (str): Interpolation method ('linear' or 'polynomial').
            order (int): The order of the polynomial for 'polynomial' interpolation.

      Returns:
            pd.DataFrame: The DataFrame with missing values imputed.
      """
      try:
            if isinstance(cols, str):
                  cols = [cols]
                  

            for col in cols:
                  if method == 'linear':
                        logger.info(f"Imputing missing values in column '{col}' using linear interpolation.")
                        df[col] = df[col].interpolate(method='linear')
                  elif method == 'polynomial':
                        logger.info(f"Imputing missing values in column '{col}' using polynomial interpolation of order {order}.")
                        df[col] = df[col].interpolate(method='polynomial', order=order)
                  else:
                        raise ValueError("Interpolation method must be 'linear' or 'polynomial'")
            
            logger.info("Successfully imputed missing values using interpolation.")
            return df
      except Exception as e:
            logger.error(f"Error in impute_interpolation: {e}")
            raise e


def impute_backward_fill(df, cols):
      """
      Impute missing values in specified columns using backward fill.

      Parameters:
            df (pd.DataFrame): The input DataFrame.
            cols (list or str): The column(s) to impute.

      Returns:
            pd.DataFrame: The DataFrame with missing values imputed.
      """
      try:
            if isinstance(cols, str):
                  cols = [cols]

            for col in cols:
                  logger.info(f"Imputing missing values in column '{col}' using backward fill.")
                  df[col] = df[col].fillna(method='bfill')

            logger.info("Successfully imputed missing values using backward fill.")
            return df
      except Exception as e:
            logger.error(f"Error in impute_backward_fill: {e}")
            raise e


def impute_forward_fill(df, cols):
      """
      Impute missing values in specified columns using forward fill.

      Parameters:
            df (pd.DataFrame): The input DataFrame.
            cols (list or str): The column(s) to impute.

      Returns:
            pd.DataFrame: The DataFrame with missing values imputed.
      """
      try:
            if isinstance(cols, str):
                  cols = [cols]

            for col in cols:
                  logger.info(f"Imputing missing values in column '{col}' using forward fill.")
                  df[col] = df[col].fillna(method='ffill')

            logger.info("Successfully imputed missing values using forward fill.")
            return df
      except Exception as e:
            logger.error(f"Error in impute_forward_fill: {e}")
            raise e

