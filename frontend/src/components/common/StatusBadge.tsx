import React from 'react';
import { Verdict } from '../../types/governance';

interface StatusBadgeProps {
  verdict: Verdict | 'completed' | 'active' | 'halted';
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ verdict, size = 'md' }) => {
  const isSm = size === 'sm';

  switch (verdict) {
    case 'allowed':
    case 'completed':
      return (
        <span
          className={`inline-flex items-center gap-1.5 font-mono font-medium rounded bg-emerald-50 text-emerald-900 border border-emerald-300/80 ${
            isSm ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-0.5 text-xs'
          }`}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 shrink-0" aria-hidden="true" />
          <span className="tracking-wide uppercase font-semibold">Allowed</span>
        </span>
      );
    case 'blocked':
    case 'halted':
      return (
        <span
          className={`inline-flex items-center gap-1.5 font-mono font-medium rounded bg-rose-50 text-rose-900 border border-rose-300/80 ${
            isSm ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-0.5 text-xs'
          }`}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-rose-600 shrink-0" aria-hidden="true" />
          <span className="tracking-wide uppercase font-semibold">Blocked</span>
        </span>
      );
    case 'quarantined':
      return (
        <span
          className={`inline-flex items-center gap-1.5 font-mono font-medium rounded bg-amber-50 text-amber-950 border border-amber-300/80 ${
            isSm ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-0.5 text-xs'
          }`}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-amber-600 shrink-0" aria-hidden="true" />
          <span className="tracking-wide uppercase font-semibold">Quarantined</span>
        </span>
      );
    case 'active':
      return (
        <span
          className={`inline-flex items-center gap-1.5 font-mono font-medium rounded bg-blue-50 text-blue-900 border border-blue-300/80 ${
            isSm ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-0.5 text-xs'
          }`}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0" aria-hidden="true" />
          <span className="tracking-wide uppercase font-semibold">Active</span>
        </span>
      );
    default:
      return (
        <span
          className={`inline-flex items-center gap-1.5 font-mono font-medium rounded bg-slate-100 text-slate-800 border border-slate-300 ${
            isSm ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-0.5 text-xs'
          }`}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-slate-500 shrink-0" aria-hidden="true" />
          <span className="tracking-wide uppercase font-semibold">Pending</span>
        </span>
      );
  }
};
