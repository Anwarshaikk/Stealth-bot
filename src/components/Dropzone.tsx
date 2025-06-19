import React from "react";
import { useDropzone } from "react-dropzone";
import { Loader2, CloudUpload } from "lucide-react";

export interface DropzoneProps {
  accept: string[];
  uploading: boolean;
  onFiles: (files: File[]) => void;
  className?: string;
}

// Simple Spinner using Loader2 from lucide-react
const Spinner: React.FC<{ className?: string }> = ({ className = "" }) => (
  <Loader2 className={`animate-spin text-primary ${className}`} />
);

const Dropzone: React.FC<DropzoneProps> = ({ accept, uploading, onFiles, className = "" }) => {
  const {
    getRootProps,
    getInputProps,
    isDragActive,
  } = useDropzone({
    accept: accept.reduce((acc, ext) => {
      // Map [".pdf", ".docx"] to { "application/pdf": [], "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [] }
      // But fallback to ext for simplicity
      acc[ext] = [];
      return acc;
    }, {} as Record<string, string[]>),
    multiple: false,
    onDrop: (acceptedFiles) => {
      onFiles(acceptedFiles);
    },
    disabled: uploading,
  });

  return (
    <div
      {...getRootProps({
        className: [
          "w-full h-72 border-2 border-dashed rounded-lg bg-surface-tier-1 flex flex-col items-center justify-center transition-colors duration-150 relative outline-none focus:ring-2 focus:ring-primary",
          isDragActive ? "border-primary" : "border-surface-tier-2",
          uploading ? "pointer-events-none opacity-70" : "cursor-pointer hover:border-primary",
          className,
        ].join(" "),
        role: "button",
        tabIndex: 0,
        "aria-disabled": uploading,
      })}
    >
      <input {...getInputProps()} />
      {!uploading && (
        <>
          <CloudUpload size={48} className="text-primary mb-4" />
          <p className="text-text-secondary text-center font-medium">
            Drag & drop PDF/DOCX here or click to browse
          </p>
        </>
      )}
      {uploading && (
        <div className="absolute inset-0 bg-black/40 flex items-center justify-center rounded-lg z-10">
          <Spinner className="w-10 h-10" />
        </div>
      )}
    </div>
  );
};

export default Dropzone; 