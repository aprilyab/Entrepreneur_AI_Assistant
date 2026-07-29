'use client';

import {
  BarChart3, BrainCircuit, Check, CircleDollarSign, FileCheck2,
  Loader2, PauseCircle, Play, RefreshCw, ShieldAlert, TrendingUp,
} from 'lucide-react';

const stages = [
  { id: 'market', label: 'Grounded market research', detail: 'Live search, source scoring, citations', threshold: 18, icon: BarChart3 },
  { id: 'strategy', label: 'Business model', detail: 'Value, channels, revenue and moat', threshold: 34, icon: BrainCircuit },
  { id: 'finance', label: 'Financial analysis', detail: 'Economics, projections and funding', threshold: 50, icon: CircleDollarSign },
  { id: 'risk', label: 'Risk stress test', detail: 'Severity, probability and mitigation', threshold: 64, icon: ShieldAlert },
  { id: 'growth', label: 'Growth strategy', detail: 'Acquisition, retention and scale', threshold: 77, icon: TrendingUp },
  { id: 'validate', label: 'Viability decision', detail: 'Score, evidence gaps and next tests', threshold: 90, icon: FileCheck2 },
  { id: 'compile', label: 'Final plan', detail: 'Compile and save the complete workspace', threshold: 100, icon: Check },
];

export default function GenerationProgress({
  plan,
  job,
  onCancel,
  onResume,
  actionLoading,
}: {
  plan: any;
  job: any;
  onCancel: () => void;
  onResume: () => void;
  actionLoading: boolean;
}) {
  const terminal = ['failed', 'cancelled'].includes(job.status);
  const cancelling = job.status === 'cancelling';

  return (
    <div className="app-shell py-10 sm:py-14">
      <div className="mx-auto max-w-5xl">
        <div className="overflow-hidden rounded-3xl bg-slate-950 text-white shadow-2xl shadow-slate-950/20">
          <div className="relative overflow-hidden px-6 py-8 sm:px-10 sm:py-10">
            <div className="absolute -right-20 -top-32 h-80 w-80 rounded-full bg-indigo-500/20 blur-3xl" />
            <div className="relative flex flex-col justify-between gap-7 sm:flex-row sm:items-end">
              <div>
                <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-[10px] font-extrabold uppercase tracking-[0.16em] text-indigo-200">
                  {terminal ? <PauseCircle size={13} /> : <Loader2 size={13} className="animate-spin" />}
                  {job.status}
                </span>
                <h1 className="mt-5 max-w-2xl text-3xl font-black tracking-[-0.04em] sm:text-4xl">{plan.title || plan.idea}</h1>
                <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">{job.message}</p>
              </div>
              <div className="shrink-0 text-left sm:text-right">
                <strong className="text-5xl font-black tracking-tight text-cyan-300">{job.progress}%</strong>
                <p className="mt-1 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">attempt {job.attempts || 1}</p>
              </div>
            </div>
            <div className="relative mt-8 h-2 overflow-hidden rounded-full bg-white/10">
              <div className="h-full rounded-full bg-gradient-to-r from-indigo-500 via-cyan-400 to-emerald-400 transition-all duration-700" style={{ width: `${Math.max(2, job.progress)}%` }} />
            </div>
          </div>

          <div className="grid gap-px bg-white/10 md:grid-cols-2">
            {stages.map(({ id, label, detail, threshold, icon: Icon }) => {
              const complete = job.progress >= threshold;
              const active = !terminal && job.current_stage === id;
              return (
                <div key={id} className={`flex gap-4 bg-slate-950 px-6 py-5 sm:px-8 ${active ? 'bg-indigo-950/70' : ''}`}>
                  <span className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${complete ? 'bg-emerald-500 text-white' : active ? 'bg-indigo-500 text-white' : 'bg-white/5 text-slate-600'}`}>
                    {complete ? <Check size={18} /> : active ? <Loader2 size={18} className="animate-spin" /> : <Icon size={18} />}
                  </span>
                  <div><p className={`text-sm font-bold ${complete || active ? 'text-white' : 'text-slate-500'}`}>{label}</p><p className="mt-1 text-xs text-slate-500">{detail}</p></div>
                </div>
              );
            })}
          </div>

          <div className="flex flex-col justify-between gap-4 border-t border-white/10 bg-white/[0.03] px-6 py-5 sm:flex-row sm:items-center sm:px-10">
            <p className="text-xs leading-5 text-slate-500">Progress is saved after every agent. You can leave this page and return later.</p>
            {terminal ? (
              <button onClick={onResume} disabled={actionLoading} className="primary-button shrink-0 px-5 py-2.5 text-sm">
                {actionLoading ? <Loader2 size={16} className="animate-spin" /> : job.status === 'failed' ? <RefreshCw size={16} /> : <Play size={16} />}
                {job.status === 'failed' ? 'Retry from saved progress' : 'Resume generation'}
              </button>
            ) : (
              <button onClick={onCancel} disabled={actionLoading || cancelling} className="flex shrink-0 items-center justify-center gap-2 rounded-xl border border-white/10 px-4 py-2.5 text-sm font-bold text-slate-300 transition hover:border-rose-400/40 hover:bg-rose-500/10 hover:text-rose-300 disabled:opacity-50">
                {actionLoading || cancelling ? <Loader2 size={16} className="animate-spin" /> : <PauseCircle size={16} />}
                {cancelling ? 'Stopping safely…' : 'Cancel'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
