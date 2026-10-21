import React, { useState } from 'react';
import { ConsoleLayout } from '../components/layout/ConsoleLayout';
import { useGovernance } from '../context/GovernanceContext';
import { useRouter } from '../router/Router';
import { ShieldCheck, Plus, Check, FileCode, Lock, ArrowRight } from 'lucide-react';

const AVAILABLE_TOOLS = [
  { id: 'read_invoice', label: 'read_invoice', desc: 'Reads an allowlisted synthetic invoice fixture' },
];

const PROHIBITED_TOOL_OPTIONS = [
  'send_email',
  'delete_backup',
];

export const CreateTaskPage: React.FC = () => {
  const { createTask, apiError, clearApiError } = useGovernance();
  const { navigate } = useRouter();

  const [title, setTitle] = useState('Process Synthetic Invoice');
  const [category, setCategory] = useState<'finance' | 'customer_ops' | 'infra' | 'data_reconcile'>('finance');
  const [description, setDescription] = useState('Read the synthetic clean invoice fixture and summarize its totals.');
  const selectedTools = ['read_invoice'];
  const prohibitedTools = ['send_email', 'delete_backup'];
  const piiFilterEnabled = true;
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [submitError, setSubmitError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearApiError();
    setSubmitError(null);
    setIsSubmitting(true);

    try {
      const newTaskId = await createTask({
        title,
        description,
      });
      navigate(`/app/tasks/${newTaskId}`);
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'Unable to create task.');
      setIsSubmitting(false);
    }
  };

  return (
    <ConsoleLayout
      breadcrumbs={[
        { label: 'Tasks', href: '/app' },
        { label: 'Issue Task Passport' }
      ]}
    >
      <div className="max-w-4xl space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-950">
            Create Invoice Task and Passport
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            The local backend currently supports invoice tasks with a deterministic, fixed tool policy.
          </p>
        </div>

        {(submitError || apiError) && (
          <p role="alert" className="text-xs text-rose-700 bg-rose-50 border border-rose-200 rounded-lg p-3">
            {submitError || apiError}
          </p>
        )}

        <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-slate-200 shadow-2xs p-6 space-y-8">
          {/* Section 1: Agent & Mission Metadata */}
          <div className="space-y-4">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              1. Agent &amp; Mission Specification
            </h2>

            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Task Title
                </label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Process Synthetic Invoice"
                  className="w-full text-xs px-3 py-2 rounded-lg border border-slate-300 focus:outline-hidden focus:border-slate-900 bg-white"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Target Agent Identifier
                </label>
                <input
                  type="text"
                  value="Kaaval Demo Agent"
                  disabled
                  className="w-full text-xs px-3 py-2 rounded-lg border border-slate-300 bg-slate-100 font-mono text-slate-500"
                />
                <p className="mt-1 text-[11px] text-slate-500">Assigned by the local demo backend.</p>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Domain Category
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {[
                  { id: 'finance', label: 'Financial Ops' },
                  { id: 'customer_ops', label: 'Customer Support' },
                  { id: 'infra', label: 'Infrastructure' },
                  { id: 'data_reconcile', label: 'Data Reconciliation' },
                ].map(cat => (
                  <button
                    type="button"
                    key={cat.id}
                    disabled
                    className={`py-2 px-3 text-xs font-medium rounded-lg border text-center transition-colors ${
                      category === cat.id
                        ? 'bg-slate-900 text-white border-slate-900 font-semibold'
                        : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    {cat.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Mission Description
              </label>
              <textarea
                rows={2}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full text-xs px-3 py-2 rounded-lg border border-slate-300 focus:outline-hidden focus:border-slate-900 bg-white"
              />
            </div>
          </div>

          {/* Section 2: Allowed Tools Whitelist */}
          <div className="space-y-4 pt-4 border-t border-slate-100">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  2. Allowed Tools Whitelist
                </h2>
                <p className="text-xs text-slate-500">
                  This fixed allowlist is generated and enforced by the backend; it cannot be changed in this demo.
                </p>
              </div>
              <span className="text-xs font-mono font-bold text-emerald-700">
                {selectedTools.length} tools allowed
              </span>
            </div>

            <div className="grid sm:grid-cols-2 gap-3">
              {AVAILABLE_TOOLS.map(tool => {
                const isChecked = selectedTools.includes(tool.id);
                return (
                  <div
                    key={tool.id}
                    className={`p-3 rounded-lg border cursor-not-allowed transition-all flex items-start gap-3 ${
                      isChecked
                        ? 'border-emerald-600 bg-emerald-50/50 shadow-2xs'
                        : 'border-slate-200 bg-white hover:bg-slate-50'
                    }`}
                  >
                    <div
                      className={`mt-0.5 w-4 h-4 rounded border flex items-center justify-center shrink-0 ${
                        isChecked ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-slate-300 bg-white'
                      }`}
                    >
                      {isChecked && <Check className="w-3 h-3 stroke-[3]" />}
                    </div>
                    <div>
                      <p className="font-mono text-xs font-bold text-slate-900">{tool.label}</p>
                      <p className="text-[11px] text-slate-500 mt-0.5">{tool.desc}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Section 3: Prohibited Tools Blacklist */}
          <div className="space-y-4 pt-4 border-t border-slate-100">
            <div>
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                3. Explicit Prohibited Tools (Blacklist)
              </h2>
              <p className="text-xs text-slate-500">
                Any attempt to invoke these tools triggers an immediate gateway abort and security incident.
              </p>
            </div>

            <div className="flex flex-wrap gap-2">
              {PROHIBITED_TOOL_OPTIONS.map(tool => {
                const isProhibited = prohibitedTools.includes(tool);
                return (
                  <button
                    type="button"
                    key={tool}
                    disabled
                    className={`text-xs font-mono px-3 py-1.5 rounded-md border transition-colors flex items-center gap-1.5 ${
                      isProhibited
                        ? 'bg-rose-50 border-rose-300 text-rose-800 font-semibold'
                        : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <span>{isProhibited ? '✕' : '+'}</span>
                    <span>{tool}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Section 4: Boundary & Rate Limits */}
          <div className="space-y-4 pt-4 border-t border-slate-100">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              4. Execution Boundaries &amp; Rate Limits
            </h2>

            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Max Calls Per Hour
                </label>
                <input
                  type="text"
                  value="Not configured"
                  disabled
                  className="w-full text-xs px-3 py-2 rounded-lg border border-slate-300 font-mono bg-slate-100 text-slate-500"
                />
                <p className="mt-1 text-[11px] text-slate-500">Rate limits are not exposed by the backend MVP.</p>
              </div>

              <div className="flex items-center gap-3 pt-6">
                <input
                  type="checkbox"
                  id="pii_toggle"
                  checked={piiFilterEnabled}
                  disabled
                  className="w-4 h-4 rounded border-slate-300 text-emerald-600 focus:ring-0"
                />
                <label htmlFor="pii_toggle" className="text-xs font-semibold text-slate-800 cursor-pointer">
                  Backend deterministic privacy inspection
                </label>
              </div>
            </div>
          </div>

          {/* Submit Action */}
          <div className="pt-6 border-t border-slate-100 flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs text-slate-500 font-mono">
              <Lock className="w-3.5 h-3.5 text-slate-400" />
              <span>Backend generates the deterministic MVP Passport</span>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-slate-900 text-white text-xs font-bold hover:bg-slate-800 transition-colors shadow-xs active:scale-[0.99] disabled:opacity-50"
            >
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>{isSubmitting ? 'Creating task and generating Passport...' : 'Create Task and Generate Passport'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </ConsoleLayout>
  );
};
