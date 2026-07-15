import { motion, AnimatePresence } from 'framer-motion';
import { Terminal as TerminalIcon, X } from 'lucide-react';

interface Props {
  output: string[];
  onClear: () => void;
  onClose: () => void;
}

export default function Terminal({ output, onClear, onClose }: Props) {
  const hasOutput = output.length > 0;

  return (
    <AnimatePresence>
      {hasOutput && (
        <motion.div
          initial={{ y: 200, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 200, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          className="absolute bottom-0 left-0 right-0 z-50"
        >
          <div style={{ background: '#050505', borderTop: '1px solid #003300' }} className="mx-2 mb-2 rounded-sm">
            <div className="flex items-center justify-between px-4 py-1.5" style={{ borderBottom: '1px solid #003300' }}>
              <div className="flex items-center gap-2">
                <TerminalIcon size={12} style={{ color: '#00ff41' }} />
                <span className="text-[9px] font-bold tracking-wider uppercase" style={{ color: '#006600' }}>
                  // EXECUTION_LOG
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={onClear}
                  className="text-[9px] uppercase tracking-wider px-2 py-0.5"
                  style={{ color: '#006600' }}
                >
                  Clear
                </button>
                <button onClick={onClose} style={{ color: '#006600' }}>
                  <X size={12} />
                </button>
              </div>
            </div>
            <div className="p-3 max-h-40 overflow-y-auto font-mono space-y-0.5">
              {output.map((line, i) => (
                <div key={i} className="text-[11px] leading-relaxed" style={{ color: '#00cc33' }}>
                  <span style={{ color: '#006600' }}>{'$ '}</span>
                  {line}
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
