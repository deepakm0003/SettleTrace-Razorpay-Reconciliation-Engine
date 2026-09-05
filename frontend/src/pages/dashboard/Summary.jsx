import { useState, useEffect } from 'react';
import { getMetrics } from '../../api';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';

const STATUS_CONFIG = {
  matched:         { label: 'Matched',          color: '#16a34a', bg: 'bg-green-50',  border: 'border-green-400'  },
  needs_review:    { label: 'Needs Review',      color: '#d97706', bg: 'bg-amber-50',  border: 'border-amber-400'  },
  partial_hold:    { label: 'Partial Hold',      color: '#7c3aed', bg: 'bg-purple-50', border: 'border-purple-400' },
  settlement_lag:  { label: 'Settlement Lag',    color: '#2563eb', bg: 'bg-blue-50',   border: 'border-blue-400'   },
};

function StatCard({ label, value, sub }) {
  return (
    <div className="bg-white border-2 border-black rounded-2xl p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,0.8)] hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,0.8)] hover:translate-x-[-2px] hover:translate-y-[-2px] transition-all">
      <p className="text-xs font-black text-gray-500 uppercase tracking-widest mb-3">{label}</p>
      <p className="text-5xl font-black text-gray-900 leading-none mb-2">{value}</p>
      {sub && <p className="text-sm text-gray-500 font-medium">{sub}</p>}
    </div>
  );
}

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border-2 border-black rounded-xl p-4 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">
        <p className="font-black text-gray-900 mb-1">{label}</p>
        <p className="text-sm text-gray-600">Count: <strong>{payload[0].value}</strong></p>
      </div>
    );
  }
  return null;
};

export default function Summary() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => { fetchMetrics(); }, []);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const data = await getMetrics();
      setMetrics(data);
      setError(null);
    } catch (err) {
      setError('Could not reach the backend. Make sure uvicorn is running on port 8001.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-black border-t-[#0066FF] rounded-full animate-spin mx-auto mb-4"></div>
          <p className="font-black text-gray-600">Loading metrics from backend...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="border-2 border-black rounded-2xl bg-red-50 p-8 shadow-[4px_4px_0px_0px_rgba(0,0,0,0.8)]">
        <p className="font-black text-red-800 text-lg mb-2">Backend Unreachable</p>
        <p className="text-red-700 font-medium">{error}</p>
        <code className="block mt-4 text-sm bg-red-100 border-2 border-red-300 rounded-lg p-3 font-mono">
          cd backend &amp;&amp; python -m uvicorn app.main:app --reload --port 8001
        </code>
      </div>
    );
  }

  const rec = metrics.reconciliation_metrics;
  const cls = metrics.classification_metrics;
  const breakdown = rec.status_breakdown;

  const chartData = Object.entries(breakdown).map(([status, count]) => ({
    name: STATUS_CONFIG[status]?.label || status,
    count,
    pct: ((count / rec.total_orders) * 100).toFixed(1),
    color: STATUS_CONFIG[status]?.color || '#666',
  }));

  return (
    <div className="space-y-8">

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard label="Total Orders"          value={rec.total_orders}                              sub="From orders_ledger.csv" />
        <StatCard label="Match Rate"            value={`${rec.match_rate_percent}%`}                 sub={`${rec.resolved_count} resolved`} />
        <StatCard label="Agent Cases"           value={cls.total_agent_cases}                        sub="Went through LLM" />
        <StatCard label="Agent Accuracy"        value={`${(cls.overall_accuracy * 100).toFixed(0)}%`} sub="NVIDIA Nemotron 550B (50 samples)" />
      </div>

      {/* Status breakdown */}
      <div className="grid lg:grid-cols-2 gap-6">

        {/* Bar chart */}
        <div className="bg-white border-2 border-black rounded-2xl p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,0.6)]">
          <p className="font-black text-gray-900 text-lg mb-1">Status Breakdown</p>
          <p className="text-sm text-gray-500 font-medium mb-6">Distribution across 2,500 orders</p>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData} barCategoryGap="30%">
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="name" tick={{ fontSize: 12, fontWeight: 700 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} stroke="#000" strokeWidth={1.5} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Status list */}
        <div className="bg-white border-2 border-black rounded-2xl p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,0.6)] space-y-3">
          <p className="font-black text-gray-900 text-lg mb-4">By Status</p>
          {chartData.map((item, i) => (
            <div key={i} className="flex items-center justify-between py-3 border-b-2 border-dashed border-gray-200 last:border-0">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-sm border border-black" style={{ backgroundColor: item.color }}></div>
                <span className="font-bold text-gray-800 text-sm">{item.name}</span>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-28 h-2 bg-gray-100 border border-gray-300 rounded-full overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${item.pct}%`, backgroundColor: item.color }}></div>
                </div>
                <span className="text-sm font-black text-gray-900 w-8 text-right">{item.count}</span>
                <span className="text-xs text-gray-400 font-medium w-10 text-right">{item.pct}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Notes from backend */}
      {metrics.notes && (
        <div className="bg-white border-2 border-black rounded-2xl p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,0.4)]">
          <p className="font-black text-gray-900 mb-2">Backend Notes</p>
          <p className="text-sm text-gray-600 font-medium">{metrics.notes}</p>
        </div>
      )}
    </div>
  );
}
