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

df.rename(columns={"Sales": "ds", "Gross Sales": "y"}, inplace=True)

# Convert gross sales string to float
# df.y = df.y.apply(lambda x: decimal.Decimal(re.sub(r'[^\d.]', '', x)))  # Removes all non-numerical char (except .)

# Drop all closed days
df = df[df['y'] != 0.0]

m = Prophet()
m.add_country_holidays(country_name='US')

m.fit(df)
print(m.train_holiday_names)

future = m.make_future_dataframe(periods=365)
# print(future.tail())

forecast = m.predict(future)
print(forecast.columns)

fig, ax = plt.subplots(figsize=(10, 6))

ax.set_xlim(pd.to_datetime(latest_date - datetime.timedelta(days=2)), pd.to_datetime(latest_date + datetime.timedelta(days=7)))

fig1 = m.plot(forecast, ax=ax)
fig2 = m.plot_components(forecast)

fig1.savefig(f"output/forecast_{datetime.datetime.now().strftime('%Y%m%d')}.png")
fig2.savefig(f"output/trends_{datetime.datetime.now().strftime('%Y%m%d')}.png")

# Create Plotly traces for the forecast
trace1 = go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecasted Sales')
trace2 = go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], mode='lines', fill='tonexty', name='Lower Confidence')
trace3 = go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], mode='lines', fill='tonexty', name='Upper Confidence')

# Create trace for the original observations (y data) as dots
trace_actual = go.Scatter(x=forecast['ds'], y=df['y'], mode='markers', name='Actual Sales', marker=dict(color='red'))

# Plotly layout
layout = go.Layout(
    title='Sales Forecast',
    xaxis={
        'title': 'Date',
        'range': [pd.to_datetime(latest_date - datetime.timedelta(days=7)), pd.to_datetime(latest_date + datetime.timedelta(days=7))]  # Adjust range as desired
           },
    yaxis={'title': 'Sales'},
    hovermode='x unified'
)

# Create and display the figure
fig = go.Figure(data=[trace1, trace2, trace3, trace_actual], layout=layout)
py.plot(fig, filename='output/sales_forecast.html', auto_open=True)


# Create traces for the trend and seasonal components
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

py.plot(fig, filename='output/sales_trends.html', auto_open=True)
