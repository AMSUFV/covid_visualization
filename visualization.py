import pandas as pd

url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series' \
      '/time_series_covid19_confirmed_global.csv '

covid = pd.read_csv(url)
# Melting it for representation
df = pd.melt(covid, id_vars=covid.columns[:4], var_name='Date', value_name='Amount')
# Date parsing
df['Date'] = pd.to_datetime(covid['Date'], infer_datetime_format=True)
# TODO: check if necessary
# Sorting by country
df.sort_values(by='Country/Region', inplace=True)
# Resetting the index
df.reset_index(drop=True, inplace=True)
