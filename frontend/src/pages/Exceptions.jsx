import { useState, useEffect } from 'react';
import { getExceptions } from '../api';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, ChevronRight, Filter } from 'lucide-react';

export default function Exceptions() {
  const [exceptions, setExceptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reasonFilter, setReasonFilter] = useState('all');
  const navigate = useNavigate();

  useEffect(() => {
    fetchExceptions();
  }, []);

  const fetchExceptions = async () => {
    try {
      setLoading(true);
      const data = await getExceptions();
      setExceptions(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch exceptions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center space-y-4">
          <div className="inline-block">
            <div className="w-12 h-12 rounded-full border-4 border-slate-600 border-t-accent-blue animate-spin"></div>
          </div>
          <p className="text-slate-300">Loading exceptions...</p>
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

  const reasons = Array.from(new Set(exceptions.map(e => e.exception_reason).filter(Boolean)));
  const filtered = reasonFilter === 'all' 
    ? exceptions 
    : exceptions.filter(e => e.exception_reason === reasonFilter);

  const getConfidenceBadgeColor = (confidence) => {
    if (confidence < 0.5) return 'bg-red-900/40 text-red-200 border border-red-600/50';
    if (confidence < 0.8) return 'bg-yellow-900/40 text-yellow-200 border border-yellow-600/50';
    return 'bg-green-900/40 text-green-200 border border-green-600/50';
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-fadeInUp">
        <h3 className="text-2xl font-bold text-gray-100">Exception Triage Queue</h3>
        <p className="text-slate-400 mt-2">Orders requiring agent review, sorted by confidence ascending (lowest first)</p>
      </div>

      {/* Triage Legend */}
      <div className="bg-gradient-to-r from-blue-900/40 to-indigo-900/40 border border-blue-600/50 rounded-xl p-6 animate-fadeInUp">
        <p className="font-semibold text-blue-200 mb-4">🎯 Confidence-Based Triage Strategy</p>
        <div className="grid grid-cols-3 gap-6 text-sm">
          <div className="space-y-2">
            <span className="inline-block px-4 py-2 rounded-full badge-small bg-red-900/40 text-red-200 border border-red-600/50">Low (&lt;0.5)</span>
            <p className="text-blue-300">Manual review required. LLM uncertain.</p>
          </div>
          <div className="space-y-2">
            <span className="inline-block px-4 py-2 rounded-full badge-small bg-yellow-900/40 text-yellow-200 border border-yellow-600/50">Medium (0.5-0.8)</span>
            <p className="text-blue-300">Verify against KB policies before approval.</p>
          </div>
          <div className="space-y-2">
            <span className="inline-block px-4 py-2 rounded-full badge-small bg-green-900/40 text-green-200 border border-green-600/50">High (&gt;0.8)</span>
            <p className="text-blue-300">High confidence classification. Fast-track.</p>
          </div>
        </div>
      </div>

      {/* Filter */}
      <div className="flex gap-4 items-center animate-fadeInUp">
        <Filter size={18} className="text-slate-400" />
        <label className="text-sm font-medium text-gray-300">Filter by reason:</label>
        <select
          value={reasonFilter}
          onChange={(e) => setReasonFilter(e.target.value)}
          className="px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-sm text-gray-100 hover:border-accent-blue transition focus:outline-none focus:ring-2 focus:ring-accent-blue"
        >
          <option value="all">All ({exceptions.length})</option>
          {reasons.map(reason => (
            <option key={reason} value={reason}>
              {reason} ({exceptions.filter(e => e.exception_reason === reason).length})
            </option>
          ))}
        </select>
      </div>

      {/* Exceptions Table */}
      <div className="card overflow-hidden animate-fadeInUp">
        {filtered.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            No exceptions found with this filter.
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-slate-800/50 border-b border-slate-700">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase">Order ID</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase">Reason</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase">Confidence</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase">Policy</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase">Explanation</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {filtered.map((ex, idx) => (
                <tr
                  key={idx}
                  onClick={() => navigate(`/order/${ex.order_id}`)}
                  className="hover:bg-slate-800/50 cursor-pointer transition group"
                >
                  <td className="px-6 py-4 text-sm font-mono text-accent-blue group-hover:text-cyan-300">{ex.order_id}</td>
                  <td className="px-6 py-4 text-sm text-gray-300 font-medium">{ex.exception_reason || 'unknown'}</td>
                  <td className="px-6 py-4">
                    <span className={`badge-small px-3 py-1 rounded-full ${getConfidenceBadgeColor(ex.confidence)}`}>
                      {(ex.confidence * 100).toFixed(0)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-300 font-mono">{ex.cited_rule || '—'}</td>
                  <td className="px-6 py-4 text-sm text-slate-400 max-w-xs truncate">
                    {ex.llm_explanation || '—'}
                  </td>
                  <td className="px-6 py-4">
                    <ChevronRight size={18} className="text-slate-500 group-hover:text-accent-blue transition" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Summary */}
      <div className="text-sm text-slate-400 animate-fadeInUp">
        Showing {filtered.length} of {exceptions.length} exceptions
      </div>
    </div>
  );
}
