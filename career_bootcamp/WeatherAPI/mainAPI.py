from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from career_bootcamp.WeatherAPI.databaseWeather import  get_db
import requests



app = FastAPI(
    title="Weather API",
    version="0.1.0",
    description="API for tracking weather"
)





def get_weather_api(city):
    url = f"https://wttr.in/{city}?format=j1"
    response = requests.get(url)
    data = response.json()

    temp = data['current_condition'][0]['temp_C']
    desc = data['current_condition'][0]['weatherDesc'][0]['value']
    humidity = data['current_condition'][0]['humidity']

    return {
        "city": city,
        "temperature": temp,
        "description": desc,
        "humidity": humidity
    }


@app.get("/weather/{city}")
def get_weather(city: str):
    with get_db() as db:

        check_cache = """
                      SELECT *
                      FROM weather_cache
                      WHERE city = %s
                        AND fetched_at > NOW() - INTERVAL 30 MINUTE
                      ORDER BY fetched_at DESC
                          LIMIT 1
                      """
        db.execute(check_cache, (city.lower(),))
        cached_data = db.fetchone()

        if cached_data:
            return {
                "city": city,
                "temperature": cached_data['temperature'],
                "description": cached_data['description'],
                "humidity": cached_data['humidity'],
                "source": "cache",
                "fetched_at": cached_data['fetched_at'],
                "message": "Data from database (fast!)"
            }


        weather = get_weather_api(city)

        if not weather:
            raise HTTPException(status_code=404, detail=f"Could not get weather for {city}")


        save_query = """
                     INSERT INTO weather_cache (city, temperature, description, humidity)
                     VALUES (%s, %s, %s, %s)
                     """
        db.execute(
            save_query,
            (city.lower(), weather['temperature'], weather['description'], weather['humidity'])
        )

        return {
            "city": city,
            "temperature": weather['temperature'],
            "description": weather['description'],
            "humidity": weather['humidity'],
            "source": "api",
            "fetched_at": datetime.now(),
            "message": "Fresh data from API (saved to database)"
        }


@app.get("/weather/{city}/history")
def get_history(city: str):
    with get_db() as db:
        query = "SELECT * FROM weather_cache WHERE city = %s ORDER BY fetched_at DESC"
        db.execute(query, (city.lower(),))
        records = db.fetchall()

        return {
            "city": city,
            "total_records": len(records),
            "history": records
        }