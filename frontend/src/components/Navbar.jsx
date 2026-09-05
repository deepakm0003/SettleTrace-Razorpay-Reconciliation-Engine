import { Link } from 'react-router-dom';
import { Menu } from 'lucide-react';
import { useState } from 'react';

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="fixed w-full bg-[#FDFBF7]/95 backdrop-blur-sm border-b-2 border-black z-50">
      <div className="max-w-7xl mx-auto px-6 md:px-12">
        <div className="flex justify-between items-center py-4">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <div className="w-10 h-10 bg-[#0066FF] border-2 border-black rounded-lg flex items-center justify-center rotate-[-3deg]">
              <span className="text-white font-black text-xl">S</span>
            </div>
            <span className="text-2xl font-black text-gray-900">SettleTrace</span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center gap-6">
            <a href="#features" className="text-gray-700 hover:text-gray-900 font-medium transition">Features</a>
            <a href="#metrics" className="text-gray-700 hover:text-gray-900 font-medium transition">Metrics</a>
            <a href="#why-us" className="text-gray-700 hover:text-gray-900 font-medium transition">Why Us</a>
            <Link to="/dashboard" className="btn-sketch text-sm py-2 px-6">
              Launch Dashboard
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden"
            onClick={() => setIsOpen(!isOpen)}
          >
            <Menu className="text-gray-900" />
          </button>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden pb-4 space-y-3 border-t-2 border-black pt-4 mt-2">
            <a href="#features" className="block text-gray-700 hover:text-gray-900 font-medium">Features</a>
            <a href="#metrics" className="block text-gray-700 hover:text-gray-900 font-medium">Metrics</a>
            <a href="#why-us" className="block text-gray-700 hover:text-gray-900 font-medium">Why Us</a>
            <Link to="/dashboard" className="block w-full text-center btn-sketch text-sm py-2">
              Launch Dashboard
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
