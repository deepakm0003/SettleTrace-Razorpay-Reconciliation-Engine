import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

export default function HeroSection() {
  return (
    <section className="pt-32 pb-20 px-6 md:px-12 lg:px-24 bg-[#FDFBF7] relative overflow-hidden">
      <div className="max-w-7xl mx-auto relative z-10">
        <div className="grid lg:grid-cols-2 gap-16 items-center">

          {/* Left Content */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>

            <div className="inline-block mb-8">
              <div className="bg-[#0066FF] text-white px-5 py-2 font-black text-sm border-2 border-black rounded-lg shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] rotate-[-1.5deg]">
                Agentic AI Platform — NVIDIA NIM Powered
              </div>
            </div>

            <h1 className="text-6xl lg:text-7xl font-black text-gray-900 leading-[1.05] mb-8">
              Razorpay<br />
              Settlement<br />
              <span className="wavy-underline text-[#0066FF]">Reconciliation</span><br />
              Done Right.
            </h1>

            <p className="text-xl text-gray-700 mb-8 leading-relaxed max-w-xl font-medium">
              Stop losing hours on manual CSV matching. SettleTrace combines deterministic rules 
              with a RAG-grounded AI agent to resolve <strong>82% of settlements automatically</strong> — 
              and tells you exactly why it flagged the other 18%.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 mb-10">
              <Link
                to="/dashboard"
                className="inline-block px-8 py-4 bg-[#0066FF] text-white font-black text-lg rounded-xl border-2 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] hover:shadow-[7px_7px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[-2px] hover:translate-y-[-2px] transition-all text-center"
              >
                Try Live Dashboard
              </Link>
              <a
                href="#features"
                className="inline-block px-8 py-4 bg-white text-gray-900 font-black text-lg rounded-xl border-2 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,0.15)] hover:shadow-[7px_7px_0px_0px_rgba(0,0,0,0.2)] hover:translate-x-[-2px] hover:translate-y-[-2px] transition-all text-center"
              >
                How It Works
              </a>
            </div>

            <div className="flex flex-col sm:flex-row gap-6 text-sm text-gray-600 font-medium">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-[#0066FF] border-2 border-black rounded-sm flex-shrink-0"></div>
                <span>Zero API cost — fully offline mock mode</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-[#0066FF] border-2 border-black rounded-sm flex-shrink-0"></div>
                <span>Honest metrics, documented limitations</span>
              </div>
            </div>
          </motion.div>

          {/* Right Content — hand-drawn dashboard preview */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="relative"
          >
            <div className="bg-white border-2 border-black rounded-2xl shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-8 rotate-[1.5deg]">

              {/* Mini header bar */}
              <div className="flex items-center gap-2 mb-6 pb-4 border-b-2 border-black">
                <div className="w-3 h-3 rounded-full bg-red-400 border border-black"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-400 border border-black"></div>
                <div className="w-3 h-3 rounded-full bg-green-400 border border-black"></div>
                <span className="ml-3 text-xs font-black text-gray-600 uppercase tracking-widest">SettleTrace Dashboard</span>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between p-4 bg-green-50 border-2 border-black rounded-xl rotate-[-0.5deg]">
                  <div>
                    <p className="text-xs font-black text-gray-500 uppercase tracking-wider">Matched</p>
                    <p className="text-sm font-bold text-gray-900">Automatically reconciled</p>
                  </div>
                  <span className="text-4xl font-black text-green-600">1,390</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-amber-50 border-2 border-black rounded-xl rotate-[0.5deg]">
                  <div>
                    <p className="text-xs font-black text-gray-500 uppercase tracking-wider">Needs Review</p>
                    <p className="text-sm font-bold text-gray-900">Agent flagged for triage</p>
                  </div>
                  <span className="text-4xl font-black text-amber-600">450</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-blue-50 border-2 border-black rounded-xl rotate-[-0.3deg]">
                  <div>
                    <p className="text-xs font-black text-gray-500 uppercase tracking-wider">Settlement Lag</p>
                    <p className="text-sm font-bold text-gray-900">T+1 / T+2 delay detected</p>
                  </div>
                  <span className="text-4xl font-black text-blue-600">342</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-purple-50 border-2 border-black rounded-xl rotate-[0.3deg]">
                  <div>
                    <p className="text-xs font-black text-gray-500 uppercase tracking-wider">Partial Hold</p>
                    <p className="text-sm font-bold text-gray-900">Reserve withheld by Razorpay</p>
                  </div>
                  <span className="text-4xl font-black text-purple-600">318</span>
                </div>
              </div>

              {/* Badge */}
              <div className="absolute -top-5 -right-5 bg-[#0066FF] text-white border-2 border-black rounded-xl px-5 py-3 rotate-[10deg] shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">
                <p className="text-xs font-bold uppercase">Match Rate</p>
                <p className="text-2xl font-black">82%</p>
              </div>
            </div>

            {/* Decorative sketch lines */}
            <svg className="absolute -bottom-6 -left-6 w-24 h-24 text-gray-300 opacity-60" viewBox="0 0 100 100" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M10 90 Q30 10 90 10" strokeDasharray="4 3"/>
              <path d="M5 70 Q40 20 85 30" strokeDasharray="4 3"/>
            </svg>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
