from flask import Flask,request, jsonify, render_template
import requests
import spacy
import datetime
from collections import defaultdict
import re

app = Flask(__name__)

API_KEY = "af8d78d978fe1db7e7a1a1ef5384fe07" 
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

print("Loading NLP model...")
nlp = spacy.load("en_core_web_md")
print("Model loaded.")


def get_weather(city):
    """
    This function calls the OpenWeatherMap API and returns a formatted string.
    """
    if not city:
        return "Sorry, I couldn't understand the city name."
        
    request_url = f"{WEATHER_URL}?q={city}&appid={API_KEY}&units=metric"
    
    response = requests.get(request_url)
    
    if response.status_code == 200:
        data = response.json()
        description = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f"The weather in {city} is {description} with a temperature of {temperature}°C."
    else:
        if response.status_code == 404:
           return f"Sorry, I couldn't find a city named '{city}'. Did you spell it correctly?"
        else:
          return f"Sorry, an error occurred with the weather service. (Code: {response.status_code})"
    
def get_5_day_forecast(city, days=5):
    """
    Fetches the 5-day forecast and processes it to find the
    min/max temp for the requested number of days.
    """

    request_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(request_url)

    if response.status_code != 200:
        if response.status_code == 404:
            return f"Sorry, I couldn't find a city named '{city}'. Did you spell it correctly?"
        else:
            return f"Sorry, an error occurred with the weather service. (Code: {response.status_code})"

    data = response.json()

    daily_temps_low = defaultdict(list)
    daily_temps_high = defaultdict(list)

    for item in data['list']:
        date_str = item['dt_txt'].split(' ')[0]
        temp_min = item['main']['temp_min']
        temp_max = item['main']['temp_max']
        daily_temps_low[date_str].append(temp_min)
        daily_temps_high[date_str].append(temp_max)

    if days > 5:
        days = 5

    response_string = f"Here is the {days}-day forecast for {city}:\n"

    sorted_dates = sorted(daily_temps_low.keys())

    for date_str in sorted_dates[:days]:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

        day_name = ""
        today = datetime.date.today()
        if date_obj == today:
            day_name = "Today"
        elif date_obj == today + datetime.timedelta(days=1):
            day_name = "Tomorrow"
        else:
            day_name = date_obj.strftime('%A') 

        low_temp = min(daily_temps_low[date_str])
        high_temp = max(daily_temps_high[date_str])

        response_string += f"\n- {day_name} ({date_str}):\n  High {high_temp:.0f}°C, Low {low_temp:.0f}°C"

    return response_string

def extract_entities(message):
    """
    Uses spaCy for location/date AND regex for number of days.
    """
    doc = nlp(message)
    location = None
    date_text = None
    num_days = None

    match = re.search(r'(\d+)\s*[-]*\s*(day|days)', message.lower())

    if match:
        num_days = int(match.group(1))

    print("\n--- spaCy Entities ---")
    for ent in doc.ents:
        print(f"  Found entity: '{ent.text}', Label: {ent.label_}")

        if ent.label_ == "GPE":
            location = ent.text
        elif ent.label_ == "DATE":
            date_text = ent.text.lower()
    print("----------------------\n")

    return location, date_text, num_days


@app.route("/")
def home():
    """
    This is the "home" route (http://127.0.0.1:5000/).
    It will serve our main chat page (index.html).
    (We haven't created index.html yet, but we will in the next step!)
    """
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    
    if not user_message:
        return jsonify({"response": "Error: No message received."}), 400

    print(f"Received message: {user_message}")

    location, date_text, num_days = extract_entities(user_message)
    
    print(f"Extracted: Location={location}, DateText={date_text}, NumDays={num_days}")

    bot_response = ""
    
    if "forecast" in user_message.lower() and location:
        if num_days:
            bot_response = get_5_day_forecast(location, days=num_days)
        else:
            bot_response = get_5_day_forecast(location)
            
    elif "weather" in user_message.lower() and location:
        bot_response = get_weather(location)
        
    elif "hello" in user_message.lower() or "hi" in user_message.lower():
        bot_response = "Hello! Ask me about the current weather or a multi-day forecast."
        
    else:
        bot_response = "Sorry, I can only provide the weather. Try 'What's the weather in London?' or 'What's the 3-day forecast for London?'"

    print(f"Sending response: {bot_response}")

    return jsonify({"response": bot_response})


if __name__ == "__main__":
    app.run(debug=True)