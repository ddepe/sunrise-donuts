"""
Script to update historical sales data using utility functions.

This script:
- Retrieves the last update date from an existing aggregated sales CSV file.
- Calls the `update_history` function to append new data starting from the last known date.

Dependencies:
- `sales_data_util`: A utility module containing functions for managing and updating sales data.
"""
import pathlib

import squareup.sales_data_util

# Get the directory of the current script
base_dir = pathlib.Path(__file__).resolve().parent.parent


data_file_path = base_dir / 'data' / 'aggregated_sales.csv'
last_date = squareup.sales_data_util.get_last_update_date(data_file_path) 

squareup.sales_data_util.update_history(last_date)