import React from 'react';
import Button from './Button';

export interface BulkToolbarProps {
  selectedCount: number;
  onApply: () => void;
  onEmail: () => void;
  onClear: () => void;
  isApplying: boolean;
}

const BulkToolbar: React.FC<BulkToolbarProps> = ({
  selectedCount,
  onApply,
  onEmail,
  onClear,
  isApplying,
}) => {
  if (selectedCount <= 0) return null;

  return (
    <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between bg-surface-tier-1 p-4 rounded-lg shadow-sm mb-4 space-y-2 md:space-y-0 md:space-x-4">
      {/* Left: Selected count */}
      <div className="text-text-primary font-medium text-base">
        {selectedCount} selected
      </div>
      {/* Right: Actions */}
      <div className="flex flex-col sm:flex-row gap-2">
        <Button
          variant="primary"
          onClick={onApply}
          aria-label="Apply to selected jobs"
          disabled={isApplying}
        >
          {isApplying ? 'Applying...' : 'Apply'}
        </Button>
        <Button
          variant="secondary"
          onClick={onEmail}
          aria-label="Email selected jobs"
          disabled={isApplying}
        >
          Email
        </Button>
        <Button
          variant="danger"
          onClick={onClear}
          aria-label="Clear selected jobs"
          disabled={isApplying}
        >
          Clear
        </Button>
      </div>
    </div>
  );
};

export default BulkToolbar; 