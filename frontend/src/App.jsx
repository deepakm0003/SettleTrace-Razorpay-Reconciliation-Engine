import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { BarChart3, AlertTriangle, Search, FileText, Zap } from 'lucide-react';
import Summary from './pages/Summary';
import Exceptions from './pages/Exceptions';
import OrderLookup from './pages/OrderLookup';
import Evaluation from './pages/Evaluation';
import './index.css';

export default function App() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <Router>
      <div className="flex h-screen bg-slate-900 text-gray-100">
        {/* Sidebar */}
        <div className="w-72 bg-gradient-to-b from-slate-900 to-slate-950 border-r border-slate-700 shadow-2xl flex flex-col">
          {/* Header */}
          <div className="p-8 border-b border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-accent-blue to-blue-600 flex items-center justify-center">
                <Zap size={24} className="text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold glow-text">SettleTrace</h1>
              </div>
            </div>
            <p className="text-sm text-slate-400">Razorpay Settlement Reconciliation</p>
            <p className="text-xs text-slate-500 mt-2">RAG-Grounded LLM Engine</p>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-8 space-y-2">
            {[
              { path: '/', icon: BarChart3, label: 'Summary' },
              { path: '/exceptions', icon: AlertTriangle, label: 'Exceptions' },
              { path: '/order-lookup', icon: Search, label: 'Order Lookup' },
              { path: '/evaluation', icon: FileText, label: 'Evaluation' },
            ].map(({ path, icon: Icon, label }) => (
              <Link
                key={path}
                to={path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300 group ${
                  isActive(path)
                    ? 'bg-gradient-to-r from-accent-blue/20 to-blue-600/20 border border-accent-blue/50 text-accent-blue'
                    : 'text-slate-300 hover:text-gray-100 hover:bg-slate-800/50'
                }`}
              >
                <Icon size={20} className={`transition-all ${isActive(path) ? 'text-accent-blue' : 'group-hover:text-accent-blue'}`} />
                <span className="font-medium">{label}</span>
                {isActive(path) && <div className="ml-auto w-1 h-6 bg-gradient-to-b from-accent-blue to-blue-600 rounded-full" />}
              </Link>
            ))}
          </nav>

          {/* Footer */}
          <div className="p-6 border-t border-slate-700 bg-slate-900/50">
            <div className="text-xs text-slate-500 space-y-2">
              <p className="font-semibold text-slate-400">250 Orders</p>
              <p>92% Reconciled</p>
              <p>40% Agent Accuracy</p>
              <p className="text-slate-600 mt-3">Honest Metrics • Zero API Cost</p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-auto bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
          {/* Top Bar */}
          <div className="sticky top-0 z-10 bg-slate-900/80 backdrop-blur-md border-b border-slate-700 px-8 py-4 flex justify-between items-center">
            <div>
              <h2 className="text-xl font-bold text-gray-100">
                {location.pathname === '/' && 'Settlement Summary'}
                {location.pathname === '/exceptions' && 'Exception Triage'}
                {location.pathname === '/order-lookup' && 'Order Lookup'}
                {location.pathname === '/evaluation' && 'Evaluation Metrics'}
              </h2>
            </div>
            <div className="text-sm text-slate-400">
              Connected to Backend • http://localhost:8000
            </div>
          </div>

          {/* Page Content */}
          <div className="p-8">
            <Routes>
              <Route path="/" element={<Summary />} />
              <Route path="/exceptions" element={<Exceptions />} />
              <Route path="/order-lookup" element={<OrderLookup />} />
              <Route path="/order/:orderId" element={<OrderLookup />} />
              <Route path="/evaluation" element={<Evaluation />} />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
}
