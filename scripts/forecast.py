import datetime
import pandas as pd
from prophet import Prophet
import re
import decimal

# df = pd.read_csv("data/combined_sales.csv")
df = pd.read_csv("data/aggregated_sales.csv")

df.rename(columns={"Sales": "ds", "Gross Sales": "y"}, inplace=True)

# Convert gross sales string to float
# df.y = df.y.apply(lambda x: decimal.Decimal(re.sub(r'[^\d.]', '', x)))  # Removes all non-numerical char (except .)
# Drop all closed days
df = df[df['y'] != 0.0]

# print(df.head(10))

m = Prophet()
m.add_country_holidays(country_name='US')

m.fit(df)
print(m.train_holiday_names)

future = m.make_future_dataframe(periods=30)
# print(future.tail())

forecast = m.predict(future)
print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(30))

fig1 = m.plot(forecast)
fig2 = m.plot_components(forecast)

fig1.savefig(f"fig1_{datetime.datetime.now().strftime('%Y%m%d')}.png")
fig2.savefig(f"fig2_{datetime.datetime.now().strftime('%Y%m%d')}.png")