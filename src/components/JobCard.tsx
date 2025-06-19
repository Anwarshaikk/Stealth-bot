import React from 'react';
import Button from './Button';
import { ExternalLink } from 'lucide-react';

export interface JobCardProps {
  job: {
    id: string;
    title: string;
    company: string;
    location: string;
    url?: string;
  };
  score: number;
  onApply: () => void;
  isApplying: boolean;
}

function getScoreColor(score: number) {
  if (score >= 80) return 'bg-green-500 text-white';
  if (score >= 50) return 'bg-amber-400 text-white';
  return 'bg-red-500 text-white';
}

const JobCard: React.FC<JobCardProps> = ({ job, score, onApply, isApplying }) => {
  return (
    <div className="bg-surface-tier-1 rounded-lg shadow-sm p-4 flex flex-col justify-between space-y-4 h-full hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-text-primary flex items-center gap-2">
            {job.title}
            {job.url && (
              <a
                href={job.url}
                target="_blank"
                rel="noopener noreferrer"
                className="ml-1 text-text-secondary hover:text-primary"
                aria-label={`View job posting for ${job.title}`}
                tabIndex={0}
                onClick={e => e.stopPropagation()}
              >
                <ExternalLink size={16} />
              </a>
            )}
          </h3>
          <p className="text-sm text-text-secondary truncate">
            {job.company} &bull; {job.location}
          </p>
        </div>
      </div>
      {/* Body: Score badge */}
      <div className="flex items-center">
        <span
          className={`inline-block px-3 py-1 rounded-full font-semibold text-xs ${getScoreColor(score)}`}
          aria-label={`Match score: ${score}%`}
        >
          Match: {score}%
        </span>
      </div>
      {/* Footer: Apply button */}
      <Button
        variant="primary"
        className="w-full mt-auto"
        onClick={onApply}
        disabled={isApplying}
        aria-label={`Apply to ${job.title}`}
      >
        {isApplying ? 'Applying...' : 'Apply'}
      </Button>
    </div>
  );
};

export default JobCard; 