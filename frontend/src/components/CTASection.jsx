import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

export default function CTASection() {
  return (
    <section className="py-20 px-6 md:px-12 lg:px-24 bg-[#0066FF] text-white relative overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 left-0 w-64 h-64 border-2 border-white rounded-full"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 border-2 border-white rounded-full"></div>
      </div>

      <div className="max-w-4xl mx-auto text-center relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
        >
          <h2 className="text-5xl lg:text-6xl font-black mb-6">
            Ready to See AI Reconciliation<br />
            in Action?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto leading-relaxed">
            Explore the live dashboard with <strong>2,500 real orders</strong>, 
            82% auto-resolution, and transparent AI metrics powered by NVIDIA NIM.
            No signup. No credit card. No BS.
          </p>
          
          <Link 
            to="/dashboard"
            className="inline-flex items-center gap-3 px-12 py-5 bg-white text-[#0066FF] rounded-xl font-black text-lg border-2 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[-2px] hover:translate-y-[-2px] transition-all"
          >
            Launch Dashboard
            <ArrowRight size={24} />
          </Link>

          <div className="mt-8 flex items-center justify-center gap-8 text-sm text-blue-100">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-white rounded-full"></div>
              <span>No Credit Card</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-white rounded-full"></div>
              <span>Full Feature Access</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-white rounded-full"></div>
              <span>Real Settlement Data</span>
            </div>
          </div>

          {/* Technical details */}
          <div className="mt-12 pt-8 border-t-2 border-white/20">
            <p className="text-sm text-blue-200 mb-4 font-bold">FOR DEVELOPERS:</p>
            <div className="grid md:grid-cols-3 gap-4 text-left">
              <div className="bg-white/10 border-2 border-white/30 rounded-xl p-4">
                <p className="text-xs text-blue-200 mb-1">Backend</p>
                <p className="text-sm font-bold">FastAPI + Python</p>
                <p className="text-xs text-blue-300 mt-2">6 REST endpoints, auto-docs at /docs</p>
              </div>
              <div className="bg-white/10 border-2 border-white/30 rounded-xl p-4">
                <p className="text-xs text-blue-200 mb-1">AI Mode</p>
                <p className="text-sm font-bold">Mock (offline) / NVIDIA NIM</p>
                <p className="text-xs text-blue-300 mt-2">Set NVIDIA_API_KEY to swap</p>
              </div>
              <div className="bg-white/10 border-2 border-white/30 rounded-xl p-4">
                <p className="text-xs text-blue-200 mb-1">Data</p>
                <p className="text-sm font-bold">2,500 orders, 7 scenarios</p>
                <p className="text-xs text-blue-300 mt-2">Seed=42, reproducible results</p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
