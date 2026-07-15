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
          <div className="bg-[#1E293B] border-t border-[#334155] rounded-t-xl mx-4 shadow-2xl">
            <div className="flex items-center justify-between px-4 py-2 border-b border-[#334155]">
              <div className="flex items-center gap-2">
                <TerminalIcon size={14} className="text-[#22C55E]" />
                <span className="text-[11px] font-semibold tracking-wider uppercase text-[#64748B]">
                  Terminal
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={onClear}
                  className="text-[10px] text-[#64748B] hover:text-[#F1F5F9] transition-colors px-2 py-1 rounded"
                >
                  Clear
                </button>
                <button
                  onClick={onClose}
                  className="text-[#64748B] hover:text-[#F1F5F9] transition-colors"
                >
                  <X size={14} />
                </button>
              </div>
            </div>
            <div className="p-4 max-h-48 overflow-y-auto font-mono text-[12px] leading-relaxed space-y-1">
              {output.map((line, i) => (
                <div key={i} className="text-[#94A3B8]">
                  <span className="text-[#475569] mr-2">{`$`}</span>
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
