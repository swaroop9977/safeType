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
    <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900 transition-colors">
      <Header darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
      
      <main className="flex-grow container mx-auto px-4 py-8 max-w-6xl">
        {/* Mode Selector */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-1">
            <button
              onClick={() => setScanMode('text')}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                scanMode === 'text'
                  ? 'bg-primary text-white'
                  : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Scan Text
            </button>
            <button
              onClick={() => setScanMode('image')}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                scanMode === 'image'
                  ? 'bg-primary text-white'
                  : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Scan Image
            </button>
          </div>
        </div>

        {/* Scanner Component */}
        {scanMode === 'text' ? <TextScanner /> : <ImageScanner />}
      </main>

      <Footer />
    </div>
  );
};

export default App;
