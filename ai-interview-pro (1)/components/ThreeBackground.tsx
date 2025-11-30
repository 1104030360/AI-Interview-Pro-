import React, { useMemo } from 'react';

// Pure CSS 3D animated background - no Three.js required!
interface DataBlock {
  left: string;
  top: string;
  size: number;
  duration: number;
  delay: number;
}

export const ThreeBackground: React.FC = () => {
  // Generate random blocks
  const blocks = useMemo<DataBlock[]>(() => {
    const items: DataBlock[] = [];
    for (let i = 0; i < 15; i++) {
      items.push({
        left: `${Math.random() * 100}%`,
        top: `${Math.random() * 100}%`,
        size: Math.random() * 80 + 40, // 40-120px
        duration: Math.random() * 10 + 15, // 15-25s
        delay: Math.random() * 5, // 0-5s
      });
    }
    return items;
  }, []);

  return (
    <div className="absolute inset-0 -z-10 bg-[#09090b] overflow-hidden">
      {/* 3D Container with perspective */}
      <div
        className="absolute inset-0"
        style={{
          perspective: '1000px',
          perspectiveOrigin: 'center center',
        }}
      >
        {blocks.map((block, i) => (
          <div
            key={i}
            className="absolute animate-float-3d"
            style={{
              left: block.left,
              top: block.top,
              width: `${block.size}px`,
              height: `${block.size}px`,
              animation: `float-3d ${block.duration}s ease-in-out ${block.delay}s infinite, rotate-3d ${block.duration * 1.5}s linear ${block.delay}s infinite`,
              transformStyle: 'preserve-3d',
            }}
          >
            {/* Cube with glowing edges */}
            <div
              className="w-full h-full relative"
              style={{
                background: '#18181b',
                border: '1px solid rgba(6, 182, 212, 0.15)',
                boxShadow: `
                  0 0 20px rgba(6, 182, 212, 0.1),
                  inset 0 0 20px rgba(6, 182, 212, 0.05)
                `,
                transform: 'translateZ(0)',
              }}
            />
          </div>
        ))}
      </div>

      {/* Vignette overlay */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(circle at center, transparent 30%, #09090b 100%)'
        }}
      />

      {/* CSS Keyframe Animations */}
      <style>{`
        @keyframes float-3d {
          0%, 100% {
            transform: translate3d(0, 0, 0) rotateX(0deg) rotateY(0deg);
          }
          25% {
            transform: translate3d(20px, -30px, 50px) rotateX(5deg) rotateY(5deg);
          }
          50% {
            transform: translate3d(-15px, 20px, -30px) rotateX(-3deg) rotateY(-8deg);
          }
          75% {
            transform: translate3d(25px, 15px, 20px) rotateX(8deg) rotateY(-5deg);
          }
        }

        @keyframes rotate-3d {
          from {
            transform: rotateZ(0deg);
          }
          to {
            transform: rotateZ(360deg);
          }
        }
      `}</style>
    </div>
  );
};
