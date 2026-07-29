'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, Check, Loader2, LockKeyhole, Mail, Sparkles } from 'lucide-react';
import { auth } from '@/lib/api';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      const result = await auth.login({ email, password });
      localStorage.setItem('token', result.access_token);
      localStorage.setItem('user', JSON.stringify(result.user));
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Sign in failed');
      setLoading(false);
    }
  };

  return (
    <div className="app-shell grid min-h-[calc(100vh-72px)] items-center gap-10 py-12 lg:grid-cols-2">
      <div className="hidden lg:block">
        <span className="eyebrow"><Sparkles size={13} /> Welcome back</span>
        <h1 className="mt-6 max-w-xl text-5xl font-black tracking-[-0.05em] text-slate-950">Your strongest ideas deserve a second look.</h1>
        <p className="mt-5 max-w-lg text-lg leading-8 text-slate-600">Return to your venture workspace, review the evidence, and keep refining the next move.</p>
        <div className="mt-8 space-y-3">
          {['Decision and risk reports stay together', 'Export investor-ready documents', 'Ask follow-up questions in context'].map((item) => (
            <p key={item} className="flex items-center gap-3 text-sm font-medium text-slate-600"><span className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100 text-emerald-600"><Check size={13} /></span>{item}</p>
          ))}
        </div>
      </div>
      <div className="glass-panel mx-auto w-full max-w-md p-6 sm:p-8">
        <h2 className="text-2xl font-black tracking-tight text-slate-950">Sign in to Prooflane</h2>
        <p className="mt-2 text-sm text-slate-500">Open your venture intelligence workspace.</p>
        <form onSubmit={handleSubmit} className="mt-7 space-y-5">
          <Field icon={Mail} label="Email address" type="email" value={email} onChange={setEmail} placeholder="you@company.com" />
          <Field icon={LockKeyhole} label="Password" type="password" value={password} onChange={setPassword} placeholder="Your password" />
          {error && <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{error}</div>}
          <button disabled={loading} className="primary-button w-full py-3.5">
            {loading ? <><Loader2 size={18} className="animate-spin" /> Signing in…</> : <>Open workspace <ArrowRight size={18} /></>}
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-slate-500">New here? <a href="/auth/register" className="font-bold text-indigo-600 hover:text-indigo-700">Create your account</a></p>
      </div>
    </div>
  );
}

function Field({ icon: Icon, label, type, value, onChange, placeholder }: any) {
  return <label className="block"><span className="text-sm font-bold text-slate-700">{label}</span><span className="relative mt-2 block"><Icon size={17} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" /><input type={type} value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} required className="w-full rounded-xl border border-slate-200 bg-white py-3 pl-11 pr-4 outline-none transition focus:border-indigo-400 focus:ring-4 focus:ring-indigo-100" /></span></label>;
}
