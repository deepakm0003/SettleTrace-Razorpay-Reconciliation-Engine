import { motion } from 'framer-motion';

export default function FeaturesGrid() {
  const features = [
    {
      title: 'Transaction Matching',
      description: 'Deterministic paisa-level matching across orders, settlements, and bank credits with ±₹0.01 tolerance.',
      details: 'Handles 3-way reconciliation: Order Ledger → Razorpay Settlements → Bank Statement',
      metric: '176/250 perfect matches',
    },
    {
      title: 'Exception Triage',
      description: 'AI-powered classification with confidence-based routing to human review.',
      details: '7 exception categories: duplicates, fee mismatches, refund shortfalls, GST errors, partial holds, lags',
      metric: '20 cases flagged for review',
    },
    {
      title: 'Order Lookup & Audit Trail',
      description: 'Full reconciliation timeline with agent reasoning and policy citations.',
      details: 'Step-by-step breakdown: order creation → matching → classification → resolution path',
      metric: 'Every order = full audit history',
    },
    {
      title: 'Evaluation Metrics',
      description: 'Per-category F1 scores with honest limitations disclosure.',
      details: 'Precision, recall, F1 per exception type. No hiding bad numbers (refund_not_netted = 0.00 F1)',
      metric: '40% overall agent accuracy',
    },
    {
      title: 'Settlement Analytics',
      description: 'Status breakdown, match rate trends, and agent performance dashboards.',
      details: 'Real-time metrics: 1,390 matched, 450 needs_review, 318 partial_hold, 342 settlement_lag',
      metric: '82% auto-resolution rate',
    },
    {
      title: 'Audit & Compliance',
      description: 'Complete audit trails, policy grounding, and transparent confidence scoring.',
      details: 'Every AI decision cites knowledge base passage + confidence score + reasoning',
      metric: '100% decisions traceable',
    },
    {
      title: 'Settlement Lag Detection',
      description: 'Automatic T+1/T+2 lag identification with temporal pattern recognition.',
      details: 'Detects normal delays (1-2 days) vs. real issues. No false alarms on expected lags.',
      metric: '36 lag cases identified',
    },
    {
      title: 'RAG-Grounded Knowledge',
      description: 'LLM decisions anchored in Razorpay policy knowledge base.',
      details: '8 KB policy text split into passages. Top-3 retrieval via keyword + topic matching. NVIDIA NIM adds semantic depth.',
      metric: 'Every prediction = policy cite',
    },
    {
      title: 'Zero-Cost Mock Mode',
      description: 'Offline keyword fallback for code review without API charges.',
      details: 'Swap mock → NVIDIA NIM via env var (NVIDIA_API_KEY). Same interface, different backend. Production-ready.',
      metric: '$0 API cost in mock',
    },
  ];

  return (
    <section className="py-20 px-6 md:px-12 lg:px-24 bg-[#FDFBF7]">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl lg:text-6xl font-black text-gray-900 mb-4">
            The AI Platform Finance Teams<br />
            <span className="wavy-underline">Actually Trust</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Unified reconciliation capabilities built for continuous, trusted results. Every step works 
            seamlessly, with AI predicting, coordinating, and executing while keeping humans in the loop.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.05 }}
              viewport={{ once: true }}
              className="sketch-border bg-white p-6 group"
            >
              <h3 className="text-xl font-black text-gray-900 mb-3">
                {feature.title}
              </h3>
              <p className="text-sm text-gray-700 mb-4 leading-relaxed font-medium">
                {feature.description}
              </p>
              <p className="text-xs text-gray-600 mb-4 leading-relaxed">
                {feature.details}
              </p>
              <div className="inline-block px-3 py-1 bg-[#0066FF] text-white text-xs font-bold rounded border-2 border-black">
                {feature.metric}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
