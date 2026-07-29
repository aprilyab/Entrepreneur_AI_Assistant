'use client';

import { useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle, Beaker, BookOpenCheck, Check, ExternalLink, Gauge,
  Loader2, Plus, RefreshCw, Save, Trash2,
} from 'lucide-react';
import { plans } from '@/lib/api';

type WorkspaceTab = 'assumptions' | 'evidence' | 'experiments';

const fieldClass = 'w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 outline-none transition focus:border-indigo-400 focus:ring-4 focus:ring-indigo-100';

function confidenceTone(confidence: number) {
  if (confidence >= 70) return 'bg-emerald-100 text-emerald-700';
  if (confidence >= 40) return 'bg-amber-100 text-amber-700';
  return 'bg-rose-100 text-rose-700';
}

function isSafeExternalUrl(value: string) {
  return /^https?:\/\//i.test(value || '');
}

export default function ValidationWorkspace({ planId, plan, onPlanUpdated }: { planId: string; plan: any; onPlanUpdated?: (plan: any) => void }) {
  const [active, setActive] = useState<WorkspaceTab>('assumptions');
  const [assumptions, setAssumptions] = useState<any[]>(plan.assumptions || []);
  const [evidence, setEvidence] = useState<any[]>(plan.evidence_claims || []);
  const [experiments, setExperiments] = useState<any[]>(plan.experiments || []);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState('');
  const [notice, setNotice] = useState('');
  const [expandedEvidence, setExpandedEvidence] = useState<Set<string>>(new Set());

  const token = () => localStorage.getItem('token') || '';

  useEffect(() => {
    if (assumptions.length || evidence.length || experiments.length) return;
    setLoading(true);
    plans.bootstrapValidationWorkspace(token(), planId)
      .then((result) => {
        setAssumptions(result.assumptions || []);
        setEvidence(result.evidence_claims || []);
        setExperiments(result.experiments || []);
      })
      .catch((error) => setNotice(error.message || 'Could not initialize validation workspace.'))
      .finally(() => setLoading(false));
  // The workspace should bootstrap only once for the opened plan.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [planId]);

  const metrics = useMemo(() => ({
    highRisk: assumptions.filter((item) => item.impact === 'high' && item.status === 'untested').length,
    verified: evidence.filter((item) => item.status === 'verified').length,
    sourced: evidence.filter((item) => item.source_url).length,
    evidenceTotal: evidence.length,
    completed: experiments.filter((item) => ['passed', 'failed', 'inconclusive'].includes(item.status)).length,
    ready: experiments.filter((item) => item.hypothesis && item.method && item.success_metric && !/define|tbd|unknown/i.test(item.success_metric)).length,
    resultsRecorded: experiments.filter((item) => ['passed', 'failed', 'inconclusive'].includes(item.status) && item.result?.trim()).length,
    experimentsTotal: experiments.length,
  }), [assumptions, evidence, experiments]);

  const patchItem = (setter: any, id: string, patch: any) => {
    setter((items: any[]) => items.map((item) => item.id === id ? { ...item, ...patch } : item));
  };

  const toggleEvidence = (id: string) => {
    setExpandedEvidence((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const saveAssumption = async (item: any) => {
    setSaving(item.id);
    try {
      const updated = await plans.updateAssumption(token(), planId, item.id, item);
      patchItem(setAssumptions, item.id, updated);
      setNotice('Assumption saved.');
    } catch (error: any) {
      setNotice(error.message || 'Could not save assumption.');
    } finally {
      setSaving('');
    }
  };

  const saveEvidence = async (item: any) => {
    setSaving(item.id);
    try {
      const updated = await plans.updateEvidence(token(), planId, item.id, item);
      patchItem(setEvidence, item.id, updated);
      setNotice('Evidence saved.');
    } catch (error: any) {
      setNotice(error.message || 'Could not save evidence.');
    } finally {
      setSaving('');
    }
  };

  const verifyEvidence = async (item: any) => {
    if (!isSafeExternalUrl(item.source_url)) {
      setNotice('Open and review a valid source URL before marking this claim verified.');
      return;
    }
    const verified = {
      ...item,
      status: 'verified',
      confidence: Math.max(70, Number(item.confidence || 0)),
      notes: `${item.notes ? `${item.notes} · ` : ''}Manually reviewed ${new Date().toLocaleDateString()}`,
    };
    patchItem(setEvidence, item.id, verified);
    setSaving(item.id);
    try {
      const updated = await plans.updateEvidence(token(), planId, item.id, verified);
      patchItem(setEvidence, item.id, updated);
      setNotice('Source marked as manually verified. The evidence-adjusted score was recalculated.');
    } catch (error: any) {
      setNotice(error.message || 'Could not verify evidence.');
    } finally {
      setSaving('');
    }
  };

  const saveExperiment = async (item: any) => {
    setSaving(item.id);
    try {
      const updated = await plans.updateExperiment(token(), planId, item.id, item);
      patchItem(setExperiments, item.id, updated);
      setNotice('Experiment saved.');
    } catch (error: any) {
      setNotice(error.message || 'Could not save experiment.');
    } finally {
      setSaving('');
    }
  };

  const addItem = async () => {
    setLoading(true);
    try {
      if (active === 'assumptions') {
        const item = await plans.createAssumption(token(), planId, {
          name: 'New assumption', value: 'Unknown', category: 'business',
          source_type: 'founder_estimate', confidence: 10, impact: 'high',
          status: 'untested', validation_method: 'Describe how this will be tested.',
        });
        setAssumptions((items) => [...items, item]);
      } else if (active === 'evidence') {
        const item = await plans.createEvidence(token(), planId, {
          claim: 'New claim to verify', status: 'unverified', confidence: 10,
          notes: 'Attach a reliable primary source.',
        });
        setEvidence((items) => [...items, item]);
      } else {
        const item = await plans.createExperiment(token(), planId, {
          title: 'New validation experiment', hypothesis: 'State the belief being tested.',
          method: 'Describe the smallest credible test.', success_metric: 'Define a numeric pass/fail threshold.',
          status: 'planned', priority: 'high',
        });
        setExperiments((items) => [...items, item]);
      }
      setNotice('New item added.');
    } catch (error: any) {
      setNotice(error.message || 'Could not add item.');
    } finally {
      setLoading(false);
    }
  };

  const refreshResearch = async () => {
    setLoading(true);
    setNotice('Searching the live web and rebuilding cited market evidence…');
    try {
      const result = await plans.refreshResearch(token(), planId);
      setEvidence(result.evidence_claims || []);
      onPlanUpdated?.(result);
      setNotice(`Research refreshed: ${(result.evidence_claims || []).filter((item: any) => item.source_url).length} cited claims are now linked. The market report and confidence score are updated.`);
    } catch (error: any) {
      setNotice(error.message || 'Live research could not be refreshed.');
    } finally {
      setLoading(false);
    }
  };

  const removeItem = async (kind: WorkspaceTab, id: string) => {
    if (!window.confirm('Remove this item from the validation workspace?')) return;
    setSaving(id);
    try {
      if (kind === 'assumptions') {
        await plans.deleteAssumption(token(), planId, id);
        setAssumptions((items) => items.filter((item) => item.id !== id));
      } else if (kind === 'evidence') {
        await plans.deleteEvidence(token(), planId, id);
        setEvidence((items) => items.filter((item) => item.id !== id));
      } else {
        await plans.deleteExperiment(token(), planId, id);
        setExperiments((items) => items.filter((item) => item.id !== id));
      }
      setNotice('Item removed.');
    } catch (error: any) {
      setNotice(error.message || 'Could not remove item.');
    } finally {
      setSaving('');
    }
  };

  const tabs = [
    { id: 'assumptions' as const, label: 'Assumptions', count: assumptions.length, icon: Gauge },
    { id: 'evidence' as const, label: 'Evidence', count: evidence.length, icon: BookOpenCheck },
    { id: 'experiments' as const, label: 'Experiments', count: experiments.length, icon: Beaker },
  ];

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-2xl bg-slate-950 text-white shadow-xl shadow-slate-950/10">
        <div className="grid gap-px bg-white/10 sm:grid-cols-2 lg:grid-cols-4">
          <Metric label="High-risk assumptions" value={metrics.highRisk} detail="still untested" tone="text-rose-300" />
          <Metric label="Linked sources" value={`${metrics.sourced}/${metrics.evidenceTotal}`} detail="claims with citations" tone="text-cyan-300" />
          <Metric label="Founder verified" value={metrics.verified} detail="sources manually reviewed" tone="text-violet-300" />
          <Metric label="Completed tests" value={`${metrics.completed}/${metrics.experimentsTotal}`} detail="experiments concluded" tone="text-emerald-300" />
        </div>
      </section>

      <section className="panel overflow-hidden">
        <header className="flex flex-col gap-4 border-b border-slate-100 px-5 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-7">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-indigo-500">Evidence before confidence</p>
            <h2 className="mt-1 text-xl font-black text-slate-950">Validation workspace</h2>
          </div>
          <div className="flex flex-wrap gap-2">
            {active === 'evidence' && <button onClick={refreshResearch} disabled={loading} className="secondary-button px-4 py-2.5 text-sm">{loading ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}Research live sources</button>}
            <button onClick={addItem} disabled={loading} className="primary-button px-4 py-2.5 text-sm">
              {loading ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />} Add {active.slice(0, -1)}
            </button>
          </div>
        </header>

        <div className="flex overflow-x-auto border-b border-slate-100 bg-slate-50 px-3 sm:px-6">
          {tabs.map(({ id, label, count, icon: Icon }) => (
            <button key={id} onClick={() => setActive(id)} className={`flex items-center gap-2 border-b-2 px-4 py-4 text-sm font-bold transition ${active === id ? 'border-indigo-600 text-indigo-700' : 'border-transparent text-slate-500 hover:text-slate-900'}`}>
              <Icon size={16} />{label}<span className="rounded-full bg-slate-200 px-2 py-0.5 text-[10px] text-slate-600">{count}</span>
            </button>
          ))}
        </div>

        {notice && <div className="mx-5 mt-5 flex items-center gap-2 rounded-xl border border-indigo-100 bg-indigo-50 px-4 py-3 text-sm text-indigo-700 sm:mx-7"><Check size={15} />{notice}</div>}

        <div className="space-y-4 p-5 sm:p-7">
          {active === 'experiments' && (
            <div className="grid gap-3 rounded-2xl border border-indigo-100 bg-indigo-50 p-4 sm:grid-cols-3">
              <MetricMini label="Ready to run" value={`${metrics.ready}/${metrics.experimentsTotal}`} />
              <MetricMini label="Tests concluded" value={`${metrics.completed}/${metrics.experimentsTotal}`} />
              <MetricMini label="Decisions recorded" value={`${metrics.resultsRecorded}/${metrics.completed || 0}`} />
            </div>
          )}
          {active === 'assumptions' && assumptions.map((item) => (
            <article key={item.id} className="rounded-2xl border border-slate-200 p-5">
              <div className="grid gap-4 md:grid-cols-[1.4fr_0.7fr_0.55fr]">
                <Field label="Assumption"><input className={fieldClass} value={item.name} onChange={(event) => patchItem(setAssumptions, item.id, { name: event.target.value })} /></Field>
                <Field label="Current value"><input className={fieldClass} value={item.value} onChange={(event) => patchItem(setAssumptions, item.id, { value: event.target.value })} /></Field>
                <Field label="Impact"><select className={fieldClass} value={item.impact} onChange={(event) => patchItem(setAssumptions, item.id, { impact: event.target.value })}><option>high</option><option>medium</option><option>low</option></select></Field>
              </div>
              <div className="mt-4 grid gap-4 md:grid-cols-[1fr_0.7fr_0.7fr]">
                <Field label="How will you validate it?"><input className={fieldClass} value={item.validation_method || ''} onChange={(event) => patchItem(setAssumptions, item.id, { validation_method: event.target.value })} /></Field>
                <Field label="Status"><select className={fieldClass} value={item.status} onChange={(event) => patchItem(setAssumptions, item.id, { status: event.target.value })}><option>untested</option><option>testing</option><option>validated</option><option>rejected</option></select></Field>
                <Field label={`Confidence · ${item.confidence}%`}><input type="range" min="0" max="100" value={item.confidence} onChange={(event) => patchItem(setAssumptions, item.id, { confidence: Number(event.target.value) })} className="mt-3 w-full accent-indigo-600" /></Field>
              </div>
              <CardActions id={item.id} saving={saving} onSave={() => saveAssumption(item)} onDelete={() => removeItem('assumptions', item.id)} />
            </article>
          ))}

          {active === 'evidence' && evidence.map((item) => (
            <article key={item.id} className="rounded-2xl border border-slate-200 p-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <span className={`rounded-full px-3 py-1 text-[10px] font-extrabold uppercase tracking-wider ${item.status === 'verified' ? 'bg-emerald-100 text-emerald-700' : item.status === 'sourced' ? 'bg-cyan-100 text-cyan-700' : item.status === 'disputed' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700'}`}>{item.status}</span>
                <div className="flex items-center gap-2">
                  <span className={`rounded-full px-3 py-1 text-[10px] font-bold ${confidenceTone(item.confidence)}`}>{item.confidence}% {item.status === 'sourced' ? 'source quality' : 'confidence'}</span>
                  <button onClick={() => toggleEvidence(item.id)} className="rounded-lg border border-slate-200 px-3 py-1 text-[10px] font-bold text-slate-500 hover:border-indigo-200 hover:text-indigo-700">
                    {expandedEvidence.has(item.id) ? 'Close editor' : 'Edit details'}
                  </button>
                </div>
              </div>
              <p className="mt-4 text-sm font-semibold leading-6 text-slate-800">{item.claim}</p>
              <p className="mt-2 line-clamp-2 text-xs text-slate-500">{item.source_title || 'No source attached'}</p>
              {isSafeExternalUrl(item.source_url) && item.status !== 'verified' && (
                <div className="mt-3 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-cyan-100 bg-cyan-50 px-4 py-3">
                  <p className="text-xs leading-5 text-cyan-900">Open the source, confirm it supports this exact claim, then record your review.</p>
                  <div className="flex gap-2">
                    <a href={item.source_url} target="_blank" rel="noreferrer" className="secondary-button px-3 py-2 text-xs"><ExternalLink size={14} />Review source</a>
                    <button onClick={() => verifyEvidence(item)} disabled={saving === item.id} className="primary-button px-3 py-2 text-xs"><BookOpenCheck size={14} />Mark verified</button>
                  </div>
                </div>
              )}
              {expandedEvidence.has(item.id) && (
                <>
                  <div className="mt-4"><Field label="Claim"><textarea className={`${fieldClass} min-h-20 resize-y`} value={item.claim} onChange={(event) => patchItem(setEvidence, item.id, { claim: event.target.value })} /></Field></div>
                  <div className="mt-4 grid gap-4 md:grid-cols-2">
                    <Field label="Source title"><input className={fieldClass} value={item.source_title || ''} placeholder="Publisher or report" onChange={(event) => patchItem(setEvidence, item.id, { source_title: event.target.value })} /></Field>
                    <Field label="Source URL"><div className="flex gap-2"><input className={fieldClass} value={item.source_url || ''} placeholder="https://…" onChange={(event) => patchItem(setEvidence, item.id, { source_url: event.target.value })} />{isSafeExternalUrl(item.source_url) && <a href={item.source_url} target="_blank" rel="noreferrer" className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-slate-200 text-slate-500 hover:text-indigo-600"><ExternalLink size={15} /></a>}</div></Field>
                  </div>
                  <div className="mt-4 grid gap-4 md:grid-cols-[0.7fr_0.7fr_1fr]">
                    <Field label="Status"><select className={fieldClass} value={item.status} onChange={(event) => patchItem(setEvidence, item.id, { status: event.target.value })}><option>unverified</option><option>sourced</option><option>verified</option><option>disputed</option></select></Field>
                    <Field label={`Confidence · ${item.confidence}%`}><input type="range" min="0" max="100" value={item.confidence} onChange={(event) => patchItem(setEvidence, item.id, { confidence: Number(event.target.value) })} className="mt-3 w-full accent-indigo-600" /></Field>
                    <Field label="Notes"><input className={fieldClass} value={item.notes || ''} onChange={(event) => patchItem(setEvidence, item.id, { notes: event.target.value })} /></Field>
                  </div>
                  <CardActions id={item.id} saving={saving} onSave={() => saveEvidence(item)} onDelete={() => removeItem('evidence', item.id)} />
                </>
              )}
            </article>
          ))}

          {active === 'experiments' && experiments.map((item, index) => (
            <article key={item.id} className="rounded-2xl border border-slate-200 p-5">
              <div className="flex items-center gap-3">
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-sm font-black text-indigo-600">{index + 1}</span>
                <input className={`${fieldClass} font-bold`} value={item.title} onChange={(event) => patchItem(setExperiments, item.id, { title: event.target.value })} />
              </div>
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <Field label="Hypothesis"><textarea className={`${fieldClass} min-h-24 resize-y`} value={item.hypothesis || ''} onChange={(event) => patchItem(setExperiments, item.id, { hypothesis: event.target.value })} /></Field>
                <Field label="Test method"><textarea className={`${fieldClass} min-h-24 resize-y`} value={item.method || ''} onChange={(event) => patchItem(setExperiments, item.id, { method: event.target.value })} /></Field>
              </div>
              <div className="mt-4 grid gap-4 md:grid-cols-[1.2fr_0.55fr_0.55fr_0.65fr]">
                <Field label="Numeric success threshold"><input className={fieldClass} value={item.success_metric || ''} onChange={(event) => patchItem(setExperiments, item.id, { success_metric: event.target.value })} /></Field>
                <Field label="Budget"><input className={fieldClass} value={item.budget || ''} placeholder="$0 / 3 days" onChange={(event) => patchItem(setExperiments, item.id, { budget: event.target.value })} /></Field>
                <Field label="Priority"><select className={fieldClass} value={item.priority} onChange={(event) => patchItem(setExperiments, item.id, { priority: event.target.value })}><option>high</option><option>medium</option><option>low</option></select></Field>
                <Field label="Status"><select className={fieldClass} value={item.status} onChange={(event) => patchItem(setExperiments, item.id, { status: event.target.value })}><option>planned</option><option>running</option><option>passed</option><option>failed</option><option>inconclusive</option></select></Field>
              </div>
              {item.status !== 'planned' && <div className="mt-4"><Field label="Observed result and resulting decision"><textarea className={`${fieldClass} min-h-20 resize-y`} value={item.result || ''} placeholder="Record the measured result, whether it passed, and the next product or investment decision…" onChange={(event) => patchItem(setExperiments, item.id, { result: event.target.value })} /></Field></div>}
              <CardActions id={item.id} saving={saving} onSave={() => saveExperiment(item)} onDelete={() => removeItem('experiments', item.id)} />
            </article>
          ))}

          {!loading && ((active === 'assumptions' && !assumptions.length) || (active === 'evidence' && !evidence.length) || (active === 'experiments' && !experiments.length)) && (
            <div className="py-14 text-center">
              <AlertTriangle className="mx-auto text-slate-300" size={30} />
              <p className="mt-3 text-sm font-semibold text-slate-500">No items yet. Add the first one to begin validating this venture.</p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

function Metric({ label, value, detail, tone }: any) {
  return <div className="bg-slate-950 p-6"><p className="text-xs font-bold uppercase tracking-[0.14em] text-slate-400">{label}</p><strong className={`mt-2 block text-3xl font-black ${tone}`}>{value}</strong><p className="mt-1 text-xs text-slate-500">{detail}</p></div>;
}

function MetricMini({ label, value }: { label: string; value: string }) {
  return <div className="rounded-xl bg-white p-3"><strong className="text-xl font-black text-indigo-700">{value}</strong><p className="mt-1 text-[10px] font-bold uppercase tracking-wider text-slate-400">{label}</p></div>;
}

function Field({ label, children }: any) {
  return <label className="block"><span className="mb-1.5 block text-[10px] font-extrabold uppercase tracking-[0.13em] text-slate-400">{label}</span>{children}</label>;
}

function CardActions({ id, saving, onSave, onDelete }: any) {
  return (
    <div className="mt-5 flex justify-end gap-2 border-t border-slate-100 pt-4">
      <button onClick={onDelete} className="flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-bold text-slate-400 transition hover:bg-rose-50 hover:text-rose-600"><Trash2 size={14} />Remove</button>
      <button onClick={onSave} disabled={saving === id} className="flex items-center gap-2 rounded-lg bg-slate-950 px-4 py-2 text-xs font-bold text-white transition hover:bg-indigo-700 disabled:opacity-60">{saving === id ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}Save</button>
    </div>
  );
}
