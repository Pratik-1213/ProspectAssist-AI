"use client";

import React, { useState, useEffect } from 'react';
import { Settings, RefreshCw, CheckCircle2, AlertTriangle, ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export default function SettingsPage() {
  const router = useRouter();
  const [config, setConfig] = useState<any>({
    weight_salary_stability: "0.25",
    weight_average_balance: "0.20",
    weight_emi_history: "0.15",
    weight_credit_score: "0.15",
    weight_product_interest: "0.15",
    weight_spending_pattern: "0.10",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [message, setMessage] = useState<{type: 'success' | 'error', text: string} | null>(null);

  const getAuthHeaders = () => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (!token) {
      router.push('/login');
      return;
    }
    
    // Check if admin
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      if (payload.role !== 'admin') {
        router.push('/');
        return;
      }
    } catch (e) {
      router.push('/');
      return;
    }

    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API_URL}/config`, { headers: getAuthHeaders() });
      setConfig(res.data);
    } catch (error) {
      console.error("Error fetching config", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate that sum is roughly 1.0
    const sum = Object.values(config).reduce((acc: number, val: any) => acc + parseFloat(val), 0);
    if (sum < 0.99 || sum > 1.01) {
      setMessage({ type: 'error', text: `Weights must sum up to exactly 1.0. Current sum is ${sum.toFixed(2)}` });
      return;
    }

    try {
      setSaving(true);
      await axios.post(`${API_URL}/config`, { configs: config }, { headers: getAuthHeaders() });
      setMessage({ type: 'success', text: "Lead scoring weights updated successfully!" });
      setTimeout(() => setMessage(null), 3000);
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || "Failed to update configuration" });
    } finally {
      setSaving(false);
    }
  };

  const handleSyncCRM = async () => {
    try {
      setSyncing(true);
      const res = await axios.post(`${API_URL}/crm/sync`, {}, { headers: getAuthHeaders() });
      setMessage({ type: 'success', text: res.data.message });
      setTimeout(() => setMessage(null), 4000);
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || "Failed to synchronize CRM" });
    } finally {
      setSyncing(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-white">Loading Settings...</div>;
  }

  return (
    <div className="min-h-screen p-6 lg:p-8 animate-fade-in relative overflow-hidden">
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-brand-600/10 blur-[120px] pointer-events-none" />
      
      <header className="mb-10 relative z-10">
        <button 
          onClick={() => router.push('/')}
          className="flex items-center gap-2 text-zinc-400 hover:text-white transition-colors mb-6 text-sm"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Dashboard
        </button>
        <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
          <div className="p-2 bg-brand-500/20 rounded-xl border border-brand-500/30">
            <Settings className="w-6 h-6 text-brand-400" />
          </div>
          System Configuration
        </h1>
        <p className="text-zinc-400 mt-2 ml-1">Admin Panel: Adjust lead scoring logic and manage integrations</p>
      </header>

      {message && (
        <div className={`p-4 rounded-xl mb-6 flex items-center gap-3 border relative z-10 ${
          message.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-rose-500/10 border-rose-500/20 text-rose-400'
        }`}>
          {message.type === 'success' ? <CheckCircle2 className="w-5 h-5" /> : <AlertTriangle className="w-5 h-5" />}
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 relative z-10">
        
        {/* Rules Engine Form */}
        <form onSubmit={handleSave} className="glass rounded-2xl p-6">
          <h2 className="text-xl font-semibold mb-2">Lead Scoring Weights</h2>
          <p className="text-sm text-zinc-400 mb-6">Configure the AI engine's emphasis on different customer metrics. Total must equal 1.0</p>
          
          <div className="space-y-4">
            {Object.entries(config).map(([key, value]: [string, any]) => (
              <div key={key} className="flex justify-between items-center bg-zinc-900/50 p-3 rounded-lg border border-zinc-800/50">
                <label className="text-sm font-medium text-zinc-300 capitalize">
                  {key.replace('weight_', '').replace(/_/g, ' ')}
                </label>
                <input 
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={value}
                  onChange={(e) => setConfig({...config, [key]: e.target.value})}
                  className="bg-zinc-950 border border-zinc-800 rounded-md px-3 py-1.5 w-24 text-right text-white focus:border-brand-500 focus:outline-none transition-colors"
                  required
                />
              </div>
            ))}
          </div>
          
          <div className="mt-6 flex justify-end">
            <button 
              type="submit"
              disabled={saving}
              className="bg-brand-600 hover:bg-brand-500 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save Configuration'}
            </button>
          </div>
        </form>

        {/* CRM Integrations */}
        <div className="glass rounded-2xl p-6 h-fit">
          <h2 className="text-xl font-semibold mb-2">CRM Integrations</h2>
          <p className="text-sm text-zinc-400 mb-6">Manage external connections and data pipelines</p>
          
          <div className="bg-zinc-900/50 border border-zinc-800/50 rounded-xl p-5">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="font-medium text-white mb-1">Salesforce CRM Sync</h3>
                <p className="text-xs text-zinc-400">Push all qualified "Hot Leads" to Salesforce automatically.</p>
              </div>
              <span className="px-2.5 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded text-xs font-medium">
                Connected
              </span>
            </div>
            <button 
              type="button"
              onClick={handleSyncCRM}
              disabled={syncing}
              className="w-full flex justify-center items-center gap-2 bg-zinc-800 hover:bg-zinc-700 text-white py-2 rounded-lg transition-colors disabled:opacity-50 text-sm font-medium border border-zinc-700"
            >
              <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
              {syncing ? 'Synchronizing...' : 'Trigger Manual Sync'}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
