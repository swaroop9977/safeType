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
      setError(err.message);
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
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-4">Upload Image to Analyze</h2>

        <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center bg-gray-50 dark:bg-gray-700/50">
          {imagePreview ? (
            <div className="space-y-4">
              <img
                src={imagePreview}
                alt="Preview"
                className="max-h-64 mx-auto rounded"
              />
              <p className="text-sm text-gray-600 dark:text-gray-400">{selectedImage?.name}</p>
            </div>
          ) : (
            <div>
              <svg
                className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
                Click to upload or drag and drop
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">PNG, JPG, GIF up to 10MB</p>
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
            className="mt-4 inline-block px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 transition-colors"
          >
            Choose Image
          </label>
        </div>

        <div className="flex justify-end space-x-2 mt-4">
          <button
            onClick={handleClear}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200 transition-colors"
          >
            Clear
          </button>
          <button
            onClick={handleScan}
            disabled={!selectedImage || isScanning}
            className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isScanning ? 'Scanning...' : 'Scan Image'}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-800 dark:text-red-300">
            <strong>Error:</strong> {error}
          </p>
        </div>
      )}

      {/* Results Section */}
      {scanResult && (
        <>
          {/* OCR Results */}
          {scanResult.ocr_data && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-3">
                Extracted Text (OCR)
              </h3>
              <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded border border-gray-200 dark:border-gray-600">
                <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                  {scanResult.ocr_data.extracted_text || 'No text detected'}
                </p>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                OCR Confidence: {scanResult.ocr_data.confidence.toFixed(1)}%
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
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-3">Risk Analysis</h3>
            <ul className="space-y-2">
              {scanResult.reasons.map((reason, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-yellow-500 mr-2">⚠️</span>
                  <span className="text-gray-700 dark:text-gray-300">{reason}</span>
                </li>
              ))}
            </ul>
          </div>

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
