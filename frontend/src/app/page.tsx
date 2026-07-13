import Link from "next/link";
import { ArrowRight, Brain, TrendingUp, ShieldCheck } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center">
      {/* Navigation */}
      <nav className="w-full max-w-7xl px-6 py-6 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Brain className="w-8 h-8 text-brand-500" />
          <span className="text-xl font-bold tracking-tight">Prospect Assist AI</span>
        </div>
        <div className="flex gap-4">
          <Link href="/login" className="px-5 py-2.5 text-sm font-medium text-zinc-300 hover:text-white transition-colors">
            Login
          </Link>
          <Link href="/register" className="px-5 py-2.5 text-sm font-medium bg-brand-600 hover:bg-brand-500 rounded-lg transition-colors">
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="flex-1 w-full max-w-7xl px-6 flex flex-col items-center justify-center text-center mt-20">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-400 text-sm font-medium mb-8">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-500"></span>
          </span>
          Production Ready AI Lead Intelligence
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold tracking-tighter mb-6 bg-gradient-to-br from-white to-zinc-500 bg-clip-text text-transparent">
          Supercharge Your <br/> Loan Conversions.
        </h1>
        
        <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mb-10">
          Move beyond traditional metrics. Leverage behavioral insights, accurate income assessment, and sentiment analysis to identify your most qualified prospects instantly.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 mb-24">
          <Link href="/register" className="px-8 py-4 bg-brand-600 hover:bg-brand-500 text-white rounded-xl font-medium transition-all flex items-center justify-center gap-2 group">
            Start Free Trial <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>
          <Link href="/login" className="px-8 py-4 bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 rounded-xl font-medium transition-all">
            Sign In to Dashboard
          </Link>
        </div>

        {/* Feature Highlights */}
        <div className="grid md:grid-cols-3 gap-8 w-full max-w-5xl text-left">
          <div className="glass p-6 rounded-2xl border border-zinc-800/50">
            <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center mb-4">
              <ShieldCheck className="w-6 h-6 text-emerald-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Accurate FOIR</h3>
            <p className="text-sm text-zinc-400">Calculate real repayment capacity by combining multiple income streams and obligations.</p>
          </div>
          <div className="glass p-6 rounded-2xl border border-zinc-800/50">
            <div className="w-12 h-12 bg-brand-500/10 rounded-xl flex items-center justify-center mb-4">
              <TrendingUp className="w-6 h-6 text-brand-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Interactive Structuring</h3>
            <p className="text-sm text-zinc-400">Pitch the perfect EMI with real-time risk alerts and what-if scenario planning.</p>
          </div>
          <div className="glass p-6 rounded-2xl border border-zinc-800/50">
            <div className="w-12 h-12 bg-rose-500/10 rounded-xl flex items-center justify-center mb-4">
              <Brain className="w-6 h-6 text-rose-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">NLP Sentiment</h3>
            <p className="text-sm text-zinc-400">Analyze unstructured CRM logs to understand customer emotional state before you call.</p>
          </div>
        </div>
      </main>
      
      {/* Footer */}
      <footer className="w-full py-8 mt-20 border-t border-zinc-800 text-center text-zinc-500 text-sm">
        <p>© 2026 Prospect Assist AI. All rights reserved.</p>
      </footer>
    </div>
  );
}
