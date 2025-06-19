import React, { useState, useEffect } from 'react';
import AppLayout from '../components/AppLayout';
import KanbanBoard from '../components/KanbanBoard';
import { useToast } from '../components/ToastContext';

const columns = [
  { id: 'Applied', title: 'Applied' },
  { id: 'Interview', title: 'Interview' },
  { id: 'Offer', title: 'Offer' },
  { id: 'Rejected', title: 'Rejected' },
];

interface Application {
  application_id: string;
  candidate_id: string;
  job_title: string;
  company: string;
  job_url: string;
  status: string;
  created_at: string;
  updated_at: string;
}

const Tracker: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { addToast } = useToast();

  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    try {
      const response = await fetch('/api/applications');
      if (!response.ok) {
        throw new Error('Failed to fetch applications');
      }
      const data = await response.json();
      setApplications(data);
      setError(null);
    } catch (err) {
      setError('Failed to load applications. Please try again later.');
      addToast({
        title: 'Error',
        description: 'Failed to load applications',
        variant: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDragEnd = async (itemId: string, fromCol: string, toCol: string) => {
    // Optimistically update the UI
    const updatedApplications = applications.map(app =>
      app.application_id === itemId ? { ...app, status: toCol } : app
    );
    setApplications(updatedApplications);

    try {
      const response = await fetch(`/api/applications/${itemId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: toCol }),
      });

      if (!response.ok) {
        throw new Error('Failed to update application status');
      }

      addToast({
        title: 'Success',
        description: 'Application status updated successfully',
        variant: 'success'
      });
    } catch (err) {
      // Revert the optimistic update on error
      setApplications(applications);
      addToast({
        title: 'Error',
        description: 'Failed to update application status',
        variant: 'error'
      });
    }
  };

  const kanbanItems = applications.map(app => ({
    id: app.application_id,
    status: app.status,
    candidate: app.candidate_id,
    job: `${app.job_title} at ${app.company}`,
    updatedAt: app.updated_at,
    url: app.job_url
  }));

  return (
    <AppLayout>
      <div className="p-6 max-w-7xl mx-auto">
        {error && (
          <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-lg">
            {error}
          </div>
        )}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-4"></div>
            <span className="text-text-secondary text-lg">Loading applications…</span>
          </div>
        ) : (
          <KanbanBoard columns={columns} items={kanbanItems} onDragEnd={handleDragEnd} />
        )}
      </div>
    </AppLayout>
  );
};

export default Tracker; 