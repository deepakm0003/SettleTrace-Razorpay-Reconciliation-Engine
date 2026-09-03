import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getAuditTrail } from '../api';
import { Search, AlertCircle, CheckCircle, ArrowRight } from 'lucide-react';

export default function OrderLookup() {
  const { orderId: paramOrderId } = useParams();
  const [searchId, setSearchId] = useState(paramOrderId || '');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchId.trim()) return;

    try {
      setLoading(true);
      setError(null);
      const data = await getAuditTrail(searchId);
      setResult(data);
    } catch (err) {
      setError(`Order ${searchId} not found`);
      setResult(null);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    if (paramOrderId && !result) {
      setSearchId(paramOrderId);
      handleSearch({ preventDefault: () => {} });
    }
  }, [paramOrderId]);

  const getStatusColor = (status) => {
    const colors = {
      'matched': 'bg-green-900/40 text-green-200 border border-green-600/50',
      'needs_review': 'bg-yellow-900/40 text-yellow-200 border border-yellow-600/50',
      'partial_hold': 'bg-purple-900/40 text-purple-200 border border-purple-600/50',
      'settlement_lag': 'bg-indigo-900/40 text-indigo-200 border border-indigo-600/50',
      'unresolved': 'bg-red-900/40 text-red-200 border border-red-600/50',
    };
    return colors[status] || 'bg-slate-700 text-slate-200 border border-slate-600';
  };

  return (
    <div className="space-y-8">
      {/* Search Box */}
      <div className="animate-fadeInUp">
        <h3 className="text-2xl font-bold text-gray-100 mb-4">Order Reconciliation Details</h3>
        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={searchId}
              onChange={(e) => setSearchId(e.target.value)}
              placeholder="Enter order ID (e.g., ORD00050)"
              className="w-full px-5 py-3 bg-slate-700 border border-slate-600 rounded-lg text-gray-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-accent-blue focus:border-transparent transition"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex items-center gap-2 disabled:opacity-50"
          >
            <Search size={18} />
            Lookup
          </button>
        </form>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-900/20 border border-red-500/50 rounded-xl p-4 flex items-start gap-3 animate-fadeInUp">
          <AlertCircle className="text-red-400 mt-0.5" size={20} />
          <div>
            <h3 className="font-semibold text-red-300">Not Found</h3>
            <p className="text-red-200 text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center h-96">
          <div className="text-center space-y-4">
            <div className="inline-block">
              <div className="w-12 h-12 rounded-full border-4 border-slate-600 border-t-accent-blue animate-spin"></div>
            </div>
            <p className="text-slate-300">Loading order details...</p>
          </div>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="space-y-6 animate-fadeInUp">
          {/* Status Card */}
          <div className="card p-8">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-2xl font-bold text-gray-100">{result.order_id}</h3>
                <p className="text-sm text-slate-400 mt-2">Settlement: <span className="text-slate-300 font-mono">{result.matched_settlement_id || 'N/A'}</span></p>
                <p className="text-sm text-slate-400">Bank Credit: <span className="text-slate-300 font-mono">{result.matched_bank_credit_id || 'N/A'}</span></p>
              </div>
              <span className={`badge-small px-6 py-3 rounded-full font-semibold ${getStatusColor(result.status)}`}>
                {result.status.replace(/_/g, ' ').toUpperCase()}
              </span>
            </div>
          </div>

          {/* Amount Details */}
          <div className="grid grid-cols-3 gap-6">
            <div className="card p-8 bg-gradient-to-br from-slate-700 to-slate-800">
              <p className="text-slate-300 text-sm font-medium">Expected Net</p>
              <p className="text-4xl font-bold text-gray-100 mt-3">₹{result.expected_net?.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</p>
            </div>
            <div className="card p-8 bg-gradient-to-br from-slate-700 to-slate-800">
              <p className="text-slate-300 text-sm font-medium">Actual Net</p>
              <p className="text-4xl font-bold text-gray-100 mt-3">₹{result.actual_net?.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</p>
            </div>
            <div className={`card p-8 ${result.delta === 0 ? 'bg-gradient-to-br from-green-900/40 to-green-800/40 border-green-600/50' : 'bg-gradient-to-br from-orange-900/40 to-orange-800/40 border-orange-600/50'}`}>
              <p className="text-slate-300 text-sm font-medium">Delta</p>
              <p className={`text-4xl font-bold mt-3 ${result.delta === 0 ? 'text-green-300' : 'text-orange-300'}`}>
                ₹{result.delta?.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
              </p>
            </div>
          </div>

          {/* Audit Trail */}
          <div className="card p-8">
            <h4 className="text-xl font-bold text-gray-100 mb-8">Reconciliation Timeline</h4>
            <div className="space-y-6">
              {result.audit_trail?.map((step, idx) => (
                <div key={idx} className="flex gap-6">
                  <div className="flex flex-col items-center">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-accent-blue to-blue-600 text-white flex items-center justify-center text-sm font-bold shadow-lg shadow-accent-blue/20">
                      {idx + 1}
                    </div>
                    {idx < result.audit_trail.length - 1 && (
                      <div className="w-0.5 h-20 bg-gradient-to-b from-accent-blue/50 to-slate-700/50 mt-3"></div>
                    )}
                  </div>
                  <div className="pt-2 pb-4 flex-1">
                    <p className="font-mono text-sm bg-slate-800/50 p-4 rounded-lg border border-slate-700 text-slate-200 leading-relaxed">
                      {step}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Agent Conclusion */}
          {result.exception_reason && result.status !== 'matched' && (
            <div className="card border-2 border-accent-blue/50 bg-gradient-to-br from-blue-900/30 to-indigo-900/30 p-8">
              <h4 className="text-xl font-bold text-gray-100 mb-6 flex items-center gap-2">
                🤖 Agent Analysis & Policy Citation
              </h4>
              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <p className="text-sm font-medium text-slate-400 uppercase tracking-wide">Exception Reason</p>
                    <p className="text-2xl font-bold text-accent-blue mt-2">{result.exception_reason.replace(/_/g, ' ').toUpperCase()}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-400 uppercase tracking-wide">Confidence Score</p>
                    <div className="flex items-center gap-4 mt-2">
                      <div className="flex-1 bg-slate-700 rounded-full h-3">
                        <div
                          className="bg-gradient-to-r from-accent-blue to-cyan-400 h-3 rounded-full transition-all duration-500"
                          style={{ width: `${result.confidence * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-2xl font-bold text-accent-blue w-16 text-right">{(result.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
                {result.cited_rule && (
                  <div>
                    <p className="text-sm font-medium text-slate-400 uppercase tracking-wide">Cited Razorpay Policy</p>
                    <p className="text-sm text-blue-300 mt-2 font-mono bg-slate-800/70 p-4 rounded-lg border border-slate-700/50">{result.cited_rule}</p>
                  </div>
                )}
                <div>
                  <p className="text-sm font-medium text-slate-400 uppercase tracking-wide">Agent Reasoning</p>
                  <p className="text-sm text-slate-200 mt-2 leading-relaxed">{result.llm_explanation}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!result && !error && !loading && (
        <div className="text-center py-20">
          <Search size={48} className="text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400 text-lg">Enter an order ID to view its full reconciliation details</p>
          <p className="text-slate-500 text-sm mt-2">Try: ORD00050, ORD00113, or any order from the exceptions list</p>
        </div>
      )}
    </div>
  );
}
