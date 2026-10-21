import React, { useState } from 'react';
import { ConsoleLayout } from '../components/layout/ConsoleLayout';
import { useGovernance } from '../context/GovernanceContext';
import { useRouter, Link } from '../router/Router';
import { StatusBadge } from '../components/common/StatusBadge';
import { CodeViewer } from '../components/common/CodeViewer';
import {
  Terminal,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  Clock,
  Cpu,
  Layers,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Lock,
  ArrowRight
} from 'lucide-react';

export const SessionMonitorPage: React.FC = () => {
  const { params, navigate } = useRouter();
  const { sessions, tasks } = useGovernance();

  const sessionId = params.id || 'sess-inv-clean';
  const session = sessions.find(s => s.id === sessionId) || sessions[0];
  const task = tasks.find(t => t.id === session.taskId);

  const [expandedSteps, setExpandedSteps] = useState<Record<number, boolean>>({ 1: true, 2: true, 3: true });

  const toggleStep = (stepIdx: number) => {
    setExpandedSteps(prev => ({ ...prev, [stepIdx]: !prev[stepIdx] }));
  };

  return (
    <ConsoleLayout
      breadcrumbs={[
        { label: 'Sessions', href: '/app' },
        { label: session.id }
      ]}
    >
      <div className="space-y-6">
        {/* Session Top Bar & Quick Switcher */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-2xs">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <span className="font-mono text-xs font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                {session.id}
              </span>
              <StatusBadge verdict={session.verdict} />
              <span className="text-xs text-slate-400">·</span>
              <span className="text-xs text-slate-500 font-mono">Agent: {session.agentName}</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-950">
              Runtime Session Trace Monitor
            </h1>
            <p className="text-xs text-slate-600">
              {task ? `Governed Task: ${task.title} (${task.id})` : 'Autonomous Agent Session'}
            </p>
          </div>

          {/* Quick Session Picker */}
          <div className="flex items-center gap-2 self-start sm:self-center">
            <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider hidden lg:inline">
              Session:
            </label>
            <select
              value={session.id}
              onChange={(e) => navigate(`/app/sessions/${e.target.value}`)}
              className="text-xs px-3 py-1.5 rounded-lg border border-slate-300 bg-white font-mono font-medium focus:border-slate-900 focus:outline-hidden"
            >
              {sessions.map(s => (
                <option key={s.id} value={s.id}>
                  {s.id} ({s.agentName} - {s.verdict.toUpperCase()})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Sentinel Quarantine Banner (If Quarantined) */}
        {session.quarantineMetadata && (
          <div className="p-6 rounded-xl border border-amber-300 bg-amber-50/80 shadow-xs space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-9 h-9 rounded-lg bg-amber-500 text-slate-950 flex items-center justify-center shrink-0">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h2 className="text-sm font-bold uppercase tracking-wider text-amber-950">
                    Sentinel Core v3.1 Quarantine Triggered
                  </h2>
                  <span className="text-[10px] bg-amber-200 text-amber-950 font-bold px-2 py-0.5 rounded font-mono">
                    SANDBOX ISOLATED
                  </span>
                </div>
                <p className="text-xs text-amber-900 leading-relaxed font-medium">
                  {session.quarantineMetadata.explanation}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-3 border-t border-amber-200 text-xs">
              <div>
                <span className="text-[11px] text-amber-800">Trigger Timestamp:</span>
                <p className="font-mono font-bold text-amber-950 tabular-nums">
                  {new Date(session.quarantineMetadata.triggeredAt).toLocaleTimeString()}
                </p>
              </div>
              <div>
                <span className="text-[11px] text-amber-800">Threat Category:</span>
                <p className="font-mono font-bold text-amber-950">
                  {session.quarantineMetadata.threatCategory}
                </p>
              </div>
              <div>
                <span className="text-[11px] text-amber-800">Isolated Sandbox Node:</span>
                <p className="font-mono font-bold text-amber-950">
                  {session.quarantineMetadata.isolatedSandboxId}
                </p>
              </div>
              <div>
                <span className="text-[11px] text-amber-800">Forensics Dump:</span>
                <p className="font-mono font-bold text-amber-950 truncate">
                  {session.quarantineMetadata.forensicDumpRef}
                </p>
              </div>
            </div>

            <div className="pt-1 flex items-center justify-between">
              <span className="text-[11px] text-amber-800 italic">
                Agent execution thread was terminated immediately to prevent downstream tool execution.
              </span>
              <Link
                href="/app/incidents/inc-403"
                className="inline-flex items-center gap-1.5 text-xs font-bold text-amber-950 hover:underline"
              >
                <span>View Incident Forensics inc-403</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        )}

        {/* Clean Invoice Banner (If Clean Allowed) */}
        {session.id === 'sess-inv-clean' && (
          <div className="p-5 rounded-xl border border-emerald-200 bg-emerald-50/70 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center shrink-0">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs font-bold text-emerald-950 uppercase tracking-wider">
                  Zero Boundary Violations · Execution Completed Safely
                </p>
                <p className="text-xs text-emerald-800 mt-0.5">
                  All 3 tool invocations matched Task Passport pass-0x98b42f1a. 0 PII leaks found. Ledger entry posted.
                </p>
              </div>
            </div>
            <Link
              href="/app/tasks/task-inv-01"
              className="text-xs font-semibold text-emerald-900 bg-white border border-emerald-300 px-3 py-1.5 rounded-lg hover:bg-emerald-50 transition-colors shrink-0"
            >
              Review Task Passport
            </Link>
          </div>
        )}

        {/* Blocked Session Banner (If Blocked) */}
        {session.id === 'sess-blocked-402' && (
          <div className="p-5 rounded-xl border border-rose-200 bg-rose-50/70 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-rose-600 text-white flex items-center justify-center shrink-0">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs font-bold text-rose-950 uppercase tracking-wider">
                  Tool Execution Intercepted &amp; Dropped at Gateway
                </p>
                <p className="text-xs text-rose-800 mt-0.5">
                  Step 2 attempted to invoke prohibited tool <code className="font-mono bg-rose-100 px-1 rounded">export_customer_pii</code>. Blocked before network egress.
                </p>
              </div>
            </div>
            <Link
              href="/app/incidents/inc-402"
              className="text-xs font-semibold text-rose-900 bg-white border border-rose-300 px-3 py-1.5 rounded-lg hover:bg-rose-50 transition-colors shrink-0"
            >
              Open Incident Report
            </Link>
          </div>
        )}

        {/* Step-by-Step Execution Trace */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Execution Trace · Step-by-Step Gateway Intercepts
            </h2>
            <span className="text-xs text-slate-400 font-mono">
              Total Steps: {session.steps.length}
            </span>
          </div>

          <div className="space-y-4">
            {session.steps.map((step) => {
              const isExpanded = !!expandedSteps[step.stepIndex];
              const isBlocked = step.verdict === 'blocked';
              const isQuarantined = step.verdict === 'quarantined';
              const isAllowed = step.verdict === 'allowed';

              return (
                <div
                  key={step.stepIndex}
                  className={`bg-white rounded-xl border transition-all overflow-hidden ${
                    isBlocked
                      ? 'border-rose-300 shadow-2xs'
                      : isQuarantined
                      ? 'border-amber-300 shadow-2xs'
                      : 'border-slate-200 shadow-2xs'
                  }`}
                >
                  {/* Step Header */}
                  <div
                    onClick={() => toggleStep(step.stepIndex)}
                    className="p-4 bg-slate-50/70 border-b border-slate-100 flex items-center justify-between gap-3 cursor-pointer hover:bg-slate-100/60 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <span className="w-6 h-6 rounded-md bg-slate-900 text-white font-mono text-xs font-bold flex items-center justify-center">
                        {step.stepIndex}
                      </span>
                      <div>
                        <p className="text-xs font-mono font-bold text-slate-900">
                          {step.tool}()
                        </p>
                        <p className="text-[11px] text-slate-500 font-mono">
                          {new Date(step.timestamp).toLocaleTimeString()} · Latency: {step.latencyMs}ms
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <StatusBadge verdict={step.verdict} size="sm" />
                      {isExpanded ? (
                        <ChevronUp className="w-4 h-4 text-slate-400" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-slate-400" />
                      )}
                    </div>
                  </div>

                  {/* Step Details Body */}
                  {isExpanded && (
                    <div className="p-5 space-y-4">
                      {/* Privacy & Inspection Verdict Bar */}
                      <div className="grid sm:grid-cols-3 gap-3 p-3 rounded-lg bg-slate-50 border border-slate-200/80 text-xs">
                        <div>
                          <span className="text-[11px] text-slate-500">Privacy Inspection:</span>
                          <p className="font-semibold text-slate-900 mt-0.5">
                            {step.inspection.piiDetected ? (
                              <span className="text-rose-700">PII Leaks Detected</span>
                            ) : (
                              <span className="text-emerald-700">0 Leaks · Clean</span>
                            )}
                          </p>
                        </div>

                        <div>
                          <span className="text-[11px] text-slate-500">Injection Risk Score:</span>
                          <p className="font-mono font-bold mt-0.5">
                            <span className={step.inspection.injectionDetected ? 'text-amber-700' : 'text-slate-900'}>
                              {step.inspection.injectionScore} / 1.00
                            </span>
                            {step.inspection.injectionDetected && (
                              <span className="text-[10px] text-amber-800 ml-1.5 uppercase font-sans font-bold">
                                Hostile
                              </span>
                            )}
                          </p>
                        </div>

                        <div>
                          <span className="text-[11px] text-slate-500">Policy Rule Applied:</span>
                          <p className="font-mono text-slate-800 mt-0.5 truncate text-[11px]">
                            {step.policyRuleApplied}
                          </p>
                        </div>
                      </div>

                      {/* Tool Arguments Input Payload */}
                      <div>
                        <p className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">
                          Tool Input Arguments (Intercepted by Gateway)
                        </p>
                        <CodeViewer
                          code={JSON.stringify(step.inputPayload, null, 2)}
                          title={`Arguments: ${step.tool}`}
                        />
                      </div>

                      {/* Execution Output or Intercept Message */}
                      <div>
                        <p className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">
                          Gateway Verdict &amp; Output
                        </p>
                        {typeof step.outputPayload === 'string' ? (
                          <div
                            className={`p-3 rounded-lg font-mono text-xs leading-relaxed ${
                              isBlocked
                                ? 'bg-rose-50 text-rose-900 border border-rose-200'
                                : isQuarantined
                                ? 'bg-amber-50 text-amber-950 border border-amber-200'
                                : 'bg-slate-100 text-slate-800 border border-slate-200'
                            }`}
                          >
                            {step.outputPayload}
                          </div>
                        ) : (
                          <CodeViewer
                            code={JSON.stringify(step.outputPayload, null, 2)}
                            title="Validated Return Payload"
                          />
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </ConsoleLayout>
  );
};
