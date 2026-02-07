/**
 * Suggestions List Component
 * Displays safer alternative suggestions
 */

import React, { useState } from 'react';
import { Suggestion } from '../services/api';

interface SuggestionsListProps {
  suggestions: Suggestion[];
}

const SuggestionsList: React.FC<SuggestionsListProps> = ({ suggestions }) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const getTypeIcon = (type: string): string => {
    switch (type) {
      case 'redacted':
        return '🔒';
      case 'rewritten':
        return '✏️';
      case 'guidance':
        return '💡';
      case 'template':
        return '📝';
      default:
        return '💬';
    }
  };

  const getTypeColor = (type: string): string => {
    switch (type) {
      case 'redacted':
        return 'bg-blue-50 dark:bg-blue-900/20';
      case 'rewritten':
        return 'bg-emerald-50 dark:bg-emerald-900/20';
      case 'guidance':
        return 'bg-purple-50 dark:bg-purple-900/20';
      case 'template':
        return 'bg-amber-50 dark:bg-amber-900/20';
      default:
        return 'bg-gray-50 dark:bg-gray-800';
    }
  };

  const getConfidenceBadge = (confidence: number): string => {
    if (confidence >= 0.9) {
      return 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300';
    } else if (confidence >= 0.7) {
      return 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300';
    } else {
      return 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300';
    }
  };

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  if (!suggestions || suggestions.length === 0) {
    return null;
  }

  return (
    <div className="bg-gradient-to-br from-white/95 to-cyan-50/95 dark:from-slate-800/95 dark:to-cyan-900/95 backdrop-blur-sm rounded-3xl shadow-lg p-8 border border-cyan-200/50 dark:border-cyan-800/50">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold bg-gradient-to-r from-teal-600 to-cyan-600 dark:from-teal-400 dark:to-cyan-400 bg-clip-text text-transparent">Safer Alternatives</h3>
        <span className="text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider bg-cyan-100/50 dark:bg-cyan-900/30 px-3 py-1.5 rounded-lg">
          {suggestions.length} suggestion{suggestions.length !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="space-y-4">
        {suggestions.map((suggestion, index) => (
          <div
            key={index}
            className={`rounded-2xl p-5 ${getTypeColor(suggestion.type)} border-2 border-opacity-40 transition-all hover:shadow-lg hover:scale-102`}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{getTypeIcon(suggestion.type)}</span>
                <span className="font-bold text-gray-800 dark:text-gray-200 capitalize text-sm uppercase tracking-wider">
                  {suggestion.type}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span className={`px-3 py-1 text-xs font-bold rounded-lg ${getConfidenceBadge(suggestion.confidence)}`}>
                  {Math.round(suggestion.confidence * 100)}%
                </span>
                <button
                  onClick={() => handleCopy(suggestion.text, index)}
                  className="text-xs text-teal-600 dark:text-teal-400 hover:text-teal-700 dark:hover:text-teal-300 font-bold transition-colors uppercase tracking-wide"
                >
                  {copiedIndex === index ? '✓ Copied' : 'Copy'}
                </button>
              </div>
            </div>

            <p className="text-gray-800 dark:text-gray-200 mb-3 bg-white/80 dark:bg-slate-700/60 p-4 rounded-xl text-sm leading-relaxed font-medium border-l-4 border-teal-500">
              {suggestion.text}
            </p>

            <p className="text-xs text-gray-700 dark:text-gray-400 italic font-medium">
              💡 {suggestion.explanation}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SuggestionsList;
