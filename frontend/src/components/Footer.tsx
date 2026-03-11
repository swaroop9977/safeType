/**
 * Footer Component - Minimal Design
 */

import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 mt-auto">
      <div className="container mx-auto px-6 py-4 max-w-3xl">
        <div className="flex flex-col sm:flex-row items-center justify-between text-xs text-gray-400 dark:text-gray-500">
          <p>SafeType+ &copy; 2026</p>
          <p className="mt-1 sm:mt-0">Privacy-first &middot; No data storage &middot; Academic Project</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
