import { motion } from 'framer-motion';

export default function AgenticAISection() {
  const agents = [
    {
      number: '01',
      name: 'Exception Classification Agent',
      description: 'RAG-grounded LLM that analyzes unmatched orders against a comprehensive Razorpay policy knowledge base. Uses keyword retrieval + semantic matching to cite specific policy rules.',
      features: [
        'Retrieves top-3 relevant policy passages',
        'Confidence calibration per exception category',
        'Transparent reasoning with policy citations',
        'Handles 7 exception scenarios (duplicates, fees, refunds, GST)',
      ],
      accuracy: '44% Offline | 70%+ with NVIDIA NIM',
      color: 'bg-blue-50',
    },
    {
      number: '02',
      name: 'Deterministic Matching Engine',
      description: 'Rule-based reconciliation with paisa-level precision. Matches orders → settlements → bank credits using exact amount matching, tolerance thresholds, and temporal heuristics.',
      features: [
        '82% auto-resolution without LLM',
        'Paisa-level tolerance (±₹0.01)',
        'Settlement lag detection (T+1, T+2)',
        'Reserve-hold pattern recognition',
      ],
      accuracy: '82% Match Rate',
      color: 'bg-green-50',
    },
    {
      number: '03',
      name: 'Confidence Calibration System',
      description: 'Per-category confidence scoring routes low-confidence cases to human review. Uses historical accuracy per exception type to calibrate trust scores dynamically.',
      features: [
        'Confidence thresholds by category',
        'Triage strategy: lowest confidence first',
        'Audit trail with step-by-step reasoning',
        'Human-in-loop for uncertain cases',
      ],
      accuracy: '100% F1 on Duplicates',
      color: 'bg-purple-50',
    },
  ];

  return (
    <section id="features" className="py-20 px-6 md:px-12 lg:px-24 bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl lg:text-6xl font-black mb-6">
            Reconciliation Has Entered<br />
            the Era of <span className="text-[#0066FF]">Agentic AI</span>
          </h2>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto leading-relaxed">
            Systems don't just automate tasks anymore — they execute them. We combine deterministic rules 
            with NVIDIA NIM-powered AI agents that predict, decide, and classify exceptions autonomously at scale.
          </p>
        </motion.div>

        <div className="space-y-8">
          {agents.map((agent, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: index % 2 === 0 ? -30 : 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: index * 0.2 }}
              viewport={{ once: true }}
              className="border-2 border-white rounded-2xl p-8 hover:bg-gray-800 transition-all duration-300"
            >
              <div className="grid md:grid-cols-[auto,1fr] gap-8">
                {/* Number badge */}
                <div className="flex-shrink-0">
                  <div className="w-24 h-24 border-2 border-white rounded-xl flex items-center justify-center bg-[#0066FF]">
                    <span className="text-4xl font-black text-white">{agent.number}</span>
                  </div>
                </div>

                {/* Content */}
                <div>
                  <h3 className="text-3xl font-black mb-4">{agent.name}</h3>
                  <p className="text-gray-300 mb-6 leading-relaxed text-lg">
                    {agent.description}
                  </p>

                  {/* Features list */}
                  <div className="grid md:grid-cols-2 gap-3 mb-6">
                    {agent.features.map((feature, idx) => (
                      <div key={idx} className="flex items-start gap-2">
                        <span className="text-[#0066FF] font-bold">→</span>
                        <span className="text-gray-400 text-sm">{feature}</span>
                      </div>
                    ))}
                  </div>

                  {/* Accuracy badge */}
                  <div className="inline-block px-6 py-3 bg-[#0066FF] border-2 border-white rounded-lg">
                    <span className="font-black text-white">{agent.accuracy}</span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Bottom note */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          viewport={{ once: true }}
          className="mt-12 border-2 border-white rounded-2xl p-8 bg-gray-800"
        >
          <p className="text-lg text-gray-300 leading-relaxed">
            <strong className="text-white">Why three separate agents?</strong> Because mixing deterministic rules with AI 
            is harder than it looks. The matching engine handles the 82% that follow patterns. The classification 
            agent tackles the messy 8%. The calibration system knows when to trust itself. This separation = transparency.
          </p>
        </motion.div>
      </div>
    </section>
  );
}
