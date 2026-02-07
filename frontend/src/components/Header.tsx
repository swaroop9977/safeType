/**
 * Header Component - Minimal Design
 */

import React from 'react';

interface HeaderProps {
  darkMode: boolean;
  toggleDarkMode: () => void;
}

const Header: React.FC<HeaderProps> = ({ darkMode, toggleDarkMode }) => {
  return (
    <header className="bg-gradient-to-r from-white/90 to-cyan-50/90 dark:from-slate-900/90 dark:to-cyan-900/90 backdrop-blur-xl border-b border-cyan-200/50 dark:border-cyan-800/50 transition-all shadow-sm">
      <div className="container mx-auto px-6 py-5">
        <div className="flex items-center justify-between">
          <div className="flex items-baseline space-x-3">
            <h1 className="text-2xl font-black bg-gradient-to-r from-teal-600 via-cyan-500 to-blue-500 dark:from-teal-400 dark:via-cyan-300 dark:to-blue-400 bg-clip-text text-transparent">
              SafeType+
            </h1>
            <span className="text-xs text-gray-500 dark:text-gray-400 font-bold hidden sm:inline uppercase tracking-wide">
              Privacy Shield
            </span>
          </div>
          
          <button
            onClick={toggleDarkMode}
            className="p-2.5 rounded-full hover:bg-cyan-100 dark:hover:bg-cyan-900 transition-all duration-200"
            aria-label="Toggle dark mode"
          >
            {darkMode ? (
              <svg className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-teal-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
