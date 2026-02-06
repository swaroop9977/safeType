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
        return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800';
      case 'rewritten':
        return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
      case 'guidance':
        return 'bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800';
      case 'template':
        return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800';
      default:
        return 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700';
    }
  };

  const getConfidenceBadge = (confidence: number): string => {
    if (confidence >= 0.9) {
      return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 border border-green-300 dark:border-green-700';
    } else if (confidence >= 0.7) {
      return 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border border-blue-300 dark:border-blue-700';
    } else {
      return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 border border-yellow-300 dark:border-yellow-700';
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
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Safer Alternatives</h3>
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {suggestions.length} suggestion{suggestions.length !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="space-y-4">
        {suggestions.map((suggestion, index) => (
          <div
            key={index}
            className={`border rounded-lg p-4 ${getTypeColor(suggestion.type)}`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center">
                <span className="text-2xl mr-2">{getTypeIcon(suggestion.type)}</span>
                <span className="font-medium text-gray-700 dark:text-gray-200 capitalize">
                  {suggestion.type}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getConfidenceBadge(suggestion.confidence)}`}>
                  {Math.round(suggestion.confidence * 100)}%
                </span>
                <button
                  onClick={() => handleCopy(suggestion.text, index)}
                  className="text-sm text-primary dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
                >
                  {copiedIndex === index ? '✓ Copied' : 'Copy'}
                </button>
              </div>
            </div>

            <p className="text-gray-800 dark:text-gray-200 mb-2 bg-white dark:bg-gray-700 p-3 rounded border border-gray-200 dark:border-gray-600">
              {suggestion.text}
            </p>

            <p className="text-sm text-gray-600 dark:text-gray-400 italic">
              {suggestion.explanation}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SuggestionsList;
