/**
 * Highlighted Text Component
 * Displays text with highlighted risky spans
 */

import React from 'react';
import { Highlight } from '../services/api';

interface HighlightedTextProps {
  originalText: string;
  highlights: Highlight[];
}

const HighlightedText: React.FC<HighlightedTextProps> = ({ originalText, highlights }) => {
  const getHighlightClass = (category: string, severity: string): string => {
    if (category === 'pii') {
      return 'bg-yellow-200 border-b-2 border-yellow-500';
    } else if (category === 'phishing') {
      return 'bg-red-200 border-b-2 border-red-500';
    } else {
      return 'bg-blue-200 border-b-2 border-blue-500';
    }
  };

  // Create spans with highlights
  const renderHighlightedText = () => {
    if (!highlights || highlights.length === 0) {
      return <span>{originalText}</span>;
    }

    // Sort highlights by start position
    const sortedHighlights = [...highlights].sort((a, b) => a.start - b.start);

    const elements: JSX.Element[] = [];
    let lastIndex = 0;

    sortedHighlights.forEach((highlight, idx) => {
      // Add text before highlight
      if (highlight.start > lastIndex) {
        elements.push(
          <span key={`text-${idx}`}>
            {originalText.substring(lastIndex, highlight.start)}
          </span>
        );
      }

      // Add highlighted text
      elements.push(
        <span
          key={`highlight-${idx}`}
          className={`${getHighlightClass(highlight.category, highlight.severity)} px-1 rounded`}
          title={`${highlight.type} (${highlight.severity})`}
        >
          {originalText.substring(highlight.start, highlight.end)}
        </span>
      );

      lastIndex = highlight.end;
    });

    // Add remaining text
    if (lastIndex < originalText.length) {
      elements.push(
        <span key="text-end">
          {originalText.substring(lastIndex)}
        </span>
      );
    }

    return elements;
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-3">Highlighted Text</h3>
      
      {/* Legend */}
      <div className="flex space-x-4 mb-4 text-sm">
        <div className="flex items-center">
          <span className="inline-block w-4 h-4 bg-yellow-200 dark:bg-yellow-500/50 border border-yellow-500 rounded mr-1"></span>
          <span className="text-gray-600 dark:text-gray-400">PII</span>
        </div>
        <div className="flex items-center">
          <span className="inline-block w-4 h-4 bg-red-200 dark:bg-red-500/50 border border-red-500 rounded mr-1"></span>
          <span className="text-gray-600 dark:text-gray-400">Phishing Keywords</span>
        </div>
      </div>

      {/* Highlighted Text */}
      <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded border border-gray-200 dark:border-gray-600">
        <p className="text-gray-800 dark:text-gray-200 leading-relaxed whitespace-pre-wrap">
          {renderHighlightedText()}
        </p>
      </div>

      <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
        {highlights.length} risky span(s) detected
      </p>
    </div>
  );
};

export default HighlightedText;
