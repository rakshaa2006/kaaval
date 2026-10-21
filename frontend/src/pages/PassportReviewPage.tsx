import React, { useCallback, useEffect, useState } from 'react';
import { ConsoleLayout } from '../components/layout/ConsoleLayout';
import { useGovernance } from '../context/GovernanceContext';
import { useRouter, Link } from '../router/Router';
import { StatusBadge } from '../components/common/StatusBadge';
import { CodeViewer } from '../components/common/CodeViewer';
import { api, ApiPassport, ApiTask } from '../api/client';
import { MOCK_TASKS } from '../data/mockData';
import {
  FileCheck2,
  ShieldCheck,
  Lock,
  Terminal,
  ExternalLink,
  CheckCircle2,
  AlertOctagon,
  Copy,
  Check,
  Calendar,
  Layers
} from 'lucide-react';

export const PassportReviewPage: React.FC = () => {
  const { params } = useRouter();
  const taskId = params.id || '';
  if (MOCK_TASKS.some((task) => task.id === taskId)) {
    return <MockPassportReview />;
  }
  return <BackendPassportReview taskId={taskId} />;
};

const BackendPassportReview: React.FC<{ taskId: string }> = ({ taskId }) => {
  const { createSession } = useGovernance();
  const { navigate } = useRouter();
  const [task, setTask] = useState<ApiTask | null>(null);
  const [passport, setPassport] = useState<ApiPassport | null>(null);
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [loadedTask, loadedPassport] = await Promise.all([
        api.getTask(taskId),
        api.getPassport(taskId),
      ]);
      setTask(loadedTask);
      setPassport(loadedPassport);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Unable to load the task passport.');
    } finally {
      setLoading(false);
    }
  }, [taskId]);

  useEffect(() => {
    void load();
  }, [load]);

  const handleActivate = async () => {
    setWorking(true);
    setError(null);
    try {
      setPassport(await api.activatePassport(taskId));
      setTask(await api.getTask(taskId));
    } catch (actionError) {
      setError(actionError instanceof Error ? actionError.message : 'Unable to activate the passport.');
    } finally {
      setWorking(false);
    }
  };

  const handleStartSession = async () => {
    setWorking(true);
    setError(null);
    try {
      const session = await createSession(taskId);
      navigate(`/app/sessions/${session.id}`);
    } catch (actionError) {
      setError(actionError instanceof Error ? actionError.message : 'Unable to start the session.');
    } finally {
      setWorking(false);
    }
  };

  if (loading) {
    return (
      <ConsoleLayout breadcrumbs={[{ label: 'Tasks', href: '/app' }, { label: 'Loading Passport' }]}>
        <p role="status" className="text-sm text-slate-600">Loading task and Passport from the backend...</p>
      </ConsoleLayout>
    );
  }
  if (error || !task || !passport) {
    return (
      <ConsoleLayout breadcrumbs={[{ label: 'Tasks', href: '/app' }, { label: 'Passport unavailable' }]}>
        <div className="max-w-2xl space-y-4 rounded-xl border border-rose-200 bg-white p-6">
          <p role="alert" className="text-sm text-rose-700">{error || 'Task or Passport was not found.'}</p>
          <button onClick={() => void load()} className="rounded-lg bg-slate-900 px-4 py-2 text-xs font-semibold text-white">
            Retry
          </button>
        </div>
      </ConsoleLayout>
    );
  }

  return (
    <ConsoleLayout breadcrumbs={[{ label: 'Tasks', href: '/app' }, { label: task.id }]}>
      <div className="max-w-4xl space-y-5">
        <section className="rounded-xl border border-slate-200 bg-white p-6">
          <div className="flex flex-wrap items-center gap-3">
            <span className="rounded bg-slate-100 px-2 py-1 font-mono text-xs text-slate-600">{task.id}</span>
            <span className="rounded bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-800">
              Task: {task.status}
            </span>
            <span className="rounded bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700">
              Passport: {passport.activation_status}
            </span>
          </div>
          <h1 className="mt-4 text-2xl font-bold text-slate-950">Task Passport review</h1>
          <p className="mt-2 text-sm text-slate-600">{task.purpose}</p>
        </section>

        <section className="space-y-4 rounded-xl border border-slate-200 bg-white p-6">
          <h2 className="text-sm font-bold uppercase tracking-wide text-slate-600">Backend-generated policy</h2>
          <p className="text-sm text-slate-600">
            Deterministic local MVP Passport, version {passport.version}. Policy choices are compiled by the backend;
            the UI does not generate signatures or independently decide permissions.
          </p>
          <div>
            <p className="text-xs font-semibold text-emerald-800">Allowed</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {passport.allowed_tools.map((tool) => (
                <span key={tool} className="rounded border border-emerald-200 bg-emerald-50 px-2 py-1 font-mono text-xs text-emerald-900">{tool}</span>
              ))}
            </div>
          </div>
          <div>
            <p className="text-xs font-semibold text-rose-800">Forbidden</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {passport.forbidden_tools.map((tool) => (
                <span key={tool} className="rounded border border-rose-200 bg-rose-50 px-2 py-1 font-mono text-xs text-rose-900">{tool}</span>
              ))}
            </div>
          </div>
          <div className="grid gap-3 border-t border-slate-100 pt-4 text-xs text-slate-600 sm:grid-cols-2">
            <p>Data is synthetic only: <strong>{passport.data_policy.synthetic_data_only ? 'Yes' : 'No'}</strong></p>
            <p>External transmission: <strong>{passport.data_policy.external_transmission}</strong></p>
            <p>Destructive operations: <strong>{passport.data_policy.destructive_operations}</strong></p>
            <p>Expires: <strong>{new Date(passport.expires_at).toLocaleString()}</strong></p>
          </div>
        </section>

        {error && <p role="alert" className="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">{error}</p>}
        <div className="flex flex-wrap gap-3">
          {passport.activation_status === 'DRAFT' && (
            <button
              disabled={working}
              onClick={() => void handleActivate()}
              className="rounded-lg bg-slate-900 px-4 py-2.5 text-xs font-semibold text-white disabled:opacity-50"
            >
              {working ? 'Activating...' : 'Activate Passport'}
            </button>
          )}
          {passport.activation_status === 'ACTIVE' && (
            <button
              disabled={working}
              onClick={() => void handleStartSession()}
              className="rounded-lg bg-emerald-700 px-4 py-2.5 text-xs font-semibold text-white disabled:opacity-50"
            >
              {working ? 'Starting...' : 'Start governed session'}
            </button>
          )}
          <Link href="/app/audit" className="rounded-lg border border-slate-300 px-4 py-2.5 text-xs font-semibold text-slate-700">
            View audit events
          </Link>
        </div>
      </div>
    </ConsoleLayout>
  );
};

