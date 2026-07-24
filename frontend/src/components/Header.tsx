import React from 'react';
import { getCurrentDateFormatted } from '../utils/weatherHelpers';

interface HeaderProps {
  onOpenSettings: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenSettings }) => {
  return (
    <header className="header">
      <div className="location">
        <span className="location-icon">📍</span>
        <span>Dallas, TX</span>
      </div>
      <div className="date-display">
        <span className="current-date">{getCurrentDateFormatted()}</span>
      </div>
      <div className="controls">
        <button className="settings" onClick={onOpenSettings} title="Settings">
          ⚙️
        </button>
      </div>
    </header>
  );
};