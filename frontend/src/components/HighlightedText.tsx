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
      return 'bg-orange-300 dark:bg-orange-600 text-gray-900 dark:text-white border-b-2 border-orange-600 dark:border-orange-400 font-medium';
    } else if (category === 'phishing') {
      return 'bg-red-300 dark:bg-red-600 text-gray-900 dark:text-white border-b-2 border-red-600 dark:border-red-400 font-medium';
    } else {
      return 'bg-blue-300 dark:bg-blue-600 text-gray-900 dark:text-white border-b-2 border-blue-600 dark:border-blue-400 font-medium';
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
    <div className="bg-gradient-to-br from-white/95 to-purple-50/95 dark:from-slate-800/95 dark:to-purple-900/95 backdrop-blur-sm rounded-3xl shadow-lg p-8 border border-purple-200/50 dark:border-purple-800/50">
      <h3 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-cyan-600 dark:from-purple-400 dark:to-cyan-400 bg-clip-text text-transparent mb-6">Highlighted Text</h3>
      
      {/* Legend */}
      <div className="flex flex-wrap gap-5 mb-6 text-sm">
        <div className="flex items-center gap-2">
          <span className="inline-block w-4 h-4 bg-gradient-to-r from-orange-400 to-orange-600 rounded-full"></span>
          <span className="text-gray-700 dark:text-gray-300 font-semibold">PII Data</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-block w-4 h-4 bg-gradient-to-r from-red-400 to-red-600 rounded-full"></span>
          <span className="text-gray-700 dark:text-gray-300 font-semibold">Phishing Keywords</span>
        </div>
      </div>

      {/* Highlighted Text */}
      <div className="bg-gradient-to-r from-purple-50 to-cyan-50 dark:from-purple-900/30 dark:to-cyan-900/30 p-6 rounded-2xl border-2 border-purple-200/50 dark:border-purple-800/50">
        <p className="text-gray-800 dark:text-gray-200 leading-relaxed whitespace-pre-wrap text-sm font-medium">
          {renderHighlightedText()}
        </p>
      </div>

      <p className="text-xs text-gray-600 dark:text-gray-400 mt-4 font-semibold">
        🎯 {highlights.length} risky span{highlights.length !== 1 ? 's' : ''} detected
      </p>
    </div>
  );
};

export default HighlightedText;
