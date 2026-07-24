export const UNITS = {
  METRIC: 'metric',
  IMPERIAL: 'imperial',
} as const;

export type Units = 'metric' | 'imperial';

export interface TodayWeather {
  date: string;
  temp: number;
  pres: number;
  prcp: number;
  wspd: number;
  wdir: number;
}

export interface WeatherPrediction {
  day_1: number;
  day_2: number;
  day_3: number;
  day_4: number;
  day_5: number;
  day_6: number;
  day_7: number;
}