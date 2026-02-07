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
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="bg-gradient-to-br from-white/95 to-cyan-50/95 dark:from-slate-800/95 dark:to-cyan-900/95 backdrop-blur-sm rounded-3xl shadow-lg p-8 border border-cyan-200/50 dark:border-cyan-800/50">
        <h2 className="text-xl font-bold bg-gradient-to-r from-teal-600 to-cyan-600 dark:from-teal-400 dark:to-cyan-400 bg-clip-text text-transparent mb-6">Upload Image</h2>

        <div className="border-3 border-dashed border-cyan-300 dark:border-cyan-800 rounded-2xl p-10 text-center bg-gradient-to-br from-cyan-50/50 to-teal-50/50 dark:from-cyan-900/20 dark:to-teal-900/20 hover:border-cyan-600 dark:hover:border-cyan-500 transition-all hover:shadow-lg">
          {imagePreview ? (
            <div className="space-y-4">
              <img
                src={imagePreview}
                alt="Preview"
                className="max-h-64 mx-auto rounded-2xl shadow-lg border-2 border-cyan-200 dark:border-cyan-800"
              />
              <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">{selectedImage?.name}</p>
            </div>
          ) : (
            <div>
              <svg
                className="mx-auto h-16 w-16 text-teal-400 dark:text-teal-600"
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
              <p className="mt-3 text-base font-semibold text-gray-700 dark:text-gray-300">
                Click to upload or drag and drop
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">PNG, JPG, GIF up to 10MB</p>
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
            className="mt-6 inline-block px-6 py-3 rounded-xl cursor-pointer bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-600 hover:to-cyan-600 text-white transition-all shadow-lg font-bold"
          >
            Choose Image
          </label>
        </div>

        <div className="flex justify-end gap-3 mt-6">
          <button
            onClick={handleClear}
            className="px-6 py-2.5 rounded-xl border-2 border-cyan-200 dark:border-cyan-800 hover:bg-cyan-50 dark:hover:bg-cyan-900/30 text-teal-700 dark:text-teal-300 transition-all font-semibold hover:shadow-md"
          >
            Clear
          </button>
          <button
            onClick={handleScan}
            disabled={!selectedImage || isScanning}
            className="px-8 py-2.5 bg-gradient-to-r from-teal-500 to-cyan-500 text-white rounded-xl hover:from-teal-600 hover:to-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-semibold shadow-lg hover:shadow-xl"
          >
            {isScanning ? 'Scanning...' : 'Scan Image'}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20 border-2 border-red-300 dark:border-red-800 rounded-2xl p-6">
          <div className="flex items-start gap-3">
            <span className="text-red-500 text-2xl">⚠️</span>
            <div className="flex-1">
              <p className="text-red-800 dark:text-red-300 font-bold mb-2">
                Error
              </p>
              <p className="text-red-700 dark:text-red-300 text-sm mb-2">{error}</p>
              {error.includes('Tesseract') && (
                <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/30 border-2 border-blue-300 dark:border-blue-800 rounded-xl">
                  <p className="text-sm text-blue-800 dark:text-blue-300 font-bold mb-3">
                    💡 Tesseract OCR Setup Required:
                  </p>
                  <ol className="text-xs text-blue-700 dark:text-blue-300 space-y-2 ml-5 font-medium">
                    <li>1. Download from: <a href="https://github.com/UB-Mannheim/tesseract/wiki" target="_blank" rel="noopener noreferrer" className="underline hover:text-blue-600 dark:hover:text-blue-200">Tesseract Installer</a></li>
                    <li>2. Run the installer (note the installation path)</li>
                    <li>3. Restart the backend server</li>
                    <li>4. See <code className="bg-blue-100 dark:bg-blue-900/40 px-1 rounded">INSTALL_TESSERACT.md</code> for detailed instructions</li>
                  </ol>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Results Section */}
      {scanResult && (
        <>
          {/* OCR Results */}
          {scanResult.ocr_data && (
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">
                Extracted Text (OCR)
              </h3>
              <div className="bg-gray-50 dark:bg-gray-700/50 p-5 rounded-xl">
                <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed">
                  {scanResult.ocr_data.extracted_text || 'No text detected'}
                </p>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-3">
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
          {scanResult.reasons && scanResult.reasons.length > 0 && (
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Risk Analysis</h3>
              <ul className="space-y-2.5">
                {scanResult.reasons.map((reason, index) => (
                  <li key={index} className="flex items-start gap-3 text-sm">
                    <span className="text-amber-500 mt-0.5">⚠</span>
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
