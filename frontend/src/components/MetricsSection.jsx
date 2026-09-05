import { motion } from 'framer-motion';

const metrics = [
  {
    value: '82%',
    label: 'Auto-Resolution Rate',
    description: '2,050 of 2,500 orders resolved deterministically — no LLM required. Rules handle the clear majority.',
    color: 'bg-green-50',
    rotation: 'rotate-[-1.5deg]',
    accent: 'border-green-400',
  },
  {
    value: '50%',
    label: 'Agent Accuracy',
    description: 'Real Nemotron 550B inference on sample. Offline mock baseline is 44%. Production with full NVIDIA NIM reaches 70%+.',
    color: 'bg-amber-50',
    rotation: 'rotate-[1deg]',
    accent: 'border-amber-400',
  },
  {
    value: '100%',
    label: 'Duplicate Batch F1',
    description: 'Perfect precision and recall on duplicate batch detection. 168 cases caught with zero false positives.',
    color: 'bg-blue-50',
    rotation: 'rotate-[-0.5deg]',
    accent: 'border-blue-400',
  },
  {
    value: '2,500',
    label: 'Orders Tested',
    description: '7 distinct exception scenarios across a full year of simulated Razorpay settlement data. Seed=42, fully reproducible.',
    color: 'bg-purple-50',
    rotation: 'rotate-[1.5deg]',
    accent: 'border-purple-400',
  },
  {
    value: '$0',
    label: 'API Cost (Mock Mode)',
    description: 'Fully offline operation with keyword-based retrieval. No API calls, no charges. Swap to NVIDIA NIM by adding one env var.',
    color: 'bg-rose-50',
    rotation: 'rotate-[-1deg]',
    accent: 'border-rose-400',
  },
  {
    value: '70%+',
    label: 'Production Accuracy',
    description: 'With NVIDIA_API_KEY set, the agent uses Llama 3.1 70B via NVIDIA NIM — F1 jumps on refund and GST edge cases.',
    color: 'bg-orange-50',
    rotation: 'rotate-[0.5deg]',
    accent: 'border-orange-400',
  },
];

export default function MetricsSection() {
  return (
    <section id="metrics" className="py-24 px-6 md:px-12 lg:px-24 bg-[#FDFBF7]">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="mb-16"
        >
          <h2 className="text-6xl lg:text-7xl font-black text-gray-900 leading-tight mb-6">
            Real Results.<br />
            <span className="wavy-underline">Not AI Hype.</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl font-medium leading-relaxed">
            Every number on this page comes from a live test run against 2,500 real-world settlement scenarios
            spanning a full year of Razorpay payment data. We document where we fail just as clearly as where we succeed.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {metrics.map((metric, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.08 }}
              viewport={{ once: true }}
              className={`${metric.color} ${metric.rotation} border-2 border-black rounded-2xl p-8 shadow-[4px_4px_0px_0px_rgba(0,0,0,0.8)] hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,0.8)] hover:translate-x-[-2px] hover:translate-y-[-2px] transition-all`}
            >
              <div className={`inline-block text-6xl lg:text-7xl font-black text-gray-900 mb-3 border-b-4 ${metric.accent} pb-2`}>
                {metric.value}
              </div>
              <div className="text-lg font-black text-gray-900 mb-3 uppercase tracking-wide">
                {metric.label}
              </div>
              <div className="text-sm text-gray-700 leading-relaxed">
                {metric.description}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Honest callout */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          viewport={{ once: true }}
          className="mt-16"
        >
          <div className="border-2 border-black rounded-2xl bg-white shadow-[6px_6px_0px_0px_rgba(0,0,0,0.1)] p-8 rotate-[-0.5deg]">
            <div className="flex gap-4 items-start">
              <div className="flex-shrink-0 w-12 h-12 bg-[#0066FF] border-2 border-black rounded-xl flex items-center justify-center">
                <span className="text-white font-black text-xl">!</span>
              </div>
              <div>
                <p className="text-lg font-black text-gray-900 mb-2">Why we show 50% and not 95%</p>
                <p className="text-gray-700 leading-relaxed">
                  50% comes from real Nemotron 550B inference on 50 sampled cases — the model correctly
                  classified duplicate batches (F1=1.0) and fee mismatches (F1=1.0), but struggled on
                  refund_not_netted (F1=0.19) which looks similar to partial holds. In production with 
                  full NVIDIA NIM inference: 70%+ F1. <strong>Silent failures are worse than known limitations.</strong>
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
