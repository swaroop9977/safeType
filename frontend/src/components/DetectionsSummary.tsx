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
      pan_card: '🪪',
      voter_id: '🗳️',
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
    <div className="card-3d bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide">Detection Details</h3>
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-xs text-teal-600 dark:text-teal-400 hover:underline"
        >
          {showDetails ? 'Hide' : 'Show All'}
        </button>
      </div>

      {/* PII */}
      <div className="mb-5">
        <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-3">
          Detected PII ({detectedPII.length})
        </p>
        {detectedPII.length > 0 ? (
          <div className="space-y-2">
            {detectedPII.slice(0, showDetails ? undefined : 3).map((pii, index) => {
              const confidenceBadge = getConfidenceBadge(pii.confidence);
              return (
                <div
                  key={index}
                  className="flex items-center justify-between px-3 py-2.5 bg-gray-50 dark:bg-gray-800 rounded border border-gray-100 dark:border-gray-700 hover:-translate-y-0.5 transition-transform shadow-sm hover:shadow"
                >
                  <div className="flex items-center gap-2.5">
                    <span className="text-base">{getPIIIcon(pii.type)}</span>
                    <div>
                      <p className="text-xs font-semibold text-gray-800 dark:text-gray-200">
                        {pii.type.replace('_', ' ').toUpperCase()}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 font-mono">{pii.value}</p>
                    </div>
                  </div>
                  <span className={`px-2 py-0.5 text-xs rounded border ${confidenceBadge.color}`}>
                    {Math.round(pii.confidence * 100)}%
                  </span>
                </div>
              );
            })}
            {!showDetails && detectedPII.length > 3 && (
              <p className="text-xs text-gray-400 dark:text-gray-500 text-center pt-1">
                +{detectedPII.length - 3} more
              </p>
            )}
          </div>
        ) : (
          <p className="text-sm text-gray-400 dark:text-gray-500">No PII detected</p>
        )}
      </div>

      {/* Intent (expanded) */}
      {showDetails && (
        <div>
          <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-3">Intent Analysis</p>
          <div className="space-y-2">
            {Object.entries(intentAnalysis.probabilities)
              .sort(([, a], [, b]) => (b as number) - (a as number))
              .map(([intent, probability]) => (
                <div key={intent} className="flex items-center justify-between gap-3">
                  <span className="text-sm text-gray-600 dark:text-gray-400 capitalize w-24">
                    {intent.replace('_', ' ')}
                  </span>
                  <div className="flex-1 h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-teal-500"
                      style={{ width: `${(probability as number) * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-500 dark:text-gray-400 w-8 text-right">
                    {Math.round((probability as number) * 100)}%
                  </span>
                </div>
              ))}
          </div>

          {intentAnalysis.manipulation_detected && (
            <div className="mt-4 p-3 border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950 rounded">
              <p className="text-xs font-medium text-amber-700 dark:text-amber-400 mb-2">Manipulation tactics detected</p>
              <ul className="text-xs text-amber-600 dark:text-amber-300 space-y-1">
                {intentAnalysis.manipulation_detected.uses_urgency && <li>Urgency pressure</li>}
                {intentAnalysis.manipulation_detected.uses_fear && <li>Fear-based language</li>}
                {intentAnalysis.manipulation_detected.uses_greed && <li>Reward / greed appeal</li>}
                {intentAnalysis.manipulation_detected.uses_authority && <li>False authority</li>}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DetectionsSummary;
