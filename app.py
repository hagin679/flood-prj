from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import random # Added for simulation fallback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⚠️ MAKE SURE THIS IS YOUR ACTIVE KEY
API_KEY = "YOUR_OPENWEATHER_API_KEY"

@app.get("/get_risk")
async def get_risk(lat: float, lon: float):
    try:
        # 1. Fetch Current Weather
        curr_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        curr_resp = requests.get(curr_url).json()

        # 2. Fetch Forecast (Next 3 hours)
        fore_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        fore_resp = requests.get(fore_url).json()

        # Extract rain from current or forecast
        rain_now = curr_resp.get("rain", {}).get("1h", 0)
        
        # Get forecast rain (3h) if available
        forecast_list = fore_resp.get("list", [])
        rain_future = forecast_list[0].get("rain", {}).get("3h", 0) if forecast_list else 0
        
        # Use the highest value found
        rainfall = max(rain_now, rain_future)
        humidity = curr_resp.get("main", {}).get("humidity", 0)

        # --- SIMULATION MODE ---
        # If the weather is perfectly clear (0 rain), we generate a 
        # random value for testing so your dashboard isn't always "LOW"
        is_simulated = False
        if rainfall == 0:
            rainfall = round(random.uniform(0, 45), 2)
            is_simulated = True
        # -----------------------

        # Risk Logic
        risk = "LOW"
        color = "#28a745" # Green

        if rainfall > 30 or (rainfall > 15 and humidity > 85):
            risk = "HIGH"
            color = "#dc3545" # Red
        elif rainfall > 10:
            risk = "MEDIUM"
            color = "#ffc107" # Yellow

        return {
            "rainfall": rainfall,
            "risk": risk,
            "color": color,
            "humidity": humidity,
            "city": curr_resp.get("name", "Search Location"),
            "simulated": is_simulated
        }

    except Exception as e:
        print(f"Error: {e}")
        return {"error": "Could not fetch data. Check API Key and Internet."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)