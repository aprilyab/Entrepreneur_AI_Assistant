'use client';

import {
  AlertTriangle,
  ArrowRight,
  BadgeDollarSign,
  BarChart3,
  CheckCircle2,
  CircleDollarSign,
  Gauge,
  Layers3,
  Route,
  ShieldAlert,
  Target,
  Users,
} from 'lucide-react';

type VisualKind = 'overview' | 'decision' | 'market' | 'model' | 'risks' | 'financials' | 'plan';

interface PlanVisualsProps {
  kind: VisualKind;
  plan: any;
}

type RiskEntry = {
  name: string;
  impact: string;
  probability: string;
};

const clean = (value = '') =>
  value
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/(?<!\*)\*([^*]+?)\*(?!\*)/g, '$1')
    .replace(/`/g, '')
    .replace(/\s+/g, ' ')
    .trim();

function labeledLine(text: string, label: string) {
  const line = (text || '').split('\n').find((candidate) =>
    clean(candidate).toLowerCase().includes(label.toLowerCase()),
  );
  if (!line) return '';
  const normalized = clean(line);
  const colon = normalized.indexOf(':', normalized.toLowerCase().indexOf(label.toLowerCase()));
  return colon >= 0 ? normalized.slice(colon + 1).trim() : normalized;
}

function currencyValue(text: string, label: string, last = false) {
  const line = labeledLine(text, label);
  const values = line.match(/\$[\d,.]+(?:\s*(?:billion|million|B|M))?/gi) || [];
  const raw = last ? values.at(-1) : values[0];
  return raw?.replace(/\s+billion/i, 'B').replace(/\s+million/i, 'M') || 'Not provided';
}

function numberFromMoney(value: string) {
  const numeric = Number(value.replace(/[^\d.]/g, '')) || 0;
  if (/b/i.test(value)) return numeric * 1_000;
  if (/m/i.test(value)) return numeric;
  return numeric / 1_000_000;
}

function sections(markdown: string) {
  const result: Record<string, string[]> = { overview: [] };
  let current = 'overview';
  (markdown || '').split('\n').forEach((raw) => {
    const match = raw.trim().match(/^#{1,4}\s+(?:\d+[.)]\s*)?(.+)$/);
    if (match) {
      current = clean(match[1]).toLowerCase();
      result[current] ||= [];
    } else {
      result[current] ||= [];
      result[current].push(raw);
    }
  });
  return Object.fromEntries(Object.entries(result).map(([key, lines]) => [key, lines.join('\n')]));
}

function findSection(markdown: string, ...needles: string[]) {
  const parsed = sections(markdown);
  const key = Object.keys(parsed).find((candidate) => needles.some((needle) => candidate.includes(needle)));
  return key ? parsed[key] : '';
}

function bullets(text: string, limit = 5) {
  return (text || '')
    .split('\n')
    .map((line) => line.match(/^\s*(?:[-*]|\d+[.)])\s+(.+)$/)?.[1])
    .filter(Boolean)
    .map((line) => clean(line as string))
    .slice(0, limit);
}

function labeledBullets(text: string, label: string, limit = 3) {
  const lines = (text || '').split('\n');
  const start = lines.findIndex((line) =>
    clean(line).replace(/^[-*]\s*/, '').toLowerCase().startsWith(`${label.toLowerCase()}:`),
  );
  if (start < 0) return [];
  const result: string[] = [];
  for (let index = start + 1; index < lines.length; index += 1) {
    const raw = lines[index];
    if (/^\s*[-*]\s+\*\*[^*]+:\*\*\s*$/.test(raw)) break;
    const match = raw.match(/^\s*[-*]\s+(.+)$/);
    if (match) result.push(clean(match[1]));
    if (result.length === limit) break;
  }
  return result;
}

function scoreBreakdown(text: string) {
  return (text || '')
    .split('\n')
    .map((line) => {
      if (line.trim().startsWith('#')) return null;
      const normalized = clean(line.replace(/^\s*[-*]\s+/, ''));
      const match = normalized.match(/^([^:]+):\s*(\d+)\s*\/\s*(\d+)/);
      return match ? { label: match[1], value: Number(match[2]), max: Number(match[3]) } : null;
    })
    .filter(Boolean)
    .slice(0, 6) as { label: string; value: number; max: number }[];
}

function parseRisks(text: string): RiskEntry[] {
  const result: RiskEntry[] = [];
  let current: RiskEntry | null = null;
  let groupImpact = 'Medium';
  (text || '').split('\n').forEach((raw) => {
    if (/^#{1,4}\s+Critical Risks/i.test(raw.trim()) || /^#{1,4}\s+High Risks/i.test(raw.trim())) groupImpact = 'High';
    if (/^#{1,4}\s+Medium Risks/i.test(raw.trim())) groupImpact = 'Medium';
    const normalized = clean(raw.replace(/^\s*[-*]\s+/, ''));
    if (/^Risk:/i.test(normalized)) {
      if (current) result.push(current);
      current = { name: normalized.replace(/^Risk:\s*/i, ''), impact: groupImpact, probability: 'Medium' };
    } else if (current && /^Impact:/i.test(normalized)) {
      const value = normalized.replace(/^Impact:\s*/i, '');
      if (/^(?:high|critical)\b/i.test(value)) current.impact = 'High';
      if (/^low\b/i.test(value)) current.impact = 'Low';
    } else if (current && /^Probability:/i.test(normalized)) {
      const value = normalized.replace(/^Probability:\s*/i, '');
      current.probability = /high/i.test(value) ? 'High' : /low/i.test(value) ? 'Low' : 'Medium';
    }
  });
  if (current) result.push(current);
  return result.slice(0, 7);
}

function revenueYears(text: string) {
  const patterns = [
    /Year 1(?:\s+Projections)?[\s\S]{0,260}?Total Revenue:[^$\n]*\$([0-9,.]+(?:\s*(?:million|M))?)/i,
    /Year 2 Total Revenue:[^$\n]*\$([0-9,.]+(?:\s*(?:million|M))?)/i,
    /Year 3[\s\S]{0,120}?Total Revenue:[^$\n]*\$([0-9,.]+(?:\s*(?:million|M))?)/i,
  ];
  const defaults = ['—', '—', '—'];
  return patterns.map((pattern, index) => {
    const match = (text || '').match(pattern);
    return match ? `$${match[1]}` : defaults[index];
  });
}

function VisualShell({
  eyebrow,
  title,
  note,
  children,
}: {
  eyebrow: string;
  title: string;
  note: string;
  children: React.ReactNode;
}) {
  return (
    <section className="visual-shell">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
        <div>
          <p className="visual-eyebrow">{eyebrow}</p>
          <h3 className="mt-1 text-xl font-black tracking-tight text-slate-950">{title}</h3>
        </div>
        <p className="max-w-md text-xs leading-5 text-slate-500">{note}</p>
      </div>
      <div className="mt-6">{children}</div>
    </section>
  );
}

function EmptyMetric({ label }: { label: string }) {
  return (
    <div className="visual-metric">
      <span className="text-lg font-black text-slate-400">—</span>
      <span>{label}</span>
    </div>
  );
}

function OverviewVisual({ plan }: { plan: any }) {
  const score = Number(plan.intelligence?.adjusted_score?.adjusted_score ?? plan.viability_score ?? 0);
  const market = plan.market_analysis || '';
  const financials = plan.financials || '';
  const structuredFunding = plan.intelligence?.financial_metrics?.recommended_funding?.display;
  const fundingFromPlan = currencyValue(plan.full_plan || '', 'Recommended Seed Capital');
  const funding = structuredFunding || (fundingFromPlan !== 'Not provided' ? fundingFromPlan : currencyValue(financials, 'Recommended seed amount'));
  const som = currencyValue(market, 'SOM (Serviceable Obtainable Market)');
  return (
    <VisualShell eyebrow="Venture map" title="One idea, four decision lenses" note="A compact map of the evidence the full report uses to reach its recommendation.">
      <div className="grid gap-3 md:grid-cols-[1fr_auto_1fr_auto_1fr_auto_1fr] md:items-center">
        {[
          { icon: Target, label: 'Opportunity', value: som, tone: 'cyan' },
          { icon: Gauge, label: 'Evidence-adjusted', value: `${score}/100`, tone: 'indigo' },
          { icon: ShieldAlert, label: 'Risk', value: `${parseRisks(plan.risks || '').length} mapped`, tone: 'amber' },
          { icon: CircleDollarSign, label: 'Funding', value: funding, tone: 'emerald' },
        ].map(({ icon: Icon, label, value, tone }, index) => (
          <div className="contents" key={label}>
            <div className={`visual-node visual-node-${tone}`}>
              <Icon size={19} />
              <span className="text-[10px] font-black uppercase tracking-[0.14em] opacity-60">{label}</span>
              <strong className="mt-1 text-lg">{value}</strong>
            </div>
            {index < 3 && <ArrowRight className="mx-auto hidden text-slate-300 md:block" size={18} />}
          </div>
        ))}
      </div>
    </VisualShell>
  );
}

function DecisionVisual({ plan }: { plan: any }) {
  const rows = scoreBreakdown(plan.validation_strategy || '');
  const contradictions = plan.intelligence?.contradiction_issues || [];
  const adjusted = plan.intelligence?.adjusted_score || {};
  return (
    <VisualShell eyebrow="Score anatomy" title="What drives the recommendation" note="These bars reproduce the category scores in the generated validation report; they are assessments, not measured outcomes.">
      <div className="grid gap-6 lg:grid-cols-[1.35fr_.65fr]">
        <div className="space-y-4">
          {rows.length ? rows.map((row) => {
            const percentage = Math.round((row.value / row.max) * 100);
            return (
              <div key={row.label}>
                <div className="mb-1.5 flex justify-between text-xs font-bold text-slate-600">
                  <span>{row.label}</span><span>{row.value}/{row.max}</span>
                </div>
                <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
                  <div className="h-full rounded-full bg-gradient-to-r from-indigo-600 to-cyan-400" style={{ width: `${percentage}%` }} />
                </div>
              </div>
            );
          }) : <EmptyMetric label="Score breakdown unavailable" />}
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="visual-stat bg-emerald-50 text-emerald-800"><CheckCircle2 size={19} /><strong>{bullets(findSection(plan.validation_strategy, 'green flags')).length}</strong><span>Green flags</span></div>
          <div className="visual-stat bg-rose-50 text-rose-800"><AlertTriangle size={19} /><strong>{bullets(findSection(plan.validation_strategy, 'red flags')).length}</strong><span>Red flags</span></div>
          <div className="visual-stat col-span-2 bg-indigo-50 text-indigo-800"><Target size={19} /><strong>{bullets(findSection(plan.validation_strategy, 'validation recommendations')).length}</strong><span>Priority validation experiments</span></div>
        </div>
      </div>
      {!!adjusted.adjusted_score && (
        <div className="mt-5 grid gap-3 sm:grid-cols-3">
          <div className="visual-metric"><strong>{adjusted.raw_score}/100</strong><span>AI assessment</span></div>
          <div className="visual-metric"><strong>{adjusted.evidence_confidence}%</strong><span>Evidence confidence</span></div>
          <div className="visual-metric"><strong>{adjusted.adjusted_score}/100</strong><span>Evidence-adjusted score</span></div>
          <p className="sm:col-span-3 text-xs leading-5 text-slate-500">{adjusted.method}</p>
        </div>
      )}
      <div className={`mt-5 rounded-2xl border p-4 ${contradictions.length ? 'border-amber-200 bg-amber-50' : 'border-emerald-200 bg-emerald-50'}`}>
        <div className="flex items-center gap-2">
          {contradictions.length ? <AlertTriangle size={18} className="text-amber-700" /> : <CheckCircle2 size={18} className="text-emerald-700" />}
          <strong className="text-sm text-slate-900">
            {contradictions.length ? `${contradictions.length} cross-report conflict${contradictions.length === 1 ? '' : 's'} to resolve` : 'No material cross-report contradictions detected'}
          </strong>
        </div>
        {!!contradictions.length && (
          <div className="mt-3 grid gap-2 md:grid-cols-2">
            {contradictions.slice(0, 4).map((issue: any, index: number) => (
              <div key={`${issue.category}-${index}`} className="rounded-xl border border-amber-200 bg-white p-3">
                <p className="text-[10px] font-black uppercase tracking-wider text-amber-700">{issue.severity} · {issue.category}</p>
                <p className="mt-1 text-xs font-bold leading-5 text-slate-800">{issue.explanation}</p>
                <p className="mt-1 text-xs leading-5 text-slate-500">{issue.recommended_resolution}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </VisualShell>
  );
}

function MarketVisual({ plan }: { plan: any }) {
  const text = plan.market_analysis || '';
  const evidence = plan.evidence_claims || [];
  const values = [
    { label: 'TAM', value: currencyValue(text, 'TAM (Total Addressable Market)', true), size: 'h-48 w-48 bg-cyan-100/80 text-cyan-900' },
    { label: 'SAM', value: currencyValue(text, 'SAM (Serviceable Available Market)'), size: 'h-36 w-36 bg-indigo-200/90 text-indigo-900' },
    { label: 'SOM', value: currencyValue(text, 'SOM (Serviceable Obtainable Market)'), size: 'h-24 w-24 bg-slate-950 text-white' },
  ];
  const growth = (text.match(/(\d+(?:\.\d+)?%\s*(?:to|–|-)\s*\d+(?:\.\d+)?%)/i) || [])[1] || 'Not provided';
  const missingMarketMetrics = [
    ...values.filter((item) => item.value === 'Not provided').map((item) => item.label),
    ...(growth === 'Not provided' ? ['CAGR'] : []),
  ];
  const linked = evidence.filter((item: any) => item.source_url).length;
  const verified = evidence.filter((item: any) => item.status === 'verified').length;
  return (
    <VisualShell eyebrow="Market funnel" title="From category opportunity to obtainable wedge" note="Market figures are extracted from the plan. They still require source citations and bottom-up validation.">
      <div className="grid items-center gap-7 lg:grid-cols-[1fr_.85fr]">
        <div className="relative mx-auto flex h-60 w-full max-w-lg items-center justify-center max-sm:h-auto max-sm:gap-2">
          {values.map(({ label, value, size }, index) => (
            <div key={label} className={`absolute flex flex-col items-center justify-center rounded-full border-4 border-white shadow-lg max-sm:static max-sm:h-20 max-sm:w-20 max-sm:shrink-0 max-sm:shadow-md ${size}`} style={{ left: `${index * 27 + 8}%`, zIndex: index + 1 }}>
              <span className="text-[9px] font-black uppercase tracking-[0.18em] opacity-60">{label}</span>
              <strong className="mt-1 text-lg max-sm:text-sm">{value}</strong>
            </div>
          ))}
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="visual-metric"><strong>{growth}</strong><span>Estimated CAGR</span></div>
          <div className="visual-metric"><strong>{bullets(findSection(text, 'target customers'), 8).length}</strong><span>Customer observations</span></div>
          <div className="visual-metric"><strong>{bullets(findSection(text, 'competitive landscape'), 8).length}</strong><span>Competitor observations</span></div>
          <div className="visual-metric"><strong>{bullets(findSection(text, 'industry trends'), 8).length}</strong><span>Trend signals</span></div>
          <div className={`col-span-2 rounded-xl border p-3 text-xs leading-5 ${missingMarketMetrics.length ? 'border-amber-200 bg-amber-50 text-amber-900' : 'border-emerald-200 bg-emerald-50 text-emerald-900'}`}>
            <strong>{missingMarketMetrics.length ? `Evidence gaps: ${missingMarketMetrics.join(', ')}` : 'Core market metrics present'}</strong>
            <p className="mt-1">{linked}/{evidence.length} claims link to sources; {verified} have been manually verified.</p>
          </div>
        </div>
      </div>
    </VisualShell>
  );
}

function ModelVisual({ plan }: { plan: any }) {
  const text = plan.business_model || '';
  const segments = bullets(findSection(text, 'customer segments'), 3).length
    ? bullets(findSection(text, 'customer segments'), 3)
    : labeledBullets(text, 'Customer Segments', 3);
  const channels = bullets(findSection(text, 'channels'), 3).length
    ? bullets(findSection(text, 'channels'), 3)
    : labeledBullets(text, 'Channels', 3);
  const revenues = bullets(findSection(text, 'revenue streams'), 3).length
    ? bullets(findSection(text, 'revenue streams'), 3)
    : labeledBullets(text, 'Revenue Streams', 3);
  const columns = [
    { icon: Users, title: 'Customers', values: segments, tone: 'cyan' },
    { icon: Route, title: 'Channels', values: channels, tone: 'violet' },
    { icon: BadgeDollarSign, title: 'Revenue', values: revenues, tone: 'emerald' },
  ];
  return (
    <VisualShell eyebrow="Value engine" title="How value moves through the business" note="The model becomes testable when each customer, channel, and revenue assumption has an owner and metric.">
      <div className="grid gap-3 lg:grid-cols-[1fr_auto_1fr_auto_1fr] lg:items-stretch">
        {columns.map(({ icon: Icon, title, values, tone }, index) => (
          <div className="contents" key={title}>
            <div className={`visual-flow-card visual-flow-${tone}`}>
              <div className="flex items-center gap-2"><Icon size={18} /><strong>{title}</strong></div>
              <div className="mt-4 space-y-2">
                {(values.length ? values : ['Not structured in this plan']).map((value) => <p key={value}>{value}</p>)}
              </div>
            </div>
            {index < 2 && <ArrowRight className="mx-auto self-center text-slate-300 max-lg:rotate-90" size={20} />}
          </div>
        ))}
      </div>
    </VisualShell>
  );
}

function RiskVisual({ plan }: { plan: any }) {
  const risks = parseRisks(plan.risks || '');
  const coordinate = (value: string) => value === 'High' ? 82 : value === 'Low' ? 18 : 50;
  return (
    <VisualShell eyebrow="Exposure map" title="Probability × impact" note="Items in the upper-right require an owner, a deadline, and an explicit validation or mitigation action.">
      <div className="grid gap-6 lg:grid-cols-[1fr_.72fr]">
        <div className="relative h-80 overflow-hidden rounded-2xl border border-slate-200 bg-white">
          <div className="absolute inset-0 grid grid-cols-3 grid-rows-3">
            {['bg-emerald-50', 'bg-amber-50', 'bg-rose-50', 'bg-emerald-50', 'bg-amber-50', 'bg-rose-100', 'bg-slate-50', 'bg-amber-50', 'bg-rose-50'].map((tone, index) => <div key={index} className={`border border-white ${tone}`} />)}
          </div>
          <span className="absolute bottom-2 left-1/2 -translate-x-1/2 text-[9px] font-black uppercase tracking-widest text-slate-400">Impact →</span>
          <span className="absolute left-2 top-1/2 -translate-y-1/2 -rotate-90 text-[9px] font-black uppercase tracking-widest text-slate-400">Probability →</span>
          {risks.map((risk, index) => (
            <span
              key={`${risk.name}-${index}`}
              className="absolute flex h-8 w-8 items-center justify-center rounded-full border-2 border-white bg-slate-950 text-[10px] font-black text-white shadow-lg"
              style={{
                left: `calc(${coordinate(risk.impact) + ((index % 3) - 1) * 6}% - 16px)`,
                bottom: `calc(${coordinate(risk.probability) + ((Math.floor(index / 3) % 3) - 1) * 5}% - 16px)`,
              }}
              title={risk.name}
            >
              {index + 1}
            </span>
          ))}
        </div>
        <div className="space-y-2">
          {(risks.length ? risks : [{ name: 'No structured risks found', impact: '—', probability: '—' }]).map((risk, index) => (
            <div key={`${risk.name}-${index}`} className="flex gap-3 rounded-xl border border-slate-200 bg-white p-3">
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-slate-950 text-xs font-black text-white">{index + 1}</span>
              <div><p className="line-clamp-2 text-xs font-bold leading-5 text-slate-800">{risk.name}</p><p className="mt-1 text-[10px] uppercase tracking-wider text-slate-400">{risk.probability} probability · {risk.impact} impact</p></div>
            </div>
          ))}
        </div>
      </div>
    </VisualShell>
  );
}

function FinancialVisual({ plan }: { plan: any }) {
  const text = plan.financials || '';
  const metrics = plan.intelligence?.financial_metrics || {};
  const structuredYears = [metrics.year_1_revenue, metrics.year_2_revenue, metrics.year_3_revenue];
  const hasStructuredYears = structuredYears.some((metric) => metric?.display);
  const years = hasStructuredYears
    ? structuredYears.map((metric) => metric?.display || 'Evidence gap')
    : revenueYears(text);
  const amounts = hasStructuredYears
    ? structuredYears.map((metric) => Number(metric?.value || 0) / 1_000_000)
    : years.map(numberFromMoney);
  const max = Math.max(...amounts, 1);
  const parsedCac = currencyValue(text, 'Blended CAC') !== 'Not provided' ? currencyValue(text, 'Blended CAC') : currencyValue(text, 'Customer Acquisition Cost');
  const parsedCogs = currencyValue(text, 'COGS (Cost of Goods Sold)') !== 'Not provided' ? currencyValue(text, 'COGS (Cost of Goods Sold)') : currencyValue(text, 'COGS');
  const cac = metrics.blended_cac?.display || parsedCac;
  const cogs = metrics.cogs_per_unit?.display || metrics.inference_cost_per_render?.display || parsedCogs;
  const ltv = metrics.ltv_cac_ratio?.display || text.match(/LTV:CAC ratio[\s\S]{0,180}?(\d+(?:\.\d+)?:1)/i)?.[1] || 'Not provided';
  const allocationFromSection = bullets(findSection(text, 'use of funds'), 5);
  const allocation = allocationFromSection.length ? allocationFromSection : labeledBullets(text, 'Use of funds breakdown', 5);
  const parsedAllocationTotal = allocation.reduce((sum, item) => {
    const match = item.match(/\$([\d,.]+)/);
    return sum + (match ? Number(match[1].replace(/,/g, '')) : 0);
  }, 0);
  const structuredAllocationTotal = (metrics.use_of_funds || []).reduce(
    (sum: number, item: any) => sum + Number(item.amount || 0),
    0,
  );
  const allocationTotal = structuredAllocationTotal || parsedAllocationTotal;
  const consistencyIssues = plan.intelligence?.consistency_issues || [];
  const requiredMetricNames = [
    ['Year 1 revenue', metrics.year_1_revenue],
    ['Blended CAC', metrics.blended_cac],
    ['ARPU', metrics.arpu],
    ['LTV', metrics.ltv],
    ['LTV:CAC', metrics.ltv_cac_ratio],
    ['Funding target', metrics.recommended_funding],
  ];
  const missingFinancialMetrics = requiredMetricNames.filter(([, metric]) => !metric?.value).map(([name]) => name);
  return (
    <VisualShell eyebrow="Economic dashboard" title="Growth assumptions and unit economics" note="Charts show the plan’s projections—not historical performance. Contradictions should be resolved before investor use.">
      <div className="grid gap-6 lg:grid-cols-[1.15fr_.85fr]">
        <div>
          <div className="flex h-60 items-end gap-5 rounded-2xl border border-slate-200 bg-white p-5 pb-10">
            {years.map((year, index) => (
              <div key={index} className="flex h-full flex-1 flex-col justify-end">
                <strong className="mb-2 text-center text-xs text-slate-700">{year}</strong>
                <div className={`mx-auto w-full max-w-24 rounded-t-xl ${['bg-indigo-500', 'bg-cyan-500', 'bg-emerald-500'][index]}`} style={{ height: `${Math.max(12, (amounts[index] / max) * 100)}%` }} />
                <span className="mt-2 text-center text-[10px] font-black uppercase tracking-wider text-slate-400">Year {index + 1}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="visual-metric"><strong>{cogs}</strong><span>COGS / unit</span></div>
          <div className="visual-metric"><strong>{cac}</strong><span>Blended CAC</span></div>
          <div className="visual-metric"><strong>{ltv}</strong><span>LTV : CAC</span></div>
          <div className="visual-metric"><strong>{allocationTotal ? `$${(allocationTotal / 1000).toFixed(0)}K` : '—'}</strong><span>Allocation total</span></div>
          <div className={`col-span-2 rounded-xl border p-3 text-xs leading-5 ${consistencyIssues.length ? 'border-rose-200 bg-rose-50 text-rose-900' : 'border-emerald-200 bg-emerald-50 text-emerald-900'}`}>
            <strong>{consistencyIssues.length ? `${consistencyIssues.length} arithmetic issue${consistencyIssues.length === 1 ? '' : 's'} found` : 'Financial arithmetic passed'}</strong>
            {consistencyIssues.length ? (
              <ul className="mt-2 space-y-1">
                {consistencyIssues.slice(0, 4).map((issue: any) => <li key={issue.code}>• {issue.message} Expected {issue.expected}; reported {issue.actual}.</li>)}
              </ul>
            ) : <span> — funding allocation and available unit-economics formulas are internally consistent.</span>}
          </div>
          {!!missingFinancialMetrics.length && (
            <div className="col-span-2 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs leading-5 text-amber-900">
              <strong>Missing decision data:</strong> {missingFinancialMetrics.join(', ')}.
            </div>
          )}
        </div>
      </div>
    </VisualShell>
  );
}

function PlanVisual({ plan }: { plan: any }) {
  const timeline = bullets(findSection(plan.full_plan || '', 'implementation timeline'), 4);
  return (
    <VisualShell eyebrow="Execution path" title="From validation to scale" note="Every phase should have a measurable exit criterion before the next capital commitment.">
      <div className="relative grid gap-4 md:grid-cols-4">
        <div className="absolute left-[12%] right-[12%] top-6 hidden h-0.5 bg-slate-200 md:block" />
        {(timeline.length ? timeline : ['Validate demand', 'Build the MVP', 'Launch and learn', 'Scale validated channels']).map((item, index) => (
          <div key={item} className="relative rounded-2xl border border-slate-200 bg-white p-4 pt-12">
            <span className="absolute left-4 top-3 z-10 flex h-7 w-7 items-center justify-center rounded-full bg-slate-950 text-xs font-black text-white">{index + 1}</span>
            <p className="text-xs font-semibold leading-5 text-slate-700">{item}</p>
          </div>
        ))}
      </div>
    </VisualShell>
  );
}

export default function PlanVisuals({ kind, plan }: PlanVisualsProps) {
  if (kind === 'overview') return <OverviewVisual plan={plan} />;
  if (kind === 'decision') return <DecisionVisual plan={plan} />;
  if (kind === 'market') return <MarketVisual plan={plan} />;
  if (kind === 'model') return <ModelVisual plan={plan} />;
  if (kind === 'risks') return <RiskVisual plan={plan} />;
  if (kind === 'financials') return <FinancialVisual plan={plan} />;
  return <PlanVisual plan={plan} />;
}
