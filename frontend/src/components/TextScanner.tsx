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
      <div className="bg-gradient-to-br from-white/95 to-cyan-50/95 dark:from-slate-800/95 dark:to-cyan-900/95 backdrop-blur-sm rounded-3xl shadow-lg p-8 border border-cyan-200/50 dark:border-cyan-800/50">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold bg-gradient-to-r from-teal-600 to-cyan-600 dark:from-teal-400 dark:to-cyan-400 bg-clip-text text-transparent">Enter Text</h2>
          <div className="flex gap-2">
            <button
              onClick={() => loadExample('safe')}
              className="px-4 py-2 text-xs font-semibold bg-gradient-to-r from-emerald-100 to-teal-100 dark:from-emerald-900/40 dark:to-teal-900/40 text-emerald-700 dark:text-emerald-300 rounded-xl hover:from-emerald-200 hover:to-teal-200 dark:hover:from-emerald-900/60 dark:hover:to-teal-900/60 transition-all shadow-sm"
            >
              ✓ Safe Example
            </button>
            <button
              onClick={() => loadExample('risky')}
              className="px-4 py-2 text-xs font-semibold bg-gradient-to-r from-red-100 to-orange-100 dark:from-red-900/40 dark:to-orange-900/40 text-red-700 dark:text-red-300 rounded-xl hover:from-red-200 hover:to-orange-200 dark:hover:from-red-900/60 dark:hover:to-orange-900/60 transition-all shadow-sm"
            >
              ⚠ Risky Example
            </button>
          </div>
        </div>

        <textarea
          value={text}
          onChange={handleTextChange}
          placeholder="Type or paste your text here... (Auto-scanning enabled after typing pauses)"
          className="w-full h-48 p-5 border-2 border-cyan-200/50 dark:border-cyan-800/50 bg-white dark:bg-slate-700/50 text-gray-900 dark:text-gray-100 rounded-2xl focus:border-cyan-500 dark:focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 dark:focus:ring-cyan-800 focus:outline-none resize-none placeholder-gray-400 dark:placeholder-gray-500 transition-all"
        />

        <div className="flex items-center justify-between mt-5">
          <div className="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-400 font-medium">
            <span>{text.length} characters</span>
            {isScanning && (
              <span className="flex items-center gap-2 text-teal-600 dark:text-teal-400 font-semibold">
                <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Scanning...
              </span>
            )}
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleClear}
              className="px-6 py-2.5 rounded-xl border-2 border-cyan-200 dark:border-cyan-800 hover:bg-cyan-50 dark:hover:bg-cyan-900/30 text-teal-700 dark:text-teal-300 transition-all font-semibold hover:shadow-md"
            >
              Clear
            </button>
            <button
              onClick={handleManualScan}
              disabled={!text.trim() || isScanning}
              className="px-8 py-2.5 bg-gradient-to-r from-teal-500 to-cyan-500 text-white rounded-xl hover:from-teal-600 hover:to-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-semibold shadow-lg hover:shadow-xl"
            >
              Scan Now
            </button>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20 border-2 border-red-300 dark:border-red-800 rounded-2xl p-5">
          <p className="text-red-800 dark:text-red-300 text-sm font-medium">
            <strong>⚠️ Error:</strong> {error}
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
            <div className="bg-gradient-to-br from-white/95 to-cyan-50/95 dark:from-slate-800/95 dark:to-cyan-900/95 backdrop-blur-sm rounded-3xl shadow-lg p-8 border border-cyan-200/50 dark:border-cyan-800/50">
              <h3 className="text-xl font-bold bg-gradient-to-r from-teal-600 to-cyan-600 dark:from-teal-400 dark:to-cyan-400 bg-clip-text text-transparent mb-6">Risk Analysis</h3>
              <ul className="space-y-3">
                {scanResult.reasons.map((reason, index) => (
                  <li key={index} className="flex items-start gap-3 text-sm">
                    <span className="text-orange-500 mt-1 text-lg">⚠</span>
                    <span className="text-gray-700 dark:text-gray-300 font-medium">{reason}</span>
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
