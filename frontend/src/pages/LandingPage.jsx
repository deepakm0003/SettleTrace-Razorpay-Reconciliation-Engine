import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Zap, TrendingUp, Shield, Clock, BarChart3, AlertTriangle,
  CheckCircle, ArrowRight, Sparkles, Brain, Target
} from 'lucide-react';
import Navbar from '../components/Navbar';
import HeroSection from '../components/HeroSection';
import MetricsSection from '../components/MetricsSection';
import AgenticAISection from '../components/AgenticAISection';
import FeaturesGrid from '../components/FeaturesGrid';
import TrustBadges from '../components/TrustBadges';
import CTASection from '../components/CTASection';
import Footer from '../components/Footer';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      <HeroSection />
      <AgenticAISection />
      <MetricsSection />
      <FeaturesGrid />
      <TrustBadges />
      <CTASection />
      <Footer />
    </div>
  );
}
