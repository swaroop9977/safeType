/**
 * Footer Component - Minimal Design
 */

import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gradient-to-r from-white/40 to-cyan-50/40 dark:from-slate-900/40 dark:to-cyan-900/40 backdrop-blur-md border-t border-cyan-200/50 dark:border-cyan-800/50 mt-auto transition-all">
      <div className="container mx-auto px-6 py-6">
        <div className="flex flex-col sm:flex-row items-center justify-between text-xs text-gray-600 dark:text-gray-400 font-medium">
          <p>SafeType+ © 2026</p>
          <p className="mt-2 sm:mt-0">🔒 Privacy-first • 🚫 No data storage • 🎓 Academic Project</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
