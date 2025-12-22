import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

function Navbar() {
  const location = useLocation();

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          📊 Economic Stability Predictor
        </Link>
        <ul className="nav-menu">
          <li>
            <Link 
              to="/" 
              className={location.pathname === '/' ? 'nav-link active' : 'nav-link'}
            >
              Dashboard
            </Link>
          </li>
          <li>
            <Link 
              to="/forecast" 
              className={location.pathname === '/forecast' ? 'nav-link active' : 'nav-link'}
            >
              Forecast
            </Link>
          </li>
          <li>
            <Link 
              to="/sentiment" 
              className={location.pathname === '/sentiment' ? 'nav-link active' : 'nav-link'}
            >
              Sentiment
            </Link>
          </li>
          <li>
            <Link 
              to="/about" 
              className={location.pathname === '/about' ? 'nav-link active' : 'nav-link'}
            >
              About
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
}

export default Navbar;

