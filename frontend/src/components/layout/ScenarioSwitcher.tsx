import React from 'react';
import { useGovernance } from '../../context/GovernanceContext';
import { useRouter } from '../../router/Router';
import { CheckCircle2, ShieldAlert, AlertTriangle, RotateCcw, Terminal } from 'lucide-react';

export const ScenarioSwitcher: React.FC = () => {
  const { activeScenario, activateScenario, resetDemoData } = useGovernance();
  const { path } = useRouter();

  return (
    <div className="bg-[#0B1120] text-slate-100 border-b border-slate-800/80 px-4 py-2 shadow-inner">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-slate-900 border border-slate-700/70 text-[10px] font-mono text-slate-300">
            <Terminal className="w-3 h-3 text-emerald-400" />
            <span>HARNESS</span>
          </div>
          <span className="hidden sm:inline text-xs text-slate-400 font-medium">
            Test Runtime Outlier &amp; Policy Bounds:
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => activateScenario('clean-invoice')}
            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded text-xs font-mono transition-all ${
              activeScenario === 'clean-invoice' && path.includes('sess-inv-clean')
                ? 'bg-emerald-500 text-slate-950 font-bold shadow-xs'
                : 'bg-slate-900/90 text-emerald-400 hover:bg-slate-800 hover:text-emerald-300 border border-emerald-900/50'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>1. Clean Invoice (Allowed)</span>
          </button>

          <button
            onClick={() => activateScenario('blocked-action')}
            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded text-xs font-mono transition-all ${
              activeScenario === 'blocked-action' && path.includes('inc-402')
                ? 'bg-rose-600 text-white font-bold shadow-xs'
                : 'bg-slate-900/90 text-rose-400 hover:bg-slate-800 hover:text-rose-300 border border-rose-900/50'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>2. Egress (Blocked)</span>
          </button>

          <button
            onClick={() => activateScenario('sentinel-quarantine')}
            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded text-xs font-mono transition-all ${
              activeScenario === 'sentinel-quarantine' && path.includes('sess-sentinel-88')
                ? 'bg-amber-500 text-slate-950 font-bold shadow-xs'
                : 'bg-slate-900/90 text-amber-400 hover:bg-slate-800 hover:text-amber-300 border border-amber-900/50'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>3. Injection (Quarantined)</span>
          </button>

          <button
            onClick={resetDemoData}
            title="Reset scenario data to default state"
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-mono text-slate-400 hover:text-slate-200 bg-slate-900/60 hover:bg-slate-800 border border-slate-700/50 transition-colors ml-1"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Reset</span>
          </button>
        </div>
      </div>
    </div>
  );
};
