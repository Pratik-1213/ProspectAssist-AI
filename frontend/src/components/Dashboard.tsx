"use client";

import React, { useState, useEffect } from 'react';
import { 
  UploadCloud, 
  Users, 
  Target, 
  Flame, 
  TrendingUp, 
  IndianRupee,
  Activity,
  LogOut,
  Download
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import CustomerSidePanel from './CustomerSidePanel';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const COLORS = ['#6366f1', '#8b5cf6', '#d946ef', '#f43f5e'];
const PIE_COLORS = ['#3f3f46', '#818cf8', '#6366f1', '#4338ca'];

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [customers, setCustomers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedCustomer, setSelectedCustomer] = useState<any>(null);
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [userRole, setUserRole] = useState('loan_officer');
  
  // Pagination
  const [page, setPage] = useState(0);
  const itemsPerPage = 10;
  
  const router = useRouter();

  const getAuthHeaders = () => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/login');
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API_URL}/dashboard`, {
        headers: getAuthHeaders()
      });
      setData(res.data);
    } catch (error: any) {
      if (error.response?.status === 401) {
        handleLogout();
      }
      console.error("Error fetching dashboard data", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCustomers = async (skip=0, limit=500) => {
    try {
      const res = await axios.get(`${API_URL}/customers?skip=${skip}&limit=${limit}`, {
        headers: getAuthHeaders()
      });
      setCustomers(res.data);
    } catch (e) {
      console.error("Error fetching customers", e);
    }
  };

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (!token) {
      router.push('/login');
      return;
    }
    
    // Parse role
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      if (payload.role) setUserRole(payload.role);
    } catch (e) {}
    
    fetchDashboardData();
    fetchCustomers();
  }, []);

  const handleDownloadMockData = async () => {
    try {
      const res = await axios.get(`${API_URL}/download-mock-csv`, {
        headers: getAuthHeaders(),
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'mock_customers.csv');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Error downloading mock data", error);
    }
  };
  
  const handleExportCSV = async () => {
    try {
      const res = await axios.get(`${API_URL}/export-customers`, {
        headers: getAuthHeaders(),
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'exported_customers.csv');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Error exporting data", error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    
    const clientId = Math.random().toString(36).substring(7);
    const WS_URL = API_URL.replace(/^http/, 'ws');
    const ws = new WebSocket(`${WS_URL}/ws/${clientId}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'progress') {
        setUploadProgress(data.percent);
      } else if (data.type === 'complete') {
        setIsUploading(false);
        setUploadProgress(0);
        ws.close();
        fetchDashboardData();
        fetchCustomers();
      }
    };

    setIsUploading(true);
    setUploadProgress(0);
    try {
      await axios.post(`${API_URL}/upload?client_id=${clientId}`, formData, {
        headers: { 
          'Content-Type': 'multipart/form-data',
          ...getAuthHeaders()
        }
      });
    } catch (error) {
      console.error("Error uploading file", error);
      alert("Error uploading file. Please ensure it's a valid CSV.");
      setIsUploading(false);
      ws.close();
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-rose-400 bg-rose-400/10 border-rose-400/20';
    if (score >= 70) return 'text-indigo-400 bg-indigo-400/10 border-indigo-400/20';
    if (score >= 40) return 'text-amber-400 bg-amber-400/10 border-amber-400/20';
    return 'text-zinc-400 bg-zinc-400/10 border-zinc-400/20';
  };
  
  const maskPII = (text: string) => {
    if (!text) return '';
    if (userRole === 'admin') return text;
    if (text.length > 4) {
      return '*'.repeat(text.length - 4) + text.slice(-4);
    }
    return '***';
  };

  const displayedCustomers = customers.slice(page * itemsPerPage, (page + 1) * itemsPerPage);

  return (
    <div className="min-h-screen p-6 lg:p-8 animate-fade-in relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-brand-600/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-rose-600/10 blur-[120px] pointer-events-none" />

      <header className="flex justify-between items-center mb-10 relative z-10">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <div className="p-2 bg-brand-500/20 rounded-xl border border-brand-500/30">
              <Activity className="w-6 h-6 text-brand-400" />
            </div>
            ProspectAssist <span className="text-brand-400 font-light">AI</span>
          </h1>
          <p className="text-zinc-400 mt-2 ml-1">AI-Powered Lending Lead Intelligence Platform | {userRole === 'admin' ? 'Admin Mode' : 'Officer Mode'}</p>
        </div>

        <div className="flex gap-4">
          <button 
            onClick={handleDownloadMockData}
            className="px-4 py-2 rounded-lg font-medium text-sm border border-zinc-700 text-zinc-300 hover:bg-zinc-800 transition-colors flex items-center gap-2"
          >
            Download Mock CSV
          </button>
          
          <button 
            onClick={handleExportCSV}
            className="px-4 py-2 rounded-lg font-medium text-sm border border-zinc-700 text-zinc-300 hover:bg-zinc-800 transition-colors flex items-center gap-2"
          >
            <Download className="w-4 h-4 text-emerald-400" /> Export Data
          </button>
          
          <label className="cursor-pointer glass px-5 py-2.5 rounded-lg font-medium text-sm text-white hover:bg-brand-600/20 hover:border-brand-500/50 transition-all flex items-center gap-2 group">
            <UploadCloud className="w-4 h-4 group-hover:scale-110 transition-transform text-brand-400" />
            {isUploading ? `Analyzing... ${uploadProgress}%` : 'Upload CSV'}
            <input type="file" accept=".csv" className="hidden" onChange={handleFileUpload} disabled={isUploading} />
          </label>
          
          <button 
            onClick={handleLogout}
            className="px-4 py-2 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 rounded-lg text-sm font-medium transition-colors border border-rose-500/20 flex items-center gap-2"
          >
            <LogOut className="w-4 h-4" /> Logout
          </button>
        </div>
      </header>
      
      {isUploading && (
        <div className="w-full h-1 bg-zinc-800 rounded-full mb-8 relative z-10 overflow-hidden">
          <div 
            className="h-full bg-brand-500 transition-all duration-300"
            style={{ width: `${uploadProgress}%` }}
          />
        </div>
      )}

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-10 relative z-10">
        <KPICard title="Total Customers" value={data?.total_customers || 0} icon={Users} color="text-zinc-400" />
        <KPICard title="Qualified Leads" value={data?.qualified_leads || 0} icon={Target} color="text-indigo-400" />
        <KPICard title="Hot Leads" value={data?.hot_leads || 0} icon={Flame} color="text-rose-400" />
        <KPICard title="Expected Conversion" value={`${data?.expected_conversion || 0}%`} icon={TrendingUp} color="text-emerald-400" />
        <KPICard title="Avg. Income" value={`₹${((data?.average_income || 0)/1000).toFixed(1)}k`} icon={IndianRupee} color="text-amber-400" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-10 relative z-10">
        {/* Charts */}
        <div className="lg:col-span-2 glass rounded-2xl p-6 animate-slide-up" style={{ animationDelay: '0.1s' }}>
          <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
            <Target className="w-5 h-5 text-brand-400" />
            Lead Distribution
          </h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.lead_distribution || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                <XAxis dataKey="name" stroke="#71717a" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#71717a" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px' }}
                  itemStyle={{ color: '#e0e7ff' }}
                />
                <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]}>
                  {
                    (data?.lead_distribution || []).map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))
                  }
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass rounded-2xl p-6 animate-slide-up" style={{ animationDelay: '0.2s' }}>
          <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
            <IndianRupee className="w-5 h-5 text-brand-400" />
            Income Segments
          </h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data?.income_distribution || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                >
                  {
                    (data?.income_distribution || []).map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))
                  }
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px' }}
                  itemStyle={{ color: '#e0e7ff' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap justify-center gap-3 mt-2">
            {(data?.income_distribution || []).map((entry: any, index: number) => (
              <div key={index} className="flex items-center gap-1.5 text-xs text-zinc-400">
                <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: PIE_COLORS[index % PIE_COLORS.length] }} />
                {entry.name}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Customer Data Table */}
      {customers.length > 0 && (
        <div className="glass rounded-2xl overflow-hidden relative z-10 animate-slide-up" style={{ animationDelay: '0.3s' }}>
          <div className="p-6 border-b border-zinc-800 flex justify-between items-center">
            <h3 className="text-lg font-semibold">Analyzed Prospects</h3>
            <div className="flex items-center gap-4">
              <span className="text-sm text-zinc-400">Total {customers.length} results</span>
              <div className="flex gap-2">
                <button 
                  onClick={() => setPage(Math.max(0, page - 1))}
                  disabled={page === 0}
                  className="px-3 py-1 bg-zinc-800 text-sm rounded disabled:opacity-50"
                >
                  Prev
                </button>
                <span className="text-sm py-1">Page {page + 1}</span>
                <button 
                  onClick={() => setPage(page + 1)}
                  disabled={(page + 1) * itemsPerPage >= customers.length}
                  className="px-3 py-1 bg-zinc-800 text-sm rounded disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-zinc-400 uppercase bg-zinc-900/50 border-b border-zinc-800">
                <tr>
                  <th className="px-6 py-4 font-medium">Customer (PII Masked)</th>
                  <th className="px-6 py-4 font-medium">Est. Income</th>
                  <th className="px-6 py-4 font-medium">Eligibility</th>
                  <th className="px-6 py-4 font-medium">Intent</th>
                  <th className="px-6 py-4 font-medium">Conversion</th>
                  <th className="px-6 py-4 font-medium">Lead Score</th>
                  <th className="px-6 py-4 text-right font-medium">Action</th>
                </tr>
              </thead>
              <tbody>
                {displayedCustomers.map((c, i) => (
                  <tr 
                    key={c.customer_id} 
                    className="border-b border-zinc-800/50 hover:bg-zinc-800/30 transition-colors group cursor-pointer"
                    onClick={() => {
                      setSelectedCustomer(c);
                      setIsPanelOpen(true);
                    }}
                  >
                    <td className="px-6 py-4">
                      <div className="font-medium text-zinc-200">{maskPII(c.customer_id)}</div>
                      <div className="text-xs text-zinc-500 mt-1">{c.occupation}, {maskPII(c.location)}</div>
                    </td>
                    <td className="px-6 py-4">
                      ₹{c.estimated_income?.toLocaleString()}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex gap-2 flex-wrap">
                        {c.eligible_loans?.map((loan: string) => (
                          <span key={loan} className="px-2 py-1 bg-zinc-800 text-zinc-300 rounded text-xs">
                            {loan}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-full bg-zinc-800 rounded-full h-1.5 max-w-[60px]">
                          <div 
                            className="bg-brand-500 h-1.5 rounded-full" 
                            style={{ width: `${c.intent_score || 0}%` }}
                          />
                        </div>
                        <span className="text-xs text-zinc-400">{c.intent_score}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1.5 font-medium text-emerald-400">
                        {c.predicted_conversion_rate || 30}%
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded-md text-xs font-semibold border ${getScoreColor(c.lead_score || 0)}`}>
                        {c.lead_score}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button 
                        className="text-brand-400 text-xs font-medium opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-end gap-1 w-full"
                      >
                        AI Insights <TrendingUp className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {customers.length === 0 && !isUploading && (
        <div className="glass rounded-2xl p-12 flex flex-col items-center justify-center text-center relative z-10 animate-slide-up" style={{ animationDelay: '0.3s' }}>
          <div className="w-16 h-16 bg-zinc-900 rounded-full flex items-center justify-center mb-4 border border-zinc-800">
            <UploadCloud className="w-8 h-8 text-zinc-500" />
          </div>
          <h3 className="text-xl font-semibold mb-2">No Data Available</h3>
          <p className="text-zinc-400 max-w-md">Upload a CSV file with customer data to generate AI insights, lead scores, and recommended actions.</p>
        </div>
      )}

      <CustomerSidePanel 
        isOpen={isPanelOpen} 
        onClose={() => setIsPanelOpen(false)} 
        customer={selectedCustomer} 
        userRole={userRole}
      />
    </div>
  );
}

function KPICard({ title, value, icon: Icon, color }: { title: string, value: string | number, icon: any, color: string }) {
  return (
    <div className="glass rounded-2xl p-5 animate-slide-up hover:-translate-y-1 transition-transform duration-300">
      <div className="flex justify-between items-start mb-4">
        <h4 className="text-sm font-medium text-zinc-400">{title}</h4>
        <div className={`p-2 rounded-lg bg-zinc-900/50 ${color}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className="text-2xl font-bold tracking-tight text-white">{value}</div>
    </div>
  );
}
