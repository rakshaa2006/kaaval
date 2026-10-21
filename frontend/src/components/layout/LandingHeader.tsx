import React from 'react';
import { Link } from '../../router/Router';
import { ShieldCheck } from 'lucide-react';

export const LandingHeader: React.FC = () => {
  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-8 px-6 py-3.5">
        {/* Zone 1: Single text element wordmark */}
        <Link href="/" className="flex items-center gap-2 text-lg font-bold tracking-tight text-slate-900 whitespace-nowrap shrink-0 hover:opacity-90 transition-opacity">
          <div className="w-8 h-8 rounded-lg bg-slate-900 text-white flex items-center justify-center shadow-xs">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
          </div>
          <span className="font-extrabold text-slate-950 tracking-tight text-xl">Kaaval</span>
        </Link>

        {/* Zone 2: 4-5 clean single-line text navigation links */}
        <nav className="hidden md:flex items-center gap-7 text-sm font-medium text-slate-600">
          <a href="#problem" className="hover:text-slate-900 transition-colors whitespace-nowrap shrink-0">Problem</a>
          <a href="#passports" className="hover:text-slate-900 transition-colors whitespace-nowrap shrink-0">Task Passports</a>
          <a href="#gateway" className="hover:text-slate-900 transition-colors whitespace-nowrap shrink-0">Enforcement Gateway</a>
          <a href="#sentinel" className="hover:text-slate-900 transition-colors whitespace-nowrap shrink-0">Sentinel Quarantine</a>
          <a href="#audit" className="hover:text-slate-900 transition-colors whitespace-nowrap shrink-0">Audit Ledger</a>
        </nav>

        {/* Zone 3: 1 primary action */}
        <div className="flex items-center gap-3 shrink-0">
          <Link
            href="/login"
            className="inline-flex items-center justify-center px-4 py-2 text-xs font-semibold text-white bg-slate-950 rounded-lg hover:bg-slate-800 transition-colors whitespace-nowrap shrink-0 shadow-xs active:scale-[0.98]"
          >
            Open Demo
          </Link>
        </div>
      </div>
    </header>
  );
};
