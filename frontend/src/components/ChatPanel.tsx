import { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Code } from 'lucide-react';
import type { ChatMessage } from '../hooks/useWebSocket';

interface Props {
  messages: ChatMessage[];
  onSend: (text: string) => void;
  disabled: boolean;
}

export default function ChatPanel({ messages, onSend, disabled }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const input = inputRef.current;
    if (input && input.value.trim()) {
      onSend(input.value.trim());
      input.value = '';
    }
  };

  const renderContent = (content: string) => {
    // Image markdown ![alt](url)
    const imgMatch = content.match(/!\[(.*?)\]\((.*?)\)/);
    if (imgMatch) {
      return (
        <div className="mt-2">
          <img src={imgMatch[2]} alt={imgMatch[1]} className="max-w-full max-h-64 rounded border border-[#21262d]" />
        </div>
      );
    }

    // Code blocks
    const codeBlock = content.match(/```(\w+)?\n([\s\S]*?)```/);
    if (codeBlock) {
      return (
        <div className="mt-2">
          <div className="flex items-center gap-1.5 text-xs text-[#8b949e] font-mono mb-1">
            <Code size={12} />
            {codeBlock[1] || 'code'}
          </div>
          <pre className="p-3 overflow-x-auto text-sm leading-relaxed rounded border font-mono"
            style={{ background: '#050505', borderColor: '#21262d', color: '#e6edf3' }}>
            {codeBlock[2]}
          </pre>
        </div>
      );
    }

    return (
      <div className="text-sm leading-relaxed whitespace-pre-wrap text-[#e6edf3]">
        {content}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-2">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <p className="text-sm text-[#8b949e]">No messages yet</p>
              <p className="text-xs text-[#8b949e] mt-1">Type a message or use the voice button</p>
            </div>
          </div>
        )}
        <AnimatePresence initial={false}>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
            >
              <div className={`px-4 py-3 rounded-lg ${msg.role === 'user' ? 'border' : 'border-l-2'}`}
                style={{
                  background: msg.role === 'user' ? '#0d1117' : 'transparent',
                  borderColor: msg.role === 'user' ? '#21262d' : '#3fb950',
                }}>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-semibold" style={{ color: msg.role === 'user' ? '#8b949e' : '#3fb950' }}>
                    {msg.role === 'user' ? 'You' : 'Vektor'}
                  </span>
                </div>
                {renderContent(msg.content)}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="px-4 pb-3 pt-2 border-t border-[#21262d]">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            placeholder="Type a message..."
            disabled={disabled}
            className="flex-1 px-3 py-2.5 text-sm rounded-lg border outline-none transition-colors"
            style={{
              background: '#0d1117',
              borderColor: '#21262d',
              color: '#e6edf3',
              caretColor: '#3fb950',
            }}
          />
          <button type="submit" disabled={disabled}
            className="px-4 py-2.5 rounded-lg text-sm font-medium disabled:opacity-40 transition-colors"
            style={{ background: '#238636', color: '#fff' }}>
            <Send size={14} />
          </button>
        </div>
      </form>
    </div>
  );
}
