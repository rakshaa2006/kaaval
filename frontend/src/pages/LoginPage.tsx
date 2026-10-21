import React, { useState } from 'react';
import { Link, useRouter } from '../router/Router';
import { useGovernance } from '../context/GovernanceContext';
import { MOCK_USERS } from '../data/mockData';
import { ShieldCheck, ArrowRight, UserCheck, Lock } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const { login } = useGovernance();
  const { navigate } = useRouter();
  const [selectedUser, setSelectedUser] = useState(MOCK_USERS[0]);
  const [loading, setLoading] = useState(false);

  const handleSignIn = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      login(selectedUser);
    }, 300);
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
          Sign in to Defense Console
        </h2>
        <p className="text-xs text-slate-500">
          Choose a pre-configured enterprise role to test governance capabilities.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4">
        <div className="bg-white py-8 px-6 shadow-sm border border-slate-200 rounded-xl space-y-6">
          <form onSubmit={handleSignIn} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                Select Demo Role &amp; Identity
              </label>
              <div className="space-y-2">
                {MOCK_USERS.map((user) => {
                  const isSelected = selectedUser.id === user.id;
                  return (
                    <button
                      type="button"
                      key={user.id}
                      onClick={() => setSelectedUser(user)}
                      className={`w-full text-left p-3 rounded-lg border transition-all flex items-center justify-between ${
                        isSelected
                          ? 'border-slate-900 bg-slate-900 text-white shadow-xs'
                          : 'border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-900'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold font-mono ${
                            isSelected ? 'bg-slate-800 text-emerald-400' : 'bg-slate-200 text-slate-700'
                          }`}
                        >
                          {user.initials}
                        </div>
                        <div>
                          <p className={`text-xs font-bold ${isSelected ? 'text-white' : 'text-slate-900'}`}>
                            {user.name}
                          </p>
                          <p className={`text-[11px] ${isSelected ? 'text-slate-300' : 'text-slate-500'}`}>
                            {user.role}
                          </p>
                        </div>
                      </div>
                      {isSelected && <UserCheck className="w-4 h-4 text-emerald-400" />}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80 text-[11px] text-slate-600 space-y-1">
              <div className="flex items-center gap-1.5 font-semibold text-slate-700">
                <Lock className="w-3.5 h-3.5 text-slate-500" />
                <span>Simulated Zero-Trust Session</span>
              </div>
              <p>
                No real credentials required. Instant entry into mock governance environment.
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg text-xs font-bold text-white bg-slate-950 hover:bg-slate-800 transition-colors shadow-xs active:scale-[0.99] disabled:opacity-50"
            >
              <span>{loading ? 'Authenticating...' : 'Enter Defense Console'}</span>
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
