/**
 * Image Scanner Component
 * Interface for image upload and OCR analysis
 */

import React, { useRef, useState } from 'react';
import { apiService, ScanResponse } from '../services/api';
import RiskMeter from './RiskMeter';
import SuggestionsList from './SuggestionsList';
import DetectionsSummary from './DetectionsSummary';

const MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024;
const ALLOWED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp'];

const formatBytes = (bytes: number): string => {
  if (bytes === 0) {
    return '0 B';
  }
  const units = ['B', 'KB', 'MB', 'GB'];
  const unitIndex = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / Math.pow(1024, unitIndex);
  return `${value.toFixed(unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`;
};

const ImageScanner: React.FC = () => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [isDragActive, setIsDragActive] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [preprocess, setPreprocess] = useState<boolean>(true);
  const [scanResult, setScanResult] = useState<ScanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const validateFile = (file: File): string | null => {
    if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
      return 'Unsupported image type. Please upload PNG, JPG, JPEG, GIF, BMP, or WEBP.';
    }

    if (file.size > MAX_IMAGE_SIZE_BYTES) {
      return `Image is too large (${formatBytes(file.size)}). Maximum allowed size is 10 MB.`;
    }

    return null;
  };

  const processSelectedFile = (file: File | null) => {
    if (!file) {
      return;
    }

    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      setSelectedImage(null);
      setImagePreview(null);
      setScanResult(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      return;
    }

    setSelectedImage(file);
    setScanResult(null);
    setError(null);
    setUploadProgress(0);

    const reader = new FileReader();
    reader.onload = (event) => {
      setImagePreview(event.target?.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    processSelectedFile(e.target.files?.[0] || null);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragActive(false);
    processSelectedFile(e.dataTransfer.files?.[0] || null);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragActive(true);
  };

  const handleDragLeave = () => {
    setIsDragActive(false);
  };

  const handleScan = async () => {
    if (!selectedImage) return;

    abortControllerRef.current = new AbortController();
    setIsScanning(true);
    setError(null);
    setUploadProgress(0);

    try {
      const result = await apiService.scanImage({
        image: selectedImage,
        preprocess,
        signal: abortControllerRef.current.signal,
        onUploadProgress: setUploadProgress,
      });
      setScanResult(result);
    } catch (err: any) {
      const errorMessage = err.message || 'Unknown error occurred';
      if (errorMessage !== 'Scan cancelled by user.') {
        setError(errorMessage);
        setScanResult(null);
      }
    } finally {
      abortControllerRef.current = null;
      setIsScanning(false);
    }
  };

  const handleCancelScan = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsScanning(false);
  };

  const handleClear = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setSelectedImage(null);
    setImagePreview(null);
    setScanResult(null);
    setError(null);
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="space-y-4">
      {/* Upload Section */}
      <div className="card-3d bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-4">Upload Image</h2>

        <div
          className={`border-2 border-dashed rounded p-8 text-center transition-colors ${
            isDragActive
              ? 'border-teal-400 bg-teal-50 dark:bg-teal-950/40'
              : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
          }`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          {imagePreview ? (
            <div className="space-y-3">
              <img
                src={imagePreview}
                alt="Preview"
                className="max-h-56 mx-auto rounded border border-gray-200 dark:border-gray-700"
              />
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {selectedImage?.name} {selectedImage ? `(${formatBytes(selectedImage.size)})` : ''}
              </p>
            </div>
          ) : (
            <div>
              <svg
                className="mx-auto h-10 w-10 text-gray-300 dark:text-gray-600"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                  strokeWidth={1.5}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <p className="mt-3 text-sm text-gray-500 dark:text-gray-400">
                Click to upload or drag and drop
              </p>
              <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">PNG, JPG, GIF, BMP, WEBP up to 10MB</p>
            </div>
          )}

          <input
            type="file"
            accept="image/*"
            onChange={handleImageSelect}
            className="hidden"
            id="image-upload"
            ref={fileInputRef}
          />
          <label
            htmlFor="image-upload"
            className="mt-4 inline-block px-4 py-2 text-sm border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 rounded cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            Choose Image
          </label>
        </div>

        <div className="mt-3 flex items-center justify-between gap-3">
          <label className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400 cursor-pointer">
            <input
              type="checkbox"
              checked={preprocess}
              onChange={(e) => setPreprocess(e.target.checked)}
              className="rounded border-gray-300 text-teal-600 focus:ring-teal-500"
            />
            OCR preprocessing (recommended for noisy photos)
          </label>
          {isScanning && (
            <span className="text-xs text-teal-600 dark:text-teal-400">Uploading {uploadProgress}%</span>
          )}
        </div>

        {isScanning && (
          <div className="mt-2 h-1.5 rounded bg-gray-100 dark:bg-gray-800 overflow-hidden">
            <div
              className="h-full bg-teal-500 transition-all duration-200"
              style={{ width: `${Math.max(uploadProgress, 8)}%` }}
            />
          </div>
        )}

        <div className="flex justify-end gap-2 mt-4">
          {isScanning && (
            <button
              onClick={handleCancelScan}
              className="px-4 py-2 text-sm border border-amber-300 dark:border-amber-700 text-amber-700 dark:text-amber-300 rounded hover:bg-amber-50 dark:hover:bg-amber-950 transition-colors"
            >
              Cancel
            </button>
          )}
          <button
            onClick={handleClear}
            className="px-4 py-2 text-sm border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 rounded hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            Clear
          </button>
          <button
            onClick={handleScan}
            disabled={!selectedImage || isScanning}
            className="btn-3d px-5 py-2 text-sm bg-teal-600 text-white rounded disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {isScanning ? 'Scanning...' : 'Scan Image'}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950 rounded p-4">
          <p className="text-red-700 dark:text-red-400 text-sm font-medium mb-1">Error</p>
          <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
          {error.includes('Tesseract') && (
            <div className="mt-3 p-3 border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950 rounded text-xs text-blue-700 dark:text-blue-300">
              <p className="font-medium mb-1">Tesseract OCR setup required:</p>
              <ol className="list-decimal list-inside space-y-1">
                <li>Download from: <a href="https://github.com/UB-Mannheim/tesseract/wiki" target="_blank" rel="noopener noreferrer" className="underline">Tesseract Installer</a></li>
                <li>Run the installer and note the path</li>
                <li>Restart the backend server</li>
              </ol>
            </div>
          )}
        </div>
      )}

      {/* Results Section */}
      {scanResult && (
        <>
          {/* OCR Results */}
          {scanResult.ocr_data && (
            <div className="card-3d bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-3">Extracted Text</h3>
              <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded p-4">
                <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed">
                  {scanResult.ocr_data.extracted_text || 'No text detected'}
                </p>
              </div>
              <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
                OCR confidence: {scanResult.ocr_data.confidence.toFixed(1)}%
              </p>
              {scanResult.ocr_data.confidence < 40 && (
                <div className="mt-3 rounded border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950 p-3 text-xs text-amber-700 dark:text-amber-300">
                  Low OCR confidence detected. For better results, use a sharper image, crop to the text area, and ensure good lighting.
                </div>
              )}
              {scanResult.ocr_data.metadata?.error && (
                <div className="mt-3 rounded border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950 p-3 text-xs text-blue-700 dark:text-blue-300">
                  OCR detail: {scanResult.ocr_data.metadata.error}
                </div>
              )}
            </div>
          )}

          {/* Risk Meter */}
          <RiskMeter
            riskScore={scanResult.risk_score}
            riskLevel={scanResult.risk_level}
            moduleBreakdown={scanResult.module_breakdown}
          />

          {/* Reasons */}
          {scanResult.reasons && scanResult.reasons.length > 0 && (
            <div className="card-3d bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-3">Risk Analysis</h3>
              <ul className="space-y-2">
                {scanResult.reasons.map((reason, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm">
                    <span className="text-amber-500 mt-0.5 flex-shrink-0">&#9679;</span>
                    <span className="text-gray-700 dark:text-gray-300">{reason}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Detections Summary */}
          <DetectionsSummary
            detectedPII={scanResult.detected_pii}
            intentAnalysis={scanResult.intent_analysis}
          />

          {/* Safer Suggestions */}
          {scanResult.safer_suggestions && scanResult.safer_suggestions.length > 0 && (
            <SuggestionsList suggestions={scanResult.safer_suggestions} />
          )}
        </>
      )}
    </div>
  );
};

export default ImageScanner;
