"use client";

import React, { useState, useEffect } from 'react';
import { X, Bot, FileText, CheckCircle, AlertTriangle, ShieldCheck, TrendingUp, IndianRupee, Loader2 } from 'lucide-react';
import axios from 'axios';
import { clsx } from 'clsx';

interface CustomerSidePanelProps {
  isOpen: boolean;
  onClose: () => void;
  customer: any | null;
}

const API_URL = 'http://localhost:8000/api';

export default function CustomerSidePanel({ isOpen, onClose, customer }: CustomerSidePanelProps) {
  const [loading, setLoading] = useState(false);
  const [aiData, setAiData] = useState<any>(null);

  useEffect(() => {
    if (isOpen && customer) {
      fetchAiAnalysis();
    } else {
      setAiData(null);
    }
  }, [isOpen, customer]);

  const fetchAiAnalysis = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/analyze/${customer.customer_id}`);
      setAiData(res.data);
    } catch (error) {
      console.error("Error fetching AI analysis", error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <div 
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity"
        onClick={onClose}
      />
      
      <div 
        className={clsx(
          "fixed right-0 top-0 bottom-0 w-full md:w-[500px] glass-panel z-50 shadow-2xl transition-transform duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] overflow-y-auto",
          isOpen ? "translate-x-0" : "translate-x-full"
        )}
      >
        <div className="p-6">
          <div className="flex justify-between items-center mb-8 sticky top-0 bg-[#09090b]/80 backdrop-blur-md pb-4 border-b border-zinc-800/50 z-10">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <Bot className="w-5 h-5 text-brand-400" />
              AI Intelligence
            </h2>
            <button 
              onClick={onClose}
              className="p-2 hover:bg-zinc-800 rounded-full transition-colors text-zinc-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {!customer && !loading && (
            <div className="text-zinc-400 text-center py-20">No customer selected</div>
          )}

          {loading && (
            <div className="flex flex-col items-center justify-center py-32 text-center animate-fade-in">
              <div className="relative">
                <div className="absolute inset-0 bg-brand-500 blur-xl opacity-20 rounded-full" />
                <Loader2 className="w-10 h-10 text-brand-400 animate-spin relative z-10" />
              </div>
              <h3 className="text-lg font-medium mt-6 text-white">Analyzing Financial Profile</h3>
              <p className="text-zinc-400 text-sm mt-2 max-w-[250px]">Gemini is processing behavioral data and generating insights...</p>
            </div>
          )}

          {!loading && aiData && customer && (
            <div className="space-y-6 animate-slide-up" style={{ animationDuration: '0.4s' }}>
              
              {/* Header Stats */}
              <div className="grid grid-cols-2 gap-4">
                <div className="glass p-4 rounded-xl border border-brand-500/20 bg-brand-500/5">
                  <div className="text-xs text-brand-300 font-medium mb-1">Lead Score</div>
                  <div className="text-3xl font-bold text-white flex items-baseline gap-1">
                    {aiData.lead_score} <span className="text-sm font-normal text-zinc-500">/ 100</span>
                  </div>
                </div>
                <div className="glass p-4 rounded-xl">
                  <div className="text-xs text-zinc-400 font-medium mb-1">Estimated Income</div>
                  <div className="text-2xl font-bold text-white">
                    ₹{aiData.income_estimate.toLocaleString()}
                  </div>
                </div>
              </div>

              {/* Badges row */}
              <div className="flex flex-wrap gap-2">
                <Badge icon={ShieldCheck} label="Repayment" value={aiData.repayment_capacity} color="emerald" />
                <Badge icon={TrendingUp} label="Intent" value={aiData.intent} color="brand" />
                <Badge icon={AlertTriangle} label="Risk" value={aiData.risk_level} color={aiData.risk_level === 'Low' ? 'emerald' : 'rose'} />
              </div>

              {/* Recommendation */}
              <div className="glass rounded-xl p-5 border-l-4 border-l-indigo-500 bg-gradient-to-r from-indigo-500/10 to-transparent">
                <h3 className="text-sm font-semibold text-indigo-300 mb-1 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" /> Recommended Product
                </h3>
                <div className="text-xl font-bold text-white">
                  {aiData.loan_recommendation}
                </div>
                <div className="text-sm text-zinc-300 mt-2">
                  Probability of conversion: <span className="font-semibold text-emerald-400">{aiData.conversion_probability}</span>
                </div>
              </div>

              {/* AI Explanation */}
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider flex items-center gap-2">
                  <FileText className="w-4 h-4" /> AI Explanation
                </h3>
                <div className="glass p-5 rounded-xl text-sm leading-relaxed text-zinc-300">
                  {aiData.summary}
                </div>
              </div>

              {/* Key Reasons */}
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider">Key Indicators</h3>
                <ul className="space-y-2">
                  {aiData.key_reasons.map((reason: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-zinc-300 bg-zinc-900/40 p-3 rounded-lg border border-zinc-800/50">
                      <div className="min-w-1.5 h-1.5 rounded-full bg-brand-500 mt-1.5" />
                      {reason}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Next Best Action */}
              <div className="mt-8 pt-6 border-t border-zinc-800/50">
                <h3 className="text-xs font-semibold text-rose-400 uppercase tracking-wider mb-3">RM Next Best Action</h3>
                <div className="bg-rose-500/10 border border-rose-500/20 rounded-xl p-5 shadow-[0_0_15px_rgba(244,63,94,0.1)]">
                  <p className="text-rose-100 font-medium">
                    {aiData.next_best_action}
                  </p>
                </div>
              </div>

            </div>
          )}
        </div>
      </div>
    </>
  );
}

function Badge({ icon: Icon, label, value, color }: { icon: any, label: string, value: string, color: 'emerald' | 'brand' | 'rose' }) {
  const colors = {
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    brand: 'bg-brand-500/10 text-brand-400 border-brand-500/20',
    rose: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
  };

  return (
    <div className={clsx("flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium", colors[color])}>
      <Icon className="w-3.5 h-3.5" />
      <span className="opacity-70">{label}:</span> {value}
    </div>
  );
}
