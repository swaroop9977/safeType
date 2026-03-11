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
      return 'bg-amber-100 dark:bg-amber-900/40 text-amber-900 dark:text-amber-200 rounded px-0.5';
    } else if (category === 'phishing') {
      return 'bg-red-100 dark:bg-red-900/40 text-red-900 dark:text-red-200 rounded px-0.5';
    } else {
      return 'bg-blue-100 dark:bg-blue-900/40 text-blue-900 dark:text-blue-200 rounded px-0.5';
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
    <div className="card-3d bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-4">Highlighted Text</h3>

      {/* Legend */}
      <div className="flex flex-wrap gap-4 mb-4 text-xs">
        <div className="flex items-center gap-1.5">
          <span className="inline-block w-3 h-3 bg-amber-200 dark:bg-amber-800 rounded-sm"></span>
          <span className="text-gray-500 dark:text-gray-400">PII Data</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="inline-block w-3 h-3 bg-red-200 dark:bg-red-800 rounded-sm"></span>
          <span className="text-gray-500 dark:text-gray-400">Phishing Keywords</span>
        </div>
      </div>

      {/* Text */}
      <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded p-4">
        <p className="text-sm text-gray-800 dark:text-gray-200 leading-relaxed whitespace-pre-wrap">
          {renderHighlightedText()}
        </p>
      </div>

      <p className="text-xs text-gray-400 dark:text-gray-500 mt-3">
        {highlights.length} risky span{highlights.length !== 1 ? 's' : ''} detected
      </p>
    </div>
  );
};

export default HighlightedText;
