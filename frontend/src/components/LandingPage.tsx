/**
 * LandingPage — SafeType+ marketing page
 * Minimal 3D design with gray theme.
 */

import React, { useState, useEffect } from 'react';

interface Props {
  onLaunch: () => void;
  darkMode: boolean;
  toggleDarkMode: () => void;
}

// ── Demo data ──────────────────────────────────────────────────────────────
const RISK_EXAMPLES = [
  {
    score: 87,
    level: 'High' as const,
    tags: ['Email', 'Phone', 'PAN Card', 'Date of Birth'],
    note: '4 sensitive items · Replace with redacted values',
  },
  {
    score: 54,
    level: 'Medium' as const,
    tags: ['Email', 'IP Address'],
    note: '2 items detected · Consider masking before sharing',
  },
  {
    score: 18,
    level: 'Low' as const,
    tags: ['Organisation name'],
    note: '1 low-severity item · Generally safe to share',
  },
  {
    score: 72,
    level: 'High' as const,
    tags: ['Aadhaar', 'Full Name', 'Phone'],
    note: '3 sensitive items · High privacy risk detected',
  },
];

const OCR_EXAMPLES = [
  {
    label: 'PAN Card',
    text: (
      <>
        <span className="font-bold text-red-600 dark:text-red-400">ABCDE1234F</span>
        {' · RAHUL SHARMA · '}
        <span className="text-orange-600 dark:text-orange-400">15/08/1990</span>
      </>
    ),
    tags: ['PAN Card', 'Full Name', 'Date of Birth'],
    color: 'red' as const,
  },
  {
    label: 'Aadhaar Card',
    text: (
      <>
        <span className="font-bold text-red-600 dark:text-red-400">2345 6789 0123</span>
        {' · PRIYA MENON · '}
        <span className="text-orange-600 dark:text-orange-400">Bengaluru, KA</span>
      </>
    ),
    tags: ['Aadhaar', 'Full Name', 'Location'],
    color: 'red' as const,
  },
  {
    label: 'Business Card',
    text: (
      <>
        <span className="font-bold text-amber-600 dark:text-amber-400">ceo@acmecorp.io</span>
        {' · '}
        <span className="text-amber-600 dark:text-amber-400">+1 415-555-0192</span>
      </>
    ),
    tags: ['Email', 'Phone'],
    color: 'amber' as const,
  },
  {
    label: 'Passport',
    text: (
      <>
        <span className="font-bold text-red-600 dark:text-red-400">A1234567</span>
        {' · AMIT VERMA · '}
        <span className="text-orange-600 dark:text-orange-400">01/01/1985</span>
      </>
    ),
    tags: ['Passport No.', 'Full Name', 'Date of Birth'],
    color: 'red' as const,
  },
];

