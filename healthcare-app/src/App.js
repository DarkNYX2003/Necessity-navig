import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Register from './components/Register';
import Login from './components/Login';
import LocationAccess from './components/LocationAccess';
import HealthcareFacilities from './components/HealthcareFacilities';
import './App.css';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/location-access" element={<LocationAccess />} />
        <Route path="/facilities" element={<HealthcareFacilities />} />
      </Routes>
    </div>
  );
}

export default App;
