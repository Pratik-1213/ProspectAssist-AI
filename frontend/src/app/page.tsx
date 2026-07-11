import Dashboard from '@/components/Dashboard';

export const metadata = {
  title: 'ProspectAssist AI',
  description: 'AI-Powered Lending Lead Intelligence Platform',
};

export default function Home() {
  return (
    <main className="min-h-screen bg-[#09090b] selection:bg-brand-500/30">
      <Dashboard />
    </main>
  );
}
