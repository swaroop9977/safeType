/**
 * Image Scanner Component
 * Interface for image upload and OCR analysis
 */

import React, { useState } from 'react';
import { apiService, ScanResponse } from '../services/api';
import RiskMeter from './RiskMeter';
import SuggestionsList from './SuggestionsList';
import DetectionsSummary from './DetectionsSummary';

const ImageScanner: React.FC = () => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [scanResult, setScanResult] = useState<ScanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      setScanResult(null);
      setError(null);

      // Create preview
      const reader = new FileReader();
      reader.onload = (event) => {
        setImagePreview(event.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleScan = async () => {
    if (!selectedImage) return;

    setIsScanning(true);
    setError(null);

    try {
      const result = await apiService.scanImage({
        image: selectedImage,
        preprocess: true,
      });
      setScanResult(result);
    } catch (err: any) {
      const errorMessage = err.message || 'Unknown error occurred';
      setError(errorMessage);
      setScanResult(null);
    } finally {
      setIsScanning(false);
    }
  };

  const handleClear = () => {
    setSelectedImage(null);
    setImagePreview(null);
    setScanResult(null);
    setError(null);
  };

  return (
    <div className="space-y-4">
      {/* Upload Section */}
      <div className="card-3d bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-4">Upload Image</h2>

        <div className="border-2 border-dashed border-gray-200 dark:border-gray-700 rounded p-8 text-center hover:border-gray-300 dark:hover:border-gray-600 transition-colors">
          {imagePreview ? (
            <div className="space-y-3">
              <img
                src={imagePreview}
                alt="Preview"
                className="max-h-56 mx-auto rounded border border-gray-200 dark:border-gray-700"
              />
              <p className="text-sm text-gray-500 dark:text-gray-400">{selectedImage?.name}</p>
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
              <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">PNG, JPG, GIF up to 10MB</p>
            </div>
          )}

          <input
            type="file"
            accept="image/*"
            onChange={handleImageSelect}
            className="hidden"
            id="image-upload"
          />
          <label
            htmlFor="image-upload"
            className="mt-4 inline-block px-4 py-2 text-sm border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 rounded cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            Choose Image
          </label>
        </div>

        <div className="flex justify-end gap-2 mt-4">
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
