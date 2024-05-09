"""
Script to merge sales data downloaded from Squareup's report summary.

This script contains functions to:
- Add a suffix to a file name for creating unique versions.
- Transpose the data in a CSV file, facilitating data manipulation.
- Combine multiple transposed CSV files into a single, clean CSV file.

Dependencies:
- argparse
- csv
- datetime
- decimal
- os
- pandas
- re
"""

import csv
import datetime
import decimal
import os
import pandas as pd
import re

def add_suffix_to_filename(file_path, suffix):
    """
    Adds a suffix to the file name of a given file path.

    Args:
        file_path (str): The file path.
        suffix (str): The suffix to be added to the file name.

    Returns:
        str: The file path with the suffix added to the file name.
    """
    # Split the file path into directory path and file name
    directory, filename = os.path.split(file_path)
    
    # Split the file name into name and extension
    name, extension = os.path.splitext(filename)
    
    # Append the suffix to the file name
    new_filename = f"{name}_{suffix}{extension}"
    
    # Join the directory path and the new file name
    new_file_path = os.path.join(directory, new_filename)
    
    return new_file_path

def transpose_csv(input_file, output_file=None):
    """
    Reads and transposes the content of a CSV file.

    Args:
        input_file (str): Path to the input CSV file.
        output_file (str, optional): Path to the output transposed CSV file. If not provided, a default will be used.

    Returns:
        None
    """
    # Read the CSV file
    with open(input_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader)

    # Transpose the data using zip and map
    transposed_data = list(map(list, zip(*data)))
    print(transposed_data[-1])

    if not output_file:
        output_file = add_suffix_to_filename(input_file, "t")
        print(output_file)

    # Write the transposed data to a new CSV file
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(transposed_data)


def combine_csv(files, output_file):
    """
    Combines multiple CSV files into a single, cleaned CSV file.

    Args:
        files (list of str): List of file paths to the input CSV files.
        output_file (str): Path to the output combined CSV file.

    Returns:
        None
    """
    # Read each CSV file into a DataFrame
    dfs = [pd.read_csv(file_path) for file_path in files]

    # Concatenate the DataFrames along the rows
    combined_df = pd.concat(dfs, ignore_index=True)

    # Remove unnamed columns and specific columns not needed in the final output
    combined_df = combined_df.loc[:, ~combined_df.columns.str.startswith('Unnamed')]
    combined_df = combined_df.drop(columns=['Payments'])

    # Function to convert non-numeric characters to a valid decimal
    process_value = lambda x: decimal.Decimal(re.sub(r'[^-\d.]', '', x))

    # Identify non-float columns in the DataFrame to process them appropriately
    non_float_columns = combined_df.iloc[:, 1:].select_dtypes(exclude=['float']).columns
    combined_df[non_float_columns] = combined_df[non_float_columns].applymap(process_value).astype(float)

    # Write the combined DataFrame to a new CSV file
    combined_df.to_csv(output_file, index=False)

# Example usage
files = ['./data/sales-summary-2022.csv', 
         './data/sales-summary-2023.csv', 
         './data/sales-summary-2024.csv']

for file_path in files:
    transpose_csv(file_path)

# Generate transposed file names with the suffix "t"
t_files = [add_suffix_to_filename(file_path, "t") for file_path in files]
output_file = f'combined_sales_{datetime.datetime.now().strftime("%Y%m%d")}.csv'
combine_csv(t_files, output_file)
