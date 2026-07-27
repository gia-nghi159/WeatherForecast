import { useState, useEffect } from 'react';
import './App.css';
import type { TodayWeather, WeatherPrediction, Units } from './types/weather';
import { Header } from './components/Header';
import { SettingsModal } from './components/SettingsModal';
import { CurrentWeather } from './components/CurrentWeather';
import { WeatherDetails } from './components/WeatherDetails';
import { ForecastGrid } from './components/ForecastGrid';
import { Footer } from './components/Footer';

const API_URL = ''; // or EC2 URL

function App() {
  const [todayWeather, setTodayWeather] = useState<TodayWeather | null>(null);
  const [predictions, setPredictions] = useState<WeatherPrediction | null>(null);
  const [loading, setLoading] = useState(true);
  const [units, setUnits] = useState<Units>('imperial');
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    const fetchAllData = async () => {
      try {
        const [todayRes, predictRes] = await Promise.all([
          fetch(`${API_URL}/today?units=${units}`),
          fetch(`${API_URL}/predict?units=${units}`, { method: 'POST' })
        ]);

        if (todayRes.ok) {
          const todayData = await todayRes.json();
          setTodayWeather(todayData);
        }

        if (predictRes.ok) {
          const predictData = await predictRes.json();
          setPredictions(predictData['7_day_tmax_prediction']);
        }
      } catch (error) {
        console.error('Error fetching weather data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
  }, [units]);

  if (loading) {
    return <div className="loading">Loading weather data...</div>;
  }

  return (
    <div className="app dark">
      <Header onOpenSettings={() => setShowSettings(true)} />

      {showSettings && (
        <SettingsModal 
          units={units} 
          onSelectUnits={setUnits} 
          onClose={() => setShowSettings(false)} 
        />
      )}

      <main className="main-content">
        <div className="weather-overview">
          <CurrentWeather weather={todayWeather} units={units} />
          <WeatherDetails weather={todayWeather} units={units} />
        </div>

        <ForecastGrid predictions={predictions} units={units} />
      </main>

      <Footer />
    </div>
  );
}

export default App;