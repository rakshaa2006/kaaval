import React, { useState } from 'react';
import { Link } from '../router/Router';
import { useGovernance } from '../context/GovernanceContext';
import { ShieldCheck, ArrowRight, Lock } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const { login, apiError, clearApiError } = useGovernance();
  const [loading, setLoading] = useState(false);

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    clearApiError();
    setLoading(true);
    try {
      await login();
    } catch {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center space-y-3">
        <Link href="/" className="inline-flex items-center gap-2 text-2xl font-extrabold text-slate-950 tracking-tight">
          <div className="w-9 h-9 rounded-lg bg-slate-900 text-emerald-400 flex items-center justify-center shadow-xs">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <span>Kaaval</span>
        </Link>
        <h2 className="text-xl font-bold tracking-tight text-slate-900">
          Enter the Defense Console
        </h2>
        <p className="text-xs text-slate-500">
          Sign in with the seeded local synthetic demo owner account.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4">
        <div className="bg-white py-8 px-6 shadow-sm border border-slate-200 rounded-xl space-y-6">
          <form onSubmit={handleSignIn} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                Demo identity
              </label>
              <div className="p-3 rounded-lg border border-slate-200 bg-slate-50">
                <p className="text-xs font-bold text-slate-900">owner@example.test</p>
                <p className="text-[11px] text-slate-500 mt-1">Owner administrator · local synthetic demo</p>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80 text-[11px] text-slate-600 space-y-1">
              <div className="flex items-center gap-1.5 font-semibold text-slate-700">
                <Lock className="w-3.5 h-3.5 text-slate-500" />
                <span>Simulated Zero-Trust Session</span>
              </div>
              <p>
                The backend sets an HttpOnly session cookie. Demo login is available only in the local synthetic environment.
              </p>
            </div>

            {apiError && (
              <p role="alert" className="text-xs text-rose-700 bg-rose-50 border border-rose-200 rounded-lg p-3">
                {apiError}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg text-xs font-bold text-white bg-slate-950 hover:bg-slate-800 transition-colors shadow-xs active:scale-[0.99] disabled:opacity-50"
            >
              <span>{loading ? 'Connecting to Kaaval API...' : 'Open Demo Console'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          <div className="pt-4 border-t border-slate-100 text-center">
            <Link href="/" className="text-xs font-medium text-slate-600 hover:text-slate-900 transition-colors">
              ← Return to Public Landing Page
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
