import sales_data_util

last_date = sales_data_util.get_last_update_date('data/aggregated_sales.csv') 

sales_data_util.update_history(last_date)