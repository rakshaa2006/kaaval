import React, { ReactNode } from 'react';
import { Link, useRouter } from '../../router/Router';
import { useGovernance } from '../../context/GovernanceContext';
import { ScenarioSwitcher } from './ScenarioSwitcher';
import {
  LayoutDashboard,
  PlusCircle,
  FileCheck2,
  Terminal,
  ShieldAlert,
  History,
  LogOut,
  ExternalLink,
  ShieldCheck,
  Info
} from 'lucide-react';

interface ConsoleLayoutProps {
  children: ReactNode;
  title?: string;
  breadcrumbs?: { label: string; href?: string }[];
}

export const ConsoleLayout: React.FC<ConsoleLayoutProps> = ({ children, breadcrumbs = [] }) => {
  const { path, navigate } = useRouter();
  const { currentUser, logout, apiError } = useGovernance();

  const navItems = [
    { label: 'Console Overview', href: '/app', icon: LayoutDashboard },
    { label: 'Issue Task Passport', href: '/app/tasks/new', icon: PlusCircle },
    { label: 'Passport Review', href: '/app/tasks/task-inv-01', icon: FileCheck2 },
    { label: 'Session Monitor', href: '/app/sessions/sess-inv-clean', icon: Terminal },
    { label: 'Incidents', href: '/app/incidents', icon: ShieldAlert },
    { label: 'Audit Timeline', href: '/app/audit', icon: History },
  ];

  const isCurrentActive = (href: string) => {
    if (href === '/app') {
      return path === '/app';
    }
    if (href === '/app/tasks/new') {
      return path === '/app/tasks/new';
    }
    if (href.startsWith('/app/tasks/')) {
      return path.startsWith('/app/tasks/') && path !== '/app/tasks/new';
    }
    if (href.startsWith('/app/sessions/')) {
      return path.startsWith('/app/sessions/');
    }
    if (href.startsWith('/app/incidents/')) {
      return path.startsWith('/app/incidents/');
    }
    return path === href;
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      {/* 1. Interactive Scenario Switcher Bar */}
      <ScenarioSwitcher />

      {/* 2. Top Header Bar with Breadcrumbs & Profile */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 px-6 py-3 flex items-center justify-between gap-4">
        {/* Left: Brand & Breadcrumbs */}
        <div className="flex items-center gap-4">
          <Link href="/app" className="flex items-center gap-2 text-slate-900 font-extrabold text-base tracking-tight shrink-0">
            <div className="w-7 h-7 rounded-md bg-slate-900 text-emerald-400 flex items-center justify-center">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <span>Kaaval Console</span>
          </Link>

          <span className="text-slate-300">/</span>

          <nav className="flex items-center gap-2 text-xs font-medium text-slate-500" aria-label="Breadcrumb">
            <Link href="/app" className="hover:text-slate-900 transition-colors">Home</Link>
            {breadcrumbs.map((crumb, idx) => (
              <React.Fragment key={idx}>
                <span className="text-slate-300">/</span>
                {crumb.href ? (
                  <Link href={crumb.href} className="hover:text-slate-900 transition-colors">
                    {crumb.label}
                  </Link>
                ) : (
                  <span className="text-slate-900 font-semibold">{crumb.label}</span>
                )}
              </React.Fragment>
            ))}
          </nav>
        </div>

        {/* Right: User Profile & Public Site link */}
        <div className="flex items-center gap-4 shrink-0">
          <Link
            href="/"
            className="hidden sm:inline-flex items-center gap-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 transition-colors"
          >
            <span>Landing Page</span>
            <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
          </Link>

          <div className="h-4 w-px bg-slate-200 hidden sm:block" />

          {currentUser ? (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-bold font-mono">
                  {currentUser.initials}
                </div>
                <div className="hidden md:block text-left">
                  <p className="text-xs font-semibold text-slate-900 leading-tight">{currentUser.name}</p>
                  <p className="text-[11px] text-slate-500 leading-tight">{currentUser.role}</p>
                </div>
              </div>
              <button
                onClick={logout}
                title="Sign out"
                className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-md transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={() => navigate('/login')}
              className="px-3 py-1 text-xs font-medium bg-slate-900 text-white rounded-md hover:bg-slate-800"
            >
              Sign In
            </button>
          )}
        </div>
      </header>

      {/* 3. Main Body: Sidebar + Viewport */}
      <div className="flex-1 flex max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 gap-6">
        {/* Sidebar Nav */}
        <aside className="w-60 shrink-0 hidden md:block">
          <div className="sticky top-20 space-y-6">
            <div>
              <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 px-3 mb-2">
                Governance & Control
              </p>
              <nav className="space-y-1">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const active = isCurrentActive(item.href);
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={`flex items-center gap-3 px-3 py-2 text-xs font-medium rounded-lg transition-colors ${
                        active
                          ? 'bg-slate-900 text-white font-semibold shadow-xs'
                          : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                      }`}
                    >
                      <Icon className={`w-4 h-4 ${active ? 'text-emerald-400' : 'text-slate-400'}`} />
                      <span>{item.label}</span>
                    </Link>
                  );
                })}
              </nav>
            </div>

            {/* Quick Helper Card */}
            <div className="p-3.5 rounded-lg border border-slate-200 bg-white shadow-2xs space-y-2">
              <div className="flex items-center gap-2 text-slate-900 font-semibold text-xs">
                <Info className="w-3.5 h-3.5 text-sky-600" />
                <span>Runtime Assurance</span>
              </div>
              <p className="text-[11px] text-slate-600 leading-relaxed">
                Task Passports enforce capability bounds before tools execute. Malicious actions are dropped at the gateway.
              </p>
            </div>
          </div>
        </aside>

        {/* Viewport Content */}
        <main className="flex-1 min-w-0">
          {apiError && (
            <div role="alert" className="mb-4 flex items-start justify-between gap-3 rounded-lg border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800">
              <span>{apiError}</span>
            </div>
          )}
          {children}
        </main>
      </div>

      {/* 4. Footer with Synthetic-Demo Disclaimer */}
      <footer className="mt-auto border-t border-slate-200 bg-white py-4 px-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-[11px]">
            <span className="font-semibold text-slate-700">Kaaval Defense Systems</span>
            <span>·</span>
            <span>Deterministic AI Governance</span>
            <span>·</span>
            <span className="text-amber-700 bg-amber-50 border border-amber-200/80 px-2 py-0.5 rounded text-[10px] font-medium">
              Synthetic Demo Environment
            </span>
          </div>
          <p className="text-[11px] text-slate-400">
            Synthetic local demo · backend policy and action decisions are authoritative.
          </p>
        </div>
      </footer>
    </div>
  );
};
