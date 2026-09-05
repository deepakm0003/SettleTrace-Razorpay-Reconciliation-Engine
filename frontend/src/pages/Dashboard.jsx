import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { BarChart3, AlertTriangle, Search, FileText, ArrowLeft, Activity } from 'lucide-react';
import Summary from './dashboard/Summary';
import Exceptions from './dashboard/Exceptions';
import OrderLookup from './dashboard/OrderLookup';
import Evaluation from './dashboard/Evaluation';

const navItems = [
  { path: '/dashboard', icon: BarChart3, label: 'Summary', description: 'Match rates & breakdown' },
  { path: '/dashboard/exceptions', icon: AlertTriangle, label: 'Exceptions', description: 'Flagged for review' },
  { path: '/dashboard/order-lookup', icon: Search, label: 'Order Lookup', description: 'Audit trail by order' },
  { path: '/dashboard/evaluation', icon: FileText, label: 'Evaluation', description: 'F1, precision, recall' },
];

const pageTitles = {
  '/dashboard': 'Settlement Summary',
  '/dashboard/exceptions': 'Exception Triage',
  '/dashboard/order-lookup': 'Order Lookup',
  '/dashboard/evaluation': 'Evaluation Metrics',
};

export default function Dashboard() {
  const location = useLocation();
  const isActive = (path) => location.pathname === path;
  const pageTitle = pageTitles[location.pathname] || 'Dashboard';

  return (
    <div className="flex h-screen bg-[#F5F4F0] font-sans">

      {/* Sidebar */}
      <aside className="w-72 bg-white border-r-2 border-black flex flex-col flex-shrink-0">

        {/* Logo area */}
        <div className="p-6 border-b-2 border-black">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-gray-500 hover:text-gray-900 text-sm font-bold mb-5 transition-colors"
          >
            <ArrowLeft size={14} />
            Back to Home
          </Link>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#0066FF] border-2 border-black rounded-xl flex items-center justify-center shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
              <Activity size={20} className="text-white" />
            </div>
            <div>
              <h1 className="text-xl font-black text-gray-900 leading-none">SettleTrace</h1>
              <p className="text-xs text-gray-500 font-medium mt-0.5">Reconciliation Engine</p>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 p-4 space-y-1">
          <p className="text-xs font-black text-gray-400 uppercase tracking-widest px-3 pt-2 pb-3">Navigation</p>
          {navItems.map(({ path, icon: Icon, label, description }) => (
            <Link
              key={path}
              to={path}
              className={`flex items-center gap-3 px-3 py-3 rounded-xl border-2 transition-all group ${
                isActive(path)
                  ? 'bg-[#0066FF] border-black text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]'
                  : 'border-transparent hover:border-black hover:bg-gray-50 text-gray-700'
              }`}
            >
              <Icon size={18} className="flex-shrink-0" />
              <div className="min-w-0">
                <p className="font-black text-sm leading-none">{label}</p>
                <p className={`text-xs mt-0.5 leading-none ${isActive(path) ? 'text-blue-100' : 'text-gray-400'}`}>
                  {description}
                </p>
              </div>
            </Link>
          ))}
        </nav>

        {/* Stats footer */}
        <div className="p-4 border-t-2 border-black">
          <div className="bg-[#F5F4F0] border-2 border-black rounded-xl p-4 space-y-2">
            <p className="text-xs font-black text-gray-500 uppercase tracking-widest mb-3">Live Stats</p>
            {[
              { label: 'Total Orders', value: '2,500' },
              { label: 'Match Rate', value: '82%' },
              { label: 'Agent Accuracy', value: '50%' },
              { label: 'API Cost', value: '$0' },
            ].map((stat) => (
              <div key={stat.label} className="flex justify-between items-center">
                <span className="text-xs text-gray-600 font-medium">{stat.label}</span>
                <span className="text-xs font-black text-gray-900">{stat.value}</span>
              </div>
            ))}
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col overflow-hidden">

        {/* Top bar */}
        <header className="bg-white border-b-2 border-black px-8 py-4 flex items-center justify-between flex-shrink-0">
          <div>
            <h2 className="text-2xl font-black text-gray-900">{pageTitle}</h2>
            <p className="text-sm text-gray-500 font-medium mt-0.5">Backend: localhost:8001 &nbsp;|&nbsp; Mode: Mock — set NVIDIA_API_KEY for NIM</p>
          </div>
          <Link
            to="/dashboard"
            className="px-4 py-2 bg-[#0066FF] text-white text-sm font-black rounded-lg border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[-1px] hover:translate-y-[-1px] transition-all"
          >
            Refresh Data
          </Link>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto p-8">
          <Routes>
            <Route path="/" element={<Summary />} />
            <Route path="/exceptions" element={<Exceptions />} />
            <Route path="/order-lookup" element={<OrderLookup />} />
            <Route path="/order/:orderId" element={<OrderLookup />} />
            <Route path="/evaluation" element={<Evaluation />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
