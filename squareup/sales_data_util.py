import csv
import datetime
import pytz
import os
import square.client
import square.http.auth.o_auth_2

LOCATION = os.environ['SQUARE_LOCATION']

bearer_auth_credential = square.http.auth.o_auth_2.BearerAuthCredentials(
    access_token=os.environ['SQUARE_ACCESS_TOKEN'])

client = square.client.Client(
    bearer_auth_credentials=bearer_auth_credential,
    environment='production')

# Set the time zone to PST (Pacific Standard Time)
pst = pytz.timezone('America/Los_Angeles')

def get_last_update_date(csv_file):
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
    delta = datetime.timedelta(days=1)
    while start_date <= end_date:
        yield start_date
        start_date += delta


def update_history(last_date, headers=None):
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
        
    file_path = f'data/aggregated_sales.csv'
    with open(file_path, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        write_history(writer, last_date, headers)

def refresh_history(headers=None):
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
        
    file_path = f'data/aggregated_sales_{datetime.datetime.now().strftime("%Y%m%d")}.csv'
    first_date = datetime.datetime(2022, 11, 1).date()
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        write_history(writer, first_date, headers)


def write_history(csv_writer, start_date, headers):
    today = datetime.datetime.now().date()

    def sum_sales(payments):
        for payment in payments:
            if payment["status"] != "COMPLETED" and payment["status"] != "APPROVED":
                continue
            sales_data["Gross Sales"] += payment["amount_money"]["amount"] if "amount_money" in payment else 0
            sales_data["Tip"] += payment["tip_money"]["amount"] if "tip_money" in payment else 0
            sales_data["Refunds by Amount"] += payment["refunded_money"]["amount"] if "refunded_money" in payment else 0
            sales_data["Total"] += payment["total_money"]["amount"] if "total_money" in payment else 0
            sales_data["Fees"] -= payment['processing_fee'][0]['amount_money']["amount"] if 'processing_fee' in payment else 0

        sales_data["Net Total"] = sales_data["Total"] + sales_data["Fees"]
        sales_data["Net Sales"] = sales_data["Gross Sales"] - sales_data["Refunds by Amount"]
        sales_data["Total Collected"] = sales_data["Total"]
        sales_data["Card"] = sales_data["Total"]

    def convert_cents_to_usd():
        for header in sales_data:
            sales_data[header] /= 100.0
    
    for date in generate_date_range(start_date, today):
        first_midnight = pst.localize(datetime.datetime.combine(date, datetime.datetime.min.time())).isoformat()
        print(first_midnight)

        last_midnight = pst.localize(datetime.datetime.combine(date, datetime.datetime.min.time()) 
                                + datetime.timedelta(days=1) - datetime.timedelta(milliseconds=1)).isoformat()
        print(last_midnight)

        result = client.payments.list_payments(
            begin_time = first_midnight,
            end_time = last_midnight,
        )

        sales_data = {header: 0.0 for header in headers}

        if result.is_success():
            if result.body and "payments" in result.body:
                sum_sales(result.body["payments"])

                while "cursor" in result.body:
                    result = client.payments.list_payments(
                        begin_time = first_midnight,
                        end_time = last_midnight,
                        cursor=result.body["cursor"]
                    )
                    print("2nd half")

                    if result.is_success():
                        if result.body and "payments" in result.body:
                            sum_sales(result.body["payments"])
                
                convert_cents_to_usd()

        sales_data["Sales"] = date.strftime('%m/%d/%Y')
        print(sales_data)
        csv_writer.writerow(sales_data)
