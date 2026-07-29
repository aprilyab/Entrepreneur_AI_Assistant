import {
  ArrowRight, BarChart3, Bot, Check, CircleDollarSign, Gauge,
  LineChart, Search, ShieldCheck, Sparkles, Target, Zap,
} from 'lucide-react';

const agents = [
  { icon: Search, label: 'Market signal', detail: 'Demand, segments & competitors', color: 'text-cyan-600 bg-cyan-50' },
  { icon: CircleDollarSign, label: 'Financial model', detail: 'Unit economics & runway', color: 'text-emerald-600 bg-emerald-50' },
  { icon: Target, label: 'Venture strategy', detail: 'Business model & GTM', color: 'text-violet-600 bg-violet-50' },
  { icon: ShieldCheck, label: 'Risk intelligence', detail: 'Exposure & mitigations', color: 'text-amber-600 bg-amber-50' },
  { icon: LineChart, label: 'Growth system', detail: 'Channels, loops & milestones', color: 'text-rose-600 bg-rose-50' },
  { icon: Gauge, label: 'Go / no-go decision', detail: 'Scored verdict & next moves', color: 'text-indigo-600 bg-indigo-50' },
];

export default function Home() {
  return (
    <div className="overflow-hidden">
      <section className="relative">
        <div className="absolute inset-0 -z-10 bg-[linear-gradient(to_right,#e2e8f055_1px,transparent_1px),linear-gradient(to_bottom,#e2e8f055_1px,transparent_1px)] bg-[size:48px_48px] [mask-image:linear-gradient(to_bottom,black,transparent_82%)]" />
        <div className="app-shell grid min-h-[680px] items-center gap-14 py-20 lg:grid-cols-[1.05fr_.95fr] lg:py-24">
          <div>
            <span className="eyebrow"><Sparkles size={13} /> Multi-agent venture intelligence</span>
            <h1 className="mt-7 max-w-3xl text-balance text-5xl font-black leading-[1.02] tracking-[-0.055em] text-slate-950 sm:text-6xl lg:text-7xl">
              From raw idea to a clear
              <span className="relative ml-3 inline-block text-indigo-600">
                go / no-go.
                <svg className="absolute -bottom-2 left-0 w-full text-cyan-400" viewBox="0 0 300 12" fill="none">
                  <path d="M3 9C70 2 190 2 297 7" stroke="currentColor" strokeWidth="5" strokeLinecap="round" />
                </svg>
              </span>
            </h1>
            <p className="mt-8 max-w-xl text-lg leading-8 text-slate-600">
              Specialist AI agents research, model, audit, and pressure-test your venture—then show what is supported, assumed, contradictory, and still unproven.
            </p>
            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <a href="/auth/register" className="primary-button px-7 py-3.5">
                Analyze my idea <ArrowRight size={18} />
              </a>
              <a href="#system" className="secondary-button px-7 py-3.5">
                See the system
              </a>
            </div>
            <div className="mt-8 flex flex-wrap gap-x-6 gap-y-2 text-sm font-medium text-slate-500">
              {['Decision score', 'Risk matrix', 'Investor exports'].map((item) => (
                <span key={item} className="flex items-center gap-2"><Check size={15} className="text-emerald-500" />{item}</span>
              ))}
            </div>
          </div>

          <div className="relative mx-auto w-full max-w-xl">
            <div className="absolute -inset-10 -z-10 rounded-full bg-gradient-to-br from-indigo-200/60 via-cyan-100/50 to-transparent blur-3xl" />
            <div className="glass-panel overflow-hidden p-3">
              <div className="rounded-xl bg-slate-950 p-6 text-white sm:p-8">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">Venture decision</p>
                    <h2 className="mt-2 text-2xl font-bold">Coffee Direct</h2>
                  </div>
                  <span className="rounded-full bg-emerald-400/15 px-3 py-1 text-xs font-bold text-emerald-300">PROMISING</span>
                </div>
                <div className="mt-8 grid grid-cols-[120px_1fr] items-center gap-6">
                  <div className="relative flex h-28 w-28 items-center justify-center rounded-full bg-[conic-gradient(#22d3ee_0_78%,#1e293b_78%)]">
                    <div className="flex h-[88px] w-[88px] flex-col items-center justify-center rounded-full bg-slate-950">
                      <strong className="text-3xl">78</strong>
                      <span className="text-[10px] uppercase tracking-widest text-slate-400">score</span>
                    </div>
                  </div>
                  <div className="space-y-3">
                    {[['Market demand', '84%'], ['Economics', '72%'], ['Execution', '76%']].map(([label, value], index) => (
                      <div key={label}>
                        <div className="mb-1.5 flex justify-between text-xs"><span className="text-slate-400">{label}</span><span>{value}</span></div>
                        <div className="h-1.5 rounded-full bg-slate-800"><div className={`h-full rounded-full ${index === 1 ? 'w-[72%] bg-violet-400' : index === 2 ? 'w-[76%] bg-emerald-400' : 'w-[84%] bg-cyan-400'}`} /></div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="mt-8 grid grid-cols-2 gap-3">
                  <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <ShieldCheck size={18} className="text-amber-300" />
                    <p className="mt-3 text-xs text-slate-400">Critical risks</p>
                    <p className="mt-1 font-bold">3 mitigations ready</p>
                  </div>
                  <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <Zap size={18} className="text-cyan-300" />
                    <p className="mt-3 text-xs text-slate-400">Next action</p>
                    <p className="mt-1 font-bold">Run buyer interviews</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="system" className="border-y border-slate-200 bg-white py-24">
        <div className="app-shell">
          <div className="max-w-2xl">
            <span className="eyebrow"><Bot size={13} /> One system, multiple expert lenses</span>
            <h2 className="mt-5 text-4xl font-black tracking-[-0.04em] text-slate-950 sm:text-5xl">A venture decision system in your corner.</h2>
            <p className="mt-5 text-lg leading-8 text-slate-600">Each agent builds on the work before it. Finance informs risk. Risk sharpens the final decision. Nothing lives in a disconnected chat.</p>
          </div>
          <div className="mt-14 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {agents.map(({ icon: Icon, label, detail, color }, index) => (
              <div key={label} className="group rounded-2xl border border-slate-200 bg-slate-50/60 p-6 transition hover:-translate-y-1 hover:border-indigo-200 hover:bg-white hover:shadow-xl hover:shadow-indigo-950/5">
                <div className="flex items-start justify-between">
                  <span className={`flex h-11 w-11 items-center justify-center rounded-xl ${color}`}><Icon size={21} /></span>
                  <span className="text-xs font-black tracking-widest text-slate-300">0{index + 1}</span>
                </div>
                <h3 className="mt-6 text-lg font-bold text-slate-900">{label}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-500">{detail}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-24">
        <div className="app-shell">
          <div className="relative overflow-hidden rounded-[2rem] bg-slate-950 px-6 py-16 text-center text-white sm:px-12">
            <div className="absolute -left-20 -top-20 h-64 w-64 rounded-full bg-indigo-600/30 blur-3xl" />
            <div className="absolute -bottom-24 right-0 h-64 w-64 rounded-full bg-cyan-500/20 blur-3xl" />
            <BarChart3 className="relative mx-auto text-cyan-300" size={32} />
            <h2 className="relative mt-5 text-4xl font-black tracking-tight">Make your next move evidence-led.</h2>
            <p className="relative mx-auto mt-4 max-w-xl text-slate-300">Bring the idea. Leave with the market case, economics, risks, decision, and action plan.</p>
            <a href="/auth/register" className="relative mt-8 inline-flex items-center gap-2 rounded-xl bg-white px-6 py-3.5 font-bold text-slate-950 transition hover:bg-cyan-50">
              Build my venture brief <ArrowRight size={18} />
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
