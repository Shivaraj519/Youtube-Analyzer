import React, { useState, useRef } from 'react';
import { Upload, FileWarning, AlertCircle, Sparkles } from 'lucide-react';

function TakeoutUpload({ onUpload, isAnalyzing }) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const validateAndUpload = (file) => {
    setErrorMessage(null);
    
    if (!file) return;

    // Check file type
    if (!file.name.endsWith('.json')) {
      setErrorMessage("Unsupported file format. Please upload your watch-history.json file.");
      return;
    }

    // Check file size (e.g., limit to 20MB for safety on local server processing)
    if (file.size > 20 * 1024 * 1024) {
      setErrorMessage("File is too large. Please limit to files under 20MB.");
      return;
    }

    onUpload(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndUpload(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndUpload(e.target.files[0]);
    }
  };

  const onButtonClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="glass-panel rounded-2xl p-6 flex flex-col gap-5 border border-gray-800">
      <div>
        <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-accent-cyan" /> Upload Google Takeout
        </h3>
        <p className="text-sm text-gray-400">
          Upload your offline YouTube <code>watch-history.json</code> file for an offline data analysis.
        </p>
      </div>

      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={onButtonClick}
        className={`border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center gap-3 transition-all duration-300 cursor-pointer ${
          isDragActive
            ? 'border-accent-violet bg-accent-violet/5 scale-[0.99]'
            : 'border-gray-800 hover:border-gray-700 bg-gray-900/10 hover:bg-gray-900/20'
        } ${isAnalyzing ? 'opacity-50 pointer-events-none' : ''}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          onChange={handleChange}
          className="hidden"
          disabled={isAnalyzing}
        />

        <div className="p-4 bg-gray-900/60 rounded-xl border border-gray-800 text-gray-400">
          <Upload className="w-8 h-8 text-accent-cyan" />
        </div>

        <p className="text-sm font-semibold text-gray-200 text-center">
          Drag and drop your <code>watch-history.json</code>, or <span className="text-accent-violet hover:underline">browse files</span>
        </p>
        <span className="text-xs text-gray-500">Max size 20MB • JSON format only</span>
      </div>

      {errorMessage && (
        <div className="flex gap-2.5 items-start p-3.5 bg-accent-rose/10 border border-accent-rose/20 text-accent-rose text-xs rounded-xl font-medium">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
}

export default TakeoutUpload;
