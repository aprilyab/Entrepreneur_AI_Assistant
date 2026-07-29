'use client';

import { useEffect, useMemo, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  ArrowLeft, BadgeCheck, BarChart3, Building2, CalendarDays, Download,
  Beaker, FileSpreadsheet, FileText, Landmark, LayoutDashboard, Lightbulb,
  Loader2, MessageCircle, Presentation, Send, ShieldAlert, Sparkles,
  WalletCards,
} from 'lucide-react';
import { plans } from '@/lib/api';
import FormattedContent from '@/components/FormattedContent';
import PlanVisuals from '@/components/PlanVisuals';
import ValidationWorkspace from '@/components/ValidationWorkspace';
import GenerationProgress from '@/components/GenerationProgress';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type TabId = 'overview' | 'validate' | 'decision' | 'risks' | 'plan' | 'market' | 'model' | 'financials' | 'mentor';

export default function PlanDetailPage() {
  const router = useRouter();
  const params = useParams();
  const planId = params.id as string;
  const [plan, setPlan] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [chatMessage, setChatMessage] = useState('');
  const [chatMessages, setChatMessages] = useState<any[]>([]);
  const [chatLoading, setChatLoading] = useState(false);
  const [downloading, setDownloading] = useState('');
  const [generationJob, setGenerationJob] = useState<any>(null);
  const [generationActionLoading, setGenerationActionLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth/login');
      return;
    }
    plans.get(token, planId)
      .then((result) => {
        setPlan(result);
        setGenerationJob(result.generation_job || null);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [planId, router]);

  useEffect(() => {
    if (!generationJob || !['queued', 'running', 'cancelling'].includes(generationJob.status)) return;
    const token = localStorage.getItem('token');
    if (!token) return;

    const poll = async () => {
      try {
        const nextJob = await plans.generationStatus(token, planId);
        setGenerationJob(nextJob);
        if (nextJob.status === 'completed') {
          const completedPlan = await plans.get(token, planId);
          setPlan(completedPlan);
          setGenerationJob(completedPlan.generation_job || nextJob);
        }
      } catch (error) {
        console.error(error);
      }
    };
    const timer = window.setInterval(poll, 1500);
    return () => window.clearInterval(timer);
  }, [generationJob?.status, planId]);

  const cancelGeneration = async () => {
    const token = localStorage.getItem('token');
    if (!token) return;
    setGenerationActionLoading(true);
    try {
      setGenerationJob(await plans.cancelGeneration(token, planId));
    } finally {
      setGenerationActionLoading(false);
    }
  };

  const resumeGeneration = async () => {
    const token = localStorage.getItem('token');
    if (!token) return;
    setGenerationActionLoading(true);
    try {
      setGenerationJob(await plans.resumeGeneration(token, planId));
    } finally {
      setGenerationActionLoading(false);
    }
  };

  const verdict = useMemo(() => {
    if (!plan?.validation_strategy) return 'Decision pending';
    const match = plan.validation_strategy.match(/Verdict[:\s*#-]*\[?([A-Z][A-Z\s/-]+)\]?/i);
    return match?.[1]?.trim().replace(/\*+$/, '') || (plan.viability_score >= 75 ? 'Promising' : 'Needs validation');
  }, [plan]);

  const downloadExport = async (kind: 'pdf' | 'pptx' | 'excel') => {
    const token = localStorage.getItem('token');
    if (!token) return;
    setDownloading(kind);
    try {
      const response = await fetch(`${API_URL}/api/plans/${planId}/export/${kind}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error('Export failed');
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${plan.title || 'venture-plan'}.${kind === 'excel' ? 'xlsx' : kind}`;
      link.click();
      URL.revokeObjectURL(url);
    } finally {
      setDownloading('');
    }
  };

  const handleChat = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!chatMessage.trim() || chatLoading) return;
    const token = localStorage.getItem('token');
    if (!token) return;
    const message = chatMessage.trim();
    setChatMessages((current) => [...current, { role: 'user', content: message }]);
    setChatMessage('');
    setChatLoading(true);
    try {
      const response = await plans.chat(token, planId, message);
      setChatMessages((current) => [...current, { role: 'assistant', content: response.content }]);
    } catch {
      setChatMessages((current) => [...current, { role: 'assistant', content: 'I could not complete that response. Please try again.' }]);
    } finally {
      setChatLoading(false);
    }
  };

  if (loading) {
    return <div className="flex min-h-[60vh] flex-col items-center justify-center"><Loader2 className="animate-spin text-indigo-600" size={34} /><p className="mt-4 text-sm font-medium text-slate-500">Opening venture brief…</p></div>;
  }

  if (!plan) {
    return <div className="app-shell py-20 text-center"><h1 className="text-2xl font-black">Plan not found</h1><button onClick={() => router.push('/dashboard')} className="secondary-button mt-6">Back to workspace</button></div>;
  }

  if (generationJob && generationJob.status !== 'completed') {
    return <GenerationProgress plan={plan} job={generationJob} onCancel={cancelGeneration} onResume={resumeGeneration} actionLoading={generationActionLoading} />;
  }

  const identity = plan.intelligence?.identity || {};
  const score = plan.intelligence?.adjusted_score?.adjusted_score ?? plan.viability_score ?? 0;
  const scoreTone = score >= 75 ? 'text-emerald-600' : score >= 50 ? 'text-amber-600' : 'text-rose-600';
  const scoreArc = score >= 75 ? '#10b981' : score >= 50 ? '#f59e0b' : '#f43f5e';

  const tabs = ([
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'validate', label: 'Validate', icon: Beaker },
    { id: 'decision', label: 'Decision', icon: BadgeCheck, show: !!plan.validation_strategy },
    { id: 'risks', label: 'Risks', icon: ShieldAlert, show: !!plan.risks },
    { id: 'plan', label: 'Full plan', icon: FileText, show: !!plan.full_plan },
    { id: 'market', label: 'Market', icon: BarChart3, show: !!plan.market_analysis },
    { id: 'model', label: 'Business model', icon: Building2, show: !!plan.business_model },
    { id: 'financials', label: 'Financials', icon: WalletCards, show: !!plan.financials },
    { id: 'mentor', label: 'AI mentor', icon: MessageCircle },
  ] as { id: TabId; label: string; icon: any; show?: boolean }[]).filter((tab) => tab.show !== false);

  return (
    <div className="pb-20">
      <section className="border-b border-slate-200 bg-white">
        <div className="app-shell py-8 sm:py-10">
          <button onClick={() => router.push('/dashboard')} className="flex items-center gap-2 text-sm font-semibold text-slate-500 transition hover:text-slate-950"><ArrowLeft size={16} /> Venture workspace</button>
          <div className="mt-7 flex flex-col justify-between gap-7 lg:flex-row lg:items-end">
            <div className="max-w-3xl">
              <div className="flex flex-wrap items-center gap-3">
                <span className="eyebrow"><Sparkles size={13} /> Decision-ready brief</span>
                <span className="flex items-center gap-1.5 text-xs font-medium text-slate-400"><CalendarDays size={14} />{new Date(plan.created_at).toLocaleDateString()}</span>
              </div>
              <h1 className="mt-4 text-3xl font-black tracking-[-0.04em] text-slate-950 sm:text-4xl">{plan.title || plan.idea}</h1>
              <p className="mt-2 text-xs font-bold uppercase tracking-[0.14em] text-indigo-500">{identity.subtitle || 'Venture concept'}</p>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">{identity.one_liner || plan.idea}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button onClick={() => downloadExport('pdf')} className="secondary-button px-4 py-2.5 text-sm"><Download size={16} /> PDF</button>
              <button onClick={() => downloadExport('pptx')} className="secondary-button px-4 py-2.5 text-sm"><Presentation size={16} /> Deck</button>
              <button onClick={() => downloadExport('excel')} className="secondary-button px-4 py-2.5 text-sm"><FileSpreadsheet size={16} /> Excel</button>
              {downloading && <span className="flex items-center px-2 text-xs text-slate-400"><Loader2 size={14} className="mr-1 animate-spin" />Preparing</span>}
            </div>
          </div>
        </div>
        <div className="app-shell overflow-x-auto">
          <nav className="flex min-w-max gap-1">
            {tabs.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`relative flex items-center gap-2 px-4 py-3.5 text-sm font-semibold transition ${activeTab === id ? 'text-indigo-700' : 'text-slate-500 hover:text-slate-900'}`}
              >
                <Icon size={16} />{label}
                {activeTab === id && <span className="absolute inset-x-3 bottom-0 h-0.5 rounded-full bg-indigo-600" />}
              </button>
            ))}
          </nav>
        </div>
      </section>

      <div className="app-shell pt-8">
        {activeTab === 'overview' && (
          <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
            <aside className="space-y-5">
              <div className="panel p-6">
                <p className="text-xs font-bold uppercase tracking-[0.16em] text-slate-400">Viability score</p>
                <div className="mt-5 flex items-center gap-5">
                  <div className="relative flex h-28 w-28 shrink-0 items-center justify-center rounded-full" style={{ background: `conic-gradient(${scoreArc} 0 ${score}%, #e2e8f0 ${score}% 100%)` }}>
                    <div className="flex h-[88px] w-[88px] flex-col items-center justify-center rounded-full bg-white">
                      <strong className={`text-3xl font-black ${scoreTone}`}>{score}</strong>
                      <span className="text-[9px] font-bold uppercase tracking-wider text-slate-400">out of 100</span>
                    </div>
                  </div>
                  <div>
                    <span className={`text-xs font-extrabold uppercase tracking-wider ${scoreTone}`}>{verdict}</span>
                    <p className="mt-2 text-xs leading-5 text-slate-500">Use the decision report to see what drives this score.</p>
                  </div>
                </div>
                <button onClick={() => setActiveTab('decision')} className="mt-5 w-full rounded-xl bg-slate-950 px-4 py-3 text-sm font-bold text-white transition hover:bg-indigo-700">Open decision report</button>
              </div>
              <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5">
                <div className="flex items-center gap-2 font-bold text-amber-900"><ShieldAlert size={18} /> Risk review</div>
                <p className="mt-2 text-sm leading-6 text-amber-800/80">Critical, high, and medium risks now have their own complete report.</p>
                <button onClick={() => setActiveTab('risks')} className="mt-3 text-sm font-bold text-amber-900 underline decoration-amber-400 underline-offset-4">Review risks</button>
              </div>
            </aside>

            <div className="space-y-6">
              <PlanVisuals kind="overview" plan={plan} />
              <div className="panel p-6 sm:p-8">
                <div className="flex items-center gap-3">
                  <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600"><Lightbulb size={20} /></span>
                  <div><p className="text-xs font-bold uppercase tracking-wider text-slate-400">Venture thesis</p><h2 className="font-bold text-slate-950">What you are building</h2></div>
                </div>
                <p className="mt-5 text-lg leading-8 text-slate-600">{identity.one_liner || plan.idea}</p>
                {identity.one_liner && <p className="mt-3 text-xs leading-5 text-slate-400"><strong>Original founder brief:</strong> {plan.idea}</p>}
                {plan.extra_info && <div className="mt-5 rounded-xl bg-slate-50 p-4 text-sm leading-6 text-slate-500"><strong className="text-slate-700">Founder context:</strong> {plan.extra_info}</div>}
                {!!plan.intelligence?.capability_claims?.length && (
                  <div className="mt-6 border-t border-slate-100 pt-5">
                    <p className="text-xs font-bold uppercase tracking-[0.14em] text-slate-400">Claim maturity</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {plan.intelligence.capability_claims.slice(0, 8).map((claim: any, index: number) => (
                        <span key={`${claim.capability}-${index}`} title={claim.evidence} className={`rounded-full px-3 py-1.5 text-xs font-bold ${claim.status === 'existing' ? 'bg-emerald-100 text-emerald-800' : claim.status === 'assumption' ? 'bg-amber-100 text-amber-800' : 'bg-indigo-100 text-indigo-800'}`}>
                          {claim.capability} · {claim.status}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              <div className="grid gap-4 sm:grid-cols-3">
                {[
                  { icon: BarChart3, title: 'Market case', text: 'Demand, customer segments, trends and competitive whitespace.', tab: 'market' as TabId, tone: 'bg-cyan-50 text-cyan-600' },
                  { icon: Landmark, title: 'Business model', text: 'Value proposition, revenue engine, channels and moat.', tab: 'model' as TabId, tone: 'bg-violet-50 text-violet-600' },
                  { icon: Beaker, title: 'Validation workspace', text: 'Test assumptions, verify evidence, and record real experiment results.', tab: 'validate' as TabId, tone: 'bg-emerald-50 text-emerald-600' },
                ].map(({ icon: Icon, title, text, tab, tone }) => (
                  <button key={title} onClick={() => setActiveTab(tab)} className="panel p-5 text-left transition hover:-translate-y-1 hover:border-indigo-200">
                    <span className={`flex h-10 w-10 items-center justify-center rounded-xl ${tone}`}><Icon size={19} /></span>
                    <h3 className="mt-4 font-bold text-slate-900">{title}</h3>
                    <p className="mt-2 text-xs leading-5 text-slate-500">{text}</p>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'validate' && <ValidationWorkspace planId={planId} plan={plan} onPlanUpdated={setPlan} />}
        {activeTab === 'decision' && <ReportPanel icon={BadgeCheck} eyebrow="Go / no-go analysis" title="Decision & validation report" intro="The score is only the headline. This report shows its drivers, red flags, validation tests, and recommended next moves." content={plan.validation_strategy} tone="indigo" visual={<PlanVisuals kind="decision" plan={plan} />} />}
        {activeTab === 'risks' && <ReportPanel icon={ShieldAlert} eyebrow="Downside intelligence" title="Risk assessment & mitigation" intro="Risks are prioritized by severity and paired with concrete mitigation actions and timing." content={plan.risks} tone="amber" visual={<PlanVisuals kind="risks" plan={plan} />} />}
        {activeTab === 'plan' && <ReportPanel icon={FileText} eyebrow="Compiled output" title="Investor-ready business plan" intro="The complete narrative assembled from every specialist agent." content={plan.full_plan} tone="slate" visual={<PlanVisuals kind="plan" plan={plan} />} />}
        {activeTab === 'market' && <ReportPanel icon={BarChart3} eyebrow="Market intelligence" title="Market analysis" intro="Market size, target customers, competitors, trends, and whitespace." content={plan.market_analysis} tone="cyan" visual={<PlanVisuals kind="market" plan={plan} />} />}
        {activeTab === 'model' && <ReportPanel icon={Building2} eyebrow="Venture architecture" title="Business model & strategy" intro="How the venture creates, delivers, and captures value." content={plan.business_model} tone="violet" visual={<PlanVisuals kind="model" plan={plan} />} />}
        {activeTab === 'financials' && <ReportPanel icon={WalletCards} eyebrow="Economic model" title="Financial outlook" intro="Revenue assumptions, cost structure, unit economics, projections, and funding needs." content={plan.financials} tone="emerald" visual={<PlanVisuals kind="financials" plan={plan} />} />}

        {activeTab === 'mentor' && (
          <div className="mx-auto max-w-4xl">
            <div className="panel overflow-hidden">
              <div className="border-b border-slate-100 bg-slate-950 px-6 py-5 text-white">
                <div className="flex items-center gap-3"><span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500"><MessageCircle size={19} /></span><div><h2 className="font-bold">Venture mentor</h2><p className="text-xs text-slate-400">Ask questions grounded in this plan</p></div></div>
              </div>
              <div className="min-h-[360px] space-y-4 p-5 sm:p-7">
                {chatMessages.length === 0 && (
                  <div className="flex min-h-72 flex-col items-center justify-center text-center">
                    <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600"><Sparkles size={24} /></span>
                    <h3 className="mt-5 font-bold text-slate-900">Pressure-test the plan</h3>
                    <p className="mt-2 max-w-sm text-sm leading-6 text-slate-500">Ask about pricing, your biggest assumption, the first 30 days, investor objections, or a specific risk.</p>
                  </div>
                )}
                {chatMessages.map((message, index) => (
                  <div key={index} className={`max-w-[88%] rounded-2xl px-4 py-3 ${message.role === 'user' ? 'ml-auto bg-indigo-600 text-white' : 'bg-slate-100 text-slate-700'}`}>
                    <p className="mb-1 text-[10px] font-bold uppercase tracking-wider opacity-60">{message.role === 'user' ? 'You' : 'Venture mentor'}</p>
                    <div className={message.role === 'assistant' ? '' : 'whitespace-pre-wrap text-sm'}>{message.role === 'assistant' ? <FormattedContent content={message.content} compact /> : message.content}</div>
                  </div>
                ))}
                {chatLoading && <div className="flex max-w-[70%] items-center gap-2 rounded-2xl bg-slate-100 px-4 py-4 text-sm text-slate-500"><Loader2 size={16} className="animate-spin" />Analyzing your plan…</div>}
              </div>
              <form onSubmit={handleChat} className="flex gap-3 border-t border-slate-100 bg-slate-50 p-4">
                <input value={chatMessage} onChange={(event) => setChatMessage(event.target.value)} placeholder="Ask a strategic follow-up…" className="min-w-0 flex-1 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition placeholder:text-slate-400 focus:border-indigo-400 focus:ring-4 focus:ring-indigo-100" />
                <button disabled={!chatMessage.trim() || chatLoading} className="primary-button px-4"><Send size={17} /><span className="hidden sm:inline">Send</span></button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function ReportPanel({ icon: Icon, eyebrow, title, intro, content, tone, visual }: any) {
  const tones: Record<string, string> = {
    indigo: 'bg-indigo-50 text-indigo-600',
    amber: 'bg-amber-50 text-amber-600',
    slate: 'bg-slate-100 text-slate-700',
    cyan: 'bg-cyan-50 text-cyan-600',
    violet: 'bg-violet-50 text-violet-600',
    emerald: 'bg-emerald-50 text-emerald-600',
  };
  return (
    <article className="mx-auto max-w-5xl overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <header className="border-b border-slate-100 px-6 py-7 sm:px-10 sm:py-9">
        <div className="flex items-start gap-4">
          <span className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl ${tones[tone]}`}><Icon size={23} /></span>
          <div><p className="text-xs font-bold uppercase tracking-[0.16em] text-slate-400">{eyebrow}</p><h2 className="mt-1 text-2xl font-black tracking-tight text-slate-950 sm:text-3xl">{title}</h2><p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">{intro}</p></div>
        </div>
      </header>
      {visual && <div className="border-b border-slate-100 bg-slate-50/70 px-4 py-5 sm:px-8 sm:py-7">{visual}</div>}
      <div className="px-6 py-7 sm:px-10 sm:py-10">
        {content ? <FormattedContent content={content} /> : <p className="text-slate-500">This section is not available for this plan.</p>}
      </div>
    </article>
  );
}
