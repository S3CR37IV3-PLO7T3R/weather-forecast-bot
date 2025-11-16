import requests
import json

API_KEY = "af8d78d978fe1db7e7a1a1ef5384fe07" 
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# City you want to test
city = "London"

# --- MAKING THE API REQUEST ---

# 1. We build the full URL with our parameters
#    q=city      -> The city name
#    appid=API_KEY -> Your key
#    units=metric -> To get temperature in Celsius
request_url = f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric"

print(f"Sending request to: {request_url}\n")

# 2. We use the 'requests' library to send a GET request
try:
    response = requests.get(request_url)

    # 3. Check if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        # 4. 'response.json()' converts the JSON data into a Python dictionary
        data = response.json()
        
        print("--- SUCCESS! Full Data Received ---")
        # We use json.dumps for "pretty printing" the dictionary
        print(json.dumps(data, indent=4))
        print("-----------------------------------")

        # 5. We extract the specific pieces of data we want
        description = data['weather'][0]['description']
        temperature = data['main']['temp']
        city_name = data['name']
        
        print(f"\n✅ Successfully parsed data for {city_name}:")
        print(f"   Temperature: {temperature}°C")
        print(f"   Description: {description}")

    else:
        # If we get a 401, it's usually an API key problem
        if response.status_code == 401:
            print("--- ERROR ---")
            print("🛑 HTTP 401 Error: Unauthorized.")
            print("This usually means your API key is wrong or not active yet.")
            print("Please double-check your API key in the script.")
        else:
            print(f"--- ERROR ---")
            print(f"🛑 Received HTTP error {response.status_code}:")
            print(response.text)

except requests.exceptions.RequestException as e:
    print(f"--- FATAL ERROR ---")
    print(f"🛑 Could not connect to the API. Check your internet connection.")
    print(e)