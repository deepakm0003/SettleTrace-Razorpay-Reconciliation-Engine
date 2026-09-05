import { motion } from 'framer-motion';

export default function TrustBadges() {
  const techStack = [
    {
      name: 'FastAPI',
      description: 'High-performance Python async framework',
      why: 'Auto-generates OpenAPI docs, handles CORS, built for ML/AI workloads',
    },
    {
      name: 'React 18',
      description: 'Modern component-based UI library',
      why: 'Fast rendering, large ecosystem, excellent dev tools',
    },
    {
      name: 'NVIDIA NIM',
      description: 'State-of-the-art LLM inference platform',
      why: 'OpenAI-compatible API, Llama 3.1 70B, free tier via build.nvidia.com — no vendor lock-in',
    },
    {
      name: 'Recharts',
      description: 'Composable charting library',
      why: 'React-first, responsive, handles real-time data updates',
    },
    {
      name: 'Tailwind CSS',
      description: 'Utility-first CSS framework',
      why: 'Rapid prototyping, consistent design system, no CSS bloat',
    },
    {
      name: 'Framer Motion',
      description: 'Production-ready animation library',
      why: 'Declarative animations, gesture support, performant',
    },
  ];

  const principles = [
    {
      title: 'Transparency Over Hype',
      description: 'We show you 40% agent accuracy, not inflated 95%. Every metric has context. Every limitation is documented.',
    },
    {
      title: 'Deterministic + AI Hybrid',
      description: '92% resolved by rules, 8% by AI. This separation means you know exactly when and why the AI was involved.',
    },
    {
      title: 'Human-in-Loop by Design',
      description: 'Low confidence → human review. The agent knows when it doesn\'t know. That\'s the point.',
    },
    {
      title: 'Zero Lock-In',
      description: 'Swap NVIDIA NIM for any OpenAI-compatible LLM via env var. Export data as CSV. Run 100% offline in mock mode.',
    },
  ];

  return (
    <section id="why-us" className="py-20 px-6 md:px-12 lg:px-24 bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto">
        {/* Tech Stack */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="mb-20"
        >
          <h2 className="text-5xl lg:text-6xl font-black text-center mb-4">
            Built With <span className="text-[#0066FF]">Best-in-Class</span> Technology
          </h2>
          <p className="text-xl text-gray-400 text-center mb-12 max-w-3xl mx-auto">
            Every tool chosen for a reason. FastAPI backend, React frontend, NVIDIA NIM for LLM inference.
            No hype stack, no trendy frameworks forced in. Just proven tech that ships.
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {techStack.map((tech, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="border-2 border-white rounded-2xl p-6 hover:bg-gray-800 transition-all"
              >
                <h3 className="text-2xl font-black mb-2">{tech.name}</h3>
                <p className="text-gray-400 text-sm mb-3">{tech.description}</p>
                <p className="text-gray-500 text-xs leading-relaxed">
                  <strong className="text-gray-400">Why:</strong> {tech.why}
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Design Principles */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
        >
          <h2 className="text-5xl lg:text-6xl font-black text-center mb-4">
            Our Design <span className="text-[#0066FF]">Principles</span>
          </h2>
          <p className="text-xl text-gray-400 text-center mb-12 max-w-3xl mx-auto">
            What separates SettleTrace from every other "AI reconciliation" tool in the market.
          </p>

          <div className="grid md:grid-cols-2 gap-6">
            {principles.map((principle, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="border-2 border-white rounded-2xl p-8"
              >
                <h3 className="text-2xl font-black mb-4">{principle.title}</h3>
                <p className="text-gray-300 leading-relaxed">
                  {principle.description}
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
