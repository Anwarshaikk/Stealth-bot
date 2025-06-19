import React from 'react';
import { CheckCircle, XCircle } from 'lucide-react';

interface Event {
  timestamp: string;
  type: 'apply' | 'error';
  message: string;
}

interface ActivityFeedProps {
  events: Event[];
}

function groupByDay(events: Event[]) {
  const groups: Record<string, Event[]> = {};
  events.forEach((event) => {
    const day = new Date(event.timestamp).toLocaleDateString();
    if (!groups[day]) groups[day] = [];
    groups[day].push(event);
  });
  // Sort days descending
  return Object.entries(groups).sort((a, b) => new Date(b[0]).getTime() - new Date(a[0]).getTime());
}

const ActivityFeed: React.FC<ActivityFeedProps> = ({ events }) => {
  const grouped = groupByDay([...events].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()));
  return (
    <div className="max-h-96 overflow-y-auto p-4 bg-surface-tier-1 rounded-lg">
      <ul>
        {grouped.map(([day, dayEvents]) => (
          <li key={day} className="mb-4">
            <div className="text-xs font-semibold text-text-secondary mb-2">{day}</div>
            <ul className="space-y-2">
              {dayEvents.map((event, idx) => (
                <li key={event.timestamp + idx} className="flex items-center gap-3">
                  {event.type === 'apply' ? (
                    <CheckCircle className="text-green-500 w-5 h-5 flex-shrink-0" />
                  ) : (
                    <XCircle className="text-red-500 w-5 h-5 flex-shrink-0" />
                  )}
                  <span className="text-xs text-text-secondary min-w-[56px]">
                    {new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                  <span className="text-sm text-text-primary">{event.message}</span>
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ActivityFeed; 