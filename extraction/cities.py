import requests

url = "https://simplemaps.com/static/data/country-cities/ma/ma.csv"


try:
    response = requests.get(url , timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"

    print("request successfull")
    with open("data/bronze/cities/ma_cities.csv" , "w" , encoding="utf_8") as file:
        file.write(response.text)

except requests.exceptions.RequestException as e:
    print(f"Request failed : {e}")
except Exception as e:
    print(f"Unexpected error: {e}")








