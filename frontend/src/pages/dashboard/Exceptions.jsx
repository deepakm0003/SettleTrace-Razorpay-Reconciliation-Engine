import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getExceptions } from '../../api';
import { ChevronRight } from 'lucide-react';

function ConfidenceBadge({ value }) {
  const pct = Math.round(value * 100);
  const color = value > 0.8
    ? 'bg-green-100 text-green-800 border-green-400'
    : value > 0.5
    ? 'bg-amber-100 text-amber-800 border-amber-400'
    : 'bg-red-100 text-red-800 border-red-400';
  const label = value > 0.8 ? 'High' : value > 0.5 ? 'Medium' : 'Low';

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-lg border-2 text-xs font-black ${color}`}>
      <span
        className="w-2 h-2 rounded-full border border-black"
        style={{ backgroundColor: value > 0.8 ? '#16a34a' : value > 0.5 ? '#d97706' : '#dc2626' }}
      ></span>
      {pct}% — {label}
    </span>
  );
}

function StatusBadge({ reason }) {
  return (
    <span className="inline-block px-3 py-1 bg-gray-100 border-2 border-black text-gray-800 rounded-lg text-xs font-black">
      {reason?.replace(/_/g, ' ') ?? 'unknown'}
    </span>
  );
}

export default function Exceptions() {
  const [exceptions, setExceptions] = useState([]);
  const [filtered, setFiltered]     = useState([]);
  const [reasonFilter, setFilter]   = useState('all');
  const [loading, setLoading]       = useState(true);
  const [error, setError]           = useState(null);
  const navigate = useNavigate();

  useEffect(() => { fetchExceptions(); }, []);

  useEffect(() => {
    setFiltered(
      reasonFilter === 'all'
        ? exceptions
        : exceptions.filter((e) => e.exception_reason === reasonFilter)
    );
  }, [reasonFilter, exceptions]);

  const fetchExceptions = async () => {
    try {
      const data = await getExceptions();
      setExceptions(data);
      setFiltered(data);
    } catch (err) {
      setError('Could not load exceptions from backend.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-12 h-12 border-4 border-black border-t-[#0066FF] rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="border-2 border-black rounded-2xl bg-red-50 p-8">
        <p className="font-black text-red-800">{error}</p>
      </div>
    );
  }

  const reasons = [...new Set(exceptions.map((e) => e.exception_reason).filter(Boolean))];
  const lowConf  = exceptions.filter((e) => e.confidence <= 0.5).length;
  const highConf = exceptions.filter((e) => e.confidence > 0.8).length;

  return (
    <div className="space-y-6">

      {/* Triage legend */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Low Confidence', sub: 'Route to human review immediately', count: lowConf, color: 'bg-red-50 border-red-400' },
          { label: 'Medium Confidence', sub: 'Review before approving', count: exceptions.filter(e => e.confidence > 0.5 && e.confidence <= 0.8).length, color: 'bg-amber-50 border-amber-400' },
          { label: 'High Confidence', sub: 'Agent is likely correct', count: highConf, color: 'bg-green-50 border-green-400' },
        ].map((t) => (
          <div key={t.label} className={`${t.color} border-2 rounded-2xl p-5 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,0.6)]`}>
            <p className="text-3xl font-black text-gray-900">{t.count}</p>
            <p className="font-black text-sm text-gray-900 mt-1">{t.label}</p>
            <p className="text-xs text-gray-600 mt-1">{t.sub}</p>
          </div>
        ))}
      </div>

      {/* Filter + table */}
      <div className="bg-white border-2 border-black rounded-2xl shadow-[4px_4px_0px_0px_rgba(0,0,0,0.6)] overflow-hidden">

        {/* Toolbar */}
        <div className="flex items-center justify-between px-6 py-4 border-b-2 border-black bg-gray-50">
          <p className="font-black text-gray-900">
            {filtered.length} exception{filtered.length !== 1 ? 's' : ''}
            {reasonFilter !== 'all' && <span className="text-[#0066FF]"> — {reasonFilter.replace(/_/g, ' ')}</span>}
          </p>
          <select
            value={reasonFilter}
            onChange={(e) => setFilter(e.target.value)}
            className="text-sm font-black bg-white border-2 border-black rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#0066FF]"
          >
            <option value="all">All reasons ({exceptions.length})</option>
            {reasons.map((r) => (
              <option key={r} value={r}>{r.replace(/_/g, ' ')}</option>
            ))}
          </select>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b-2 border-black bg-gray-50">
                <th className="px-6 py-4 text-left text-xs font-black uppercase tracking-widest text-gray-500">Order ID</th>
                <th className="px-6 py-4 text-left text-xs font-black uppercase tracking-widest text-gray-500">Exception Reason</th>
                <th className="px-6 py-4 text-left text-xs font-black uppercase tracking-widest text-gray-500">Confidence</th>
                <th className="px-6 py-4 text-left text-xs font-black uppercase tracking-widest text-gray-500">Cited Rule</th>
                <th className="px-6 py-4 text-left text-xs font-black uppercase tracking-widest text-gray-500">Explanation</th>
                <th className="px-6 py-4"></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((ex, idx) => (
                <tr
                  key={idx}
                  onClick={() => navigate(`/dashboard/order/${ex.order_id}`)}
                  className="border-b-2 border-dashed border-gray-200 hover:bg-blue-50 cursor-pointer transition-colors last:border-0"
                >
                  <td className="px-6 py-4">
                    <span className="font-black text-[#0066FF] font-mono">{ex.order_id}</span>
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge reason={ex.exception_reason} />
                  </td>
                  <td className="px-6 py-4">
                    <ConfidenceBadge value={ex.confidence ?? 0} />
                  </td>
                  <td className="px-6 py-4 max-w-[200px]">
                    <p className="text-xs text-gray-600 font-medium truncate" title={ex.cited_rule}>
                      {ex.cited_rule || '—'}
                    </p>
                  </td>
                  <td className="px-6 py-4 max-w-[240px]">
                    <p className="text-xs text-gray-600 truncate" title={ex.llm_explanation}>
                      {ex.llm_explanation || '—'}
                    </p>
                  </td>
                  <td className="px-6 py-4">
                    <ChevronRight size={16} className="text-gray-400" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Legend note */}
      <div className="border-2 border-black border-dashed rounded-2xl p-5 bg-white">
        <p className="text-xs font-black text-gray-500 uppercase tracking-widest mb-2">Triage Strategy</p>
        <p className="text-sm text-gray-700 font-medium">
          Exceptions are sorted by confidence ascending — the most uncertain cases appear first.
          Low confidence (&lt; 50%) means the offline keyword model had weak signal and the case
          should be routed to a human reviewer before action is taken.
        </p>
      </div>
    </div>
  );
}
