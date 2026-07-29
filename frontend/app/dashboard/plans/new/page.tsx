'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  ArrowLeft, ArrowRight, BarChart3, Building2, Check, CircleDollarSign,
  Gauge, Lightbulb, Loader2, ShieldAlert, Sparkles, TrendingUp,
} from 'lucide-react';
import { plans } from '@/lib/api';

const agents = [
  { icon: BarChart3, label: 'Market', color: 'text-cyan-600 bg-cyan-50' },
  { icon: Building2, label: 'Strategy', color: 'text-violet-600 bg-violet-50' },
  { icon: CircleDollarSign, label: 'Finance', color: 'text-emerald-600 bg-emerald-50' },
  { icon: ShieldAlert, label: 'Risk', color: 'text-amber-600 bg-amber-50' },
  { icon: TrendingUp, label: 'Growth', color: 'text-rose-600 bg-rose-50' },
  { icon: Gauge, label: 'Decision', color: 'text-indigo-600 bg-indigo-50' },
];

export default function NewPlanPage() {
  const router = useRouter();
  const [idea, setIdea] = useState('');
  const [title, setTitle] = useState('');
  const [extraInfo, setExtraInfo] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!idea.trim()) return;
    const token = localStorage.getItem('token');
    if (!token) return router.push('/auth/login');
    setLoading(true);
    setError('');
    try {
      const result = await plans.create(token, {
        idea: idea.trim(),
        title: title.trim() || undefined,
        extra_info: extraInfo.trim() || undefined,
      });
      router.push(`/dashboard/plans/${result.id}`);
    } catch (err: any) {
      setError(err.message || 'The analysis could not be completed. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="app-shell py-10 sm:py-14">
      <button onClick={() => router.push('/dashboard')} className="flex items-center gap-2 text-sm font-semibold text-slate-500 transition hover:text-slate-950"><ArrowLeft size={16} /> Venture workspace</button>

      <div className="mt-8 grid items-start gap-8 lg:grid-cols-[1fr_360px]">
        <section className="panel overflow-hidden">
          <div className="border-b border-slate-100 px-6 py-7 sm:px-9">
            <span className="eyebrow"><Sparkles size={13} /> New venture analysis</span>
            <h1 className="mt-4 text-3xl font-black tracking-[-0.035em] text-slate-950">What are you thinking of building?</h1>
            <p className="mt-2 text-slate-500">Give the agents enough context to challenge the idea, not just describe it.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-7 p-6 sm:p-9">
            <div>
              <label className="flex items-center justify-between text-sm font-bold text-slate-800">
                Venture idea <span className="text-xs font-medium text-slate-400">{idea.length}/2000</span>
              </label>
              <textarea
                value={idea}
                onChange={(event) => setIdea(event.target.value)}
                maxLength={2000}
                placeholder="Example: A B2B marketplace that connects small Ethiopian coffee farmers directly with specialty cafés, with quality verification and predictable logistics…"
                className="mt-3 min-h-44 w-full resize-y rounded-2xl border border-slate-200 bg-slate-50/60 px-5 py-4 leading-7 text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-indigo-400 focus:bg-white focus:ring-4 focus:ring-indigo-100"
                required
              />
              <p className="mt-2 flex items-center gap-2 text-xs text-slate-400"><Lightbulb size={13} /> Include the customer, problem, solution, and geography if you know them.</p>
            </div>

            <div className="grid gap-6 sm:grid-cols-2">
              <div>
                <label className="text-sm font-bold text-slate-800">Working title <span className="font-normal text-slate-400">(optional)</span></label>
                <input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Coffee Direct" className="mt-3 w-full rounded-xl border border-slate-200 px-4 py-3 outline-none transition focus:border-indigo-400 focus:ring-4 focus:ring-indigo-100" />
              </div>
              <div>
                <label className="text-sm font-bold text-slate-800">Founder context <span className="font-normal text-slate-400">(optional)</span></label>
                <input value={extraInfo} onChange={(event) => setExtraInfo(event.target.value)} placeholder="Location, budget, team, traction…" className="mt-3 w-full rounded-xl border border-slate-200 px-4 py-3 outline-none transition focus:border-indigo-400 focus:ring-4 focus:ring-indigo-100" />
              </div>
            </div>

            {error && <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{error}</div>}

            <button disabled={loading || !idea.trim()} className="primary-button w-full py-4 text-base">
              {loading ? <><Loader2 size={19} className="animate-spin" /> Building your venture brief…</> : <>Run venture analysis <ArrowRight size={19} /></>}
            </button>
          </form>
        </section>

        <aside className="space-y-5 lg:sticky lg:top-24">
          <div className="rounded-2xl bg-slate-950 p-6 text-white shadow-xl shadow-slate-950/10">
            <p className="text-xs font-bold uppercase tracking-[0.17em] text-slate-400">Analysis pipeline</p>
            <h2 className="mt-2 text-xl font-bold">Six agents. One decision.</h2>
            <div className="mt-6 grid grid-cols-2 gap-3">
              {agents.map(({ icon: Icon, label, color }, index) => (
                <div key={label} className="rounded-xl border border-white/10 bg-white/5 p-3">
                  <div className="flex items-center justify-between">
                    <span className={`flex h-8 w-8 items-center justify-center rounded-lg ${color}`}><Icon size={16} /></span>
                    {loading && <span className={`h-1.5 w-1.5 rounded-full ${index === 0 ? 'animate-pulse bg-cyan-300' : 'bg-slate-700'}`} />}
                  </div>
                  <p className="mt-3 text-xs font-bold">{label}</p>
                </div>
              ))}
            </div>
            <div className="mt-6 space-y-2 border-t border-white/10 pt-5">
              {['Scored viability decision', 'Prioritized risk matrix', 'PDF, deck & Excel exports'].map((item) => (
                <p key={item} className="flex items-center gap-2 text-xs text-slate-300"><Check size={14} className="text-emerald-400" />{item}</p>
              ))}
            </div>
          </div>
          <p className="px-2 text-center text-xs leading-5 text-slate-400">Your analysis runs safely in the background. You can leave the progress page and return at any time.</p>
        </aside>
      </div>
    </div>
  );
}
