/**
 * Footer Component
 */

import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-auto transition-colors">
      <div className="container mx-auto px-4 py-6">
        <div className="text-center">
          <p className="text-gray-600 dark:text-gray-300 text-sm">
            SafeType+ © 2026 | Academic Project
          </p>
          <p className="text-gray-500 dark:text-gray-400 text-xs mt-2">
            Privacy-first design • No data storage • Local processing when possible
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
