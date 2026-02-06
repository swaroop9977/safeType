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
    <div className="space-y-6">
      {/* Input Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100">Enter Text to Analyze</h2>
          <div className="flex space-x-2">
            <button
              onClick={() => loadExample('safe')}
              className="px-3 py-1 text-sm bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded hover:bg-green-200 dark:hover:bg-green-800"
            >
              Load Safe Example
            </button>
            <button
              onClick={() => loadExample('risky')}
              className="px-3 py-1 text-sm bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded hover:bg-red-200 dark:hover:bg-red-800"
            >
              Load Risky Example
            </button>
          </div>
        </div>

        <textarea
          value={text}
          onChange={handleTextChange}
          placeholder="Type or paste your text here... (Auto-scanning enabled)"
          className="w-full h-48 p-4 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none placeholder-gray-400 dark:placeholder-gray-500"
        />

        <div className="flex items-center justify-between mt-4">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            {text.length} characters
            {isScanning && <span className="ml-2 text-primary dark:text-blue-400">• Scanning...</span>}
          </div>
          <div className="space-x-2">
            <button
              onClick={handleClear}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200"
            >
              Clear
            </button>
            <button
              onClick={handleManualScan}
              disabled={!text.trim() || isScanning}
              className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Scan Now
            </button>
          </div>
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
