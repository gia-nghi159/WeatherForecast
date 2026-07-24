import React from 'react';
import type { Units } from '../types/weather';

interface SettingsModalProps {
  units: Units;
  onSelectUnits: (units: Units) => void;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ units, onSelectUnits, onClose }) => {
  return (
    <div className="settings-panel">
      <div className="settings-content">
        <h3>Settings</h3>
        <div className="setting-item">
          <label>Units:</label>
          <div className="unit-toggle">
            <button 
              className={`unit-btn ${units === 'metric' ? 'active' : ''}`}
              onClick={() => onSelectUnits('metric')}
            >
              Metric (°C, km/h, mm, kPa)
            </button>
            <button 
              className={`unit-btn ${units === 'imperial' ? 'active' : ''}`}
              onClick={() => onSelectUnits('imperial')}
            >
              Imperial (°F, mph, in, inHg)
            </button>
          </div>
        </div>
        <button className="close-settings" onClick={onClose}>
          Close
        </button>
      </div>
    </div>
  );
};