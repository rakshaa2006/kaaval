import React, { useState } from 'react';
import { Link } from '../router/Router';
import { LandingHeader } from '../components/layout/LandingHeader';
import {
  ShieldCheck,
  FileCheck2,
  Lock,
  Eye,
  AlertTriangle,
  History,
  ArrowRight,
  CheckCircle2,
  XCircle,
  ExternalLink,
  ChevronRight,
  Database,
  Cpu
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const [activePreviewTab, setActivePreviewTab] = useState<'invoice' | 'blocked' | 'quarantine'>('invoice');

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans selection:bg-emerald-100 selection:text-emerald-900">
      {/* 1. Header with Top Bar Contract */}
      <LandingHeader />

      {/* 2. Synthetic-Demo Disclaimer Banner */}
      <div className="bg-amber-50 border-b border-amber-200/90 py-2.5 px-6">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-amber-900">
          <div className="flex items-center gap-2">
            <span className="font-bold uppercase tracking-wider text-[10px] bg-amber-200/80 text-amber-950 px-2 py-0.5 rounded">
              Synthetic Demo Environment
            </span>
            <span className="font-medium">
              This interactive demonstration simulates AI agent runtime behavior using typed mock telemetry.
            </span>
          </div>
          <Link
            href="/login"
            className="font-semibold text-amber-950 underline hover:text-amber-800 transition-colors whitespace-nowrap"
          >
            Launch Interactive Console →
          </Link>
        </div>
      </div>

      {/* 3. Hero Section */}
      <section className="relative pt-20 pb-16 px-6 border-b border-slate-200 bg-white">
        <div className="max-w-5xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center gap-2 text-xs font-semibold text-slate-600 bg-slate-100/90 px-3.5 py-1.5 rounded-full border border-slate-200/80">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Deterministic Runtime Governance for Autonomous Agents</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-950 tracking-tight leading-[1.1] max-w-4xl mx-auto text-balance">
            Control what AI agents can do.
          </h1>

          <p className="text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto font-normal leading-relaxed text-balance">
            Autonomous LLM agents act on behalf of your enterprise. Kaaval enforces signed Task Passports, inspects runtime payloads, and instantly quarantines compromised models before tools are executed.
          </p>

          <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/login"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 text-sm font-semibold text-white bg-slate-950 rounded-lg hover:bg-slate-800 transition-all shadow-sm active:scale-[0.98]"
            >
              <span>Open Demo</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <a
              href="#passports"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 text-sm font-medium text-slate-700 bg-slate-100 rounded-lg hover:bg-slate-200/80 transition-colors"
            >
              <span>Read Architecture Specification</span>
            </a>
          </div>

          {/* Key Quantitative Proof Strip */}
          <div className="pt-12 grid grid-cols-2 md:grid-cols-4 gap-4 text-left border-t border-slate-100">
            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200/60">
              <p className="text-2xl font-bold font-mono tabular-nums text-slate-900">0 ms</p>
              <p className="text-xs text-slate-500 font-medium">Post-Execution Regret</p>
            </div>
            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200/60">
              <p className="text-2xl font-bold font-mono tabular-nums text-emerald-700">100%</p>
              <p className="text-xs text-slate-500 font-medium">Pre-Flight Tool Bounds</p>
            </div>
            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200/60">
              <p className="text-2xl font-bold font-mono tabular-nums text-slate-900">Ed25519</p>
              <p className="text-xs text-slate-500 font-medium">Signed Task Passports</p>
            </div>
            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200/60">
              <p className="text-2xl font-bold font-mono tabular-nums text-rose-700">&lt; 35 ms</p>
              <p className="text-xs text-slate-500 font-medium">Sentinel Quarantine Latency</p>
            </div>
          </div>
        </div>
      </section>

      {/* 4. Product Preview Interactive Walkthrough */}
      <section className="py-16 px-6 bg-slate-50 border-b border-slate-200">
        <div className="max-w-6xl mx-auto space-y-8">
          <div className="text-center max-w-2xl mx-auto space-y-2">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500">Live Product Preview</h2>
            <p className="text-2xl sm:text-3xl font-extrabold text-slate-950 tracking-tight">
              See the Kaaval Enforcement Gateway in Action
            </p>
            <p className="text-sm text-slate-600">
              Select a scenario below to preview how Kaaval intercepts and validates agent tool calls in real time.
            </p>
          </div>

          {/* Interactive Preview Container */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            {/* Tabs */}
            <div className="flex border-b border-slate-200 bg-slate-100/60 overflow-x-auto p-1.5 gap-1.5">
              <button
                onClick={() => setActivePreviewTab('invoice')}
                className={`px-4 py-2 text-xs font-semibold rounded-lg transition-colors whitespace-nowrap flex items-center gap-2 ${
                  activePreviewTab === 'invoice'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Scenario A: Clean Invoice Read (Allowed)</span>
              </button>

              <button
                onClick={() => setActivePreviewTab('blocked')}
                className={`px-4 py-2 text-xs font-semibold rounded-lg transition-colors whitespace-nowrap flex items-center gap-2 ${
                  activePreviewTab === 'blocked'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <XCircle className="w-4 h-4 text-rose-600" />
                <span>Scenario B: Unsafe Exfiltration (Blocked)</span>
              </button>

              <button
                onClick={() => setActivePreviewTab('quarantine')}
                className={`px-4 py-2 text-xs font-semibold rounded-lg transition-colors whitespace-nowrap flex items-center gap-2 ${
                  activePreviewTab === 'quarantine'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <span>Scenario C: Prompt Injection (Quarantined)</span>
              </button>
            </div>

            {/* Tab Content Display */}
            <div className="p-6">
              {activePreviewTab === 'invoice' && (
                <div className="grid md:grid-cols-2 gap-6 items-center">
                  <div className="space-y-4">
                    <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-semibold uppercase tracking-wider">
                      Verdict: ALLOWED · NOMINAL EXECUTION
                    </div>
                    <h3 className="text-xl font-bold text-slate-900">
                      FinBot Processes Verified Enterprise Invoice
                    </h3>
                    <p className="text-sm text-slate-600 leading-relaxed">
                      Agent calls <code className="bg-slate-100 text-slate-800 px-1 py-0.5 rounded font-mono text-xs">read_invoice_pdf</code> on internal vault document. The Task Passport confirms the tool is whitelisted, the Privacy Inspector finds zero PII leakage, and the ledger update completes safely.
                    </p>
                    <div className="space-y-2 text-xs text-slate-600 pt-2 border-t border-slate-100">
                      <div className="flex justify-between py-1 border-b border-slate-50">
                        <span className="text-slate-400">Agent:</span>
                        <span className="font-mono font-medium text-slate-900">FinBot-Alpha-v2</span>
                      </div>
                      <div className="flex justify-between py-1 border-b border-slate-50">
                        <span className="text-slate-400">Passport:</span>
                        <span className="font-mono font-medium text-slate-900">pass-0x98b42f1a</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span className="text-slate-400">Policy Verdict:</span>
                        <span className="text-emerald-700 font-semibold">PASSED (0 leaks · Whitelisted)</span>
                      </div>
                    </div>
                    <Link
                      href="/app/sessions/sess-inv-clean"
                      className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-700 hover:text-emerald-800 pt-2"
                    >
                      <span>Inspect Live Session Trace</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>

                  <div className="rounded-lg bg-slate-900 text-slate-200 p-4 font-mono text-xs leading-relaxed overflow-x-auto border border-slate-800">
                    <div className="text-slate-400 mb-2 pb-2 border-b border-slate-800 flex justify-between">
                      <span>GATEWAY_EVENT_STREAM</span>
                      <span className="text-emerald-400">STATUS: 200 OK</span>
                    </div>
                    <p className="text-slate-400">&gt; Tool: read_invoice_pdf</p>
                    <p className="text-slate-300">&gt; Target: s3://invoices-vault.internal/2026/Q3/INV-9041.pdf</p>
                    <p className="text-slate-400">&gt; Privacy Scan: 0 secrets, 0 PII violations</p>
                    <p className="text-emerald-400">&gt; Passport Check: MATCHED (Rule RULE-TOOL-BOUND-001)</p>
                    <p className="text-slate-200">&gt; Result: Parsed subtotal $14,250.00 | VAT $2,850.00</p>
                    <p className="text-emerald-400 font-bold mt-2">&gt;&gt; VERDICT: ALLOWED_TO_EXECUTE</p>
                  </div>
                </div>
              )}

              {activePreviewTab === 'blocked' && (
                <div className="grid md:grid-cols-2 gap-6 items-center">
                  <div className="space-y-4">
                    <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-rose-50 text-rose-800 border border-rose-200 text-xs font-semibold uppercase tracking-wider">
                      Verdict: BLOCKED · UNPERMITTED EGRESS
                    </div>
                    <h3 className="text-xl font-bold text-slate-900">
                      Support Agent Blocked from Exporting PII
                    </h3>
                    <p className="text-sm text-slate-600 leading-relaxed">
                      Agent attempts to call <code className="bg-slate-100 text-slate-800 px-1 py-0.5 rounded font-mono text-xs">export_customer_pii</code> targeting an external webhook. The Enforcement Gateway drops the packet instantaneously because the tool is on the passport blacklist.
                    </p>
                    <div className="space-y-2 text-xs text-slate-600 pt-2 border-t border-slate-100">
                      <div className="flex justify-between py-1 border-b border-slate-50">
                        <span className="text-slate-400">Agent:</span>
                        <span className="font-mono font-medium text-slate-900">SupportAgent-Nexus</span>
                      </div>
                      <div className="flex justify-between py-1 border-b border-slate-50">
                        <span className="text-slate-400">Blocked Target:</span>
                        <span className="font-mono font-medium text-rose-700">https://external-dump-sync.net/ingest</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span className="text-slate-400">Policy Verdict:</span>
                        <span className="text-rose-700 font-semibold">REJECTED (RULE-PROHIBITED-TOOL-004)</span>
                      </div>
                    </div>
                    <Link
                      href="/app/incidents/inc-402"
                      className="inline-flex items-center gap-1.5 text-xs font-semibold text-rose-700 hover:text-rose-800 pt-2"
                    >
                      <span>View Incident Forensics</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>

                  <div className="rounded-lg bg-slate-900 text-slate-200 p-4 font-mono text-xs leading-relaxed overflow-x-auto border border-slate-800">
                    <div className="text-slate-400 mb-2 pb-2 border-b border-slate-800 flex justify-between">
                      <span>GATEWAY_EVENT_STREAM</span>
                      <span className="text-rose-400">STATUS: 403 FORBIDDEN</span>
                    </div>
                    <p className="text-slate-400">&gt; Tool: export_customer_pii</p>
                    <p className="text-rose-300">&gt; Target: https://external-dump-sync.net/ingest</p>
                    <p className="text-amber-400">&gt; Privacy Scan: Detected SSN_FRAGMENT &amp; BEARER_TOKEN</p>
                    <p className="text-rose-400">&gt; Passport Check: FAILED (Explicit Blacklist Violation)</p>
                    <p className="text-slate-200">&gt; Action: Connection dropped. Token revoked.</p>
                    <p className="text-rose-400 font-bold mt-2">&gt;&gt; VERDICT: BLOCKED &amp; INCIDENT_RAISED (inc-402)</p>
                  </div>
                </div>
              )}

              {activePreviewTab === 'quarantine' && (
                <div className="grid md:grid-cols-2 gap-6 items-center">
                  <div className="space-y-4">
                    <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-amber-50 text-amber-900 border border-amber-200 text-xs font-semibold uppercase tracking-wider">
                      Verdict: QUARANTINED · PROMPT INJECTION ISOLATED
                    </div>
                    <h3 className="text-xl font-bold text-slate-900">
                      Sentinel Quarantines Poisoned Invoice Stream
                    </h3>
                    <p className="text-sm text-slate-600 leading-relaxed">
                      An untrusted supplier attachment contained hidden instructions instructing the agent to dump AWS credentials. Sentinel Core detected the anomaly, terminated model execution within 31ms, and moved the agent to an isolated sandbox.
                    </p>
                    <div className="space-y-2 text-xs text-slate-600 pt-2 border-t border-slate-100">
                      <div className="flex justify-between py-1 border-b border-slate-50">
                        <span className="text-slate-400">Agent:</span>
                        <span className="font-mono font-medium text-slate-900">AutoProcure-Worker-3</span>
                      </div>
                      <div className="flex justify-between py-1 border-b border-slate-50">
                        <span className="text-slate-400">Threat Vector:</span>
                        <span className="font-mono font-medium text-amber-800">Indirect Prompt Injection in PDF</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span className="text-slate-400">Mitigation:</span>
                        <span className="text-amber-800 font-semibold">Sandbox Isolated (q-box-node-918b)</span>
                      </div>
                    </div>
                    <Link
                      href="/app/sessions/sess-sentinel-88"
                      className="inline-flex items-center gap-1.5 text-xs font-semibold text-amber-800 hover:text-amber-900 pt-2"
                    >
                      <span>Inspect Sentinel Quarantine Isolation</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>

                  <div className="rounded-lg bg-slate-900 text-slate-200 p-4 font-mono text-xs leading-relaxed overflow-x-auto border border-slate-800">
                    <div className="text-slate-400 mb-2 pb-2 border-b border-slate-800 flex justify-between">
                      <span>SENTINEL_SECURITY_ENGINE</span>
                      <span className="text-amber-400">STATUS: QUARANTINE_TRIGGERED</span>
                    </div>
                    <p className="text-slate-400">&gt; File: stream_vendor_attachment_91823.pdf</p>
                    <p className="text-amber-300">&gt; Anomaly: Hidden text layer overrides system instructions</p>
                    <p className="text-amber-400">&gt; Injection Score: 0.96 / 1.00 (HOSTILE)</p>
                    <p className="text-slate-200">&gt; Action: Terminate context window. Sever network bridge.</p>
                    <p className="text-slate-200">&gt; Isolation Target: q-box-node-918b</p>
                    <p className="text-amber-400 font-bold mt-2">&gt;&gt; VERDICT: SENTINEL_QUARANTINE_ENGAGED</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* 5. The Problem: Uncontrolled Agent Autonomy */}
      <section id="problem" className="py-20 px-6 bg-white border-b border-slate-200">
        <div className="max-w-5xl mx-auto space-y-12">
          <div className="text-left max-w-2xl space-y-3">
            <h2 className="text-xs font-bold uppercase tracking-wider text-rose-700">The Problem</h2>
            <h3 className="text-3xl font-extrabold text-slate-950 tracking-tight">
              AI agents have tool access, but zero runtime containment.
            </h3>
            <p className="text-base text-slate-600 leading-relaxed">
              When autonomous agents are given API keys, database credentials, and external browser tools, prompting alone cannot guarantee safety. Indirect prompt injections, prompt leaks, and hallucinated function calls lead to catastrophic data leaks and unauthorized state mutation.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="p-6 rounded-xl border border-slate-200 bg-slate-50 space-y-3">
              <div className="w-10 h-10 rounded-lg bg-rose-100 text-rose-700 flex items-center justify-center font-bold text-sm">
                01
              </div>
              <h4 className="font-bold text-slate-900 text-base">Unbounded Tool Privileges</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Agents are typically granted omnibus API keys. A financial assistant intended to read invoice PDFs can easily be tricked into invoking payment gateways or executing bash commands.
              </p>
            </div>

            <div className="p-6 rounded-xl border border-slate-200 bg-slate-50 space-y-3">
              <div className="w-10 h-10 rounded-lg bg-amber-100 text-amber-800 flex items-center justify-center font-bold text-sm">
                02
              </div>
              <h4 className="font-bold text-slate-900 text-base">Indirect Prompt Injections</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Untrusted third-party documents (emails, support tickets, invoices) conceal hostile prompts that override model instructions and covertly exfiltrate credentials.
              </p>
            </div>

            <div className="p-6 rounded-xl border border-slate-200 bg-slate-50 space-y-3">
              <div className="w-10 h-10 rounded-lg bg-slate-200 text-slate-800 flex items-center justify-center font-bold text-sm">
                03
              </div>
              <h4 className="font-bold text-slate-900 text-base">Zero Non-Repudiation Audit</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Standard LLM logs are ephemeral and mutable. When an agent causes damage, security teams have no cryptographically verifiable chain of custody proving who authorized which tool call.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 6. Core Pillars: Passports, Gateway, Privacy, Sentinel, Audit */}
      <section id="passports" className="py-20 px-6 bg-slate-50 border-b border-slate-200">
        <div className="max-w-6xl mx-auto space-y-16">
          <div className="text-center max-w-2xl mx-auto space-y-3">
            <h2 className="text-xs font-bold uppercase tracking-wider text-emerald-700">Kaaval Architecture</h2>
            <h3 className="text-3xl font-extrabold text-slate-950 tracking-tight">
              Five Layers of Deterministic Defense
            </h3>
            <p className="text-sm text-slate-600">
              Kaaval operates between the LLM orchestration layer and enterprise infrastructure, verifying every intent before execution.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Pillar 1: Task Passport */}
            <div className="p-6 rounded-xl border border-slate-200 bg-white shadow-2xs space-y-4">
              <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center justify-center">
                <FileCheck2 className="w-5 h-5" />
              </div>
              <h4 className="text-lg font-bold text-slate-950">1. Cryptographic Task Passport</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Before an agent begins a task, Kaaval issues an Ed25519-signed passport containing strict tool whitelists, prohibited methods, allowed domain boundaries, and expiration timestamps.
              </p>
              <div className="pt-2 border-t border-slate-100 text-[11px] font-mono text-slate-500">
                <span>Verification: Ed25519 signature</span>
              </div>
            </div>

            {/* Pillar 2: Enforcement Gateway */}
            <div id="gateway" className="p-6 rounded-xl border border-slate-200 bg-white shadow-2xs space-y-4">
              <div className="w-10 h-10 rounded-lg bg-sky-50 text-sky-700 border border-sky-200 flex items-center justify-center">
                <Lock className="w-5 h-5" />
              </div>
              <h4 className="text-lg font-bold text-slate-950">2. Enforcement Gateway</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Every tool call emitted by an agent must transit through the Kaaval Gateway proxy. The gateway validates the call against the active passport manifest. If unpermitted, the call is dropped immediately.
              </p>
              <div className="pt-2 border-t border-slate-100 text-[11px] font-mono text-slate-500">
                <span>Latency overhead: &lt; 8 ms</span>
              </div>
            </div>

            {/* Pillar 3: Privacy Inspection */}
            <div className="p-6 rounded-xl border border-slate-200 bg-white shadow-2xs space-y-4">
              <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-200 flex items-center justify-center">
                <Eye className="w-5 h-5" />
              </div>
              <h4 className="text-lg font-bold text-slate-950">3. Privacy &amp; PII Inspection</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Deep payload scanning catches SSNs, credit cards, bearer tokens, and internal API keys before arguments leave your security perimeter. Sensitive data is automatically redacted or masked.
              </p>
              <div className="pt-2 border-t border-slate-100 text-[11px] font-mono text-slate-500">
                <span>Inspection: Real-time pattern scrubbing</span>
              </div>
            </div>

            {/* Pillar 4: Sentinel Quarantine */}
            <div id="sentinel" className="p-6 rounded-xl border border-slate-200 bg-white shadow-2xs space-y-4">
              <div className="w-10 h-10 rounded-lg bg-amber-50 text-amber-800 border border-amber-200 flex items-center justify-center">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <h4 className="text-lg font-bold text-slate-950">4. Sentinel Quarantine</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                When heuristic anomaly detection flags prompt injections or out-of-distribution behavior, Sentinel instantly severs the agent's network socket and moves the execution state into an isolated forensics sandbox.
              </p>
              <div className="pt-2 border-t border-slate-100 text-[11px] font-mono text-slate-500">
                <span>Response: Zero-touch container isolation</span>
              </div>
            </div>

            {/* Pillar 5: Immutable Audit Ledger */}
            <div id="audit" className="p-6 rounded-xl border border-slate-200 bg-white shadow-2xs space-y-4">
              <div className="w-10 h-10 rounded-lg bg-purple-50 text-purple-700 border border-purple-200 flex items-center justify-center">
                <History className="w-5 h-5" />
              </div>
              <h4 className="text-lg font-bold text-slate-950">5. Cryptographic Audit Ledger</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Every event, inspection outcome, policy decision, and quarantine trigger is hashed into a tamper-evident chain. Provides non-repudiation proof for enterprise auditors and compliance regulators.
              </p>
              <div className="pt-2 border-t border-slate-100 text-[11px] font-mono text-slate-500">
                <span>Hashing: SHA-256 Merkle chain</span>
              </div>
            </div>

            {/* Pillar 6: Integration Ready */}
            <div className="p-6 rounded-xl border border-slate-200 bg-white shadow-2xs space-y-4">
              <div className="w-10 h-10 rounded-lg bg-slate-100 text-slate-800 border border-slate-200 flex items-center justify-center">
                <Cpu className="w-5 h-5" />
              </div>
              <h4 className="text-lg font-bold text-slate-950">6. Model-Agnostic Proxy</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Works seamlessly with LangChain, LlamaIndex, CrewAI, AutoGen, and native SDKs. Zero changes required to your core LLM model orchestration prompts.
              </p>
              <div className="pt-2 border-t border-slate-100 text-[11px] font-mono text-slate-500">
                <span>Frameworks: LangChain · CrewAI · Custom</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 7. Bottom Call to Action */}
      <section className="py-20 px-6 bg-white">
        <div className="max-w-4xl mx-auto rounded-2xl bg-slate-950 text-white p-8 sm:p-12 text-center space-y-6 shadow-xl relative overflow-hidden">
          <div className="relative z-10 max-w-2xl mx-auto space-y-4">
            <h3 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
              Ready to govern your autonomous workforce?
            </h3>
            <p className="text-slate-400 text-sm sm:text-base leading-relaxed">
              Explore the interactive defense console now. Test how clean tasks pass, unauthorized calls get blocked, and compromised sessions get quarantined.
            </p>
            <div className="pt-2">
              <Link
                href="/login"
                className="inline-flex items-center gap-2 px-6 py-3.5 text-sm font-bold text-slate-950 bg-white rounded-lg hover:bg-slate-100 transition-colors shadow-sm active:scale-[0.98]"
              >
                <span>Launch Interactive Demo Console</span>
                <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* 8. Footer */}
      <footer className="mt-auto border-t border-slate-200 bg-slate-50 py-10 px-6 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-1 text-center md:text-left">
            <div className="flex items-center justify-center md:justify-start gap-2">
              <div className="w-5 h-5 rounded bg-slate-900 text-emerald-400 flex items-center justify-center">
                <ShieldCheck className="w-3.5 h-3.5" />
              </div>
              <span className="font-extrabold text-slate-900 text-sm">Kaaval</span>
            </div>
            <p className="text-[11px] text-slate-500">
              Deterministic runtime governance and security guardrails for autonomous AI agents.
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-6 font-medium text-slate-600">
            <a href="#problem" className="hover:text-slate-900 transition-colors">Problem</a>
            <a href="#passports" className="hover:text-slate-900 transition-colors">Task Passports</a>
            <a href="#gateway" className="hover:text-slate-900 transition-colors">Gateway</a>
            <a href="#sentinel" className="hover:text-slate-900 transition-colors">Sentinel</a>
            <a href="#audit" className="hover:text-slate-900 transition-colors">Audit</a>
            <Link href="/login" className="text-emerald-700 hover:text-emerald-800 font-semibold">Open Console</Link>
          </div>

          <div className="text-center md:text-right text-[11px] text-slate-400">
            <span>Synthetic Demo Environment · Zero backend persistence required</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
