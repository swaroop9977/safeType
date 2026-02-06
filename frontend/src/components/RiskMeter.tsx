/**
 * Risk Meter Component
 * Visual representation of risk score with color-coded meter
 */

import React from 'react';

interface RiskMeterProps {
  riskScore: number;
  riskLevel: string;
  moduleBreakdown: {
    pii: number;
    nlp: number;
    ocr: number;
  };
}

const RiskMeter: React.FC<RiskMeterProps> = ({ riskScore, riskLevel, moduleBreakdown }) => {
  const getRiskColor = (level: string): string => {
    switch (level) {
      case 'Low':
        return 'bg-risk-low';
      case 'Medium':
        return 'bg-risk-medium';
      case 'High':
        return 'bg-risk-high';
      default:
        return 'bg-gray-400';
    }
  };

  const getRiskTextColor = (level: string): string => {
    switch (level) {
      case 'Low':
        return 'text-risk-low';
      case 'Medium':
        return 'text-risk-medium';
      case 'High':
        return 'text-risk-high';
      default:
        return 'text-gray-600';
    }
  };

  const percentage = Math.round(riskScore * 100);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Risk Assessment</h3>
        <div className={`text-2xl font-bold ${getRiskTextColor(riskLevel)}`}>
          {riskLevel}
        </div>
      </div>

      {/* Risk Meter Bar */}
      <div className="relative">
        <div className="w-full h-8 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
          <div
            className={`h-full ${getRiskColor(riskLevel)} transition-all duration-500 flex items-center justify-end pr-3`}
            style={{ width: `${percentage}%` }}
          >
            <span className="text-white text-sm font-semibold">{percentage}%</span>
          </div>
        </div>

        {/* Threshold markers */}
        <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
          <span>0%</span>
          <span>30%</span>
          <span>60%</span>
          <span>100%</span>
        </div>
      </div>

      {/* Module Breakdown */}
      <div className="mt-6 space-y-3">
        <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300">Module Contributions</h4>
        
        {/* PII Score */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600 dark:text-gray-400">PII Detection</span>
            <span className="font-medium text-gray-800 dark:text-gray-200">{Math.round(moduleBreakdown.pii * 100)}%</span>
          </div>
          <div className="w-full h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 dark:bg-blue-400"
              style={{ width: `${moduleBreakdown.pii * 100}%` }}
            />
          </div>
        </div>

        {/* NLP Score */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600 dark:text-gray-400">NLP Intent Analysis</span>
            <span className="font-medium text-gray-800 dark:text-gray-200">{Math.round(moduleBreakdown.nlp * 100)}%</span>
          </div>
          <div className="w-full h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
            <div
              className="h-full bg-purple-500 dark:bg-purple-400"
              style={{ width: `${moduleBreakdown.nlp * 100}%` }}
            />
          </div>
        </div>

        {/* OCR Score (if present) */}
        {moduleBreakdown.ocr > 0 && (
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600 dark:text-gray-400">OCR Analysis</span>
              <span className="font-medium text-gray-800 dark:text-gray-200">{Math.round(moduleBreakdown.ocr * 100)}%</span>
            </div>
            <div className="w-full h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
              <div
                className="h-full bg-indigo-500 dark:bg-indigo-400"
                style={{ width: `${moduleBreakdown.ocr * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RiskMeter;
