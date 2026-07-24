import React from 'react';
import type { TodayWeather, Units } from '../types/weather';
import { getWeatherIcon, getWeatherCondition, getUnitLabels } from '../utils/weatherHelpers';

interface CurrentWeatherProps {
  weather: TodayWeather | null;
  units: Units;
}

export const CurrentWeather: React.FC<CurrentWeatherProps> = ({ weather, units }) => {
  const unitLabels = getUnitLabels(units);
  const temp = weather?.temp || 70;
  const prcp = weather?.prcp || 0;

  return (
    <div className="current-weather">
      <div className="weather-icon">
        {getWeatherIcon(temp, prcp, units)}
      </div>
      <div className="temperature">
        <span className="temp-main">
          {weather?.temp !== undefined ? weather.temp : '--'}
          {unitLabels.temp}
        </span>
        <span className="detail-label">{unitLabels.labels.currentTemp}</span>
        <span className="condition">
          {weather ? getWeatherCondition(temp, prcp, units) : 'Loading...'}
        </span>
      </div>
    </div>
  );
};