const LEVEL_STYLES = {
  High:   { badge: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400',   bar: 'bg-red-500' },
  Medium: { badge: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400', bar: 'bg-amber-500' },
  Low:    { badge: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400', bar: 'bg-emerald-500' },
};

const TAG_COLOR: Record<'red' | 'amber', string> = {
  red:   'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  amber: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
};

const TEXT_EXAMPLES = [
  {
    body: (
      <>
        Hi, my email is{' '}
        <span className="bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400 rounded px-0.5 font-medium">john@example.com</span>
        {' '}and my number is{' '}
        <span className="bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400 rounded px-0.5 font-medium">+91 9876543210</span>.
      </>
    ),
    count: 2,
    score: 58,
    level: 'Medium' as const,
  },
  {
    body: (
      <>
        Please verify your account urgently. Click{' '}
        <span className="bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400 rounded px-0.5 font-medium">http://secure-login.xyz</span>
        {' '}and enter your{' '}
        <span className="bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400 rounded px-0.5 font-medium">password</span> now.
      </>
    ),
    count: 2,
    score: 82,
    level: 'High' as const,
  },
  {
    body: (
      <>
        My Aadhaar is{' '}
        <span className="bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400 rounded px-0.5 font-medium">2345 6789 0123</span>
        {' '}and DOB is{' '}
        <span className="bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400 rounded px-0.5 font-medium">15/08/1990</span>.
      </>
    ),
    count: 2,
    score: 91,
    level: 'High' as const,
  },
  {
    body: (
      <>
        Meeting tomorrow at{' '}
        <span className="bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400 rounded px-0.5 font-medium">Acme Corp</span>
        {' '}HQ. Agenda is attached.
      </>
    ),
    count: 1,
    score: 12,
    level: 'Low' as const,
  },
];

const TEXT_LEVEL_COLOR: Record<'High'|'Medium'|'Low', string> = {
  High:   'text-red-600 dark:text-red-400',
  Medium: 'text-amber-600 dark:text-amber-400',
  Low:    'text-emerald-600 dark:text-emerald-400',
};
const TEXT_BAR_COLOR: Record<'High'|'Medium'|'Low', string> = {
  High:   'bg-red-500',
  Medium: 'bg-amber-500',
  Low:    'bg-emerald-500',
};
// ───────────────────────────────────────────────────────────────────────────

const LandingPage: React.FC<Props> = ({ onLaunch, darkMode, toggleDarkMode }) => {
  const [riskIdx, setRiskIdx] = useState(0);
  const [ocrIdx,  setOcrIdx]  = useState(0);
  const [textIdx, setTextIdx] = useState(0);
  const [riskFade, setRiskFade] = useState(true);
  const [ocrFade,  setOcrFade]  = useState(true);
  const [textFade, setTextFade] = useState(true);

  // Auto-cycle risk card every 3 s
  useEffect(() => {
    const id = setInterval(() => {
      setRiskFade(false);
      setTimeout(() => {
        setRiskIdx(i => (i + 1) % RISK_EXAMPLES.length);
        setRiskFade(true);
      }, 300);
    }, 3000);
    return () => clearInterval(id);
  }, []);

  // Auto-cycle OCR card every 3.5 s (offset so they don't flip together)
  useEffect(() => {
    const id = setInterval(() => {
      setOcrFade(false);
      setTimeout(() => {
        setOcrIdx(i => (i + 1) % OCR_EXAMPLES.length);
        setOcrFade(true);
      }, 300);
    }, 3500);
    return () => clearInterval(id);
  }, []);

  // Auto-cycle text card every 4 s
  useEffect(() => {
    const id = setInterval(() => {
      setTextFade(false);
      setTimeout(() => {
        setTextIdx(i => (i + 1) % TEXT_EXAMPLES.length);
        setTextFade(true);
      }, 300);
    }, 4000);
    return () => clearInterval(id);
  }, []);

  const risk = RISK_EXAMPLES[riskIdx];
  const ocr  = OCR_EXAMPLES[ocrIdx];
  const txt  = TEXT_EXAMPLES[textIdx];
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 overflow-x-hidden">

      {/* ── Navigation ──────────────────────────────────────────── */}
      <nav className="sticky top-0 z-50 bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm border-b border-gray-200 dark:border-gray-800 shadow-sm">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-semibold text-gray-900 dark:text-white">SafeType+</span>
            <span className="hidden sm:inline text-xs text-gray-400 dark:text-gray-500">Privacy Shield</span>
          </div>

          <div className="hidden md:flex items-center gap-8 text-sm text-gray-500 dark:text-gray-400">
            <a href="#features" className="hover:text-gray-900 dark:hover:text-white transition-colors">Features</a>
            <a href="#how-it-works" className="hover:text-gray-900 dark:hover:text-white transition-colors">How it works</a>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              aria-label="Toggle dark mode"
            >
              {darkMode ? (
                <svg className="w-4 h-4 text-gray-500 dark:text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg className="w-4 h-4 text-gray-500 dark:text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                </svg>
              )}
            </button>
            <button
              onClick={onLaunch}
              className="btn-3d px-5 py-2 text-sm bg-teal-600 text-white rounded font-medium"
            >
              Open App
            </button>
          </div>
        </div>
      </nav>

      {/* ── Hero ────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden pt-24 pb-32 bg-gray-50 dark:bg-gray-950">
        {/* Floating neumorphic blobs */}
        <div className="shape-float absolute w-72 h-72" style={{ top: '-2rem', right: '-2rem', animationDelay: '0s' }} />
        <div className="shape-float absolute w-44 h-44" style={{ top: '8rem', right: '18rem', opacity: 0.5 }} />
        <div className="shape-float absolute w-24 h-24" style={{ bottom: '4rem', right: '6rem', opacity: 0.4 }} />
        <div className="shape-float absolute w-12 h-12 rounded-full" style={{ bottom: '8rem', right: '28rem', opacity: 0.6 }} />

        <div className="relative max-w-6xl mx-auto px-6 flex flex-col lg:flex-row items-center gap-16">
          {/* Left: copy */}
          <div className="flex-1 max-w-xl">
            <span className="inline-block text-xs font-bold tracking-widest text-teal-600 uppercase mb-5">
              Privacy-first detection
            </span>
            <h1 className="text-5xl sm:text-6xl font-extrabold text-gray-900 dark:text-white leading-[1.08] tracking-tight">
              Know what's<br />sensitive<br />before you<br />share it.
            </h1>
            <p className="mt-7 text-base text-gray-500 dark:text-gray-400 leading-relaxed max-w-md">
              SafeType+ scans text and images for personal data, phishing patterns, and privacy risks — in real time, privately, with zero data stored.
            </p>
            <div className="mt-10 flex items-center gap-6">
              <button
                onClick={onLaunch}
                className="btn-3d px-8 py-3 bg-teal-600 text-white rounded text-sm font-semibold"
              >
                Try it free
              </button>
              <a
                href="#how-it-works"
                className="text-sm text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors flex items-center gap-1"
              >
                How it works
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </a>
            </div>
          </div>

          {/* Right: mock risk card */}
          <div className="hidden lg:flex flex-1 justify-end items-start pt-8">
            <div
              className="card-3d bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-7 w-80"
              style={{ transition: 'opacity 0.3s ease', opacity: riskFade ? 1 : 0 }}
            >
              <div className="flex items-center justify-between mb-5">
                <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Risk Assessment</span>
                <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${LEVEL_STYLES[risk.level].badge}`}>
                  {risk.level}
                </span>
              </div>
              <div className="text-4xl font-extrabold text-gray-900 dark:text-white mb-1">
                {risk.score}
                <span className="text-lg font-medium text-gray-400">/100</span>
              </div>
              <div className="bar-track w-full h-3 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden mb-6">
                <div
                  className={`bar-fill h-full rounded-full ${LEVEL_STYLES[risk.level].bar}`}
                  style={{ width: `${risk.score}%`, transition: 'width 0.5s ease' }}
                />
              </div>
              <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Detected</div>
              <div className="flex flex-wrap gap-1.5 mb-6">
                {risk.tags.map(tag => (
                  <span key={tag} className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 rounded">
                    {tag}
                  </span>
                ))}
              </div>
              <div className="text-xs text-gray-400 border-t border-gray-100 dark:border-gray-800 pt-4">
                {risk.note}
              </div>
              {/* Dot indicators */}
              <div className="flex gap-1.5 mt-4 justify-center">
                {RISK_EXAMPLES.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => { setRiskFade(false); setTimeout(() => { setRiskIdx(i); setRiskFade(true); }, 300); }}
                    className={`w-1.5 h-1.5 rounded-full transition-colors ${
                      i === riskIdx ? 'bg-teal-500' : 'bg-gray-300 dark:bg-gray-700'
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Stats strip ─────────────────────────────────────────── */}
      <section className="bg-white dark:bg-gray-900 border-y border-gray-200 dark:border-gray-800">
        <div className="max-w-6xl mx-auto px-6 py-14 grid grid-cols-1 sm:grid-cols-3 divide-y sm:divide-y-0 sm:divide-x divide-gray-200 dark:divide-gray-800">
          {[
            { value: '20+', label: 'PII types detected' },
            { value: '10+', label: 'Languages supported' },
            { value: '0 bytes', label: 'Data ever stored' },
          ].map(s => (
            <div key={s.label} className="text-center sm:px-12 py-6 sm:py-0">
              <p className="text-5xl font-extrabold text-gray-900 dark:text-white">{s.value}</p>
              <p className="mt-2 text-sm text-gray-400">{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Feature 1: Text Scanner ─────────────────────────────── */}
      <section id="features" className="py-28 bg-gray-50 dark:bg-gray-950">
        <div className="max-w-6xl mx-auto px-6 flex flex-col lg:flex-row items-center gap-20">
          {/* Copy */}
          <div className="flex-1">
            <span className="text-xs font-bold tracking-widest text-teal-600 uppercase">Text Analysis</span>
            <h2 className="mt-4 text-4xl font-bold text-gray-900 dark:text-white leading-tight">
              Paste text.<br />Get a risk score.
            </h2>
            <p className="mt-5 text-gray-500 dark:text-gray-400 leading-relaxed max-w-sm">
              Detects emails, phone numbers, national IDs, Aadhaar, PAN cards, passwords and dozens more — across English and multiple languages.
            </p>
            <ul className="mt-7 space-y-3 text-sm text-gray-500 dark:text-gray-400">
              {[
                'Regex + NLP dual-engine detection',
                'Phishing intent classification',
                'Safer alternatives suggested automatically',
              ].map(item => (
                <li key={item} className="flex items-center gap-3">
                  <span className="w-1.5 h-1.5 rounded-full bg-teal-500 flex-shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
            <button
              onClick={onLaunch}
              className="mt-9 btn-3d px-7 py-2.5 bg-teal-600 text-white rounded text-sm font-semibold"
            >
              Try Text Scanner
            </button>
          </div>

          {/* Visual */}
          <div className="flex-1 flex justify-center">
            <div
              className="card-3d bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 w-full max-w-sm"
              style={{ transition: 'opacity 0.3s ease', opacity: textFade ? 1 : 0 }}
            >
              <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Input text</div>
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 text-sm text-gray-700 dark:text-gray-300 leading-relaxed mb-5">
                {txt.body}
              </div>
              <div className="bar-track w-full h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden mb-3">
                <div
                  className={`bar-fill h-full rounded-full ${TEXT_BAR_COLOR[txt.level]}`}
                  style={{ width: `${txt.score}%`, transition: 'width 0.5s ease' }}
                />
              </div>
              <div className="flex items-center justify-between text-xs text-gray-400">
                <span>{txt.count} item{txt.count !== 1 ? 's' : ''} detected</span>
                <span className={`font-semibold ${TEXT_LEVEL_COLOR[txt.level]}`}>
                  {txt.level} risk · {txt.score}/100
                </span>
              </div>
              {/* Dot indicators */}
              <div className="flex gap-1.5 mt-4 justify-center">
                {TEXT_EXAMPLES.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => { setTextFade(false); setTimeout(() => { setTextIdx(i); setTextFade(true); }, 300); }}
                    className={`w-1.5 h-1.5 rounded-full transition-colors ${
                      i === textIdx ? 'bg-teal-500' : 'bg-gray-300 dark:bg-gray-700'
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Feature 2: Image Scanner ────────────────────────────── */}
      <section className="py-28 bg-white dark:bg-gray-900">
        <div className="max-w-6xl mx-auto px-6 flex flex-col-reverse lg:flex-row items-center gap-20">
          {/* Visual */}
          <div className="flex-1 flex justify-center">
            <div
              className="card-3d bg-gray-50 dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 w-full max-w-sm flex flex-col gap-5"
              style={{ transition: 'opacity 0.3s ease', opacity: ocrFade ? 1 : 0 }}
            >
              <div className="w-full h-36 bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600 rounded-xl flex flex-col items-center justify-center gap-2">
                <svg className="w-10 h-10 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span className="text-xs font-semibold text-gray-400 uppercase tracking-widest">{ocr.label}</span>
              </div>
              <div>
                <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">OCR Extracted</div>
                <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{ocr.text}</div>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {ocr.tags.map(tag => (
                  <span key={tag} className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${TAG_COLOR[ocr.color]}`}>
                    {tag}
                  </span>
                ))}
              </div>
              {/* Dot indicators */}
              <div className="flex gap-1.5 justify-center">
                {OCR_EXAMPLES.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => { setOcrFade(false); setTimeout(() => { setOcrIdx(i); setOcrFade(true); }, 300); }}
                    className={`w-1.5 h-1.5 rounded-full transition-colors ${
                      i === ocrIdx ? 'bg-teal-500' : 'bg-gray-300 dark:bg-gray-700'
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Copy */}
          <div className="flex-1">
            <span className="text-xs font-bold tracking-widest text-teal-600 uppercase">Image OCR</span>
            <h2 className="mt-4 text-4xl font-bold text-gray-900 dark:text-white leading-tight">
              Scan any ID card<br />or document photo.
            </h2>
            <p className="mt-5 text-gray-500 dark:text-gray-400 leading-relaxed max-w-sm">
              Upload a photo or screenshot. OCR extracts text, then the full PII pipeline runs — detecting PAN cards, Aadhaar, passports, and more.
            </p>
            <ul className="mt-7 space-y-3 text-sm text-gray-500 dark:text-gray-400">
              {[
                'Multi-strategy preprocessing for colored cards',
                'Hindi + English OCR with LSTM engine',
                'Instant results — nothing sent to any cloud',
              ].map(item => (
                <li key={item} className="flex items-center gap-3">
                  <span className="w-1.5 h-1.5 rounded-full bg-teal-500 flex-shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
            <button
              onClick={onLaunch}
              className="mt-9 btn-3d px-7 py-2.5 bg-teal-600 text-white rounded text-sm font-semibold"
            >
              Try Image Scanner
            </button>
          </div>
        </div>
      </section>

      {/* ── How it works ────────────────────────────────────────── */}
      <section id="how-it-works" className="py-28 bg-gray-50 dark:bg-gray-950">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <span className="text-xs font-bold tracking-widest text-teal-600 uppercase">Process</span>
            <h2 className="mt-4 text-4xl font-bold text-gray-900 dark:text-white">How SafeType+ works</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {[
              {
                step: '01',
                title: 'Input',
                desc: 'Paste text or upload an image. Everything processes locally in your browser session — nothing is sent to external servers.',
              },
              {
                step: '02',
                title: 'Detect',
                desc: 'Dual-engine detection: regex patterns plus NLP named-entity recognition find PII and phishing signals simultaneously.',
              },
              {
                step: '03',
                title: 'Review',
                desc: 'A risk score, highlighted sensitive fields, and safer replacement suggestions are returned within seconds.',
              },
            ].map(s => (
              <div key={s.step} className="card-3d bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-8">
                <div className="step-num mb-4">{s.step}</div>
                <div className="text-base font-semibold text-gray-900 dark:text-white mb-3">{s.title}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">{s.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA Banner ──────────────────────────────────────────── */}
      <section className="bg-gray-900 dark:bg-black py-28 border-t border-gray-800">
        <div className="max-w-2xl mx-auto px-6 text-center">
          <span className="text-xs font-bold tracking-widest text-teal-500 uppercase">Get started</span>
          <h2 className="mt-5 text-4xl sm:text-5xl font-extrabold text-white leading-tight">
            Start protecting<br />your data today.
          </h2>
          <p className="mt-5 text-gray-400 text-base leading-relaxed">
            Free, open-source, no sign-up required.
          </p>
          <button
            onClick={onLaunch}
            className="mt-12 btn-3d px-10 py-4 bg-teal-600 text-white rounded text-base font-semibold"
          >
            Open SafeType+ →
          </button>
        </div>
      </section>

      {/* ── Footer ──────────────────────────────────────────────── */}
      <footer className="bg-gray-900 border-t border-gray-800 py-10">
        <div className="max-w-6xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <span className="text-base font-semibold text-white">SafeType+</span>
            <p className="text-xs text-gray-500 mt-1">Privacy-first · No data storage · Academic Project</p>
          </div>
          <div className="flex items-center gap-6 text-xs text-gray-500">
            <span>© 2026 SafeType+</span>
            <button onClick={onLaunch} className="hover:text-gray-300 transition-colors">
              Open App
            </button>
          </div>
        </div>
      </footer>

    </div>
  );
};

export default LandingPage;
