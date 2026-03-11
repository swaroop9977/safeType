/**
 * Text Scanner Component
 * Main interface for text analysis
 */

import React, { useState, useCallback, useEffect } from 'react';
import { apiService, ScanResponse } from '../services/api';
import RiskMeter from './RiskMeter';
import HighlightedText from './HighlightedText';
import SuggestionsList from './SuggestionsList';
import DetectionsSummary from './DetectionsSummary';

const TextScanner: React.FC = () => {
  const [text, setText] = useState<string>('');
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [scanResult, setScanResult] = useState<ScanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [debounceTimer, setDebounceTimer] = useState<NodeJS.Timeout | null>(null);

  // Debounced scan function
  const performScan = useCallback(async (textToScan: string) => {
    if (!textToScan.trim()) {
      setScanResult(null);
      return;
    }

    setIsScanning(true);
    setError(null);

    try {
      const result = await apiService.scanText({
        text: textToScan,
        include_suggestions: true,
        include_highlights: true,
      });
      setScanResult(result);
    } catch (err: any) {
      setError(err.message);
      setScanResult(null);
    } finally {
      setIsScanning(false);
    }
  }, []);

  // Handle text change with debounce
  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newText = e.target.value;
    setText(newText);

    // Clear previous timer
    if (debounceTimer) {
      clearTimeout(debounceTimer);
    }

    // Set new timer (auto-scan after 1.5 seconds of no typing)
    const timer = setTimeout(() => {
      if (newText.length > 10) { // Only scan if meaningful text
        performScan(newText);
      }
    }, 1500);

    setDebounceTimer(timer);
  };

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (debounceTimer) {
        clearTimeout(debounceTimer);
      }
    };
  }, [debounceTimer]);

  // Manual scan
  const handleManualScan = () => {
    if (text.trim()) {
      performScan(text);
    }
  };

  // Clear all
  const handleClear = () => {
    setText('');
    setScanResult(null);
    setError(null);
    if (debounceTimer) {
      clearTimeout(debounceTimer);
    }
  };

  // Example texts for quick testing
  const loadExample = (type: 'safe' | 'risky') => {
    const examples = {
      safe: "Hi team, let's schedule a meeting for next week to discuss the project updates. Please share your availability.",
      risky: "URGENT! Your account has been suspended. Click here immediately to verify your credit card information or your account will be permanently closed. Call us at 555-123-4567."
    };
    setText(examples[type]);
    performScan(examples[type]);
  };

  return (
    <div className="space-y-4">
      {/* Input Section */}
      <div className="card-3d bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide">Enter Text</h2>
          <div className="flex gap-2">
            <button
              onClick={() => loadExample('safe')}
              className="px-3 py-1 text-xs font-medium border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 rounded hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              Safe Example
            </button>
            <button
              onClick={() => loadExample('risky')}
              className="px-3 py-1 text-xs font-medium border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 rounded hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              Risky Example
            </button>
          </div>
        </div>

        <textarea
          value={text}
          onChange={handleTextChange}
          placeholder="Type or paste your text here..."
          className="w-full h-40 p-3 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 rounded focus:border-teal-500 dark:focus:border-teal-500 focus:outline-none resize-none placeholder-gray-400 dark:placeholder-gray-600 text-sm transition-colors"
        />

        <div className="flex items-center justify-between mt-3">
          <div className="flex items-center gap-3 text-xs text-gray-400 dark:text-gray-500">
            <span>{text.length} characters</span>
            {isScanning && (
              <span className="flex items-center gap-1.5 text-teal-600 dark:text-teal-400">
                <svg className="animate-spin h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Scanning...
              </span>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleClear}
              className="px-4 py-2 text-sm border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 rounded hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              Clear
            </button>
            <button
              onClick={handleManualScan}
              disabled={!text.trim() || isScanning}
              className="btn-3d px-5 py-2 text-sm bg-teal-600 text-white rounded disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Scan Now
            </button>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950 rounded p-4">
          <p className="text-red-700 dark:text-red-400 text-sm">
            <strong>Error:</strong> {error}
          </p>
        </div>
      )}

      {/* Results Section */}
      {scanResult && (
        <>
          {/* Risk Meter */}
          <RiskMeter
            riskScore={scanResult.risk_score}
            riskLevel={scanResult.risk_level}
            moduleBreakdown={scanResult.module_breakdown}
          />

          {/* Reasons */}
          {scanResult.reasons && scanResult.reasons.length > 0 && (
            <div className="card-3d bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-4">Risk Analysis</h3>
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

          {/* Highlighted Text */}
          {scanResult.highlights && scanResult.highlights.length > 0 && (
            <HighlightedText
              originalText={text}
              highlights={scanResult.highlights}
            />
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

export default TextScanner;
