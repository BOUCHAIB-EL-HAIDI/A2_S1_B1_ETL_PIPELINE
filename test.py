import requests
import pandas as pd
from io import StringIO

url = "https://simplemaps.com/static/data/country-cities/ma/ma.csv"

response = requests.get(url)
response.encoding = "utf-8"

df = pd.read_csv(StringIO(response.text))

print(df.head(10))
print(df.columns)
print(df.shape)
