import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import type { StatusState } from '../hooks/useWebSocket';

interface Props {
  status: StatusState;
  onToggleVoice: () => void;
}

export default function JarvisCore({ status, onToggleVoice }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const frameRef = useRef(0);
  const timeRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const cx = rect.width / 2;
    const cy = rect.height / 2;
    const maxR = Math.min(cx, cy) * 0.7;

    const animate = (t: number) => {
      ctx.clearRect(0, 0, rect.width, rect.height);
      timeRef.current = t / 1000;

      const pulse = 0.85 + 0.15 * Math.sin(timeRef.current * 1.5);
      const radius = maxR * pulse;

      // Glow
      const glow = ctx.createRadialGradient(cx, cy, radius * 0.3, cx, cy, radius * 1.5);
      glow.addColorStop(0, 'rgba(0, 255, 65, 0.15)');
      glow.addColorStop(0.5, 'rgba(0, 255, 65, 0.05)');
      glow.addColorStop(1, 'rgba(0, 255, 65, 0)');
      ctx.fillStyle = glow;
      ctx.fillRect(0, 0, rect.width, rect.height);

      // Main ring
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(0, 255, 65, 0.6)';
      ctx.lineWidth = 1.5;
      ctx.shadowColor = 'rgba(0, 255, 65, 0.5)';
      ctx.shadowBlur = 10;
      ctx.stroke();
      ctx.shadowBlur = 0;

      // Inner ring
      ctx.beginPath();
      ctx.arc(cx, cy, radius * 0.7, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(0, 255, 65, 0.2)';
      ctx.lineWidth = 1;
      ctx.stroke();

      // Center dot
      ctx.beginPath();
      ctx.arc(cx, cy, 2, 0, Math.PI * 2);
      ctx.fillStyle = '#00ff41';
      ctx.shadowColor = 'rgba(0, 255, 65, 0.8)';
      ctx.shadowBlur = 8;
      ctx.fill();
      ctx.shadowBlur = 0;

      if (status === 'listening') {
        const waves = 3;
        for (let i = 0; i < waves; i++) {
          const r = radius * (0.8 + 0.2 * Math.sin(timeRef.current * 3 + i * 2.09));
          ctx.beginPath();
          ctx.arc(cx, cy, r, 0, Math.PI * (1 + Math.sin(timeRef.current * 2 + i * 2.09)));
          ctx.strokeStyle = `rgba(0, 255, 65, ${0.3 - i * 0.08})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }

      if (status === 'thinking' || status === 'executing') {
        const speed = status === 'thinking' ? 2 : 3;
        for (let i = 0; i < 3; i++) {
          const angle = timeRef.current * speed + i * 2.09;
          const r = radius * (0.6 + 0.3 * Math.sin(timeRef.current * 2 + i));
          ctx.beginPath();
          ctx.arc(cx, cy, r, angle, angle + Math.PI * 0.8);
          ctx.strokeStyle = `rgba(0, 255, 65, ${0.4 - i * 0.1})`;
          ctx.lineWidth = 1.5;
          ctx.stroke();
        }
      }

      // Hex grid overlay
      const hexSize = 12;
      for (let row = -2; row <= 2; row++) {
        for (let col = -2; col <= 2; col++) {
          if (row === 0 && col === 0) continue;
          const hx = cx + col * hexSize * 1.5;
          const hy = cy + row * hexSize * Math.sqrt(3) + (col % 2) * hexSize * Math.sqrt(3) / 2;
          const dist = Math.sqrt((hx - cx) ** 2 + (hy - cy) ** 2);
          if (dist > radius * 1.3) continue;
          ctx.beginPath();
          for (let s = 0; s < 6; s++) {
            const a = Math.PI / 3 * s - Math.PI / 6;
            const px = hx + hexSize * 0.4 * Math.cos(a);
            const py = hy + hexSize * 0.4 * Math.sin(a);
            s === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
          }
          ctx.closePath();
          ctx.strokeStyle = `rgba(0, 255, 65, ${0.06 + 0.04 * Math.sin(timeRef.current + dist * 0.1)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }

      frameRef.current = requestAnimationFrame(animate);
    };

    frameRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frameRef.current);
  }, [status]);

  return (
    <motion.div
      className="relative flex items-center justify-center cursor-pointer"
      style={{ width: 160, height: 160 }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onToggleVoice}
    >
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" />
      <motion.div
        className="absolute z-10 text-[9px] font-bold tracking-widest uppercase"
        style={{ color: '#006600' }}
        animate={{ opacity: status === 'idle' ? [0.3, 0.6, 0.3] : 1 }}
        transition={{ repeat: Infinity, duration: 2 }}
      >
        {status === 'idle' && 'SPACE_TO_TALK'}
        {status === 'listening' && 'LISTENING'}
        {status === 'thinking' && 'PROCESSING'}
        {status === 'executing' && 'EXECUTING'}
      </motion.div>
    </motion.div>
  );
}
