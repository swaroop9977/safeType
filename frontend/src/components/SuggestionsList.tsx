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
    <div className="card-3d bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide">Safer Alternatives</h3>
        <span className="text-xs text-gray-400 dark:text-gray-500">
          {suggestions.length} suggestion{suggestions.length !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="space-y-3">
        {suggestions.map((suggestion, index) => (
          <div
            key={index}
            className="border border-gray-200 dark:border-gray-700 rounded p-4 hover:-translate-y-0.5 transition-transform shadow-sm hover:shadow"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">
                {suggestion.type}
              </span>
              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-400 dark:text-gray-500">
                  {Math.round(suggestion.confidence * 100)}%
                </span>
                <button
                  onClick={() => handleCopy(suggestion.text, index)}
                  className="text-xs text-teal-600 dark:text-teal-400 hover:underline"
                >
                  {copiedIndex === index ? 'Copied' : 'Copy'}
                </button>
              </div>
            </div>

            <p className="text-sm text-gray-800 dark:text-gray-200 bg-gray-50 dark:bg-gray-800 rounded p-3 mb-2 leading-relaxed border-l-2 border-teal-500">
              {suggestion.text}
            </p>

            <p className="text-xs text-gray-500 dark:text-gray-400">
              {suggestion.explanation}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SuggestionsList;
