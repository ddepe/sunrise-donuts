"""
Weather Data and Sales Analysis Script

This script performs analysis on Meteostat weather data and sales data using the Prophet model.
It includes functions to run Prophet with cross-validation, integrating various weather variables as regressors.
The script fetches the latest data, merges it, and runs the analysis, saving the results to a CSV file.

Functions:
- run_prophet_with_cv: Runs Prophet with cross-validation using different sets of weather variables.
"""

import pandas as pd
import pathlib
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics

from  squareup.sales_util import get_last_update_date
 


def run_prophet_with_cv(weather_variable_sets, df):
    """
    Runs Prophet with cross-validation for different sets of weather variables.

    Parameters:
    - weather_variable_sets (list of list of str): List of weather variable sets to use as regressors.
    - df (DataFrame): The merged DataFrame containing sales and weather data.
    """
    results = []

    for variables in weather_variable_sets:

        # Initialize a Prophet model with US holidays
        model = Prophet()
        model.add_country_holidays(country_name='US')

        # Add weather variables as regressors
        for var in variables:
            model.add_regressor(var)

        model.fit(df)

        # Perform cross-validation
        df_cv = cross_validation(model, initial="366 days", period="1 days", horizon="7 days", parallel="processes")

        # Calculate performance metrics
        df_p = performance_metrics(df_cv, rolling_window=1)

        # Add variables column to performance metrics DataFrame
        df_p['variables'] = ', '.join(variables)

        results.append(df_p)
        print(df_p)

    # Concatenate all the results
    final_results = pd.concat(results, ignore_index=True)

    # Save the results to a CSV file
    final_results.to_csv('output/cross_validation_meteostat.csv', index=False)


if __name__ == "__main__":
     # Get the directory of the current script
    base_dir = pathlib.Path(__file__).resolve().parent.parent

    sales_file_path = base_dir / 'data' / 'aggregated_sales.csv'
    weather_file_path = base_dir / 'data' / 'weather_meteostat.csv'
    output_dir_path = base_dir / 'output'

    sales_df = pd.read_csv(sales_file_path)
    weather_df = pd.read_csv(weather_file_path)

    # Define sets of weather variables to be used as regressors
    weather_variable_sets = [
        [],
        ['tavg'],
        ['wspd'],
        ['prcp'],
        ['tavg', 'wspd'],
        ['tavg', 'prcp'],
        ['wspd', 'prcp'],
        ['tavg', 'wspd', 'prcp']
    ]

    # Convert date columns to datetime
    sales_df['Sales'] = pd.to_datetime(sales_df['Sales'], format='%m/%d/%Y')
    weather_df['time'] = pd.to_datetime(weather_df['time'])

    df = pd.merge(sales_df, weather_df, left_on='Sales', right_on='time')
    df.drop(columns=['time'], inplace=True)

    latest_date = get_last_update_date(sales_file_path)

    # Rename the necessary columns to match Prophet's requirements
    df.rename(columns={"Sales": "ds", "Gross Sales": "y"}, inplace=True)

    # Drop all closed days
    df = df[df['y'] != 0.0]
    print(df.tail(10))

    run_prophet_with_cv(weather_variable_sets, df)