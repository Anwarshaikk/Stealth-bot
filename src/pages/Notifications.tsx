import React, { useState, useEffect } from 'react';
import AppLayout from '../components/AppLayout';
import ActivityFeed from '../components/ActivityFeed';

const Notifications: React.FC = () => {
  const [events, setEvents] = useState<{
    timestamp: string;
    type: 'apply' | 'error';
    message: string;
  }[]>([]);

  useEffect(() => {
    fetch('/logs')
      .then((res) => res.json())
      .then((data) => setEvents(data.events))
      .catch(console.error);
  }, []);

  return (
    <AppLayout>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        <h1 className="text-2xl font-semibold text-text-primary">Notifications & Logs</h1>
        <ActivityFeed events={events} />
      </div>
    </AppLayout>
  );
};

export default Notifications; 