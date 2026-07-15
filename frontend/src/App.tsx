import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff, Globe, Database, Cpu, BookmarkCheck } from 'lucide-react';
import ChatPanel from './components/ChatPanel';
import JarvisCore from './components/JarvisCore';
import Terminal from './components/Terminal';
import { useWebSocket } from './hooks/useWebSocket';

const WS_URL = `ws://${window.location.hostname}:8000/ws`;

export default function App() {
  const {
    connected,
    status,
    messages,
    commandOutput,
    previewPath,
    memoryUpdate,
    sendMessage,
    triggerVoice,
    clearTerminal,
  } = useWebSocket(WS_URL);

  const isDisabled = status !== 'idle';

  const sidebarItems = [
    { icon: Database, label: 'SQLite DB', active: connected },
    { icon: Cpu, label: 'Local LLM', active: status === 'thinking', state: status },
    { icon: Globe, label: 'WebSocket', active: connected },
  ];

  return (
    <div className="flex h-screen bg-[#0F172A]">
      {/* Sidebar */}
      <motion.aside
        initial={{ x: -60, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        className="w-[200px] bg-[#1E293B] border-r border-[#334155] flex flex-col shrink-0"
      >
        <div className="px-4 pt-5 pb-3">
          <h1 className="text-[15px] font-bold tracking-widest text-[#F1F5F9]" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
            VEKTOR
          </h1>
        </div>

        <div className="px-3 mb-2">
          <span className="text-[10px] font-semibold tracking-wider text-[#64748B] px-1">
            SYSTEM STATUS
          </span>
        </div>

        <div className="px-3 space-y-1">
          {sidebarItems.map((item) => (
            <div key={item.label} className="flex items-center gap-2.5 px-2 py-1.5 rounded-md">
              <span
                className={`w-2 h-2 rounded-full ${
                  item.active ? 'bg-[#22C55E]' : 'bg-[#EF4444]'
                } ${item.state === 'thinking' ? 'animate-pulse' : ''}`}
              />
              <item.icon size={12} className="text-[#64748B]" />
              <span className="text-[12px] text-[#94A3B8]">{item.label}</span>
            </div>
          ))}
        </div>

        <div className="mt-4 px-3 mb-2">
          <span className="text-[10px] font-semibold tracking-wider text-[#64748B] px-1">
            ACTIVE MODEL
          </span>
        </div>
        <div className="px-4">
          <span className="text-[12px] text-[#E2E8F0] font-mono">llama3.2:1b</span>
        </div>

        <div className="mt-auto px-4 py-3">
          <span className="text-[10px] text-[#475569]">v0.4.0 — local</span>
        </div>
      </motion.aside>

      {/* Main */}
      <div className="flex-1 flex flex-col relative">
        {/* Top bar */}
        <header className="flex items-center justify-between px-6 py-3 border-b border-[#334155]">
          <div className="flex items-center gap-3">
            <span className="text-[11px] font-mono text-[#64748B]">
              {connected ? 'CONNECTED' : 'DISCONNECTED'}
            </span>
            <span className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-[#22C55E]' : 'bg-[#EF4444]'}`} />
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={triggerVoice}
              disabled={isDisabled}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#1E293B] border border-[#334155] text-[11px] text-[#94A3B8] hover:text-[#F1F5F9] hover:border-[#3B82F6] transition-colors disabled:opacity-50"
            >
              {status === 'listening' ? (
                <MicOff size={13} className="text-[#EF4444]" />
              ) : (
                <Mic size={13} />
              )}
              {status === 'listening' ? 'Listening...' : 'Voice'}
            </button>
          </div>
        </header>

        {/* Content */}
        <div className="flex-1 flex relative overflow-hidden">
          {/* Chat area */}
          <div className="flex-1 flex flex-col">
            <ChatPanel messages={messages} onSend={sendMessage} disabled={isDisabled} />
          </div>

          {/* Preview panel */}
          <AnimatePresence>
            {previewPath && (
              <motion.div
                initial={{ width: 0, opacity: 0 }}
                animate={{ width: 500, opacity: 1 }}
                exit={{ width: 0, opacity: 0 }}
                transition={{ type: 'spring', stiffness: 200, damping: 25 }}
                className="border-l border-[#334155] overflow-hidden shrink-0"
              >
                <div className="flex items-center justify-between px-4 py-2 border-b border-[#334155] bg-[#1E293B]">
                  <span className="text-[10px] font-semibold tracking-wider uppercase text-[#64748B]">
                    Live Preview
                  </span>
                  <button
                    onClick={() => {/* close handled by parent state */}}
                    className="text-[#64748B] hover:text-[#F1F5F9] text-[10px]"
                  >
                    Close
                  </button>
                </div>
                <iframe
                  src={previewPath}
                  className="w-full flex-1 bg-white"
                  style={{ height: 'calc(100% - 33px)' }}
                  title="Preview"
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Memory notification */}
        <AnimatePresence>
          {memoryUpdate && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="absolute top-16 right-6 z-50 bg-[#1E293B] border border-[#22C55E] rounded-lg px-4 py-3 shadow-lg"
            >
              <div className="flex items-center gap-2">
                <BookmarkCheck size={14} className="text-[#22C55E]" />
                <span className="text-[12px] text-[#E2E8F0]">
                  Stored: <span className="font-mono text-[#A78BFA]">{memoryUpdate.key}</span>
                </span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Terminal overlay */}
        <Terminal
          output={commandOutput}
          onClear={clearTerminal}
          onClose={clearTerminal}
        />
      </div>

      {/* Jarvis Orb - floating */}
      <motion.div
        className="fixed bottom-6 right-6 z-40"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', stiffness: 200, damping: 15, delay: 0.3 }}
      >
        <JarvisCore status={status} onToggleVoice={triggerVoice} />
      </motion.div>
    </div>
  );
}
