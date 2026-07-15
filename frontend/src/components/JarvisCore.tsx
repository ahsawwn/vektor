import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import type { StatusState } from '../hooks/useWebSocket';

interface Props {
  status: StatusState;
  onToggleVoice: () => void;
}

const COLORS = {
  idle: { r: 148, g: 163, b: 184 },
  listening: { r: 59, g: 130, b: 246 },
  thinking: { r: 167, g: 139, b: 250 },
  executing: { r: 34, g: 197, b: 94 },
};

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
    const color = COLORS[status] || COLORS.idle;

    const animate = (t: number) => {
      ctx.clearRect(0, 0, rect.width, rect.height);
      timeRef.current = t / 1000;

      const pulse = 0.85 + 0.15 * Math.sin(timeRef.current * 2);
      const radius = maxR * pulse;

      const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius * 1.2);
      grad.addColorStop(0, `rgba(${color.r},${color.g},${color.b},0.3)`);
      grad.addColorStop(0.4, `rgba(${color.r},${color.g},${color.b},0.15)`);
      grad.addColorStop(1, `rgba(${color.r},${color.g},${color.b},0)`);

      ctx.beginPath();
      ctx.arc(cx, cy, radius * 1.2, 0, Math.PI * 2);
      ctx.fillStyle = grad;
      ctx.fill();

      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(${color.r},${color.g},${color.b},0.5)`;
      ctx.lineWidth = 1.5;
      ctx.stroke();

      if (status === 'listening' || status === 'thinking') {
        const rings = 3;
        for (let i = 0; i < rings; i++) {
          const phase = timeRef.current * (status === 'thinking' ? 3 : 1.5) + i * 2.1;
          const r = radius * (0.7 + 0.3 * Math.sin(phase));
          ctx.beginPath();
          ctx.arc(cx, cy, r, 0, Math.PI * 2);
          ctx.strokeStyle = `rgba(${color.r},${color.g},${color.b},${0.2 - i * 0.05})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }

      if (status === 'listening') {
        const waves = 4;
        for (let i = 0; i < waves; i++) {
          const phase = timeRef.current * 4 + i * 1.57;
          const r = radius * (0.9 + 0.15 * Math.sin(phase));
          ctx.beginPath();
          ctx.arc(cx, cy, r, 0, Math.PI * 2 * (0.5 + 0.5 * Math.sin(phase)));
          ctx.strokeStyle = `rgba(59,130,246,${0.15 - i * 0.03})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }

      if (status === 'executing') {
        const angle = timeRef.current * 2;
        ctx.beginPath();
        ctx.arc(cx, cy, radius * 1.1, angle, angle + Math.PI * 1.5);
        ctx.strokeStyle = `rgba(34,197,94,0.4)`;
        ctx.lineWidth = 2;
        ctx.stroke();
      }

      frameRef.current = requestAnimationFrame(animate);
    };

    frameRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frameRef.current);
  }, [status]);

  return (
    <motion.div
      className="relative flex items-center justify-center cursor-pointer"
      style={{ width: 200, height: 200 }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onToggleVoice}
    >
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full"
      />
      <motion.div
        className="absolute z-10 text-[11px] font-medium tracking-widest uppercase"
        style={{ color: '#94A3B8' }}
        animate={{ opacity: status === 'idle' ? 0.6 : 1 }}
      >
        {status === 'idle' && 'Click to speak'}
        {status === 'listening' && 'Listening...'}
        {status === 'thinking' && 'Thinking...'}
        {status === 'executing' && 'Executing...'}
      </motion.div>
    </motion.div>
  );
}
