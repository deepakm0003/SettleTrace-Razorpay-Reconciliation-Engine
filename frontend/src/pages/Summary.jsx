import { useState, useEffect } from 'react';
import { getMetrics, refreshReconciliation } from '../api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell, LineChart, Line } from 'recharts';
import { RefreshCw, AlertCircle, TrendingUp } from 'lucide-react';

export default function Summary() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const data = await getMetrics();
      setMetrics(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch metrics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      await refreshReconciliation();
      await fetchMetrics();
    } catch (err) {
      setError('Failed to refresh reconciliation');
      console.error(err);
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center space-y-4">
          <div className="inline-block">
            <div className="w-12 h-12 rounded-full border-4 border-slate-600 border-t-accent-blue animate-spin"></div>
          </div>
          <p className="text-slate-300">Loading metrics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-500/50 rounded-xl p-4 flex items-start gap-3">
        <AlertCircle className="text-red-400 mt-0.5" size={20} />
        <div>
          <h3 className="font-semibold text-red-300">Error</h3>
          <p className="text-red-200 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  if (!metrics) return null;

  const recon = metrics.reconciliation_metrics || {};
  const classif = metrics.classification_metrics || {};
  
  const totalOrders = recon.total_orders || 0;
  const matchRate = recon.match_rate_percent || 0;
  const resolvedCount = recon.resolved_count || 0;
  const resolvedPercent = totalOrders > 0 ? ((resolvedCount / totalOrders) * 100).toFixed(1) : 0;
  const agentCases = classif.total_agent_cases || 0;

  const statusBreakdown = recon.status_breakdown ? 
    Object.entries(recon.status_breakdown).map(([status, count]) => ({
      name: status.replace(/_/g, ' ').toUpperCase(),
      count,
      percentage: totalOrders > 0 ? ((count / totalOrders) * 100).toFixed(1) : 0,
    })) : [];

  const statusColors = {
    'MATCHED': '#10b981',
    'NEEDS_REVIEW': '#f59e0b',
    'PARTIAL_HOLD': '#8b5cf6',
    'SETTLEMENT_LAG': '#6366f1',
  };

  return (
    <div className="space-y-8">
      {/* Header with Refresh */}
      <div className="flex justify-between items-center animate-fadeInUp">
        <div>
          <h3 className="text-2xl font-bold text-gray-100">Settlement Pipeline</h3>
          <p className="text-slate-400 mt-2">250 Razorpay orders across 42 settlement batches</p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="btn-primary flex items-center gap-2 disabled:opacity-50"
        >
          <RefreshCw size={18} className={refreshing ? 'animate-spin' : ''} />
          Refresh Pipeline
        </button>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-4 gap-6 animate-fadeInUp">
        {[
          { label: 'Total Orders', value: totalOrders, unit: '', color: 'from-blue-600 to-blue-400', icon: '📊' },
          { label: 'Match Rate', value: matchRate.toFixed(1), unit: '%', color: 'from-green-600 to-green-400', icon: '✅' },
          { label: 'Deterministically Resolved', value: resolvedPercent, unit: '%', color: 'from-indigo-600 to-indigo-400', icon: '⚙️' },
          { label: 'Agent Review Cases', value: agentCases, unit: '', color: 'from-orange-600 to-orange-400', icon: '🤖' },
        ].map((stat, idx) => (
          <div key={idx} className="stat-card group hover:pulse-glow">
            <div className="flex items-start justify-between mb-4">
              <span className="text-3xl">{stat.icon}</span>
              <TrendingUp size={16} className="text-slate-400 group-hover:text-accent-blue transition" />
            </div>
            <p className="text-slate-300 text-sm font-medium">{stat.label}</p>
            <p className={`text-4xl font-bold mt-3 bg-gradient-to-r ${stat.color} bg-clip-text text-transparent`}>
              {stat.value}{stat.unit}
            </p>
          </div>
        ))}
      </div>

      {/* Chart Section */}
      <div className="card p-8 animate-fadeInUp">
        <h3 className="text-xl font-bold text-gray-100 mb-6">Status Breakdown</h3>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={statusBreakdown}>
            <defs>
              <linearGradient id="gradientBar" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#0066FF" />
                <stop offset="100%" stopColor="#00D4FF" />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#404854" />
            <XAxis dataKey="name" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #404854', borderRadius: '8px' }}
              labelStyle={{ color: '#e5e7eb' }}
              formatter={(value, name) => {
                if (name === 'count') return [value, 'Count'];
                return value;
              }}
              content={({ active, payload }) => {
                if (active && payload && payload[0]) {
                  const data = payload[0].payload;
                  return (
                    <div className="bg-slate-800 p-3 border border-slate-600 rounded-lg shadow-xl">
                      <p className="font-semibold text-gray-100">{data.name}</p>
                      <p className="text-sm text-accent-blue">Count: {data.count}</p>
                      <p className="text-sm text-green-400">{data.percentage}%</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar dataKey="count" radius={[12, 12, 0, 0]} fill="url(#gradientBar)">
              {statusBreakdown.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={statusColors[entry.name] || '#6b7280'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Info Banner */}
      <div className="bg-gradient-to-r from-blue-900/40 to-indigo-900/40 border border-blue-600/50 rounded-xl p-6 animate-fadeInUp">
        <p className="text-blue-200 font-semibold mb-2">📌 Batch-Level Anomalies</p>
        <p className="text-blue-300 text-sm leading-relaxed">
          4 orphan bank credits detected as batch-level anomalies with no matching settlement. 
          They are tracked separately and excluded from order-level metrics to maintain accuracy.
        </p>
      </div>
    </div>
  );
}
