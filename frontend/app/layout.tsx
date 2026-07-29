import type { Metadata } from 'next';
import { ArrowUpRight, Layers3 } from 'lucide-react';
import './globals.css';

export const metadata: Metadata = {
  title: 'Prooflane — Evidence-first venture intelligence',
  description: 'Turn an early idea into an evidence-aware venture decision with specialized AI agents.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="sticky top-0 z-50 border-b border-slate-200/70 bg-white/80 backdrop-blur-xl">
          <div className="app-shell flex h-[72px] items-center justify-between">
            <a href="/" className="group flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-950 text-white shadow-lg shadow-slate-950/15 transition group-hover:rotate-3">
                <Layers3 size={20} />
              </span>
              <span>
                <span className="block text-[15px] font-extrabold tracking-tight text-slate-950">Prooflane</span>
                <span className="block text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">Evidence before confidence</span>
              </span>
            </a>
            <nav className="flex items-center gap-2 sm:gap-5">
              <a href="/dashboard" className="hidden text-sm font-semibold text-slate-600 transition hover:text-slate-950 sm:block">
                Workspace
              </a>
              <a href="/auth/login" className="inline-flex items-center gap-2 rounded-xl bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-700">
                Open studio <ArrowUpRight size={15} />
              </a>
            </nav>
          </div>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
