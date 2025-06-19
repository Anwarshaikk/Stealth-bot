import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css'; // adjust path if your global stylesheet is named differently

const rootEl = document.getElementById('root');
if (!rootEl) throw new Error('Root element not found');

ReactDOM.createRoot(rootEl).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
); 