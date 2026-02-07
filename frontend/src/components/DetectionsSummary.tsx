/**
 * Detections Summary Component
 * Shows detailed breakdown of PII and intent analysis
 */

import React, { useState } from 'react';
import { PIIDetection } from '../services/api';

interface DetectionsSummaryProps {
  detectedPII: PIIDetection[];
  intentAnalysis: {
    probabilities: Record<string, number>;
    manipulation_detected: any;
  };
}

const DetectionsSummary: React.FC<DetectionsSummaryProps> = ({
  detectedPII,
  intentAnalysis,
}) => {
  const [showDetails, setShowDetails] = useState(false);

  const getPIIIcon = (type: string): string => {
    const icons: Record<string, string> = {
      email: '📧',
      phone: '📱',
      credit_card: '💳',
      ssn: '🆔',
      aadhaar: '🆔',
      person: '👤',
      org: '🏢',
      gpe: '🌍',
      ip_address: '🌐',
      date_of_birth: '📅',
      passport: '🛂',
      drivers_license: '🚗',
      medical_id: '🏥',
    };
    return icons[type] || '📄';
  };

  const getConfidenceBadge = (confidence: number): { color: string; label: string } => {
    if (confidence >= 0.9) {
      return { color: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 border-green-300 dark:border-green-700', label: 'High' };
    } else if (confidence >= 0.7) {
      return { color: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border-blue-300 dark:border-blue-700', label: 'Good' };
    } else if (confidence >= 0.5) {
      return { color: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 border-yellow-300 dark:border-yellow-700', label: 'Medium' };
    } else {
      return { color: 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 border-orange-300 dark:border-orange-700', label: 'Low' };
    }
  };

  return (
    <div className="bg-gradient-to-br from-white/95 to-cyan-50/95 dark:from-slate-800/95 dark:to-cyan-900/95 backdrop-blur-sm rounded-3xl shadow-lg p-8 border border-cyan-200/50 dark:border-cyan-800/50">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold bg-gradient-to-r from-teal-600 to-cyan-600 dark:from-teal-400 dark:to-cyan-400 bg-clip-text text-transparent">Detection Details</h3>
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-xs font-bold text-teal-600 dark:text-teal-400 hover:text-teal-700 dark:hover:text-teal-300 uppercase tracking-wider transition-colors"
        >
          {showDetails ? 'Hide' : 'Show All'}
        </button>
      </div>

      {/* PII Summary */}
      <div className="mb-8">
        <h4 className="text-sm font-bold text-gray-700 dark:text-gray-300 mb-4 uppercase tracking-wider">
          Detected PII ({detectedPII.length})
        </h4>
        {detectedPII.length > 0 ? (
          <div className="space-y-3">
            {detectedPII.slice(0, showDetails ? undefined : 3).map((pii, index) => {
              const confidenceBadge = getConfidenceBadge(pii.confidence);
              return (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 bg-gradient-to-r from-teal-100/50 to-cyan-100/50 dark:from-teal-900/20 dark:to-cyan-900/20 rounded-2xl hover:shadow-lg transition-all border border-teal-200/50 dark:border-teal-800/50"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{getPIIIcon(pii.type)}</span>
                    <div>
                      <span className="text-sm font-bold text-gray-800 dark:text-gray-200 block">
                        {pii.type.replace('_', ' ').toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-600 dark:text-gray-400 font-mono">{pii.value}</span>
                    </div>
                  </div>
                  <span className={`px-3 py-1.5 text-xs font-bold rounded-lg ${confidenceBadge.color}`}>
                    {Math.round(pii.confidence * 100)}%
                  </span>
                </div>
              );
            })}
            {!showDetails && detectedPII.length > 3 && (
              <p className="text-xs text-gray-600 dark:text-gray-400 text-center pt-2 font-medium">
                +{detectedPII.length - 3} more...
              </p>
            )}
          </div>
        ) : (
          <p className="text-sm text-gray-600 dark:text-gray-400 italic">No PII detected</p>
        )}
      </div>

      {/* Intent Analysis */}
      {showDetails && (
        <div>
          <h4 className="text-sm font-bold text-gray-700 dark:text-gray-300 mb-4 uppercase tracking-wider">Intent Analysis</h4>
          <div className="space-y-3">
            {Object.entries(intentAnalysis.probabilities)
              .sort(([, a], [, b]) => (b as number) - (a as number))
              .map(([intent, probability]) => (
                <div key={intent} className="flex items-center justify-between">
                  <span className="text-sm text-gray-700 dark:text-gray-300 font-medium capitalize">
                    {intent.replace('_', ' ')}
                  </span>
                  <div className="flex items-center gap-3">
                    <div className="w-28 h-2 bg-gray-200 dark:bg-slate-700 rounded-full overflow-hidden shadow-inner">
                      <div
                        className="h-full bg-gradient-to-r from-teal-400 to-cyan-400"
                        style={{ width: `${(probability as number) * 100}%` }}
                      />
                    </div>
                    <span className="text-xs font-bold text-gray-800 dark:text-gray-200 w-10 text-right">
                      {Math.round((probability as number) * 100)}%
                    </span>
                  </div>
                </div>
              ))}
          </div>

          {/* Manipulation Detection */}
          {intentAnalysis.manipulation_detected && (
            <div className="mt-6 p-4 bg-gradient-to-r from-orange-100 to-red-100 dark:from-orange-900/30 dark:to-red-900/30 border-2 border-orange-300 dark:border-orange-800 rounded-2xl">
              <p className="text-sm font-bold text-orange-800 dark:text-orange-400 mb-3">
                ⚠ Manipulation Tactics Detected
              </p>
              <ul className="text-xs text-orange-700 dark:text-orange-300 space-y-1.5 font-medium">
                {intentAnalysis.manipulation_detected.uses_urgency && (
                  <li>🔥 Urgency pressure</li>
                )}
                {intentAnalysis.manipulation_detected.uses_fear && (
                  <li>😰 Fear-based language</li>
                )}
                {intentAnalysis.manipulation_detected.uses_greed && (
                  <li>💰 Reward/greed appeal</li>
                )}
                {intentAnalysis.manipulation_detected.uses_authority && (
                  <li>👑 False authority</li>
                )}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DetectionsSummary;
