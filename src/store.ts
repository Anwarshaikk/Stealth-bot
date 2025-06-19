import { create } from 'zustand';

interface CandidateStore {
  candidateId: string | null;
  setCandidateId: (id: string | null) => void;
}

export const useCandidateStore = create<CandidateStore>((set) => ({
  candidateId: null,
  setCandidateId: (id) => set({ candidateId: id }),
})); 