import { useState, useEffect } from 'react'
import './App.css'

interface TodayWeather {
  date: string;
  tavg: number;
  tmax: number;
  tmin: number;
  pres: number;
  prcp: number;
  wspd: number;
}

interface WeatherPrediction {
  day_1: number;
  day_2: number;
  day_3: number;
  day_4: number;
  day_5: number;
  day_6: number;
  day_7: number;
}

function App() {
  const [todayWeather, setTodayWeather] = useState<TodayWeather | null>(null);
  const [predictions, setPredictions] = useState<WeatherPrediction | null>(null);
  const [loading, setLoading] = useState(true);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [units, setUnits] = useState<'metric' | 'imperial'>('imperial');
  const [showSettings, setShowSettings] = useState(false);
  const [showAbout, setShowAbout] = useState(false);

  useEffect(() => {
    fetchTodayWeather();
    fetchPredictions();
  }, [units]); // Re-fetch when units change

  const fetchTodayWeather = async () => {
    try {
      console.log('Fetching today weather from:', `http://localhost:8000/today?units=${units}`);
      const response = await fetch(`http://localhost:8000/today?units=${units}`);
      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Today weather data:', data);
      setTodayWeather(data);
    } catch (error) {
      console.error('Error fetching today weather:', error);
    }
  };

  const fetchPredictions = async () => {
    try {
      console.log('Fetching predictions from:', `http://localhost:8000/predict?units=${units}`);
      const response = await fetch(`http://localhost:8000/predict?units=${units}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      console.log('Predictions response status:', response.status);
      const data = await response.json();
      console.log('Predictions data:', data);
      setPredictions(data['7_day_tmax_prediction']);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching predictions:', error);
      setLoading(false);
    }
  };

  const getWeatherIcon = (temp: number, precipitation: number = 0) => {
    // If there's precipitation, always show rain icon
    if (precipitation > 0.5) return '🌧️';
    
    // Temperature thresholds based on unit system
    if (units === 'imperial') {
      // Fahrenheit thresholds
      if (temp > 80) return '☀️';
      if (temp > 70) return '⛅';
      if (temp > 60) return '☁️';
    } else {
      // Celsius thresholds
      if (temp > 27) return '☀️';  // ~80°F
      if (temp > 21) return '⛅';  // ~70°F
      if (temp > 16) return '☁️';  // ~60°F
    }
    return '☁️';
  };

  const getWeatherCondition = (temp: number, precipitation: number) => {
    if (precipitation > 0.5) return 'Rainy';

    if (units === 'imperial'){
      if (temp > 80) return 'Sunny';
      if (temp > 70) return 'Partly cloudy';
      if (temp > 60) return 'Mostly cloudy';
    } else {
      if (temp > 27) return 'Sunny';
      if (temp > 21) return 'Partly cloudy';
      if (temp > 16) return 'Mostly cloudy';
    }
    return 'Overcast';
  };

  const getDateLabel = (dayIndex: number) => {
    const today = new Date();
    const targetDate = new Date(today);
    targetDate.setDate(today.getDate() + dayIndex);
    
    const dateOptions: Intl.DateTimeFormatOptions = { 
      month: 'short', 
      day: 'numeric' 
    };
    
    const dayOptions: Intl.DateTimeFormatOptions = { 
      weekday: 'short' 
    };
    
    if (dayIndex === 0) {
      return 'Tomorrow';
    } else {
      const dayName = targetDate.toLocaleDateString('en-US', dayOptions);
      const date = targetDate.toLocaleDateString('en-US', dateOptions);
      return `${dayName}, ${date}`;
    }
  };

  const getCurrentDate = () => {
    const today = new Date();
    const options: Intl.DateTimeFormatOptions = {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    };
    return today.toLocaleDateString('en-US', options);
  };

  const toggleAbout = () => {
    setShowAbout(!showAbout);
  };

  const getUnitLabels = () => {
    if (units === 'imperial') {
      return {
        temp: '°F',
        pressure: 'inHg',
        precipitation: 'in',
        windSpeed: 'mph',
        labels: {
          precipitation: 'Precipitation',
          windSpeed: 'Wind Speed',
          pressure: 'Pressure',
          maxTemp: 'Max Temp',
          minTemp: 'Min Temp'
        }
      };
    } else {
      return {
        temp: '°C',
        pressure: 'kPa',
        precipitation: 'mm',
        windSpeed: 'km/h',
        labels: {
          precipitation: 'Precipitation',
          windSpeed: 'Wind Speed',
          pressure: 'Pressure',
          maxTemp: 'Max Temp',
          minTemp: 'Min Temp'
        }
      };
    }
  };

  if (loading) {
    return <div className="loading">Loading weather data...</div>;
  }

  return (
    <div className={`app ${isDarkMode ? 'dark' : 'light'}`}>
      <header className="header">
        <div className="location">
          <span className="location-icon">📍</span>
          <span>Dallas, TX</span>
        </div>
        <div className="date-display">
          <span className="current-date">{getCurrentDate()}</span>
        </div>
        <div className="controls">
          <button 
            className="theme-toggle"
            onClick={() => setIsDarkMode(!isDarkMode)}
          >
            {isDarkMode ? '☀️' : '🌙'}
          </button>
          <button 
            className="settings"
            onClick={() => setShowSettings(!showSettings)}
          >
            ⚙️
          </button>
        </div>
      </header>

      {/* Settings Panel */}
      {showSettings && (
        <div className="settings-panel">
          <div className="settings-content">
            <h3>Settings</h3>
            <div className="setting-item">
              <label>Units:</label>
              <div className="unit-toggle">
                <button 
                  className={`unit-btn ${units === 'metric' ? 'active' : ''}`}
                  onClick={() => setUnits('metric')}
                >
                  Metric (°C, km/h, mm, kPa)
                </button>
                <button 
                  className={`unit-btn ${units === 'imperial' ? 'active' : ''}`}
                  onClick={() => setUnits('imperial')}
                >
                  Imperial (°F, mph, in, inHg)
                </button>
              </div>
            </div>
            <button 
              className="close-settings"
              onClick={() => setShowSettings(false)}
            >
              Close
            </button>
          </div>
        </div>
      )}

      <main className="main-content">
        <div className="weather-overview">
          <div className="current-weather">
            <div className="weather-icon">
              {getWeatherIcon(todayWeather?.tmax || 70, todayWeather?.prcp || 0)}
            </div>
            <div className="temperature">
              <span className="temp-main">{todayWeather?.tmax || '--'}{getUnitLabels().temp}</span>
              <span className="detail-label">{getUnitLabels().labels.maxTemp}</span>
              <span className="condition">
                {todayWeather ? getWeatherCondition(todayWeather.tmax, todayWeather.prcp) : 'Loading...'}
              </span>
            </div>
          </div>

          <div className="weather-details">                        
            <div className="detail-item">
              <span className="detail-icon">🌡️</span>
              <span className="detail-value">{todayWeather?.tmin || '--'}{getUnitLabels().temp}</span>
              <span className="detail-label">{getUnitLabels().labels.minTemp}</span>
            </div>
            <div className="detail-item">
              <span className="detail-icon">💧</span>
              <span className="detail-value">{todayWeather?.prcp || 0} {getUnitLabels().precipitation}</span>
              <span className="detail-label">{getUnitLabels().labels.precipitation}</span>
            </div>
            <div className="detail-item">
              <span className="detail-icon">💨</span>
              <span className="detail-value">{todayWeather?.wspd || '--'} {getUnitLabels().windSpeed}</span>
              <span className="detail-label">{getUnitLabels().labels.windSpeed}</span>
            </div>
            <div className="detail-item">
              <span className="detail-icon">🏔️</span>
              <span className="detail-value">{todayWeather?.pres || '--'} {getUnitLabels().pressure}</span>
              <span className="detail-label">{getUnitLabels().labels.pressure}</span>
            </div>            
          </div>
        </div>

        <section className="forecast-section">
          <h2>7 DAYS FORECAST</h2>
          <div className="forecast-grid">
            {predictions && Object.entries(predictions).map(([day, temp], index) => (
              <div key={day} className="forecast-card">
                <span className="forecast-day">{getDateLabel(index)}</span>
                <div className="forecast-icon">
                  {getWeatherIcon(temp, 0)}
                </div>
                <div className="forecast-temps">
                  <span className="temp-high">{Math.round(temp)}{getUnitLabels().temp}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* About This Project Button */}
        <div className="about-toggle-container">
          <button 
            className="about-toggle-btn"
            onClick={toggleAbout}
          >
            <span>About This Project</span>
            <span className={`about-arrow ${showAbout ? 'expanded' : ''}`}>▼</span>
          </button>
          
          {/* Expandable About Content */}
          <div className={`about-expandable ${showAbout ? 'expanded' : ''}`}>
            <div className="about-content">
              <p><strong>Created by:</strong> Gia Nghi Dang – Computer Science student @ University of Texas at Dallas (UTD)</p>
              
              <div className="about-description">
                <h3>Project Description:</h3>
                <p>This web application uses a custom-trained machine learning model to forecast the maximum daily temperature for the next 7 days based on historical weather data.</p>
                <p className="about-note"><i>
                  <u>Note</u>: This forecast is based on historical and current weather data from Dallas Fort Worth International Airport (DFW) — the closest available weather station to Carrollton, TX.<br />
                  It reflects general regional conditions and may differ slightly from hyper-local observations (e.g., your phone’s weather app).
                </i></p>
              </div>

              <div className="about-how-it-works">
                <h3>How it works:</h3>
                <ul>
                  <li>The backend is powered by <strong>FastAPI</strong>, which handles data preprocessing, model inference, and serves the prediction API.</li>
                  <li>The model was trained using <strong>Lasso Regression</strong> and built with <strong>scikit-learn</strong>, using engineered features like rolling averages and seasonal trends.</li>
                  <li>The frontend is built with <strong>React</strong> and styled to provide a clean, intuitive display of the weather information.</li>
                </ul>
              </div>

              <div className="about-features">
                <h3>Features:</h3>
                <ul>
                  <li>Displays today's average, min, and max temperatures along with wind speed, pressure, and precipitation.</li>
                  <li>Forecasts max temperatures for the upcoming 7 days.</li>
                  <li>Toggle between metric (°C, km/h, mm, kPa) and imperial (°F, mph, inches, inHg) units.</li>
                  <li>Dynamic weather icons based on temperature and precipitation conditions.</li>
                  <li>Responsive design that works on all device sizes.</li>
                </ul>
              </div>

              <div className="about-data-source">
                <h3>Data Source:</h3>
                <p>
                  <i>Weather data sourced from <a href="https://meteostat.net/en/place/us/carrollton?s=KADS0&t=2025-07-20/2025-07-20" target="_blank" rel="noopener noreferrer" className="data-source-link">Meteostat</a></i>
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer className="footer">
        <div className="footer-content">
          <div className="footer-left">
            <p>&copy; 2025 Weather Forecast App</p>
          </div>
          <div className="footer-right">
            <a href="https://github.com/gia-nghi159" target="_blank" rel="noopener noreferrer" className="github-link">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App
