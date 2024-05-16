"""
Functions to update, refresh, and maintain sales history data using the Square API.

This script includes functions to:
- Retrieve the latest update date from an aggregated sales CSV file.
- Generate a range of dates to cover historical sales data.
- Update existing sales data or create a fresh sales history file.
- Fetch data via the Square API and write it to a CSV file.

Dependencies:
- `csv`, `datetime`, `pytz`, `os`: Built-in Python libraries for data processing.
- `square.client`, `square.http.auth.o_auth_2`: Square SDK for accessing the Square API.
"""

import csv
import datetime
import pytz
import os
import pathlib
import square.client
import square.http.auth.o_auth_2

# Square location ID and API credentials fetched from environment variables
LOCATION = os.environ['SQUARE_LOCATION']
bearer_auth_credential = square.http.auth.o_auth_2.BearerAuthCredentials(
    access_token=os.environ['SQUARE_ACCESS_TOKEN'])

# Initialize the Square client with production credentials
client = square.client.Client(
    bearer_auth_credentials=bearer_auth_credential,
    environment='production')

# Set the time zone to PST (Pacific Standard Time)
pst = pytz.timezone('America/Los_Angeles')


def get_last_update_date(csv_file):
    """
    Retrieve the last recorded date from the given sales CSV file and return the next date.

    Args:
        csv_file (str): Path to the aggregated sales CSV file.

    Returns:
        datetime.date: The date immediately following the latest recorded date.
    """
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        # Move the pointer to the end of the file
        file.seek(0, 2)
        # Get the position of the last character
        pos = file.tell() - 1
        # Start searching backwards until a newline character is found
        while pos > 0 and file.read(1) != '\n':
            pos -= 1
            file.seek(pos)
        # Read the last row
        last_row_date = file.readline().strip().split(',')[0]
        last_date = datetime.datetime.strptime(last_row_date, '%m/%d/%Y').date()
        return last_date + datetime.timedelta(days=1)

def generate_date_range(start_date, end_date):
    """
    Generate a range of dates from the start to end date, inclusive.

    Args:
        start_date (datetime.date): The starting date of the range.
        end_date (datetime.date): The final date of the range.

    Yields:
        datetime.date: The current date within the specified range.
    """
    delta = datetime.timedelta(days=1)
    while start_date <= end_date:
        yield start_date
        start_date += delta


def update_history(last_date, file_path=None, headers=None):
    """
    Append historical sales data starting from the last recorded date to an existing aggregated sales CSV file.

    Args:
        last_date (datetime.date): The starting date for historical data updates.
        headers (list of str, optional): Column headers for the CSV file. If not specified, a default set is used.
    """
    if not headers:
        headers = [
            "Sales",
            "Gross Sales",
            "Returns",
            "Discounts & Comps",
            "Net Sales",
            "Gift Card Sales",
            "Tax",
            "Tip",
            "Refunds by Amount",
            "Total",
            "Total Collected",
            "Cash",
            "Card",
            "Other",
            "Gift Card",
            "Fees",
            "Net Total"
        ]
    
    # Open the existing aggregated sales CSV file in append mode
    if file_path is None:
        file_path = f'data/aggregated_sales.csv'
    with open(file_path, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        write_history(writer, last_date, headers)

def refresh_history(headers=None):
    """
    Create a new aggregated sales CSV file containing historical data starting from November 1, 2022.

    Args:
        headers (list of str, optional): Column headers for the CSV file. If not specified, a default set is used.
    """
    if not headers:
        headers = [
            "Sales",
            "Gross Sales",
            "Returns",
            "Discounts & Comps",
            "Net Sales",
            "Gift Card Sales",
            "Tax",
            "Tip",
            "Refunds by Amount",
            "Total",
            "Total Collected",
            "Cash",
            "Card",
            "Other",
            "Gift Card",
            "Fees",
            "Net Total"
        ]
    
    # Set up a new CSV file with the current date and start from November 1, 2022
    file_path = f'data/aggregated_sales_{datetime.datetime.now().strftime("%Y%m%d")}.csv'
    first_date = datetime.datetime(2022, 11, 1).date()
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        write_history(writer, first_date, headers)


def write_history(csv_writer, start_date, headers):
    """
    Fetch and write sales data for each date from the start date to the current date via the Square API.

    Args:
        csv_writer (csv.DictWriter): Writer object for the aggregated sales CSV file.
        start_date (datetime.date): The date from which to start writing sales data.
        headers (list of str): Column headers to structure the output data.
    """
    today = datetime.datetime.now().date()

    def sum_sales(payments):
        """
        Aggregate and update the sales data from a list of payments.

        Args:
            payments (list of dict): A list of payment dictionaries containing sales data.
        """
        for payment in payments:
            # Ignore payments that are not completed or approved
            if payment["status"] != "COMPLETED" and payment["status"] != "APPROVED":
                continue
            sales_data["Gross Sales"] += payment["amount_money"]["amount"] if "amount_money" in payment else 0
            sales_data["Tip"] += payment["tip_money"]["amount"] if "tip_money" in payment else 0
            sales_data["Refunds by Amount"] += payment["refunded_money"]["amount"] if "refunded_money" in payment else 0
            sales_data["Total"] += payment["total_money"]["amount"] if "total_money" in payment else 0
            sales_data["Fees"] += payment['processing_fee'][0]['amount_money']["amount"] if 'processing_fee' in payment else 0

        sales_data["Net Total"] = sales_data["Total"] - sales_data["Fees"]
        sales_data["Net Sales"] = sales_data["Gross Sales"] - sales_data["Refunds by Amount"]
        sales_data["Total Collected"] = sales_data["Total"]
        sales_data["Card"] = sales_data["Total"]

    def convert_cents_to_usd():
        """
        Convert all sales data values from cents to USD.
        """
        for header in sales_data:
            sales_data[header] /= 100.0
    
    for date in generate_date_range(start_date, today):
        first_midnight = pst.localize(datetime.datetime.combine(date, datetime.datetime.min.time())).isoformat()
        last_midnight = pst.localize(datetime.datetime.combine(date, datetime.datetime.min.time()) 
                                + datetime.timedelta(days=1) - datetime.timedelta(milliseconds=1)).isoformat()
        print(first_midnight, last_midnight)
        
        # Fetch payments data from the Square API for the given date range
        result = client.payments.list_payments(
            begin_time = first_midnight,
            end_time = last_midnight,
        )

        # Initialize an empty dictionary to store sales data for the current date
        sales_data = {header: 0.0 for header in headers}

        # Process and aggregate the payments data if the API call was successful
        if result.is_success():
            if result.body and "payments" in result.body:
                sum_sales(result.body["payments"])

                # Necessary for day with lots sales to pull until no more data
                while "cursor" in result.body:
                    result = client.payments.list_payments(
                        begin_time = first_midnight,
                        end_time = last_midnight,
                        cursor=result.body["cursor"]
                    )

                    if result.is_success():
                        if result.body and "payments" in result.body:
                            sum_sales(result.body["payments"])
                
                convert_cents_to_usd()

        # Set the date as the "Sales" field and write the data to the CSV file
        sales_data["Sales"] = date.strftime('%m/%d/%Y')
        print(sales_data)
        csv_writer.writerow(sales_data)
