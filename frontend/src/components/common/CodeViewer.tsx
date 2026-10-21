import React, { useState } from 'react';
import { Copy, Check, Terminal } from 'lucide-react';

interface CodeViewerProps {
  code: string;
  title?: string;
  language?: string;
}

export const CodeViewer: React.FC<CodeViewerProps> = ({ code, title, language = 'json' }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-lg border border-slate-800 bg-[#0B0F19] overflow-hidden text-slate-100 shadow-sm">
      <div className="flex items-center justify-between px-3.5 py-2 bg-[#0F172A]/90 border-b border-slate-800/90 text-xs">
        <div className="flex items-center gap-2">
          <Terminal className="w-3.5 h-3.5 text-slate-400" />
          {title && <span className="font-mono text-xs font-semibold text-slate-200">{title}</span>}
          <span className="text-[10px] font-mono text-slate-500 uppercase px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800">
            {language}
          </span>
        </div>
        <button
          onClick={handleCopy}
          className="inline-flex items-center gap-1.5 px-2 py-1 text-[11px] font-mono font-medium text-slate-300 hover:text-white bg-slate-800/80 hover:bg-slate-700/80 rounded border border-slate-700/60 transition-colors"
          title="Copy code"
        >
          {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3 text-slate-400" />}
          <span>{copied ? 'Copied' : 'Copy'}</span>
        </button>
      </div>
      <div className="p-4 overflow-x-auto font-mono text-xs leading-relaxed text-slate-300">
        <pre className="whitespace-pre">
          <code>{code}</code>
        </pre>
      </div>
    </div>
  );
};
