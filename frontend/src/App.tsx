/**
 * SafeType+ Main Application Component
 */

import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import TextScanner from './components/TextScanner';
import ImageScanner from './components/ImageScanner';
import Footer from './components/Footer';
import LandingPage from './components/LandingPage';

type ScanMode = 'text' | 'image';
type AppView = 'landing' | 'app';

const App: React.FC = () => {
  const [view, setView] = useState<AppView>('landing');
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

  if (view === 'landing') {
    return (
      <LandingPage
        onLaunch={() => setView('app')}
        darkMode={darkMode}
        toggleDarkMode={toggleDarkMode}
      />
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-100 via-white to-sky-50 dark:from-gray-950 dark:via-gray-900 dark:to-slate-950">
      <Header darkMode={darkMode} toggleDarkMode={toggleDarkMode} onHome={() => setView('landing')} />
      
      <main className="flex-grow container mx-auto px-4 py-8 max-w-3xl">
        {/* Mode Selector */}
        <div className="flex border-b border-gray-200 dark:border-gray-800 mb-8">
          <button
            onClick={() => setScanMode('text')}
            className={`px-6 py-3 text-sm font-medium transition-colors ${
              scanMode === 'text'
                ? 'border-b-2 border-teal-600 text-teal-600 dark:text-teal-400 dark:border-teal-400 -mb-px'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
            }`}
          >
            Text Scanner
          </button>
          <button
            onClick={() => setScanMode('image')}
            className={`px-6 py-3 text-sm font-medium transition-colors ${
              scanMode === 'image'
                ? 'border-b-2 border-teal-600 text-teal-600 dark:text-teal-400 dark:border-teal-400 -mb-px'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
            }`}
          >
            Image Scanner
          </button>
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