const MockPassportReview: React.FC = () => {
  const { params } = useRouter();
  const { tasks } = useGovernance();
  const [copiedHash, setCopiedHash] = useState(false);

  const taskId = params.id || 'task-inv-01';
  const task = tasks.find(t => t.id === taskId) || tasks[0];

  const passport = task.passport;
  if (!passport) return null;

  const handleCopyHash = () => {
    navigator.clipboard.writeText(passport.policyHash);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  const rawJson = JSON.stringify(
    {
      passport_id: passport.passportId,
      task_id: task.id,
      agent_id: task.agentId,
      agent_name: task.agentName,
      issuer: passport.issuer,
      validity: {
        issued_at: passport.issuedAt,
        expires_at: passport.expiresAt,
      },
      capability_manifest: {
        allowed_tools: passport.allowedTools,
        prohibited_tools: passport.prohibitedTools,
        rate_limits: {
          max_calls_per_hour: passport.maxCallsPerHour,
        },
      },
      data_boundaries: passport.dataBoundaries,
      cryptographic_attestation: {
        algorithm: 'Ed25519-SHA256',
        policy_hash: passport.policyHash,
        signature: passport.signature,
      },
    },
    null,
    2
  );

  return (
    <ConsoleLayout
      breadcrumbs={[
        { label: 'Tasks', href: '/app' },
        { label: task.id }
      ]}
    >
      <div className="space-y-6">
        {/* Header Strip */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-2xs">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <span className="font-mono text-xs font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                {task.id}
              </span>
              <StatusBadge verdict={task.status} />
              <span className="text-xs text-slate-400">·</span>
              <span className="text-xs font-mono text-slate-500">{task.agentName}</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-950">
              {task.title}
            </h1>
            <p className="text-xs text-slate-600 max-w-2xl leading-relaxed">
              {task.description}
            </p>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-center">
            {task.activeSessionId && (
              <Link
                href={`/app/sessions/${task.activeSessionId}`}
                className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800 transition-colors shadow-xs"
              >
                <Terminal className="w-3.5 h-3.5 text-emerald-400" />
                <span>Inspect Active Session</span>
              </Link>
            )}
          </div>
        </div>

        {/* Cryptographic Attestation Card */}
        <div className="p-5 rounded-xl border border-emerald-200 bg-emerald-50/60 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center shrink-0">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-bold text-emerald-950 uppercase tracking-wider">
                  Cryptographically Verified Passport
                </p>
                <span className="text-[10px] bg-emerald-200/80 text-emerald-900 font-semibold px-2 py-0.2 rounded">
                  Ed25519 Valid
                </span>
              </div>
              <p className="text-xs text-emerald-800 mt-0.5 font-mono break-all">
                Hash: {passport.policyHash}
              </p>
            </div>
          </div>

          <button
            onClick={handleCopyHash}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-white text-emerald-900 border border-emerald-300 text-xs font-medium hover:bg-emerald-50 transition-colors shrink-0"
          >
            {copiedHash ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copiedHash ? 'Hash Copied' : 'Copy Policy Hash'}</span>
          </button>
        </div>

        {/* 2-Column Passport Details */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Left Column: Capability Manifest */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-2xs p-5 space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <FileCheck2 className="w-4 h-4 text-slate-700" />
                <span>Tool Capability Boundaries</span>
              </h2>
              <span className="text-xs font-mono font-bold text-slate-900">
                {passport.passportId}
              </span>
            </div>

            {/* Whitelisted Tools */}
            <div className="space-y-2">
              <p className="text-xs font-semibold text-emerald-800 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Whitelisted Tools ({passport.allowedTools.length})</span>
              </p>
              <div className="flex flex-wrap gap-1.5">
                {passport.allowedTools.map(tool => (
                  <span
                    key={tool}
                    className="font-mono text-xs px-2.5 py-1 rounded bg-emerald-50 text-emerald-800 border border-emerald-200/80"
                  >
                    {tool}
                  </span>
                ))}
              </div>
            </div>

            {/* Prohibited Tools */}
            <div className="space-y-2 pt-3 border-t border-slate-100">
              <p className="text-xs font-semibold text-rose-800 flex items-center gap-1">
                <AlertOctagon className="w-3.5 h-3.5 text-rose-600" />
                <span>Prohibited Tools (Instant Abort)</span>
              </p>
              <div className="flex flex-wrap gap-1.5">
                {passport.prohibitedTools.map(tool => (
                  <span
                    key={tool}
                    className="font-mono text-xs px-2.5 py-1 rounded bg-rose-50 text-rose-800 border border-rose-200/80"
                  >
                    {tool}
                  </span>
                ))}
              </div>
            </div>

            {/* Rate & Boundaries */}
            <div className="space-y-2 pt-3 border-t border-slate-100 text-xs">
              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-500">Max Calls / Hour:</span>
                <span className="font-mono font-bold text-slate-900 tabular-nums">{passport.maxCallsPerHour} calls</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-500">Egress Restricted:</span>
                <span className="font-semibold text-slate-900">{passport.dataBoundaries.egressRestricted ? 'Enforced (Zero 3P Egress)' : 'Open'}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-500">PII Redaction Filter:</span>
                <span className="font-semibold text-emerald-700">{passport.dataBoundaries.piiFilterEnabled ? 'Active (Deep Inspection)' : 'Disabled'}</span>
              </div>
            </div>
          </div>

          {/* Right Column: Issuance & Key Metadata */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-2xs p-5 space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <Lock className="w-4 h-4 text-slate-700" />
                <span>Issuance Authority &amp; Signature</span>
              </h2>
              <span className="text-xs text-slate-400">Ed25519</span>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <p className="text-slate-500 text-[11px]">Issuing Key Management System (KMS):</p>
                <p className="font-mono font-bold text-slate-900 text-xs mt-0.5">{passport.issuer}</p>
              </div>

              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-100">
                <div>
                  <p className="text-slate-500 text-[11px]">Issued At:</p>
                  <p className="font-mono text-slate-800 text-xs">{new Date(passport.issuedAt).toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-slate-500 text-[11px]">Expires At:</p>
                  <p className="font-mono text-slate-800 text-xs">{new Date(passport.expiresAt).toLocaleString()}</p>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-100">
                <p className="text-slate-500 text-[11px]">Allowed Domain Whitelist:</p>
                <div className="mt-1 flex flex-wrap gap-1">
                  {passport.dataBoundaries.allowedDomains.map(d => (
                    <span key={d} className="font-mono text-[11px] bg-slate-100 text-slate-800 px-2 py-0.5 rounded">
                      {d}
                    </span>
                  ))}
                </div>
              </div>

              <div className="pt-2 border-t border-slate-100">
                <p className="text-slate-500 text-[11px]">Digital Signature Payload:</p>
                <div className="mt-1 p-2 bg-slate-100 rounded text-[11px] font-mono break-all text-slate-700">
                  {passport.signature}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Raw Signed JSON Manifest */}
        <div className="space-y-2">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Cryptographic Task Passport Manifest (Raw JSON)
          </h2>
          <CodeViewer code={rawJson} title={`Passport: ${passport.passportId}`} />
        </div>
      </div>
    </ConsoleLayout>
  );
};
