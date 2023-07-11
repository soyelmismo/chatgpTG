from python_weather import METRIC, IMPERIAL, Client

async def getweather(location: str, unit: str = "C"):
    if unit == "C":
        newwnit = METRIC
    else:
        newwnit = IMPERIAL
    info = ""

    # declare the client. the measuring unit used defaults to the metric system (celcius, km/h, etc.)
    try:
        async with Client(unit=newwnit) as client:
            # fetch a weather forecast from a city
            weather = await client.get(location=location)

            # returns the current day's forecast temperature (int)
            info += f"Current temperature: {weather.current.temperature}°{unit}"

            # get the weather forecast for a few days
            for forecast in weather.forecasts:
                info += f"\n{forecast.date:%A, %B %d, %Y}: {forecast.temperature}°{unit}"
                info += f"\nSunrise: {forecast.astronomy.sun_rise:%H:%M}"
                info += f"\nSunset: {forecast.astronomy.sun_set:%H:%M}"

                # hourly forecasts
                for hourly in forecast.hourly:
                    info += f"\n{hourly.time:%I:%M %p}: {hourly.temperature}°{unit}, {hourly.description}"
        return info

    except Exception as e: raise ConnectionError(e)
