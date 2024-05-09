"""
This module provides a complete pipeline to forecast and visualize sales data using Facebook Prophet and Plotly.

The module:
- Loads aggregated sales data from a CSV file.
- Preprocesses the data by renaming columns, removing non-sales days, and adding US holidays to the Prophet model.
- Trains a Prophet model using the preprocessed data.
- Forecasts future sales over a specified period and generates plots using both Matplotlib and Plotly.
- Exports the forecast and trends plots as images and interactive HTML files.

Functions and Classes Used:
- `Prophet`: Forecasting model from the `prophet` package.
- `get_last_update_date`: A utility function from `squareup.sales_data_util`.
- `plotly.graph_objs`: Used for creating interactive plots.

Dependencies:
- `datetime`
- `pandas`
- `prophet`
- `matplotlib`
- `plotly`
"""

import datetime
import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.offline as py

from  squareup.sales_data_util import get_last_update_date
 
input_csv = "data/aggregated_sales.csv"

df = pd.read_csv(input_csv)

latest_date = get_last_update_date(input_csv)

# Rename the necessary columns to match Prophet's requirements
df.rename(columns={"Sales": "ds", "Gross Sales": "y"}, inplace=True)

# Drop all closed days
df = df[df['y'] != 0.0]

# Initialize a Prophet model with US holidays
model = Prophet()
model.add_country_holidays(country_name='US')

model.fit(df)

# Create a future DataFrame with predictions for the next 365 days
future = model.make_future_dataframe(periods=365)

forecast = model.predict(future)

fig, ax = plt.subplots(figsize=(10, 6))

ax.set_xlim(pd.to_datetime(latest_date - datetime.timedelta(days=2)), 
            pd.to_datetime(latest_date + datetime.timedelta(days=7)))

fig1 = model.plot(forecast, ax=ax)
fig2 = model.plot_components(forecast)

fig1.savefig(f"output/forecast_{datetime.datetime.now().strftime('%Y%m%d')}.png")
fig2.savefig(f"output/trends_{datetime.datetime.now().strftime('%Y%m%d')}.png")

# Create Plotly traces for the forecast and confidence intervals
trace1 = go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecasted Sales')
trace2 = go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], mode='lines', fill='tonexty', name='Lower Confidence')
trace3 = go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], mode='lines', fill='tonexty', name='Upper Confidence')

# Create a trace for the actual historical data (sales) as dots
trace_actual = go.Scatter(x=forecast['ds'], y=df['y'], mode='markers', name='Actual Sales', marker=dict(color='red'))

# Plotly layout
layout = go.Layout(
    title='Sales Forecast',
    xaxis={
        'title': 'Date',
        'range': [pd.to_datetime(latest_date - datetime.timedelta(days=7)), 
                  pd.to_datetime(latest_date + datetime.timedelta(days=7))]
           },
    yaxis={'title': 'Sales'},
    hovermode='x unified'
)

# Create and display the forecast plot using Plotly
fig = go.Figure(data=[trace1, trace2, trace3, trace_actual], layout=layout)
py.plot(fig, filename='output/sales_forecast.html', auto_open=False)


# Create traces for the trend component and its confidence intervals
trace_trend = go.Scatter(x=forecast['ds'], y=forecast['trend'], mode='lines', name='Trend')
trace_trend2 = go.Scatter(x=forecast['ds'], y=forecast['trend_lower'], mode='lines', fill='tonexty', name='Lower Confidence')
trace_trend3 = go.Scatter(x=forecast['ds'], y=forecast['trend_upper'], mode='lines', fill='tonexty', name='Upper Confidence')

fig = go.Figure(data=[trace_trend,trace_trend2,trace_trend3])

fig.update_layout(
    title='Sales Trends',
    xaxis_title='Date',
    yaxis_title='Sales',
    hovermode='x unified'
)

py.plot(fig, filename='output/sales_trends.html', auto_open=False)
