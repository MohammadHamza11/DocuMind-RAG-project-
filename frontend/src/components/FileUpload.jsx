import React, { useCallback } from "react";
import { useDropzone } from "react-dropzone";

export default function FileUpload({ onUpload, uploading }) {
  const onDrop = useCallback(
    (acceptedFiles) => {
      acceptedFiles.forEach((file) => onUpload(file));
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
    disabled: uploading,
  });

  return (
    <div {...getRootProps()} className={`dropzone ${isDragActive ? "active" : ""}`}>
      <input {...getInputProps()} />
      {uploading ? (
        <p>Processing...</p>
      ) : isDragActive ? (
        <p>Drop files here...</p>
      ) : (
        <>
          <p>Drag & drop documents here, or click to browse</p>
          <p className="formats">PDF, DOCX — up to 50 MB</p>
        </>
      )}
    </div>
  );
}
