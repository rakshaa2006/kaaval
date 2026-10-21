import React from 'react';
import { ConsoleLayout } from '../components/layout/ConsoleLayout';
import { useGovernance } from '../context/GovernanceContext';
import { Link } from '../router/Router';
import { StatusBadge } from '../components/common/StatusBadge';
import {
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  FileCheck2,
  ArrowUpRight,
  PlusCircle,
  ExternalLink,
  ChevronRight,
  Terminal,
  Activity
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { tasks, sessions, incidents, auditLogs, activateScenario } = useGovernance();
  const backendAllowedActions = auditLogs.filter(
    (event) => event.source === 'api' && event.action === 'ACTION_ALLOWED',
  ).length;
  const backendBlockedActions = auditLogs.filter(
    (event) => event.source === 'api' && event.action.includes('BLOCK'),
  ).length;

  return (
    <ConsoleLayout breadcrumbs={[{ label: 'Dashboard' }]}>
      <div className="space-y-6">
        {/* Top Header & Fast Action */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-950">
              Autonomous Governance Console
            </h1>
            <p className="text-xs text-slate-500 mt-1">
            Live records are loaded from the local API; scenario cards below are mock previews.
            </p>
          </div>
          <Link
            href="/app/tasks/new"
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800 transition-colors shadow-xs shrink-0 self-start sm:self-auto"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Issue Task Passport</span>
          </Link>
        </div>

        {/* Core KPI Metrics Strip (Tabular Figures) */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-1">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-medium">Task Records</span>
              <FileCheck2 className="w-4 h-4 text-slate-500" />
            </div>
            <p className="text-2xl font-extrabold font-mono tabular-nums text-slate-900">
              {tasks.length}
            </p>
            <p className="text-[11px] text-slate-500">Backend records and mock previews</p>
          </div>

          <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-1">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-medium">Allowed Actions</span>
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
            </div>
            <p className="text-2xl font-extrabold font-mono tabular-nums text-emerald-700">
              {backendAllowedActions}
            </p>
            <p className="text-[11px] text-slate-500">Persisted backend decisions</p>
          </div>

          <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-1">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-medium">Blocked Violations</span>
              <ShieldAlert className="w-4 h-4 text-rose-600" />
            </div>
            <p className="text-2xl font-extrabold font-mono tabular-nums text-rose-700">
              {backendBlockedActions}
            </p>
            <p className="text-[11px] text-slate-500">Blocked by backend policy</p>
          </div>

          <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-1">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-medium">Quarantined Sessions</span>
              <AlertTriangle className="w-4 h-4 text-amber-600" />
            </div>
            <p className="text-2xl font-extrabold font-mono tabular-nums text-amber-800">
              {sessions.filter(s => s.status === 'quarantined').length}
            </p>
            <p className="text-[11px] text-slate-500">Mock and backend sessions</p>
          </div>
        </div>

        {/* 3 Core Security Demonstration Cards */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Demonstration Scenarios · Mock Previews
            </h2>
            <span className="text-[11px] text-slate-400">Click to inspect sample telemetry</span>
          </div>

          <div className="grid md:grid-cols-3 gap-4">
            {/* Scenario 1 Card */}
            <div
              onClick={() => activateScenario('clean-invoice')}
              className="group p-5 rounded-xl border border-slate-200 bg-white hover:border-emerald-500/60 transition-all cursor-pointer shadow-2xs hover:shadow-xs space-y-3"
            >
              <div className="flex items-center justify-between">
                <StatusBadge verdict="allowed" size="sm" />
                <ArrowUpRight className="w-4 h-4 text-slate-400 group-hover:text-emerald-600 transition-colors" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-sm group-hover:text-emerald-700 transition-colors">
                  1. Clean Invoice Read
                </h3>
                <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                  FinBot-Alpha calls whitelisted tool <code className="font-mono text-[11px] bg-slate-100 px-1 py-0.5 rounded">read_invoice_pdf</code>. Zero PII leaks, within bounds, execution permitted.
                </p>
              </div>
              <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500 font-mono">
                <span>Task: task-inv-01</span>
                <span className="text-emerald-700 font-semibold font-sans">Inspect Trace →</span>
              </div>
            </div>

            {/* Scenario 2 Card */}
            <div
              onClick={() => activateScenario('blocked-action')}
              className="group p-5 rounded-xl border border-slate-200 bg-white hover:border-rose-500/60 transition-all cursor-pointer shadow-2xs hover:shadow-xs space-y-3"
            >
              <div className="flex items-center justify-between">
                <StatusBadge verdict="blocked" size="sm" />
                <ArrowUpRight className="w-4 h-4 text-slate-400 group-hover:text-rose-600 transition-colors" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-sm group-hover:text-rose-700 transition-colors">
                  2. Unsafe Action Blocked
                </h3>
                <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                  SupportAgent attempts calling blacklisted tool <code className="font-mono text-[11px] bg-slate-100 px-1 py-0.5 rounded">export_customer_pii</code>. Dropped with zero egress.
                </p>
              </div>
              <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500 font-mono">
                <span>Incident: inc-402</span>
                <span className="text-rose-700 font-semibold font-sans">Inspect Incident →</span>
              </div>
            </div>

            {/* Scenario 3 Card */}
            <div
              onClick={() => activateScenario('sentinel-quarantine')}
              className="group p-5 rounded-xl border border-slate-200 bg-white hover:border-amber-500/60 transition-all cursor-pointer shadow-2xs hover:shadow-xs space-y-3"
            >
              <div className="flex items-center justify-between">
                <StatusBadge verdict="quarantined" size="sm" />
                <ArrowUpRight className="w-4 h-4 text-slate-400 group-hover:text-amber-600 transition-colors" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-sm group-hover:text-amber-800 transition-colors">
                  3. Sentinel Quarantine
                </h3>
                <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                  Untrusted invoice stream contained hidden prompt injection. Model context severed, agent moved to isolated container.
                </p>
              </div>
              <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500 font-mono">
                <span>Session: sess-sentinel-88</span>
                <span className="text-amber-800 font-semibold font-sans">Inspect Quarantine →</span>
              </div>
            </div>
          </div>
        </div>

        {/* Governed Tasks Table */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
          <div className="p-4 border-b border-slate-200 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-slate-900">Task and Passport Records</h2>
              <p className="text-xs text-slate-500">Backend-issued policies and demo fixtures</p>
            </div>
            <Link
              href="/app/audit"
              className="text-xs font-semibold text-slate-600 hover:text-slate-900 flex items-center gap-1 transition-colors"
            >
              <span>View Full Audit Ledger</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[11px]">
                <tr>
                  <th className="py-3 px-4">Task Name</th>
                  <th className="py-3 px-4">Agent Identifier</th>
                  <th className="py-3 px-4">Policy</th>
                  <th className="py-3 px-4">Allowed Tools</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {tasks.map((task) => (
                  <tr key={task.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-4">
                      <Link
                        href={`/app/tasks/${task.id}`}
                        className="font-bold text-slate-900 hover:text-emerald-700 transition-colors block"
                      >
                        {task.title}
                      </Link>
                      <span className="text-[11px] text-slate-400 font-mono">{task.id}</span>
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-700">
                      {task.agentName}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-500 text-[11px]">
                      {task.source === 'api' ? 'Backend policy' : `${task.passport?.policyHash.slice(0, 14) ?? 'No passport'}...`}
                    </td>
                    <td className="py-3 px-4 text-slate-600">
                      {task.source === 'api'
                        ? <span>Invoice policy · {task.backendStatus}</span>
                        : (
                          <>
                            <span>{task.passport?.allowedTools.length ?? 0} tools</span>
                            <span className="text-slate-400 ml-1">({task.passport?.allowedTools.slice(0, 2).join(', ')})</span>
                          </>
                        )}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge verdict={task.status} size="sm" />
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Link
                        href={`/app/tasks/${task.id}`}
                        className="font-semibold text-slate-700 hover:text-slate-950 inline-flex items-center gap-1"
                      >
                        <span>Review</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Live Monitored Sessions Stream */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
          <div className="p-4 border-b border-slate-200 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-slate-600" />
              <div>
                <h2 className="text-sm font-bold text-slate-900">Runtime Sessions Feed</h2>
                <p className="text-xs text-slate-500">Live agent tool executions inspected at gateway</p>
              </div>
            </div>
            <span className="text-[11px] font-mono text-slate-400 tabular-nums">
              {sessions.length} sessions recorded
            </span>
          </div>

          <div className="divide-y divide-slate-100">
            {sessions.map((sess) => (
              <div key={sess.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/60 transition-colors">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Link
                      href={`/app/sessions/${sess.id}`}
                      className="font-mono text-xs font-bold text-slate-900 hover:text-emerald-700 transition-colors"
                    >
                      {sess.id}
                    </Link>
                    <span className="text-slate-300">·</span>
                    <span className="text-xs text-slate-600 font-medium">{sess.agentName}</span>
                    <span className="text-slate-300">·</span>
                    <span className="text-[11px] text-slate-400 font-mono tabular-nums">{sess.source === 'api' ? sess.backendStatus : `${sess.steps.length} steps`}</span>
                  </div>
                  <p className="text-xs text-slate-500">
                    {sess.source === 'api' ? 'Backend session · no action submitted yet' : <>Latest tool: <code className="font-mono text-[11px] bg-slate-100 text-slate-800 px-1 py-0.5 rounded">{sess.steps[sess.steps.length - 1]?.tool}</code></>}
                  </p>
                </div>

                <div className="flex items-center gap-3 self-end sm:self-center">
                  <StatusBadge verdict={sess.verdict} size="sm" />
                  <Link
                    href={`/app/sessions/${sess.id}`}
                    className="text-xs font-semibold text-slate-700 hover:text-slate-950 px-2.5 py-1.5 rounded bg-slate-100 hover:bg-slate-200/70 transition-colors inline-flex items-center gap-1"
                  >
                    <span>Inspect</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </ConsoleLayout>
  );
};
