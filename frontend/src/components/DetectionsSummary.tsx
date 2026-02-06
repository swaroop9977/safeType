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
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Detection Details</h3>
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-sm text-primary dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
        >
          {showDetails ? 'Hide Details' : 'Show Details'}
        </button>
      </div>

      {/* PII Summary */}
      <div className="mb-4">
        <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
          Detected PII ({detectedPII.length})
        </h4>
        {detectedPII.length > 0 ? (
          <div className="space-y-2">
            {detectedPII.slice(0, showDetails ? undefined : 3).map((pii, index) => {
              const confidenceBadge = getConfidenceBadge(pii.confidence);
              return (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-100 dark:border-gray-600"
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-xl">{getPIIIcon(pii.type)}</span>
                    <div>
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300 block">
                        {pii.type.replace('_', ' ').toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400 font-mono">{pii.value}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full border ${confidenceBadge.color}`}>
                      {Math.round(pii.confidence * 100)}%
                    </span>
                    <span className={`px-2 py-1 text-xs font-medium rounded ${confidenceBadge.color}`} title="Detection confidence level">
                      {confidenceBadge.label}
                    </span>
                  </div>
                </div>
              );
            })}
            {!showDetails && detectedPII.length > 3 && (
              <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
                +{detectedPII.length - 3} more...
              </p>
            )}
          </div>
        ) : (
          <p className="text-sm text-gray-500 dark:text-gray-400 italic">No PII detected</p>
        )}
      </div>

      {/* Intent Analysis */}
      {showDetails && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Intent Analysis</h4>
          <div className="space-y-2">
            {Object.entries(intentAnalysis.probabilities)
              .sort(([, a], [, b]) => (b as number) - (a as number))
              .map(([intent, probability]) => (
                <div key={intent} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                    {intent.replace('_', ' ')}
                  </span>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary"
                        style={{ width: `${(probability as number) * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-700 w-12 text-right">
                      {Math.round((probability as number) * 100)}%
                    </span>
                  </div>
                </div>
              ))}
          </div>

          {/* Manipulation Detection */}
          {intentAnalysis.manipulation_detected && (
            <div className="mt-4 p-3 bg-orange-50 border border-orange-200 rounded">
              <p className="text-sm font-semibold text-orange-800 mb-1">
                Manipulation Tactics Detected
              </p>
              <ul className="text-xs text-orange-700 space-y-1">
                {intentAnalysis.manipulation_detected.uses_urgency && (
                  <li>• Urgency pressure</li>
                )}
                {intentAnalysis.manipulation_detected.uses_fear && (
                  <li>• Fear-based language</li>
                )}
                {intentAnalysis.manipulation_detected.uses_greed && (
                  <li>• Reward/greed appeal</li>
                )}
                {intentAnalysis.manipulation_detected.uses_authority && (
                  <li>• False authority</li>
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
