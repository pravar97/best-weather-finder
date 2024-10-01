import requests
from requests.auth import HTTPBasicAuth

import csv
printed = set()
def read_csv_file(file_path):
    rows = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file, delimiter=';')
        field_names = next(reader)  # Get the field names from the first row
        for row in reader:
            row_dict = {}
            for field, value in zip(field_names, row):
                if ', ' in value:
                    try:
                        x, y = map(float, value.split(', '))
                        value = (x, y)
                    except ValueError:
                        pass
                row_dict[field] = value
            rows.append(row_dict)
    return rows


def getData(hourly, output, lat, long):
    # API endpoint and key
    api_url = 'https://archive-api.open-meteo.com/v1/archive'
    api_key = '890bc29ca963407bb7e173936231306'

    # API request headers
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # API request parameters (if required)
    params = {
        "latitude": lat,
        "longitude": long,
        "start_date": "2012-01-01",
        "end_date": "2022-12-31",
        "hourly": hourly,
        "timezone": 'auto'

    }

    auth = HTTPBasicAuth('apikey', api_key)

    # Make the API request
    try:
        response = requests.get(api_url, headers=headers, auth=auth, params=params)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx errors
        data = response.json()
        # Process the response data

    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')

    for time, value in zip(data['hourly']['time'],  data['hourly'][hourly]):
        if time not in output:
            output[time] = {}

        output[time][hourly] = value


    return output

rows = read_csv_file('a.csv')
def getScores(lat, long):
    data = {}
    measurements = ['temperature_2m', "dewpoint_2m", "precipitation", "windspeed_10m"]
    for hourly in measurements:
        data = getData(hourly, data, str(lat), str(long))

    sum = 0
    length = len(data)
    for date, value in data.items():
        temp = value['temperature_2m']
        dew = value['dewpoint_2m']
        prec = value['precipitation']
        wind = value['windspeed_10m']
        if date is None or temp is None:
            length -= 1;
            continue

        score = 10

        isDay = int(date[-5:-3]) >= 5 and int(date[-5:-3]) < 21
        if isDay:
            minTemp = 20
            maxTemp = 36
        else:
            minTemp = 10
            maxTemp = 20

        if temp > maxTemp:
            score -= temp - maxTemp
        elif temp < minTemp:
            score -= minTemp - temp

        if dew > 20:
            score -= dew - 20

        if isDay:
            score -= prec * 10

        if wind > 20 and isDay:
            score -= 0.3 * (wind - 20)

        if score < 0:
            score = 0
        sum += score


    return sum/length

scores = {}

# for lat in range(-90, 90, 10):
#     for long in range(-180, 180, 10):
#


for row in rows:
    if int(row['Population']) > 100000 and row['Country Code'] == 'CA':
        score = getScores(row['Coordinates'][0], row['Coordinates'][1])

        print(row['Name'], score)
print(scores)

