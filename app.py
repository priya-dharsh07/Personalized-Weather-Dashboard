from flask import Flask, render_template, request
import requests
import os
import plotly.graph_objects as go
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
API_KEY = os.getenv('OPENWEATHER_API_KEY')
def get_weather_data(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        weather = {
            'city': data['name'],
            'temp': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon'],
        }
        weather['alert'] = get_weather_alerts(weather['temp']) 
        return weather
    else:
        return {'error': 'City not found'}
    
def get_weather_forecast(city_name):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    dates = [entry['dt_txt'] for entry in data['list']][:10]  
    temps = [entry['main']['temp'] for entry in data['list']][:10]

    return dates, temps

def get_weather_alerts(temp):
    if temp > 30:
        return "It's a hot day! Stay hydrated."
    elif temp < 0:
        return "It's freezing outside! Dress warmly."
    else:
        return "The weather looks pleasant."

def create_weather_chart(dates, temps):
    fig = go.Figure(data=go.Scatter(x=dates, y=temps, mode='lines', name='Temperature'))
    
    fig.update_layout(
        title='Temperature Forecast',
        xaxis_title='Date',
        yaxis_title='Temperature (°C)',
        template='plotly_dark'
    )
    
    graph_html = fig.to_html(full_html=False)
    return graph_html

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city = request.form['city']
        weather_data = get_weather_data(city)
        
        if 'error' not in weather_data:
            dates, temps = get_weather_forecast(city)
            chart = create_weather_chart(dates, temps)
        else:
            chart = None

        return render_template('index.html', weather=weather_data, chart=chart)
    return render_template('index.html', weather=None, chart=None)

if __name__ == '__main__':
    app.run(debug=True)
