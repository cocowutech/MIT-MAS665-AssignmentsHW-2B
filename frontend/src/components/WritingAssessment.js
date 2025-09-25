import React, { useState } from 'react';
import { Upload, X, FileText, Camera } from 'lucide-react';

const WritingAssessment = ({ 
  textResponse, 
  onTextChange, 
  imageFile, 
  imagePreview, 
  onImageUpload, 
  onImageRemove, 
  fileInputRef 
}) => {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith('image/')) {
        const event = {
          target: {
            files: [file]
          }
        };
        onImageUpload(event);
      }
    }
  };

  return (
    <div className="writing-assessment">
      <div className="writing-prompt">
        <h3>Writing Task</h3>
        <p>Write your response in the text area below, or upload an image of your handwritten work.</p>
      </div>

      {/* Text Input */}
      <div className="text-input-section">
        <label htmlFor="writing-text" className="form-label">
          <FileText size={16} />
          Your Response
        </label>
        <textarea
          id="writing-text"
          value={textResponse}
          onChange={onTextChange}
          className="writing-textarea"
          placeholder="Write your response here..."
          rows={8}
        />
        <div className="character-count">
          {textResponse.length} characters
        </div>
      </div>

      {/* Image Upload */}
      <div className="image-upload-section">
        <label className="form-label">
          <Camera size={16} />
          Upload Image (Optional)
        </label>
        
        {!imagePreview ? (
          <div
            className={`file-upload ${dragActive ? 'dragover' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload size={32} />
            <p>Click to upload or drag and drop</p>
            <p className="file-upload-hint">PNG, JPG, GIF up to 10MB</p>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={onImageUpload}
              style={{ display: 'none' }}
            />
          </div>
        ) : (
          <div className="image-preview">
            <img src={imagePreview} alt="Upload preview" />
            <button
              onClick={onImageRemove}
              className="remove-image-btn"
            >
              <X size={16} />
            </button>
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="writing-instructions">
        <h4>Instructions:</h4>
        <ul>
          <li>Write clearly and organize your ideas logically</li>
          <li>Use appropriate vocabulary and grammar for your level</li>
          <li>Address all parts of the task</li>
          <li>Write at least 100 words for a complete response</li>
        </ul>
      </div>

      <style jsx>{`
        .writing-assessment {
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }

        .writing-prompt {
          background: #f8fafc;
          padding: 1.5rem;
          border-radius: 0.75rem;
          border-left: 4px solid #3b82f6;
        }

        .writing-prompt h3 {
          font-size: 1.25rem;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 0.5rem;
        }

        .writing-prompt p {
          color: #64748b;
          margin: 0;
        }

        .text-input-section {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .form-label {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-weight: 500;
          color: #374151;
          font-size: 0.875rem;
        }

        .writing-textarea {
          width: 100%;
          padding: 1rem;
          border: 2px solid #e2e8f0;
          border-radius: 0.75rem;
          font-size: 1rem;
          line-height: 1.6;
          resize: vertical;
          font-family: inherit;
          min-height: 200px;
        }

        .writing-textarea:focus {
          outline: none;
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .character-count {
          font-size: 0.75rem;
          color: #64748b;
          text-align: right;
        }

        .image-upload-section {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .file-upload {
          border: 2px dashed #d1d5db;
          border-radius: 0.75rem;
          padding: 2rem;
          text-align: center;
          cursor: pointer;
          transition: all 0.2s ease;
          background: #fafafa;
        }

        .file-upload:hover {
          border-color: #3b82f6;
          background: #f0f9ff;
        }

        .file-upload.dragover {
          border-color: #3b82f6;
          background: #dbeafe;
        }

        .file-upload svg {
          color: #9ca3af;
          margin-bottom: 0.5rem;
        }

        .file-upload p {
          margin: 0.25rem 0;
          color: #64748b;
        }

        .file-upload-hint {
          font-size: 0.75rem;
          color: #9ca3af;
        }

        .image-preview {
          position: relative;
          display: inline-block;
          max-width: 100%;
        }

        .image-preview img {
          max-width: 100%;
          max-height: 300px;
          border-radius: 0.75rem;
          border: 2px solid #e2e8f0;
        }

        .remove-image-btn {
          position: absolute;
          top: 0.5rem;
          right: 0.5rem;
          background: #ef4444;
          color: white;
          border: none;
          border-radius: 50%;
          width: 2rem;
          height: 2rem;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: background-color 0.2s ease;
        }

        .remove-image-btn:hover {
          background: #dc2626;
        }

        .writing-instructions {
          background: #f8fafc;
          padding: 1.5rem;
          border-radius: 0.75rem;
          border: 1px solid #e2e8f0;
        }

        .writing-instructions h4 {
          font-size: 1rem;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 0.75rem;
        }

        .writing-instructions ul {
          margin: 0;
          padding-left: 1.25rem;
          color: #64748b;
        }

        .writing-instructions li {
          margin-bottom: 0.5rem;
          line-height: 1.5;
        }

        @media (max-width: 768px) {
          .file-upload {
            padding: 1.5rem;
          }

          .writing-instructions {
            padding: 1rem;
          }
        }
      `}</style>
    </div>
  );
};

export default WritingAssessment;
