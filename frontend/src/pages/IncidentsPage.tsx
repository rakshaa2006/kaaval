import React from 'react';
import { ConsoleLayout } from '../components/layout/ConsoleLayout';
import { StatusBadge } from '../components/common/StatusBadge';
import { useGovernance } from '../context/GovernanceContext';
import { Link } from '../router/Router';

export const IncidentsPage: React.FC = () => {
  const { incidents, refreshDashboard, apiError } = useGovernance();
  const backendIncidents = incidents.filter((incident) => incident.source === 'api');

  return (
    <ConsoleLayout breadcrumbs={[{ label: 'Incidents' }]}>
      <div className="space-y-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-950">Incident review</h1>
            <p className="mt-1 text-sm text-slate-600">Backend incidents are persisted by the enforcement service. Sample scenarios are labeled separately.</p>
          </div>
          <button
            onClick={() => void refreshDashboard()}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-semibold text-slate-700"
          >
            Refresh
          </button>
        </div>
        {apiError && <p role="alert" className="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">{apiError}</p>}
        {backendIncidents.length === 0 ? (
          <div className="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-600">
            No backend incidents yet. From an active session, try the forbidden <code>send_email</code> or <code>delete_backup</code> action.
          </div>
        ) : (
          <div className="divide-y divide-slate-100 rounded-xl border border-slate-200 bg-white">
            {backendIncidents.map((incident) => (
              <Link
                key={incident.id}
                href={`/app/incidents/${incident.id}`}
                className="flex flex-wrap items-center justify-between gap-3 p-4 hover:bg-slate-50"
              >
                <div>
                  <p className="font-mono text-xs font-bold text-slate-900">{incident.id}</p>
                  <p className="mt-1 text-sm text-slate-700">{incident.summary}</p>
                  <p className="mt-1 text-[11px] text-slate-500">{new Date(incident.timestamp).toLocaleString()}</p>
                </div>
                <div className="flex items-center gap-3">
                  <StatusBadge verdict="blocked" size="sm" />
                  <span className="text-xs font-semibold text-slate-700">{incident.severity} · {incident.mitigationStatus}</span>
                </div>
              </Link>
            ))}
          </div>
        )}
        <details className="rounded-xl border border-slate-200 bg-white p-4">
          <summary className="cursor-pointer text-xs font-semibold text-slate-700">Show mock scenario incidents</summary>
          <ul className="mt-3 space-y-2">
            {incidents.filter((incident) => incident.source !== 'api').map((incident) => (
              <li key={incident.id}>
                <Link className="text-xs text-slate-600 underline" href={`/app/incidents/${incident.id}`}>
                  {incident.id} — {incident.title}
                </Link>
              </li>
            ))}
          </ul>
        </details>
      </div>
    </ConsoleLayout>
  );
};
