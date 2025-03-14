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
            day_forecasts = []
            night_forecasts = []
            
            # Since timestamps may not be available, we'll create our own forecasts
            # based on the available weather data
            weathers = weather_data.weathers
            
            # Current time and date
            current_hour = now.hour
            current_date = now.date()
            tomorrow_date = current_date + datetime.timedelta(days=1)
            
            # Determine number of forecasts to show (daylight and evening)
            day_forecast_count = min(8, len(weathers))
            night_forecast_count = min(4, len(weathers))
            
            # Create daytime forecasts (for remaining hours of today)
            for i in range(day_forecast_count):
                if i < len(weathers):
                    hours_ahead = i + 1  # Start from 1 hour ahead
                    
                    # Calculate forecast time
                    forecast_time = now + datetime.timedelta(hours=hours_ahead)
                    # Round to the nearest hour
                    forecast_time = forecast_time.replace(minute=0, second=0, microsecond=0)
                    
                    # Only include forecasts for today's daytime (up to 18:00)
                    if forecast_time.date() == current_date and forecast_time.hour <= 18:
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
                        day_forecasts.append(forecast)
            
            # Create night forecasts (evening and night hours)
            night_offset = day_forecast_count
            for i in range(night_forecast_count):
                idx = i + night_offset
                if idx < len(weathers):
                    weather_entry = weathers[idx]
                    
                    # For night hours, we'll start from 19:00 today and go into early hours of tomorrow
                    if current_hour < 19:
                        # If it's before 19:00, create forecasts starting from 19:00
                        night_hours = [19, 21, 23, 1]  # Fixed hours for evening and night
                        hour = night_hours[i] if i < len(night_hours) else 1
                        
                        # Handle hours past midnight
                        if hour < 12 and hour < 6:  # Early morning hours
                            forecast_time = datetime.datetime.combine(
                                tomorrow_date,  # Use tomorrow's date
                                datetime.time(hour, 0)
                            )
                        else:
                            forecast_time = datetime.datetime.combine(
                                current_date,  # Use today's date
                                datetime.time(hour, 0)
                            )
                    else:
                        # If it's already evening/night, create forecasts for the next 8 hours
                        hours_ahead = i * 2 + 1  # Every 2 hours
                        
                        # Calculate forecast time
                        forecast_time = now + datetime.timedelta(hours=hours_ahead)
                        # Round to the nearest hour
                        forecast_time = forecast_time.replace(minute=0, second=0, microsecond=0)
                    
                    # Get temperature
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
                    night_forecasts.append(forecast)
            
            # Format forecasts into message
            # Daytime forecasts
            if day_forecasts:
                has_forecasts = True
                message += "*Prakiraan Cuaca Siang Hari:*\n"
                
                # Add forecasts as a simple list
                for forecast in day_forecasts:
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
            
            # Night forecasts
            if night_forecasts:
                has_forecasts = True
                
                # Add a line break between day and night forecasts
                if day_forecasts:
                    message += "\n"
                
                message += "*Prakiraan Cuaca Malam Hari:*\n"
                
                # Add forecasts as a simple list
                for forecast in night_forecasts:
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
            
            if not has_forecasts:
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
        print("⚠️ Tidak dapat mengambil data cuaca dari BMKG. Silakan periksa koneksi internet Anda atau coba lagi nanti.")

if __name__ == "__main__":
    asyncio.run(main())
