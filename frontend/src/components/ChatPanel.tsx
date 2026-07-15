import { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { User, Bot, Code } from 'lucide-react';
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
    const codeBlock = content.match(/```(\w+)?\n([\s\S]*?)```/);
    if (codeBlock) {
      return (
        <div className="mt-2">
          <div className="flex items-center gap-1.5 text-[10px] text-[#64748B] font-mono mb-1">
            <Code size={12} />
            {codeBlock[1] || 'code'}
          </div>
          <pre className="bg-[#1E293B] border border-[#334155] rounded-lg p-3 overflow-x-auto text-[12px] leading-relaxed font-mono text-[#A5B4FC]">
            {codeBlock[2]}
          </pre>
        </div>
      );
    }
    return (
      <div className="text-[13px] leading-relaxed text-[#E2E8F0] whitespace-pre-wrap">
        {content}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
        <AnimatePresence initial={false}>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
              className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[75%] rounded-xl px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-[#1E293B] border border-[#334155]'
                    : 'bg-[#0F172A] border border-[#1E3A5C]'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  {msg.role === 'user' ? (
                    <User size={12} className="text-[#60A5FA]" />
                  ) : (
                    <Bot size={12} className="text-[#A78BFA]" />
                  )}
                  <span className="text-[10px] font-semibold tracking-wider uppercase text-[#64748B]">
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

      <form onSubmit={handleSubmit} className="px-4 pb-4 pt-2 border-t border-[#334155]">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            placeholder="Ask Vektor anything..."
            disabled={disabled}
            className="flex-1 bg-[#0F172A] border border-[#334155] rounded-xl px-4 py-3 text-[13px] text-[#E2E8F0] placeholder-[#64748B] outline-none focus:border-[#3B82F6] transition-colors disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={disabled}
            className="bg-[#3B82F6] hover:bg-[#2563EB] disabled:opacity-50 text-white rounded-xl px-5 py-3 text-[13px] font-semibold transition-colors"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
