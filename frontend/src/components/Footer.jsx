export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-gray-400 py-12 border-t-2 border-white">
      <div className="max-w-7xl mx-auto px-6 md:px-12">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-[#0066FF] border-2 border-white rounded-lg flex items-center justify-center">
                <span className="text-white font-black">S</span>
              </div>
              <span className="text-xl font-black text-white">SettleTrace</span>
            </div>
            <p className="text-sm leading-relaxed">
              AI-powered Razorpay settlement reconciliation. 
              Deterministic rules + RAG-grounded LLM agents. 
              Honest metrics, zero API cost in mock mode.
            </p>
          </div>

          {/* Product */}
          <div>
            <h4 className="text-white font-black mb-4">Product</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#features" className="hover:text-[#0066FF] transition">Features</a></li>
              <li><a href="#metrics" className="hover:text-[#0066FF] transition">Metrics</a></li>
              <li><a href="/dashboard" className="hover:text-[#0066FF] transition">Dashboard</a></li>
              <li><a href="#" className="hover:text-[#0066FF] transition">API Docs</a></li>
            </ul>
          </div>

          {/* Technical */}
          <div>
            <h4 className="text-white font-black mb-4">Technical</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="hover:text-[#0066FF] transition">Documentation</a></li>
              <li><a href="#" className="hover:text-[#0066FF] transition">GitHub Repo</a></li>
              <li><a href="#" className="hover:text-[#0066FF] transition">API Reference</a></li>
              <li><a href="#" className="hover:text-[#0066FF] transition">Architecture</a></li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="text-white font-black mb-4">Company</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="hover:text-[#0066FF] transition">About</a></li>
              <li><a href="#" className="hover:text-[#0066FF] transition">Case Study</a></li>
              <li><a href="#" className="hover:text-[#0066FF] transition">Contact</a></li>
              <li><a href="#" className="hover:text-[#0066FF] transition">Privacy</a></li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t-2 border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center text-sm">
          <p className="mb-4 md:mb-0">
            © {currentYear} SettleTrace. Built with FastAPI, React, NVIDIA NIM, and brutal honesty.
          </p>
          <div className="flex gap-6">
            <a href="#" className="hover:text-[#0066FF] transition font-medium">
              GitHub
            </a>
            <a href="#" className="hover:text-[#0066FF] transition font-medium">
              LinkedIn
            </a>
            <a href="#" className="hover:text-[#0066FF] transition font-medium">
              Twitter
            </a>
          </div>
        </div>

        {/* Technical note */}
        <div className="mt-8 pt-8 border-t-2 border-gray-800">
          <div className="bg-gray-800 border-2 border-gray-700 rounded-xl p-6">
            <p className="text-xs text-gray-400 leading-relaxed">
              <strong className="text-white">Tech Stack:</strong> FastAPI (Python backend, async) • 
              React 18 (JSX frontend) • NVIDIA NIM — Llama 3.1 70B (LLM, swappable) • 
              Tailwind CSS (utility-first styling) • Framer Motion (animations) • 
              Recharts (data viz) • Axios (HTTP client) • Uvicorn (ASGI server)
            </p>
            <p className="text-xs text-gray-500 mt-2">
              <strong className="text-gray-400">Data:</strong> 2,500 orders, 7 exception scenarios, seed=42 for reproducibility. 
              <strong className="text-gray-400 ml-4">API Cost:</strong> $0 in mock mode, NVIDIA NIM usage-based in production.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
