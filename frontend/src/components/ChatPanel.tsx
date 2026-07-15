import { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal as TerminalIcon, Code } from 'lucide-react';
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
          <div className="flex items-center gap-1.5 text-[10px] mb-1" style={{ color: '#006600' }}>
            <Code size={11} />
            {'// '}{codeBlock[1] || 'code'}
          </div>
          <pre
            className="p-3 overflow-x-auto text-[12px] leading-relaxed"
            style={{
              background: '#050505',
              border: '1px solid #003300',
              color: '#00ff41',
            }}
          >
<code>{codeBlock[2]}</code></pre>
        </div>
      );
    }

    // Check for command output
    if (content.startsWith('$ ')) {
      return (
        <div className="flex items-start gap-1.5 text-[12px] leading-relaxed" style={{ color: '#00cc33' }}>
          <span style={{ color: '#006600' }}>{'>'}</span>
          <span>{content.slice(2)}</span>
        </div>
      );
    }

    return (
      <div className="text-[13px] leading-relaxed whitespace-pre-wrap" style={{ color: '#00cc33' }}>
        {content}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-2">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <TerminalIcon size={24} style={{ color: '#003300' }} className="mx-auto mb-3" />
              <p className="text-[11px] tracking-wider" style={{ color: '#006600' }}>
                {'// AWAITING INPUT'}
              </p>
              <p className="text-[10px] mt-1" style={{ color: '#004400' }}>
                Type a message or use voice trigger
              </p>
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
              <div
                className="px-4 py-2.5 rounded-sm"
                style={{
                  background: msg.role === 'user' ? '#0d1117' : 'transparent',
                  border: msg.role === 'user' ? '1px solid #003300' : '1px solid transparent',
                  borderLeft: msg.role === 'assistant' ? '2px solid #00ff41' : 'none',
                }}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[9px] font-bold tracking-wider uppercase" style={{ color: msg.role === 'user' ? '#006600' : '#00ff41' }}>
                    {msg.role === 'user' ? '>> USER' : 'VEKTOR'}
                  </span>
                  <span className="text-[8px]" style={{ color: '#004400' }}>
                    {new Date().toLocaleTimeString()}
                  </span>
                </div>
                {renderContent(msg.content)}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="px-4 pb-3 pt-2" style={{ borderTop: '1px solid #003300' }}>
        <div className="flex gap-2">
          <div className="flex-1 flex items-center gap-2 px-3" style={{ background: '#050505', border: '1px solid #003300' }}>
            <span style={{ color: '#006600', fontSize: 12 }}>{'>'}</span>
            <input
              ref={inputRef}
              type="text"
              placeholder="type here..."
              disabled={disabled}
              className="flex-1 bg-transparent py-2.5 text-[13px] outline-none"
              style={{ color: '#00ff41', caretColor: '#00ff41' }}
            />
          </div>
          <button
            type="submit"
            disabled={disabled}
            className="px-4 py-2.5 text-[11px] font-bold tracking-wider uppercase disabled:opacity-40"
            style={{
              background: '#003300',
              color: '#00ff41',
              border: '1px solid #005500',
            }}
          >
            Enter
          </button>
        </div>
      </form>
    </div>
  );
}
