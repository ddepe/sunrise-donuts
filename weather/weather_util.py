"""
Weather Data Retrieval and Analysis Script

This script retrieves weather data from two sources: Meteostat and Visual Crossing.
It provides functions to update and refresh weather data, as well as to forecast future weather conditions.
The data is saved to CSV files, and visualizations are generated using matplotlib.

Functions:
- update_weather_meteostat: Appends new weather data from Meteostat to an existing CSV file.
- refresh_weather_meteostat: Fetches and saves weather data from Meteostat to a new CSV file.
- forecast_weather_meteostat: Fetches and plots hourly weather forecast data from Meteostat.
- get_visual_crossing_weather: Retrieves weather data from Visual Crossing.
- update_weather_visual_crossing: Appends new weather data from Visual Crossing to an existing CSV file.
- refresh_weather_visual_crossing: Fetches and saves weather data from Visual Crossing to a new CSV file.
- forecast_weather_visual_crossing: Fetches and returns a 15-day weather forecast from Visual Crossing.

Constants:
- VISUAL_CROSSING_KEY: API key for Visual Crossing retrieved from environment variables.
- LOCATION: Meteostat location object for a specific latitude, longitude, and altitude.
- ZIPCODE: ZIP code for the location.

Usage:
Set the VISUAL_CROSSING_KEY environment variable before running the script.
Call the functions as needed to update, refresh, or forecast weather data.

Example:
update_weather_meteostat(datetime.datetime(2022, 11, 1))
"""

import csv
import datetime
from io import StringIO
import matplotlib.pyplot as plt
import meteostat
import os
import pandas as pd
import requests
import sys

# Retrieve API key for Visual Crossing from environment variables
VISUAL_CROSSING_KEY = os.environ['VISUAL_CROSSING_KEY']

LOCATION = meteostat.Point(38.0194, -122.1341, 135)
ZIPCODE = 94553

def update_weather_meteostat(last_date, file_path=None):
    """
    Append new weather data from Meteostat to an existing CSV file.

    Parameters:
    - last_date (datetime): The last date of the existing data.
    - file_path (str, optional): The path to the CSV file. Defaults to 'data/weather_meteostat.csv'.
    """

    if file_path is None:
        file_path = f'data/weather_meteostat.csv'

    end = datetime.datetime.now()

    # Fetch daily weather data from Meteostat
    data = meteostat.Daily(LOCATION, last_date, end)
    data = data.fetch()

    # Append data to the CSV file
    data.to_csv(file_path, mode='a', header=False)

def refresh_weather_meteostat():
    """
    Fetch and save weather data from Meteostat to a new CSV file starting from November 1, 2022.
    """
    
    # Set up a new CSV file with the current date and start from November 1, 2022
    file_path = f'data/weather_meteostat_{datetime.datetime.now().strftime("%Y%m%d")}.csv'
    first_date = datetime.datetime(2022, 11, 1)
    end = datetime.datetime.now()

    # Fetch daily weather data from Meteostat
    data = meteostat.Daily(LOCATION, first_date, end)
    data = data.fetch()

    # Save data to a new CSV file
    data.to_csv(file_path)
        
    # Plot line chart including average, minimum and maximum temperature
    data.plot(y=['tavg', 'tmin', 'tmax'])
    plt.show()

def forecast_weather_meteostat():
    """
    Fetch and plot hourly weather forecast data for the next 3 days from Meteostat.
    
    Returns:
    - data (DataFrame): The weather forecast data.
    """
    start_date = datetime.datetime.now() - datetime.timedelta(days=2)
    end_date = datetime.datetime.now() + datetime.timedelta(days=3)

    # Get daily data
    data = meteostat.Hourly(LOCATION, start_date, end_date)
    data = data.fetch()

    # Plot temperature line chart 
    data.plot(y=['temp'])
    plt.show()

    return data

def get_visual_crossing_weather(zip_code, start_date, end_date, api_key):
    """
    Retrieve weather data from Visual Crossing for a given ZIP code and date range.

    Parameters:
    - zip_code (str): The ZIP code for the location.
    - start_date (str): The start date in 'YYYY-MM-DD' format.
    - end_date (str): The end date in 'YYYY-MM-DD' format.
    - api_key (str): The Visual Crossing API key.
    
    Returns:
    - response (Response): The HTTP response object.
    """
    base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
    params = {
        "unitGroup": "metric",
        "include": "days",
        "key": api_key,
        "contentType": "csv"
    }
    url = f"{base_url}/{zip_code}/{start_date}/{end_date}"
    response = requests.get(url, params=params)
    return response

def update_weather_visual_crossing(last_date, file_path=None):
    """
    Append new weather data from Visual Crossing to an existing CSV file.

    Parameters:
    - last_date (str): The last date of the existing data.
    - file_path (str, optional): The path to the CSV file. Defaults to 'data/weather_visual_crossing.csv'.
    """

    if file_path is None:
        file_path = f'data/weather_visual_crossing.csv'

    end_date = datetime.datetime.now()

    # Get daily weather data from Visual Crossing
    response = get_visual_crossing_weather(ZIPCODE, last_date, end_date, VISUAL_CROSSING_KEY)

    if response.status_code!=200:
        print('Unexpected Status code: ', response.status_code)
        sys.exit()  

    # Append the CSV data to the file
    with open(file_path, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Parse the CSV text from the response
        CSVText = csv.reader(response.text.splitlines())

        # Write each row from the parsed CSV to the file
        for row in CSVText:
            writer.writerow(row)

def refresh_weather_visual_crossing():
    """
    Fetch and save weather data from Visual Crossing to a new CSV file starting from November 1, 2022.
    """

    # Set up a new CSV file with the current date and start from November 1, 2022
    file_path = f'data/weather_meteostat_{datetime.datetime.now().strftime("%Y%m%d")}.csv'
    first_date = datetime.datetime(2022, 11, 1)
    end_date = datetime.datetime.now()

    # Get daily weather data from Visual Crossing
    response = get_visual_crossing_weather(ZIPCODE, first_date, end_date, VISUAL_CROSSING_KEY)

    if response.status_code!=200:
        print('Unexpected Status code: ', response.status_code)
        sys.exit()  

    # Open a file to write the CSV data
    with open(file_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Parse the CSV text from the response
        CSVText = csv.reader(response.text.splitlines())

        # Write each row from the parsed CSV to the file
        for row in CSVText:
            writer.writerow(row)

    # Load the data into a DataFrame
    data = StringIO(response.text)
    df = pd.read_csv(data)

    # Plot the weather data
    df.plot(y=['temp', 'tempmin', 'tempmax'])
    plt.show()


def forecast_weather_visual_crossing():
    """
    Fetch and return a 15-day weather forecast from Visual Crossing.

    Returns:
    - df (DataFrame): The weather forecast data.
    """
    start_date = datetime.datetime.now() - datetime.timedelta(days=2)
    end_date = datetime.datetime.now() + datetime.timedelta(days=15)

    # Get daily weather forecast data from Visual Crossing
    response = get_visual_crossing_weather(ZIPCODE, start_date, end_date, VISUAL_CROSSING_KEY)
    if response.status_code!=200:
        print('Unexpected Status code: ', response.status_code)
        sys.exit()  

    # Load the data into a DataFrame
    data = StringIO(response.text)
    df = pd.read_csv(data)

    return df