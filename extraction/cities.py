import requests

url = "https://simplemaps.com/static/data/country-cities/ma/ma.csv"

response = requests.get(url)
with open("data/bronze/cities/ma_cities.csv", "w", encoding="utf-8") as file:
    file.write(response.text)
