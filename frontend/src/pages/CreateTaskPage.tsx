import React, { useState } from 'react';
import { ConsoleLayout } from '../components/layout/ConsoleLayout';
import { useGovernance } from '../context/GovernanceContext';
import { useRouter } from '../router/Router';
import { ShieldCheck, Plus, Check, FileCode, Lock, ArrowRight } from 'lucide-react';

const AVAILABLE_TOOLS = [
  { id: 'read_invoice_pdf', label: 'read_invoice_pdf', desc: 'Extracts tables and key-value fields from PDF invoices' },
  { id: 'fetch_vendor_balance', label: 'fetch_vendor_balance', desc: 'Queries ERP accounting ledger for vendor receivables' },
  { id: 'validate_vat_id', label: 'validate_vat_id', desc: 'Validates EU/US tax identification numbers with authority API' },
  { id: 'generate_ledger_entry', label: 'generate_ledger_entry', desc: 'Posts reconciliation transaction to accounts payable' },
  { id: 'query_customer_crm', label: 'query_customer_crm', desc: 'Looks up customer account tier and support tickets' },
  { id: 'fetch_ticket_history', label: 'fetch_ticket_history', desc: 'Retrieves prior resolution history for escalated tickets' },
  { id: 'summarize_case_notes', label: 'summarize_case_notes', desc: 'Summarizes diagnostic notes for support engineers' },
];

const PROHIBITED_TOOL_OPTIONS = [
  'curl_external_url',
  'export_customer_pii',
  'modify_payment_gateway',
  'execute_shell_command',
  'network_raw_socket',
  'query_dns',
];

export const CreateTaskPage: React.FC = () => {
  const { createTask } = useGovernance();
  const { navigate } = useRouter();

  const [title, setTitle] = useState('Vendor Statement Verification');
  const [agentName, setAgentName] = useState('ReconcileBot-Pro');
  const [category, setCategory] = useState<'finance' | 'customer_ops' | 'infra' | 'data_reconcile'>('finance');
  const [description, setDescription] = useState('Inspect and cross-reference monthly vendor billing statements with purchase orders.');
  const [selectedTools, setSelectedTools] = useState<string[]>(['read_invoice_pdf', 'fetch_vendor_balance', 'validate_vat_id']);
  const [prohibitedTools, setProhibitedTools] = useState<string[]>(['curl_external_url', 'modify_payment_gateway', 'export_customer_pii']);
  const [maxCallsPerHour, setMaxCallsPerHour] = useState(100);
  const [piiFilterEnabled, setPiiFilterEnabled] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const toggleTool = (toolId: string) => {
    setSelectedTools(prev =>
      prev.includes(toolId) ? prev.filter(t => t !== toolId) : [...prev, toolId]
    );
  };

  const toggleProhibited = (toolId: string) => {
    setProhibitedTools(prev =>
      prev.includes(toolId) ? prev.filter(t => t !== toolId) : [...prev, toolId]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedTools.length === 0) {
      alert('Please select at least one allowed tool for the passport.');
      return;
    }
    setIsSubmitting(true);

    const newTaskId = createTask({
      title,
      agentName,
      category,
      allowedTools: selectedTools,
      prohibitedTools,
      maxCallsPerHour,
      description,
    });

    setTimeout(() => {
      navigate(`/app/tasks/${newTaskId}`);
    }, 250);
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
            Issue Signed Task Passport
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Define capability boundaries and runtime permissions for an autonomous AI agent before deployment.
          </p>
        </div>

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
                  placeholder="e.g. Vendor Statement Verification"
                  className="w-full text-xs px-3 py-2 rounded-lg border border-slate-300 focus:outline-hidden focus:border-slate-900 bg-white"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Target Agent Identifier
                </label>
                <input
                  type="text"
                  required
                  value={agentName}
                  onChange={(e) => setAgentName(e.target.value)}
                  placeholder="e.g. ReconcileBot-Pro"
                  className="w-full text-xs px-3 py-2 rounded-lg border border-slate-300 focus:outline-hidden focus:border-slate-900 bg-white font-mono"
                />
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
                    onClick={() => setCategory(cat.id as any)}
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
                  Only selected tools will be authorized by the Enforcement Gateway during execution.
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
                    onClick={() => toggleTool(tool.id)}
                    className={`p-3 rounded-lg border cursor-pointer transition-all flex items-start gap-3 ${
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
                    onClick={() => toggleProhibited(tool)}
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
                  type="number"
                  min={10}
                  max={1000}
                  value={maxCallsPerHour}
                  onChange={(e) => setMaxCallsPerHour(Number(e.target.value))}
                  className="w-full text-xs px-3 py-2 rounded-lg border border-slate-300 font-mono bg-white"
                />
              </div>

              <div className="flex items-center gap-3 pt-6">
                <input
                  type="checkbox"
                  id="pii_toggle"
                  checked={piiFilterEnabled}
                  onChange={(e) => setPiiFilterEnabled(e.target.checked)}
                  className="w-4 h-4 rounded border-slate-300 text-emerald-600 focus:ring-0"
                />
                <label htmlFor="pii_toggle" className="text-xs font-semibold text-slate-800 cursor-pointer">
                  Enable Real-time PII &amp; Secret Redaction Filter
                </label>
              </div>
            </div>
          </div>

          {/* Submit Action */}
          <div className="pt-6 border-t border-slate-100 flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs text-slate-500 font-mono">
              <Lock className="w-3.5 h-3.5 text-slate-400" />
              <span>Will be signed with Ed25519 Kaaval KMS key</span>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-slate-900 text-white text-xs font-bold hover:bg-slate-800 transition-colors shadow-xs active:scale-[0.99] disabled:opacity-50"
            >
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>{isSubmitting ? 'Computing Cryptographic Passport...' : 'Issue Task Passport'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </ConsoleLayout>
  );
};
