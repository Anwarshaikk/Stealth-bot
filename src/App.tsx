import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Upload from './pages/Upload';
import Matches from './pages/Matches';
import Tracker from './pages/Tracker';
import Settings from './pages/Settings';
import Notifications from './pages/Notifications';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/upload" replace />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/matches" element={<Matches />} />
        <Route path="/tracker" element={<Tracker />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/notifications" element={<Notifications />} />
        <Route path="*" element={<Navigate to="/upload" replace />} />
      </Routes>
    </BrowserRouter>
  );
} 