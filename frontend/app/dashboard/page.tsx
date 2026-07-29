'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, CalendarDays, FileText, Plus, Sparkles, Trash2, TrendingUp } from 'lucide-react';
import { plans as plansApi } from '@/lib/api';

export default function DashboardPage() {
  const router = useRouter();
  const [planList, setPlanList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth/login');
      return;
    }
    plansApi.list(token).then(setPlanList).catch(console.error).finally(() => setLoading(false));
  }, [router]);

  const deletePlan = async (event: React.MouseEvent, id: string) => {
    event.stopPropagation();
    const token = localStorage.getItem('token');
    if (!token || !confirm('Delete this venture plan? This cannot be undone.')) return;
    await plansApi.delete(token, id);
    setPlanList((current) => current.filter((plan) => plan.id !== id));
  };

  const scoredPlans = planList.filter((plan) => plan.status === 'complete' && plan.viability_score);
  const averageScore = scoredPlans.length
    ? Math.round(scoredPlans.reduce((total, plan) => total + plan.viability_score, 0) / scoredPlans.length)
    : 0;

  const scoreStyle = (score: number | null) => {
    if (!score) return 'bg-slate-100 text-slate-500';
    if (score >= 75) return 'bg-emerald-50 text-emerald-700 ring-emerald-200';
    if (score >= 50) return 'bg-amber-50 text-amber-700 ring-amber-200';
    return 'bg-rose-50 text-rose-700 ring-rose-200';
  };

  const statusDot = (status: string) => {
    if (status === 'complete') return 'bg-emerald-500';
    if (status === 'error' || status === 'failed') return 'bg-rose-500';
    if (status === 'cancelled') return 'bg-amber-500';
    return 'animate-pulse bg-indigo-500';
  };

  return (
    <div className="app-shell py-10 sm:py-14">
      <div className="flex flex-col justify-between gap-6 sm:flex-row sm:items-end">
        <div>
          <span className="eyebrow"><Sparkles size={13} /> Venture workspace</span>
          <h1 className="mt-4 text-4xl font-black tracking-[-0.04em] text-slate-950">Your venture portfolio</h1>
          <p className="mt-2 text-slate-500">Review decisions, compare scores, and keep moving the strongest ideas forward.</p>
        </div>
        <a href="/dashboard/plans/new" className="primary-button"><Plus size={18} /> New analysis</a>
      </div>

      {!loading && planList.length > 0 && (
        <div className="mt-9 grid gap-4 sm:grid-cols-3">
          {[
            { label: 'Ideas analyzed', value: planList.length, icon: FileText, tint: 'bg-indigo-50 text-indigo-600' },
            { label: 'Average viability', value: `${averageScore}/100`, icon: TrendingUp, tint: 'bg-emerald-50 text-emerald-600' },
            { label: 'Decision-ready', value: planList.filter((p) => p.status === 'complete').length, icon: Sparkles, tint: 'bg-cyan-50 text-cyan-600' },
          ].map(({ label, value, icon: Icon, tint }) => (
            <div key={label} className="panel flex items-center gap-4 p-5">
              <span className={`flex h-11 w-11 items-center justify-center rounded-xl ${tint}`}><Icon size={20} /></span>
              <div><p className="text-2xl font-black text-slate-950">{value}</p><p className="text-sm text-slate-500">{label}</p></div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-10">
        {loading ? (
          <div className="panel flex min-h-64 flex-col items-center justify-center">
            <div className="h-9 w-9 animate-spin rounded-full border-[3px] border-indigo-600 border-t-transparent" />
            <p className="mt-4 text-sm font-medium text-slate-500">Loading your workspace…</p>
          </div>
        ) : planList.length === 0 ? (
          <div className="panel relative overflow-hidden px-6 py-20 text-center">
            <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-indigo-500 via-cyan-400 to-emerald-400" />
            <span className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600"><Sparkles size={28} /></span>
            <h2 className="mt-6 text-2xl font-black tracking-tight text-slate-950">Your first decision starts here</h2>
            <p className="mx-auto mt-3 max-w-md text-slate-500">Describe a venture idea and let six agents turn it into a scored, risk-aware action plan.</p>
            <a href="/dashboard/plans/new" className="primary-button mt-7">Analyze an idea <ArrowRight size={18} /></a>
          </div>
        ) : (
          <div className="grid gap-5 lg:grid-cols-2">
            {planList.map((plan) => (
              <article
                key={plan.id}
                onClick={() => router.push(`/dashboard/plans/${plan.id}`)}
                className="panel group cursor-pointer p-6 transition hover:-translate-y-1 hover:border-indigo-200 hover:shadow-xl hover:shadow-indigo-950/5"
              >
                <div className="flex items-start justify-between gap-5">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className={`h-2 w-2 rounded-full ${statusDot(plan.status)}`} />
                      <span className="text-xs font-bold uppercase tracking-[0.15em] text-slate-400">{plan.status}</span>
                    </div>
                    <h2 className="mt-4 truncate text-xl font-extrabold tracking-tight text-slate-950">{plan.title || plan.idea}</h2>
                    <p className="mt-2 line-clamp-2 min-h-12 text-sm leading-6 text-slate-500">{plan.idea}</p>
                  </div>
                  <div className={`flex h-16 w-16 shrink-0 flex-col items-center justify-center rounded-2xl ring-1 ${scoreStyle(plan.viability_score)}`}>
                    <strong className="text-xl">{plan.viability_score || '—'}</strong>
                    <span className="text-[9px] font-bold uppercase tracking-wider">score</span>
                  </div>
                </div>
                <div className="mt-6 flex items-center justify-between border-t border-slate-100 pt-4">
                  <span className="flex items-center gap-2 text-xs font-medium text-slate-400"><CalendarDays size={14} />{new Date(plan.created_at).toLocaleDateString()}</span>
                  <div className="flex items-center gap-2">
                    <button onClick={(event) => deletePlan(event, plan.id)} className="rounded-lg p-2 text-slate-300 transition hover:bg-rose-50 hover:text-rose-600" aria-label="Delete plan"><Trash2 size={16} /></button>
                    <span className="flex items-center gap-1 text-sm font-bold text-indigo-600">Open brief <ArrowRight size={15} className="transition group-hover:translate-x-1" /></span>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
