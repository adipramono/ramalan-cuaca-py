#!/usr/bin/env python3
"""
Simple BMKG Weather Forecast Generator
Generates today's hourly weather forecast that can be copied and pasted
"""

import asyncio
import datetime
import os
import logging
from dotenv import load_dotenv
from bmkg import WeatherForecast

# Load environment variables
load_dotenv()

# Configure logging with custom format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Set higher level for other loggers to reduce noise
logging.getLogger("bmkg").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)

# Get logger for this module
logger = logging.getLogger(__name__)

# Get area code from environment variable or use default
AREA_CODE = os.getenv("AREA_CODE", "62.71.03.1003")  # Default is Palangkaraya

def get_weather_condition_description_id(code):
    """
    Convert BMKG weather code to Indonesian weather description.
    """
    weather_codes = {
        "0": "Cerah ☀️",
        "1": "Cerah Berawan 🌤️",
        "2": "Cerah Berawan 🌤️",
        "3": "Berawan ☁️",
        "4": "Berawan Tebal ☁️",
        "5": "Udara Kabur 🌫️",
        "10": "Asap 🌫️",
        "45": "Berkabut 🌫️",
        "60": "Hujan Ringan 🌦️",
        "61": "Hujan Sedang 🌧️",
        "63": "Hujan Lebat 🌧️",
        "80": "Hujan Lokal 🌦️",
        "95": "Hujan Petir ⛈️",
        "97": "Hujan Petir ⛈️"
    }
    return weather_codes.get(code, f"Kondisi Cuaca Tidak Diketahui (Kode: {code})")

async def get_bmkg_weather_data():
    """
    Fetch weather data from BMKG for the specified area code.
    """
    try:
        async with WeatherForecast() as weather_forecast:
            weather_data = await weather_forecast.get_weather_forecast(AREA_CODE)
            logger.info(f"Successfully fetched weather data for area code: {AREA_CODE}")
            return weather_data
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        return None

def format_weather_message(weather_data):
    """
    Format the weather data into a readable message in Bahasa Indonesia
    with forecasts for today's hours.
    """
    if not weather_data:
        return "⚠️ Tidak dapat mengambil data cuaca dari BMKG."

    now = datetime.datetime.now()
    # Format date in Bahasa Indonesia
    day_names = {
        "Monday": "Senin",
        "Tuesday": "Selasa",
        "Wednesday": "Rabu",
        "Thursday": "Kamis",
        "Friday": "Jumat",
        "Saturday": "Sabtu",
        "Sunday": "Minggu"
    }
    
    month_names = {
        "January": "Januari",
        "February": "Februari",
        "March": "Maret",
        "April": "April",
        "May": "Mei",
        "June": "Juni",
        "July": "Juli",
        "August": "Agustus",
        "September": "September",
        "October": "Oktober",
        "November": "November",
        "December": "Desember"
    }
    
    eng_day = now.strftime("%A")
    eng_month = now.strftime("%B")
    
    current_date = f"{day_names.get(eng_day, eng_day)}, {now.strftime('%d')} {month_names.get(eng_month, eng_month)} {now.strftime('%Y')}"
    
    # Default area name
    area_name = "Bukit Tunggal, Palangkaraya"
    
    # Start building the message
    message = f"*Info Cuaca BMKG* 🌤️\n\n"
    message += f"*Tanggal:* {current_date}\n"
    
    has_forecasts = False
    
    try:
        # Get location information if available
        if hasattr(weather_data, 'location') and weather_data.location:
            location = weather_data.location
            if hasattr(location, 'name') and location.name:
                area_name = location.name
        
        message += f"*Lokasi:* {area_name}\n\n"
        
        # Process weather forecasts
        if hasattr(weather_data, 'weathers') and weather_data.weathers:
            today_forecasts = []
            
            # Since timestamps may not be available, we'll create our own forecasts
            # for today's hours based on the available weather data
            weathers = weather_data.weathers
            
            # Create more hourly forecasts for today
            # Generate forecast times for each hour remaining in the day
            current_hour = now.hour
            
            # Calculate hours remaining in the day (from current hour to midnight)
            hours_remaining = 24 - current_hour
            
            # Determine number of forecasts to show (use at most 8 forecasts)
            forecast_count = min(8, hours_remaining, len(weathers))
            
            # Calculate the interval between forecasts to spread them throughout the day
            interval = max(1, hours_remaining // forecast_count)
            
            # Create forecasts at regular intervals
            for i in range(forecast_count):
                if i < len(weathers):
                    hours_ahead = i * interval + 1  # Start from 1 hour ahead
                    
                    # Calculate forecast time
                    forecast_time = now + datetime.timedelta(hours=hours_ahead)
                    # Round to the nearest hour
                    forecast_time = forecast_time.replace(minute=0, second=0, microsecond=0)
                    
                    # Only include forecasts for today
                    if forecast_time.date() == now.date():
                        weather_entry = weathers[i]
                        
                        # Get temperature - try different attribute names that might be used
                        temperature = None
                        for temp_attr in ['temperature', 'temp', 't', 'suhu']:
                            if hasattr(weather_entry, temp_attr):
                                temperature = getattr(weather_entry, temp_attr)
                                if temperature is not None:
                                    break
                        
                        forecast = {
                            'datetime': forecast_time,
                            'weather': getattr(weather_entry, 'weather', None),
                            'temperature': temperature
                        }
                        today_forecasts.append(forecast)
            
            # Format forecasts into message
            if today_forecasts:
                has_forecasts = True
                message += "*Prakiraan Cuaca Hari Ini:*\n"
                
                # Add forecasts as a simple list
                for forecast in today_forecasts:
                    # Format time - only show the hour, no minutes
                    time_str = forecast['datetime'].strftime("%H:00")
                    
                    # Get weather description
                    weather_condition = "Data tidak tersedia"
                    if forecast['weather'] is not None:
                        weather_code = str(forecast['weather'])
                        weather_condition = get_weather_condition_description_id(weather_code)
                    
                    # Format temperature
                    temp_str = ""
                    if forecast['temperature'] is not None:
                        temp_str = f" {forecast['temperature']}°C"
                    
                    # Add forecast to message in a simple list format
                    message += f"• {time_str} WIB: {weather_condition}{temp_str}\n"
            else:
                message += "*Prakiraan Cuaca:* Tidak ada prakiraan untuk hari ini\n"
        else:
            message += "*Prakiraan Cuaca:* Data tidak tersedia\n"
    except Exception as e:
        logger.error(f"Error formatting weather data: {e}")
        message += "*Prakiraan Cuaca:* Error saat memproses data\n"
    
    # Add source
    message += f"\nSumber data: BMKG Indonesia"
    
    return message

async def main():
    """
    Generate weather forecast and display it for copy-pasting.
    """
    print("Fetching weather data from BMKG...")
    weather_data = await get_bmkg_weather_data()
    
    if weather_data:
        # Format and display the weather message
        message = format_weather_message(weather_data)
        print("\n" + "="*50)
        print("WEATHER FORECAST")
        print("="*50)
        print(message)
        print("="*50)
    else:
        print("⚠️ Failed to retrieve weather data. Please check your internet connection or try again later.")

if __name__ == "__main__":
    asyncio.run(main())
