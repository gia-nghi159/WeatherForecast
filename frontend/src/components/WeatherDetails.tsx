import React from 'react';
import type { TodayWeather, Units } from '../types/weather';
import { getUnitLabels } from '../utils/weatherHelpers';

interface WeatherDetailsProps {
  weather: TodayWeather | null;
  units: Units;
}

export const WeatherDetails: React.FC<WeatherDetailsProps> = ({ weather, units }) => {
  const labels = getUnitLabels(units);

  return (
    <div className="weather-details">                        
      <div className="detail-item">
        <span className="detail-icon">💧</span>
        <span className="detail-value">{weather?.prcp ?? 0} {labels.precipitation}</span>
        <span className="detail-label">{labels.labels.precipitation}</span>
      </div>
      <div className="detail-item">
        <span className="detail-icon">🏔️</span>
        <span className="detail-value">{weather?.pres ?? '--'} {labels.pressure}</span>
        <span className="detail-label">{labels.labels.pressure}</span>
      </div> 
      <div className="detail-item">
        <span className="detail-icon">💨</span>
        <span className="detail-value">{weather?.wspd ?? '--'} {labels.windSpeed}</span>
        <span className="detail-label">{labels.labels.windSpeed}</span>
      </div>
      <div className="detail-item">
        <span className="detail-icon">🌀</span>
        <span className="detail-value">{weather?.wdir ?? '--'} {labels.windDirection}</span>
        <span className="detail-label">{labels.labels.windDirection}</span>
      </div>
    </div>
  );
};