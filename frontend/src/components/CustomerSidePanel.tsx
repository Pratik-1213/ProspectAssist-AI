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

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export default function CustomerSidePanel({ isOpen, onClose, customer }: CustomerSidePanelProps) {
  const [loading, setLoading] = useState(false);
  const [aiData, setAiData] = useState<any>(null);
  const [proposedEmi, setProposedEmi] = useState<number>(0);

  useEffect(() => {
    if (isOpen && customer) {
      setProposedEmi(customer.fixed_emi_obligations || 5000);
      fetchAiAnalysis();
    } else {
      setAiData(null);
    }
  }, [isOpen, customer]);

  const fetchAiAnalysis = async () => {
    try {
      setLoading(true);
      const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      const res = await axios.post(`${API_URL}/analyze/${customer.customer_id}`, {}, { headers });
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
                <div className="glass p-4 rounded-xl relative group">
                  <div className="text-xs text-zinc-400 font-medium mb-1">Accurate Income</div>
                  <div className="text-2xl font-bold text-white">
                    ₹{aiData.income_estimate.toLocaleString()}
                  </div>
                  <div className="text-xs text-zinc-500 mt-1 flex justify-between">
                    <span>FOIR: {Math.round((customer.foir || 0)*100)}%</span>
                  </div>
                  
                  {/* Tooltip for Income Breakdown */}
                  <div className="absolute top-full right-0 mt-2 p-3 bg-zinc-900 border border-zinc-800 rounded-lg shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50 text-xs w-48 space-y-1.5">
                    <div className="flex justify-between"><span className="text-zinc-400">Salary:</span> <span>₹{customer.salary_credits?.toLocaleString()}</span></div>
                    <div className="flex justify-between"><span className="text-zinc-400">Investments:</span> <span>₹{customer.investment_income?.toLocaleString()}</span></div>
                    <div className="flex justify-between"><span className="text-zinc-400">RDs:</span> <span>₹{customer.recurring_deposits?.toLocaleString()}</span></div>
                  </div>
                </div>
              </div>

              {/* Badges row */}
              <div className="flex flex-wrap gap-2">
                <Badge icon={ShieldCheck} label="Repayment" value={aiData.repayment_capacity} color="emerald" />
                <Badge icon={TrendingUp} label="Intent" value={aiData.intent} color="brand" />
                <Badge icon={AlertTriangle} label="Risk" value={aiData.risk_level} color={aiData.risk_level === 'Low' ? 'emerald' : 'rose'} />
                
                {customer.sentiment_score !== undefined && (
                  <Badge 
                    icon={customer.sentiment_score >= 60 ? TrendingUp : (customer.sentiment_score <= 40 ? AlertTriangle : CheckCircle)} 
                    label="Sentiment" 
                    value={customer.sentiment_score >= 60 ? "Positive" : (customer.sentiment_score <= 40 ? "Negative" : "Neutral")} 
                    color={customer.sentiment_score >= 60 ? 'emerald' : (customer.sentiment_score <= 40 ? 'rose' : 'brand')} 
                  />
                )}
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

              {/* Interactive RM Deal Structurer */}
              <div className="mt-8 pt-6 border-t border-zinc-800/50">
                <h3 className="text-xs font-semibold text-brand-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" /> RM Deal Structurer
                </h3>
                <div className="glass p-5 rounded-xl bg-gradient-to-br from-brand-500/5 to-transparent border-brand-500/20">
                  <div className="flex justify-between items-end mb-4">
                    <div>
                      <div className="text-sm text-zinc-400 mb-1">Proposed Monthly EMI</div>
                      <div className="text-2xl font-bold text-white">₹{proposedEmi.toLocaleString()}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-zinc-400 mb-1">Projected FOIR</div>
                      <div className={clsx("text-xl font-bold", (proposedEmi / (customer.estimated_income || 1)) > 0.5 ? "text-rose-400" : "text-emerald-400")}>
                        {Math.round((proposedEmi / (customer.estimated_income || 1)) * 100)}%
                      </div>
                    </div>
                  </div>
                  
                  <input 
                    type="range" 
                    min="1000" 
                    max={Math.max(100000, (customer.estimated_income || 50000))} 
                    step="500" 
                    value={proposedEmi}
                    onChange={(e) => setProposedEmi(Number(e.target.value))}
                    className="w-full h-2 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-brand-500"
                  />
                  
                  {(proposedEmi / (customer.estimated_income || 1)) > 0.5 && (
                    <div className="mt-4 p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg flex items-start gap-2 text-rose-400 text-sm">
                      <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      <p>Warning: Pitching this EMI pushes the customer's FOIR over 50%. High risk of default and likely rejection.</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Next Best Action */}
              <div className="mt-6 pt-6 border-t border-zinc-800/50">
                <h3 className="text-xs font-semibold text-rose-400 uppercase tracking-wider mb-3">AI Next Best Action</h3>
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
