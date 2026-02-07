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
    <div className="bg-gradient-to-br from-white/90 to-cyan-50/90 dark:from-slate-800/90 dark:to-cyan-900/90 backdrop-blur-sm rounded-3xl shadow-lg p-8 border border-cyan-200/50 dark:border-cyan-800/50">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <h3 className="text-xl font-bold bg-gradient-to-r from-teal-600 to-cyan-600 dark:from-teal-400 dark:to-cyan-400 bg-clip-text text-transparent">Risk Assessment</h3>
        <div className="flex items-center gap-2">
          <span className="text-2xl">{getRiskIcon(riskLevel)}</span>
          <span className={`text-2xl font-bold ${
            riskLevel === 'Low' ? 'text-emerald-600 dark:text-emerald-400' :
            riskLevel === 'Medium' ? 'text-amber-600 dark:text-amber-400' :
            'text-rose-600 dark:text-rose-400'
          }`}>
            {riskLevel}
          </span>
        </div>
      </div>

      {/* Risk Meter Bar */}
      <div className="relative mb-8">
        <div className="w-full h-12 bg-gradient-to-r from-gray-100 to-gray-200 dark:from-slate-700 dark:to-slate-600 rounded-full overflow-hidden shadow-inner">
          <div
            className={`h-full bg-gradient-to-r ${getRiskColor(riskLevel)} transition-all duration-700 ease-out flex items-center justify-end pr-6 shadow-lg`}
            style={{ width: `${percentage}%` }}
          >
            <span className="text-white text-sm font-bold drop-shadow-lg">{percentage}%</span>
          </div>
        </div>

        {/* Threshold markers */}
        <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-3 px-2 font-medium">
          <span>Safe</span>
          <span>Moderate</span>
          <span>Risky</span>
        </div>
      </div>

      {/* Module Breakdown */}
      <div className="space-y-5">
        <h4 className="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">Detection Modules</h4>
        
        {/* PII Score */}
        <div>
          <div className="flex justify-between text-xs mb-2">
            <span className="text-gray-600 dark:text-gray-400 font-medium">PII Detection</span>
            <span className="font-bold bg-gradient-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">{Math.round(moduleBreakdown.pii * 100)}%</span>
          </div>
          <div className="w-full h-3 bg-gray-200 dark:bg-slate-700 rounded-full overflow-hidden shadow-inner">
            <div
              className="h-full bg-gradient-to-r from-teal-400 to-teal-600 transition-all duration-500 shadow-md"
              style={{ width: `${moduleBreakdown.pii * 100}%` }}
            />
          </div>
        </div>

        {/* NLP Score */}
        <div>
          <div className="flex justify-between text-xs mb-2">
            <span className="text-gray-600 dark:text-gray-400 font-medium">Intent Analysis</span>
            <span className="font-bold bg-gradient-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">{Math.round(moduleBreakdown.nlp * 100)}%</span>
          </div>
          <div className="w-full h-3 bg-gray-200 dark:bg-slate-700 rounded-full overflow-hidden shadow-inner">
            <div
              className="h-full bg-gradient-to-r from-cyan-400 to-cyan-600 transition-all duration-500 shadow-md"
              style={{ width: `${moduleBreakdown.nlp * 100}%` }}
            />
          </div>
        </div>

        {/* OCR Score (if present) */}
        {moduleBreakdown.ocr > 0 && (
          <div>
            <div className="flex justify-between text-xs mb-2">
              <span className="text-gray-600 dark:text-gray-400 font-medium">OCR Analysis</span>
              <span className="font-bold bg-gradient-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">{Math.round(moduleBreakdown.ocr * 100)}%</span>
            </div>
            <div className="w-full h-3 bg-gray-200 dark:bg-slate-700 rounded-full overflow-hidden shadow-inner">
              <div
                className="h-full bg-gradient-to-r from-blue-400 to-blue-600 transition-all duration-500 shadow-md"
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
