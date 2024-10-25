import tkinter as tk
import requests
import time

# List of cities for real-time weather updates
cities = ["Delhi", "Mumbai", "Chennai", "Bangalore", "Kolkata", "Hyderabad"]

# Function to get weather data for each city in the list
def get_weather():
    weather_data = ""
    for city in cities:
        api = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=11f654576dccb13e42018b3087676715"
        try:
            json_data = requests.get(api).json()

            # Check if city is found
            if json_data.get("cod") != 200:
                weather_data += f"{city}: City not found\n\n"
                continue

            # Extract and format weather data
            condition = json_data['weather'][0]['main']
            temp = int(json_data['main']['temp'] - 273.15)
            min_temp = int(json_data['main']['temp_min'] - 273.15)
            max_temp = int(json_data['main']['temp_max'] - 273.15)
            pressure = json_data['main']['pressure']
            humidity = json_data['main']['humidity']
            wind = json_data['wind']['speed']
            sunrise = time.strftime("%I:%M:%S", time.gmtime(json_data['sys']['sunrise']))
            sunset = time.strftime("%I:%M:%S", time.gmtime(json_data['sys']['sunset']))

            # Append weather data for each city
            weather_data += (
                f"{city}\n"
                f"Condition: {condition}\n"
                f"Temp: {temp}°C\n"
                f"Max Temp: {max_temp}°C\n"
                f"Min Temp: {min_temp}°C\n"
                f"Pressure: {pressure} hPa\n"
                f"Humidity: {humidity}%\n"
                f"Wind Speed: {wind} m/s\n"
                f"Sunrise: {sunrise}\n"
                f"Sunset: {sunset}\n\n"
            )

        except Exception as e:
            weather_data += f"{city}: Error fetching data - {e}\n\n"

    # Update the label with all cities' weather data
    label.config(text=weather_data)
    canvas.after(300000, get_weather)  # Schedule to run every 5 minutes (300,000 ms)

# Set up the tkinter window
canvas = tk.Tk()
canvas.geometry("600x500")
canvas.title("Real-Time Weather Monitoring")

f = ("poppins", 12, "bold")

label = tk.Label(canvas, font=f, justify='left')
label.pack(pady=20)

# Initial call to start fetching weather data
get_weather()

canvas.mainloop()
