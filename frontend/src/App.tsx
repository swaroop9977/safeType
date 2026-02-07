/**
 * SafeType+ Main Application Component
 */

import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import TextScanner from './components/TextScanner';
import ImageScanner from './components/ImageScanner';
import Footer from './components/Footer';

type ScanMode = 'text' | 'image';

const App: React.FC = () => {
  const [scanMode, setScanMode] = useState<ScanMode>('text');
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    // Check local storage or system preference
    const saved = localStorage.getItem('darkMode');
    if (saved !== null) {
      return JSON.parse(saved);
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    // Apply dark mode class to document
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    // Save preference
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-50 via-cyan-50 to-blue-50 dark:from-slate-950 dark:via-cyan-950 dark:to-blue-900 transition-all">
      <Header darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
      
      <main className="flex-grow container mx-auto px-4 py-8 max-w-5xl">
        {/* Mode Selector */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex rounded-2xl bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm p-1.5 shadow-lg border border-white/20 dark:border-white/10">
            <button
              onClick={() => setScanMode('text')}
              className={`px-8 py-2.5 rounded-xl font-semibold transition-all duration-200 ${
                scanMode === 'text'
                  ? 'bg-gradient-to-r from-teal-500 to-cyan-500 text-white shadow-lg'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              📝 Text Scanner
            </button>
            <button
              onClick={() => setScanMode('image')}
              className={`px-8 py-2.5 rounded-xl font-semibold transition-all duration-200 ${
                scanMode === 'image'
                  ? 'bg-gradient-to-r from-teal-500 to-cyan-500 text-white shadow-lg'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              🖼️ Image Scanner
            </button>
          </div>
        </div>

        {/* Scanner Components - Keep both mounted to preserve state */}
        <div style={{ display: scanMode === 'text' ? 'block' : 'none' }}>
          <TextScanner />
        </div>
        <div style={{ display: scanMode === 'image' ? 'block' : 'none' }}>
          <ImageScanner />
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default App;
