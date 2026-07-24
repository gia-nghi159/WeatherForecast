import React from 'react';
import type { WeatherPrediction, Units } from '../types/weather';
import { getDateLabel, getWeatherIcon, getUnitLabels } from '../utils/weatherHelpers';

interface ForecastGridProps {
  predictions: WeatherPrediction | null;
  units: Units;
}

export const ForecastGrid: React.FC<ForecastGridProps> = ({ predictions, units }) => {
  const unitLabels = getUnitLabels(units);

  if (!predictions) return null;

  return (
    <section className="forecast-section">
      <h2>7 DAYS FORECAST</h2>
      <div className="forecast-grid">
        {Object.entries(predictions).map(([dayKey, temp], index) => (
          <div key={dayKey} className="forecast-card">
            <span className="forecast-day">{getDateLabel(index)}</span>
            <div className="forecast-icon">
              {getWeatherIcon(temp, 0, units)}
            </div>
            <div className="forecast-temps">
              <span className="temp-high">{Math.round(temp)}{unitLabels.temp}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};