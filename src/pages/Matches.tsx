import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AppLayout from '../components/AppLayout';
import CandidateSummary from '../components/CandidateSummary';
import JobCard from '../components/JobCard';
import Button from '../components/Button';
import { Search } from 'lucide-react';
import BulkToolbar from '../components/BulkToolbar';
import { useCandidateStore } from '../store';
import { useToast } from '../components/ToastContext';

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  url: string;
  description?: string;
  score?: number;
}

interface Candidate {
  name: string;
  location: string;
  skills: string[];
  experienceYears: number;
  [key: string]: any;
}

const Matches: React.FC = () => {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const candidateId = useCandidateStore((state) => state.candidateId);

  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedJobs, setSelectedJobs] = useState<string[]>([]);
  const [isApplying, setIsApplying] = useState(false);

  // Selection handlers
  const toggleSelect = (jobId: string) => {
    setSelectedJobs(prev =>
      prev.includes(jobId) ? prev.filter(id => id !== jobId) : [...prev, jobId]
    );
  };

  const clearSelection = () => setSelectedJobs([]);

  // Handle both single and bulk job applications
  const handleApply = async (jobIds: string[]) => {
    if (!candidateId) {
      addToast({
        title: 'No Resume Found',
        description: 'Please upload a resume first.',
        variant: 'error',
      });
      navigate('/upload');
      return;
    }

    setIsApplying(true);

    try {
      // Get the full job objects for the selected IDs
      const jobsToApply = jobs.filter(job => jobIds.includes(job.id));

      const response = await fetch('/api/apply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          candidate_id: candidateId,
          jobs: jobsToApply,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit applications');
      }

      const data = await response.json();
      
      addToast({
        title: 'Applications Submitted',
        description: `Successfully queued ${jobIds.length} job application${jobIds.length > 1 ? 's' : ''}!`,
        variant: 'success',
      });

      // Clear selection after successful submission
      setSelectedJobs([]);

    } catch (error) {
      console.error('Error submitting applications:', error);
      addToast({
        title: 'Error',
        description: 'Failed to submit job applications. Please try again later.',
        variant: 'error',
      });
    } finally {
      setIsApplying(false);
    }
  };

  // Handler for bulk apply button
  const bulkApply = () => {
    handleApply(selectedJobs);
  };

  // Handler for single job apply
  const onApplyJob = (job: Job) => {
    handleApply([job.id]);
  };

  // Fetch jobs when component mounts or candidateId changes
  useEffect(() => {
    if (!candidateId) {
      addToast({
        title: 'No Resume Found',
        description: 'Please upload a resume first.',
        variant: 'error',
      });
      navigate('/upload');
      return;
    }

    const fetchJobs = async () => {
      setLoading(true);
      try {
        const response = await fetch(`/api/jobs/${candidateId}`);
        if (!response.ok) {
          throw new Error('Failed to fetch jobs');
        }
        const data = await response.json();
        
        // Transform the data to match our Job interface
        const transformedJobs = data.map((job: any) => ({
          id: job.url, // Using URL as ID since the backend doesn't provide one
          title: job.title,
          company: job.company,
          location: job.location,
          url: job.url,
          description: job.description,
          score: 75 // Default score since backend doesn't provide one yet
        }));
        
        setJobs(transformedJobs);
      } catch (error) {
        console.error('Error fetching jobs:', error);
        addToast({
          title: 'Error',
          description: 'Failed to fetch job matches. Please try again later.',
          variant: 'error',
        });
        setJobs([]);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, [candidateId, navigate, addToast]);

  return (
    <AppLayout>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        {/* Candidate Summary */}
        {candidate && (
          <CandidateSummary
            name={candidate.name}
            location={candidate.location}
            skills={candidate.skills}
            experienceYears={candidate.experienceYears}
          />
        )}

        {/* Bulk Toolbar */}
        {selectedJobs.length > 0 && (
          <BulkToolbar
            selectedCount={selectedJobs.length}
            onApply={bulkApply}
            onEmail={() => {}}
            onClear={clearSelection}
            isApplying={isApplying}
          />
        )}

        {/* Jobs Grid */}
        <div>
          {loading ? (
            <div className="flex flex-col items-center justify-center py-16">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
              <span className="text-text-secondary text-lg mt-4">Finding your matches...</span>
            </div>
          ) : jobs.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16">
              <Search size={40} className="mb-4 text-text-secondary" />
              <span className="text-text-secondary text-lg">No job matches found.</span>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {jobs.map((job) => (
                <div key={job.id} className="relative">
                  <input
                    type="checkbox"
                    checked={selectedJobs.includes(job.id)}
                    onChange={() => toggleSelect(job.id)}
                    className="absolute top-2 left-2 z-10"
                    aria-label={`Select ${job.title}`}
                    disabled={isApplying}
                  />
                  <JobCard
                    job={job}
                    score={job.score || 75}
                    onApply={() => onApplyJob(job)}
                    isApplying={isApplying}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
};

export default Matches; 