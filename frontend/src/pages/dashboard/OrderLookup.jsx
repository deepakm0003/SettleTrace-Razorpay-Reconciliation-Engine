import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getAuditTrail } from '../../api';
import { Search, ArrowRight } from 'lucide-react';

const STATUS_STYLES = {
  matched:        'bg-green-100 text-green-800 border-green-400',
  needs_review:   'bg-amber-100 text-amber-800 border-amber-400',
  partial_hold:   'bg-purple-100 text-purple-800 border-purple-400',
  settlement_lag: 'bg-blue-100 text-blue-800 border-blue-400',
  unresolved:     'bg-red-100 text-red-800 border-red-400',
};

function AmountCard({ label, value, highlight }) {
  return (
    <div className={`border-2 border-black rounded-xl p-5 ${highlight ? 'bg-orange-50' : 'bg-white'} shadow-[3px_3px_0px_0px_rgba(0,0,0,0.6)]`}>
      <p className="text-xs font-black text-gray-500 uppercase tracking-widest mb-2">{label}</p>
      <p className={`text-3xl font-black ${highlight ? 'text-orange-600' : 'text-gray-900'}`}>
        {value !== null && value !== undefined ? `₹${Number(value).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '—'}
      </p>
    </div>
  );
}

export default function OrderLookup() {
  const { orderId: paramId } = useParams();
  const [searchId, setSearchId] = useState(paramId || '');
  const [result, setResult]     = useState(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (paramId) {
      setSearchId(paramId);
      doSearch(paramId);
    }
  }, [paramId]);

  const doSearch = async (id) => {
    const target = id || searchId;
    if (!target.trim()) return;
    try {
      setLoading(true);
      setError(null);
      const data = await getAuditTrail(target.trim().toUpperCase());
      setResult(data);
    } catch {
      setError(`Order "${target.trim().toUpperCase()}" not found. Try ORD00050, ORD00113, or pick from the Exceptions tab.`);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    navigate(`/dashboard/order/${searchId.trim().toUpperCase()}`);
  };

  return (
    <div className="space-y-6">

      {/* Search */}
      <div className="bg-white border-2 border-black rounded-2xl p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,0.6)]">
        <p className="font-black text-gray-900 text-lg mb-4">Look Up an Order</p>
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={searchId}
            onChange={(e) => setSearchId(e.target.value)}
            placeholder="e.g.  ORD00050"
            className="flex-1 px-5 py-3 bg-[#F5F4F0] border-2 border-black rounded-xl font-mono font-bold text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0066FF]"
          />
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-7 py-3 bg-[#0066FF] text-white font-black rounded-xl border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[-2px] hover:translate-y-[-2px] disabled:opacity-50 transition-all"
          >
            <Search size={18} />
            Search
          </button>
        </form>
        <p className="mt-3 text-xs text-gray-500 font-medium">
          Try: ORD00050 (fee mismatch) &nbsp;|&nbsp; ORD01200 (refund) &nbsp;|&nbsp; any order from the Exceptions tab
        </p>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center h-40">
          <div className="w-12 h-12 border-4 border-black border-t-[#0066FF] rounded-full animate-spin"></div>
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="border-2 border-black rounded-2xl bg-red-50 p-6">
          <p className="font-black text-red-800 mb-1">Not Found</p>
          <p className="text-red-700 text-sm font-medium">{error}</p>
        </div>
      )}

      {/* Result */}
      {result && !loading && (
        <div className="space-y-5">

          {/* Header row */}
          <div className="bg-white border-2 border-black rounded-2xl p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,0.6)] flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
            <div>
              <p className="text-xs font-black text-gray-500 uppercase tracking-widest mb-1">Order ID</p>
              <p className="text-4xl font-black text-gray-900 font-mono">{result.order_id}</p>
              <div className="flex flex-wrap gap-3 mt-3 text-xs font-medium text-gray-500">
                {result.matched_settlement_id && (
                  <span>Settlement: <strong className="text-gray-800 font-mono">{result.matched_settlement_id}</strong></span>
                )}
                {result.matched_bank_credit_id && (
                  <span>Bank Credit: <strong className="text-gray-800 font-mono">{result.matched_bank_credit_id}</strong></span>
                )}
              </div>
            </div>
            <span className={`self-start inline-block px-5 py-2 border-2 border-black rounded-xl font-black text-sm ${STATUS_STYLES[result.status] || 'bg-gray-100 text-gray-800 border-gray-400'}`}>
              {result.status?.replace(/_/g, ' ').toUpperCase()}
            </span>
          </div>

          {/* Amount cards */}
          <div className="grid grid-cols-3 gap-4">
            <AmountCard label="Expected Net"   value={result.expected_net} />
            <AmountCard label="Actual Net"     value={result.actual_net} />
            <AmountCard label="Delta"          value={result.delta} highlight={result.delta !== 0} />
          </div>

          {/* Audit trail */}
          <div className="bg-white border-2 border-black rounded-2xl p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,0.6)]">
            <p className="font-black text-gray-900 text-lg mb-6">Reconciliation Timeline</p>
            <div className="relative">
              {/* Vertical line */}
              <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-gray-200"></div>

              <div className="space-y-4">
                {result.audit_trail?.map((step, idx) => (
                  <div key={idx} className="flex items-start gap-5 relative">
                    <div className="flex-shrink-0 w-10 h-10 rounded-xl border-2 border-black bg-[#0066FF] flex items-center justify-center text-white font-black text-sm shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] z-10">
                      {idx + 1}
                    </div>
                    <div className="flex-1 pt-2">
                      <p className="text-sm font-mono font-medium text-gray-800 bg-[#F5F4F0] border-2 border-dashed border-gray-300 rounded-xl p-4 leading-relaxed">
                        {step}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Agent analysis */}
          {result.exception_reason && result.status !== 'matched' && (
            <div className="bg-white border-2 border-[#0066FF] rounded-2xl p-6 shadow-[4px_4px_0px_0px_rgba(0,102,255,0.3)]">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-[#0066FF] border-2 border-black rounded-xl flex items-center justify-center">
                  <span className="text-white font-black text-xs">AI</span>
                </div>
                <p className="font-black text-gray-900 text-lg">Agent Analysis</p>
              </div>

              <div className="grid md:grid-cols-2 gap-6 mb-6">
                <div>
                  <p className="text-xs font-black text-gray-500 uppercase tracking-widest mb-2">Exception Reason</p>
                  <p className="text-xl font-black text-[#0066FF]">
                    {result.exception_reason.replace(/_/g, ' ').toUpperCase()}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-black text-gray-500 uppercase tracking-widest mb-2">Confidence Score</p>
                  <div className="flex items-center gap-4">
                    <div className="flex-1 h-3 bg-gray-100 border-2 border-black rounded-full overflow-hidden">
                      <div
                        className="h-full bg-[#0066FF] rounded-full transition-all"
                        style={{ width: `${(result.confidence ?? 0) * 100}%` }}
                      ></div>
                    </div>
                    <span className="font-black text-xl text-gray-900 w-12 text-right">
                      {Math.round((result.confidence ?? 0) * 100)}%
                    </span>
                  </div>
                </div>
              </div>

              {result.cited_rule && (
                <div className="mb-5">
                  <p className="text-xs font-black text-gray-500 uppercase tracking-widest mb-2">Cited Razorpay Policy</p>
                  <p className="text-sm text-gray-800 bg-blue-50 border-2 border-[#0066FF] rounded-xl p-4 font-mono leading-relaxed">
                    {result.cited_rule}
                  </p>
                </div>
              )}

              <div>
                <p className="text-xs font-black text-gray-500 uppercase tracking-widest mb-2">Agent Reasoning</p>
                <p className="text-sm text-gray-800 leading-relaxed bg-[#F5F4F0] border-2 border-dashed border-gray-300 rounded-xl p-4">
                  {result.llm_explanation || 'No explanation provided in mock mode.'}
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty state */}
      {!result && !error && !loading && (
        <div className="border-2 border-dashed border-gray-300 rounded-2xl p-16 text-center">
          <Search size={40} className="mx-auto text-gray-300 mb-4" />
          <p className="font-black text-gray-500 text-lg">Enter an order ID above</p>
          <p className="text-sm text-gray-400 mt-2">
            Click any row in the Exceptions tab to jump here automatically
          </p>
        </div>
      )}
    </div>
  );
}
