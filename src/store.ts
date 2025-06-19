import { create } from 'zustand';

interface Candidate {
  candidate_id: string;
  name: string;
  email?: string;
  location?: string;
  skills: string[];
  experienceYears?: number;
  [key: string]: any;
}

interface CandidateStore {
  candidate: Candidate | null;
  setCandidate: (candidate: Candidate | null) => void;
}

export const useCandidateStore = create<CandidateStore>((set) => ({
  candidate: null,
  setCandidate: (candidate) => set({ candidate }),
})); 