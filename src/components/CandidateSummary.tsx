import React from "react";
import { MapPin } from "lucide-react";

export interface CandidateSummaryProps {
  name: string;
  location: string;
  skills: string[];
  experienceYears: number;
}

const CandidateSummary: React.FC<CandidateSummaryProps> = ({
  name,
  location,
  skills,
  experienceYears,
}) => {
  return (
    <section aria-label="Candidate summary">
      <div className="bg-surface-tier-1 rounded-lg p-6 shadow-sm flex flex-col md:flex-row items-start space-y-4 md:space-y-0 md:space-x-6">
        {/* Left: PDF Preview Placeholder */}
        <div
          className="w-full md:w-2/5 h-32 bg-surface-tier-2 rounded flex items-center justify-center"
          aria-label="Résumé preview placeholder"
        >
          <span className="text-text-secondary text-sm" aria-label="PDF Preview">PDF Preview</span>
        </div>
        {/* Right: Candidate Info */}
        <div className="flex-1 w-full md:w-3/5 flex flex-col justify-between">
          <h2 className="text-xl font-semibold text-text-primary mb-1">{name}</h2>
          <div className="flex items-center text-text-secondary mb-2">
            <MapPin size={16} className="mr-1" aria-hidden="true" />
            <span>{location}</span>
          </div>
          <div className="flex flex-wrap mb-2">
            {skills.map((skill) => (
              <span
                key={skill}
                className="inline-block bg-accent/10 text-accent px-2 py-1 rounded-full text-xs mr-2 mb-2"
              >
                {skill}
              </span>
            ))}
          </div>
          <div className="text-sm text-text-primary">Experience: {experienceYears} year{experienceYears !== 1 ? 's' : ''}</div>
        </div>
      </div>
    </section>
  );
};

export default CandidateSummary; 