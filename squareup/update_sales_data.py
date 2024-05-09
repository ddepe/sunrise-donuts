"""
Script to update historical sales data using utility functions.

This script:
- Retrieves the last update date from an existing aggregated sales CSV file.
- Calls the `update_history` function to append new data starting from the last known date.

Dependencies:
- `sales_data_util`: A utility module containing functions for managing and updating sales data.
"""

import sales_data_util

last_date = sales_data_util.get_last_update_date('data/aggregated_sales.csv') 

sales_data_util.update_history(last_date)