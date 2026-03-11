/**
 * Risk Meter Component - Minimal Design
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
        return 'from-emerald-400 to-emerald-500';
      case 'Medium':
        return 'from-amber-400 to-amber-500';
      case 'High':
        return 'from-rose-400 to-rose-500';
      default:
        return 'from-gray-400 to-gray-500';
    }
  };

  const getRiskIcon = (level: string): string => {
    switch (level) {
      case 'Low':
        return '✓';
      case 'Medium':
        return '⚠';
      case 'High':
        return '⛔';
      default:
        return '•';
    }
  };

  const percentage = Math.round(riskScore * 100);

  return (
    <div className={`card-3d bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 border-t-4 p-6 ${
      riskLevel === 'Low' ? 'border-t-emerald-500' :
      riskLevel === 'Medium' ? 'border-t-amber-500' :
      'border-t-red-500'
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide">Risk Assessment</h3>
        <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${
          riskLevel === 'Low' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-400' :
          riskLevel === 'Medium' ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-400' :
          'bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-400'
        }`}>
          {riskLevel}
        </span>
      </div>

      {/* Risk Bar */}
      <div className="mb-5">
        <div className="bar-track w-full h-3 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
          <div
            className={`bar-fill h-full transition-all duration-500 rounded-full ${
              riskLevel === 'Low' ? 'bg-emerald-500' :
              riskLevel === 'Medium' ? 'bg-amber-500' :
              'bg-red-500'
            }`}
            style={{ width: `${percentage}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-400 dark:text-gray-500 mt-1.5">
          <span>Safe</span>
          <span>{percentage}%</span>
          <span>Risky</span>
        </div>
      </div>

      {/* Module Breakdown */}
      <div className="space-y-3">
        <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Detection Modules</p>

        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-600 dark:text-gray-400">PII Detection</span>
            <span className="text-gray-700 dark:text-gray-300">{Math.round(moduleBreakdown.pii * 100)}%</span>
          </div>
          <div className="bar-track w-full h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
            <div className="bar-fill h-full bg-teal-500 transition-all duration-500" style={{ width: `${moduleBreakdown.pii * 100}%` }} />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-600 dark:text-gray-400">Intent Analysis</span>
            <span className="text-gray-700 dark:text-gray-300">{Math.round(moduleBreakdown.nlp * 100)}%</span>
          </div>
          <div className="bar-track w-full h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
            <div className="bar-fill h-full bg-blue-500 transition-all duration-500" style={{ width: `${moduleBreakdown.nlp * 100}%` }} />
          </div>
        </div>

        {moduleBreakdown.ocr > 0 && (
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-gray-600 dark:text-gray-400">OCR Analysis</span>
              <span className="text-gray-700 dark:text-gray-300">{Math.round(moduleBreakdown.ocr * 100)}%</span>
            </div>
            <div className="bar-track w-full h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
              <div className="bar-fill h-full bg-purple-500 transition-all duration-500" style={{ width: `${moduleBreakdown.ocr * 100}%` }} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RiskMeter;
