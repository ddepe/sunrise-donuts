# Sunrise Donuts Sales Data Analysis

This repository contains Python scripts and utilities for processing and forecasting sales data from Square's reporting system. Using the Square API and external libraries like Prophet, these scripts provide automated tools to maintain and analyze aggregated sales data.

## Features
- **Sales Data Aggregation:** Efficiently merges and processes multiple CSV files containing sales summaries.
- **Data Update:** Automatically appends new data to an aggregated file starting from the last recorded date.
- **Forecasting:** Utilizes Facebook Prophet to predict future trends based on historical data.
- **Interactive Visualization:** Generates interactive plots using Plotly for exploring and analyzing forecasts.

## Installation
1. Clone this repository:
   ```bash
   git clone git@github.com:ddepe/sunrise-donuts.git
   ```
2. Navigate to the project folder:
   ```bash
   cd sunrise-donuts
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
4. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
5. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
1. **Environment Variables:**
   - Set up the following environment variables:
     - `SQUARE_LOCATION`: Your Square location ID.
     - `SQUARE_ACCESS_TOKEN`: Your Square API access token.

2. **Data Files:**
   - Place all your input CSV files in the `data/` folder.

## Usage
### Merging and Processing Sales Data
1. **Merging Data:**
   - `merge_reports.py`: Aggregates data from multiple input CSV files into a single combined file and transposes rows and columns in the input sales data files.
    - Usage:
    ```bash
     python merge_reports.py
     ```

2. **Updating Aggregated Sales Data:**
   - `update_sales.py`: Updates historical sales data by appending new data starting from the last recorded date.
   - Usage:
     ```bash
     python update_sales.py
     ```

### Forecasting Sales Data
- `forecast_sales.py`: Generates future forecasts based on historical sales data using Facebook Prophet.
- Usage:
  ```bash
  python forecast_sales.py
  ```

### Utility Functions
- `sales_util.py`: Contains utility functions for managing sales data files, including:
  - `get_last_update_date(csv_file)`: Retrieves the last recorded date from a given sales CSV file.
  - `update_history(last_date)`: Updates historical sales data from the last recorded date.

## Visualization
- **Plotly Interactive Plots:**
  - Generated in `forecast_sales.py` for forecasting and exploring trends.
  - Saved as HTML files in the `output/` folder for easy viewing.

- **Matplotlib Plots:**
  - Also generated in `forecast_sales.py` for static visualizations and saved as PNG files.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact
For questions or suggestions, please reach out via GitHub issues.
