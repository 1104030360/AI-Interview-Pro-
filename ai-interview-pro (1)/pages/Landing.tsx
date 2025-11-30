import React from 'react';
import { ArrowRight, ShieldCheck, Zap, Globe } from 'lucide-react';
import { ThreeBackground } from '../components/ThreeBackground';

interface LandingProps {
  onEnter: () => void;
}

export const Landing: React.FC<LandingProps> = ({ onEnter }) => {
  return (
    <div className="relative w-full h-screen flex flex-col items-center justify-center overflow-hidden bg-background text-textMain">
      {/* 3D Background Layer */}
      <ThreeBackground />
      
      {/* Content Layer */}
      <div className="z-10 flex flex-col items-center text-center max-w-4xl px-6">
        {/* Brand Mark */}
        <div className="w-16 h-16 bg-surfaceHighlight/30 rounded-2xl flex items-center justify-center mb-8 border border-border/50 backdrop-blur-md">
           <div className="w-8 h-8 bg-primary rounded-sm shadow-[0_0_15px_rgba(6,182,212,0.4)]" />
        </div>

        {/* Headline */}
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 text-white">
          AI Insight<span className="text-primary">.</span>
        </h1>
        
        {/* Subheadline */}
        <p className="text-lg md:text-xl text-textMuted mb-10 max-w-2xl leading-relaxed font-light">
          The professional intelligence layer for your engineering career. 
          Analyze behavioral patterns and system design communication with privacy-first AI.
        </p>

        {/* Main Action */}
        <button 
          onClick={onEnter}
          className="group relative px-8 py-4 bg-white text-black font-semibold rounded-full text-lg transition-all duration-300 hover:bg-zinc-200 hover:scale-105 hover:shadow-[0_0_30px_rgba(255,255,255,0.1)] flex items-center gap-3"
        >
          Enter System
          <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </button>

        {/* Trust Indicators */}
        <div className="mt-16 grid grid-cols-3 gap-8 md:gap-16 border-t border-border/30 pt-8 opacity-80">
           <div className="flex flex-col items-center gap-2">
              <ShieldCheck size={20} className="text-zinc-500" />
              <span className="text-xs font-medium text-zinc-500 uppercase tracking-wider">Secure Analysis</span>
           </div>
           <div className="flex flex-col items-center gap-2">
              <Zap size={20} className="text-zinc-500" />
              <span className="text-xs font-medium text-zinc-500 uppercase tracking-wider">Real-time</span>
           </div>
           <div className="flex flex-col items-center gap-2">
              <Globe size={20} className="text-zinc-500" />
              <span className="text-xs font-medium text-zinc-500 uppercase tracking-wider">Enterprise Ready</span>
           </div>
        </div>
      </div>
    </div>
  );
};