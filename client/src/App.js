import React from 'react';
import { Routes, Route } from 'react-router-dom';
import CustomerChat from './components/CustomerChat';
import AdminDashboard from './components/AdminDashboard';
import AdminStatistics from './components/AdminStatistics';
import HotelManagement from './components/HotelManagement';
import TourManagement from './components/TourManagement';
import './App.css';

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<CustomerChat />} />
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/admin/dashboard" element={<AdminDashboard />} />
        <Route path="/admin/statistics" element={<AdminStatistics />} />
        <Route path="/admin/hotels" element={<HotelManagement />} />
        <Route path="/admin/tours" element={<TourManagement />} />
      </Routes>
    </div>
  );
}

export default App;