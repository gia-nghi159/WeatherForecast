import type { Units } from '../types/weather';

export const getWeatherIcon = (temp: number, precipitation: number = 0, units: Units = 'imperial') => {
  if (precipitation > 0.5) return '🌧️';
  
  if (units === 'imperial') {
    if (temp > 80) return '☀️';
    if (temp > 70) return '⛅';
    if (temp > 60) return '☁️';
  } else {
    if (temp > 27) return '☀️';
    if (temp > 21) return '⛅';
    if (temp > 16) return '☁️';
  }
  return '☁️';
};

export const getWeatherCondition = (temp: number, precipitation: number, units: Units) => {
  if (precipitation > 0.5) return 'Rainy';

  if (units === 'imperial') {
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

export const getDateLabel = (dayIndex: number) => {
  const today = new Date();
  const targetDate = new Date(today);
  targetDate.setDate(today.getDate() + dayIndex);
  
  if (dayIndex === 0) return 'Today';
  if (dayIndex === 1) return 'Tomorrow';
  
  return targetDate.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
};

export const getCurrentDateFormatted = () => {
  return new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

export const getUnitLabels = (units: Units) => {
  if (units === 'imperial') {
    return {
      temp: '°F',
      pressure: 'inHg',
      precipitation: 'in',
      windSpeed: 'mph',
      windDirection: '°',
      labels: {
        precipitation: 'Precipitation',
        windSpeed: 'Wind Speed',
        pressure: 'Pressure',
        currentTemp: 'Current Temp',
        maxTemp: 'Max Temp',
        minTemp: 'Min Temp',
        windDirection: 'Wind Direction'
      }
    };
  }
  return {
    temp: '°C',
    pressure: 'kPa',
    precipitation: 'mm',
    windSpeed: 'km/h',
    windDirection: '°',
    labels: {
      precipitation: 'Precipitation',
      windSpeed: 'Wind Speed',
      pressure: 'Pressure',
      maxTemp: 'Max Temp',
      minTemp: 'Min Temp',
      windDirection: 'Wind Direction'
    }
  };
};