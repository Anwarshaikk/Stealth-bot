import React, { useState } from "react";
import AppLayout from "../components/AppLayout";
import Dropzone from "../components/Dropzone";
import { useNavigate } from "react-router-dom";
import Button from "../components/Button";
import { X } from "lucide-react";
import { useToast } from '../components/ToastContext';
import { useCandidateStore } from '../store';
// import { Toast } from "../components/Toast"; // No Toast utility found
// import { Spinner } from "shadcn/ui"; // If you want to use a Spinner in the button

const Upload: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();
  const { addToast } = useToast();
  const { setCandidate } = useCandidateStore();

  const handleRemove = (fileToRemove: File) => {
    setFiles((prev) => prev.filter((file) => file !== fileToRemove));
  };

  const onParseClick = async () => {
    if (!files.length) return;
    setUploading(true);
    try {
      const form = new FormData();
      form.append('file', files[0]);
      const res = await fetch('/resume', {
        method: 'POST',
        body: form,
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json(); // { candidate_id, skills, ... }
      
      // Store the full candidate object in the global store
      setCandidate(data);
      
      addToast({
        title: 'Success',
        description: 'Resume uploaded successfully! Redirecting to matches...',
        variant: 'success',
      });
      navigate(`/matches?candidate_id=${data.candidate_id}`);
    } catch (err: any) {
      // Toast.error(`Parsing failed: ${err.message}`);
      const errorMessage = err.response?.data?.detail || err.message;
      addToast({
        title: 'Upload Failed',
        description: `There was an error processing your resume: ${errorMessage}`,
        variant: 'error',
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <AppLayout>
      <div className="max-w-lg w-full md:w-2/3 mx-auto mt-20 space-y-6">
        <Dropzone
          accept={[".pdf", ".docx"]}
          uploading={uploading}
          onFiles={setFiles}
          className="h-[300px] bg-surface-tier-1 border border-surface-tier-2 rounded-lg flex items-center justify-center w-full"
        />
        {files.length > 0 && (
          <div className="space-y-2">
            {files.map((file) => (
              <div
                key={file.name + file.size}
                className="flex items-center justify-between bg-surface-tier-0 border border-surface-tier-2 rounded-lg px-4 py-2"
              >
                <div className="flex flex-col">
                  <span className="font-medium text-text-primary">{file.name}</span>
                  <span className="text-xs text-text-secondary">{(file.size / 1024).toFixed(1)} KB</span>
                </div>
                <button
                  type="button"
                  className="ml-4 p-1 rounded hover:bg-surface-tier-2"
                  aria-label="Remove file"
                  onClick={() => handleRemove(file)}
                >
                  <X size={18} />
                </button>
              </div>
            ))}
          </div>
        )}
        <Button
          className="w-full flex items-center justify-center"
          disabled={files.length === 0 || uploading}
          onClick={onParseClick}
        >
          {uploading ? (
            // <Spinner className="mr-2" /> Parsing résumé…
            <>Parsing résumé…</>
          ) : (
            "Parse & Match"
          )}
        </Button>
      </div>
    </AppLayout>
  );
};

export default Upload; 