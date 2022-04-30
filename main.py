from audioop import add
from tracemalloc import start
import requests
import urllib.parse
import datetime

import json
from flask import Flask, request, jsonify
app = Flask(__name__)


def forecast(addr: str, forecastLength: int) -> dict:
    """Returns json data for weather on specified hour

    Args:
        addr (str): Address including city, state, and zip 
        forecastLength (int): hours in the future to forecast

    Returns:
        dict: data
    """

    def convertDateStr(dateStr: str) -> datetime.datetime:
        """Convert the weather.gov datestring to a datetime object

        Args:
            dateStr (str): weather.gov datestring

        Returns:
            datetime.datetime: datetime object
        """
        # Example - 2022-04-29T13:00:00-05:00
        # see https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior for details
        formattingStr = "%Y-%m-%dT%H:%M:%S%z"
        return datetime.datetime.strptime(dateStr, formattingStr)

    # Get Lat/lon
    url = 'https://nominatim.openstreetmap.org/search/' + \
        urllib.parse.quote(addr) + '?format=json'
    response = requests.get(url).json()
    lat = response[0]['lat']
    lon = response[0]['lon']

    # Get hourly forecast URL in weather api. Accurate to 2.5km
    url = 'https://api.weather.gov/points/'+lat+','+lon
    response = requests.get(url).json()

    hourlyforecastURL = response['properties']['forecastHourly']
    radarStation = response['properties']['radarStation']

    response = requests.get(hourlyforecastURL).json()

    periods = response['properties']['periods']
    reply = {
        'time': '',
        'station': radarStation,
        'fuzzy': '',
        'temperature': '',
        'temperatureUnit': '',
        'windSpeedMPH': '',
        'windDirection': ''
    }
    period = periods[forecastLength]

    startTime = convertDateStr(period['startTime'])
    startHour = startTime.hour

    tempValue = period['temperature']
    tempUnit = period['temperatureUnit']
    windSpeed = int(period['windSpeed'].replace(' mph', ''))
    windDirection = period['windDirection']

    reply['time'] = startTime
    reply['fuzzy'] = period['shortForecast']
    reply['temperature'] = tempValue
    reply['temperatureUnit'] = tempUnit
    reply['windSpeedMPH'] = windSpeed
    reply['windDirection'] = windDirection
    return reply


address = '2119 Dakota St, norman, ok, 73069'
output = forecast(address, 2)
print(output)


@app.route('/', methods=['GET'])
def serve_forecast():
    address = request.args.get('address')
    leadHours = int(request.args.get('leadHours'))
    output = forecast(address, leadHours)
    print(output['fuzzy'])
    return jsonify(output)


app.run()
