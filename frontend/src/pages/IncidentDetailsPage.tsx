import React from 'react';
import { ConsoleLayout } from '../components/layout/ConsoleLayout';
import { useGovernance } from '../context/GovernanceContext';
import { useRouter, Link } from '../router/Router';
import { CodeViewer } from '../components/common/CodeViewer';
import {
  ShieldAlert,
  AlertTriangle,
  Terminal,
  Lock,
  ArrowRight,
  CheckCircle2,
  Calendar,
  Layers,
  FileText
} from 'lucide-react';

export const IncidentDetailsPage: React.FC = () => {
  const { params, navigate } = useRouter();
  const { incidents } = useGovernance();

  const incidentId = params.id || 'inc-402';
  const incident = incidents.find(i => i.id === incidentId) || incidents[0];

  const isCritical = incident.severity === 'critical';

  return (
    <ConsoleLayout
      breadcrumbs={[
        { label: 'Incidents', href: '/app' },
        { label: incident.id }
      ]}
    >
      <div className="space-y-6">
        {/* Top Header Card */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-2xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <span className="font-mono text-xs font-bold text-slate-500 bg-slate-100 px-2.5 py-1 rounded">
                {incident.id}
              </span>
              <span
                className={`text-xs font-bold uppercase tracking-wider px-2.5 py-1 rounded border ${
                  isCritical
                    ? 'bg-rose-50 text-rose-800 border-rose-200'
                    : 'bg-amber-50 text-amber-800 border-amber-200'
                }`}
              >
                Severity: {incident.severity}
              </span>
              <span className="text-xs font-semibold uppercase tracking-wider px-2.5 py-1 rounded bg-slate-100 text-slate-700">
                Status: {incident.mitigationStatus}
              </span>
            </div>

            {/* Quick Switcher */}
            <div className="flex items-center gap-2">
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Select Incident:
              </label>
              <select
                value={incident.id}
                onChange={(e) => navigate(`/app/incidents/${e.target.value}`)}
                className="text-xs px-3 py-1.5 rounded-lg border border-slate-300 bg-white font-mono font-medium focus:border-slate-900 focus:outline-hidden"
              >
                {incidents.map(inc => (
                  <option key={inc.id} value={inc.id}>
                    {inc.id} ({inc.threatType})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-950">
              {incident.title}
            </h1>
            <p className="text-xs text-slate-600 mt-1 max-w-3xl leading-relaxed">
              {incident.summary}
            </p>
          </div>

          <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center gap-6 text-xs text-slate-500">
            <div className="flex items-center gap-1.5 font-mono">
              <span className="text-slate-400">Timestamp:</span>
              <span className="text-slate-900 font-medium tabular-nums">{new Date(incident.timestamp).toUTCString()}</span>
            </div>
            <div className="flex items-center gap-1.5 font-mono">
              <span className="text-slate-400">Origin Session:</span>
              <Link href={`/app/sessions/${incident.sessionId}`} className="text-slate-900 hover:text-emerald-700 font-bold underline">
                {incident.sessionId}
              </Link>
            </div>
            <div className="flex items-center gap-1.5 font-mono">
              <span className="text-slate-400">Agent:</span>
              <span className="text-slate-900 font-medium">{incident.agentId}</span>
            </div>
          </div>
        </div>

        {/* Threat Forensics Card */}
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl border border-slate-200 shadow-2xs p-5 space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
              <ShieldAlert className="w-4 h-4 text-rose-600" />
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Threat Classification &amp; Target
              </h2>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-[11px] text-slate-500">Threat Type:</span>
                <p className="font-mono font-bold text-slate-900 mt-0.5">{incident.threatType}</p>
              </div>

              <div className="pt-2 border-t border-slate-100">
                <span className="text-[11px] text-slate-500">Policy Rule Breached:</span>
                <p className="font-mono font-bold text-rose-700 mt-0.5">{incident.ruleBreached}</p>
              </div>

              <div className="pt-2 border-t border-slate-100">
                <span className="text-[11px] text-slate-500">Intercepted Destination / Sandbox:</span>
                <p className="font-mono font-semibold text-slate-900 mt-0.5 bg-slate-50 p-2 rounded border border-slate-200">
                  {incident.blockedTarget}
                </p>
              </div>
            </div>
          </div>

          {/* Mitigation Actions Taken */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-2xs p-5 space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
              <Lock className="w-4 h-4 text-emerald-600" />
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Automated Containment Actions Taken
              </h2>
            </div>

            <div className="space-y-2.5">
              {incident.remediationSteps.map((step, idx) => (
                <div key={idx} className="flex items-start gap-2.5 text-xs text-slate-700">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                  <span>{step}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Intercepted Payload Sample */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              {incident.source === 'api' ? 'Action Payload' : 'Forensic Evidence: Sample Payload'}
            </h2>
            <span className="text-[11px] font-mono text-slate-400">
              {incident.source === 'api' ? 'Raw payload is not exposed by the backend' : 'Mock scenario sample'}
            </span>
          </div>
          <CodeViewer code={incident.rawPayloadSample} language="text" title={`Incident Forensics Dump (${incident.id})`} />
        </div>

        {/* Action Link to Session or Audit */}
        <div className="flex items-center justify-between p-4 bg-slate-100 rounded-xl border border-slate-200 text-xs">
          <span className="text-slate-600">
            Review the backend incident and containment events in the audit timeline.
          </span>
          <Link
            href="/app/audit"
            className="inline-flex items-center gap-1.5 font-bold text-slate-900 hover:text-emerald-700 transition-colors"
          >
            <span>Inspect Audit Timeline</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </ConsoleLayout>
  );
};
