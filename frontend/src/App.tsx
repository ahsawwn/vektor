import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Database, Cpu, Globe, BookmarkCheck, Zap } from 'lucide-react';
import ChatPanel from './components/ChatPanel';
import JarvisCore from './components/JarvisCore';
import Terminal from './components/Terminal';
import { useWebSocket } from './hooks/useWebSocket';

const WS_URL = `ws://${window.location.hostname}:8000/ws`;

function useTypewriter(text: string, speed: number = 30) {
  const [displayed, setDisplayed] = useState('');
  useEffect(() => {
    if (!text) { setDisplayed(''); return; }
    let i = 0;
    setDisplayed('');
    const timer = setInterval(() => {
      setDisplayed(text.slice(0, i + 1));
      i++;
      if (i >= text.length) clearInterval(timer);
    }, speed);
    return () => clearInterval(timer);
  }, [text, speed]);
  return displayed;
}

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
  const bootText = useTypewriter(
    connected ? 'SYSTEM ONLINE // VEKTOR v0.4.0 // SECURE CONNECTION ESTABLISHED' : 'CONNECTING...',
    25
  );

  const sidebarItems = [
    { icon: Database, label: 'SQLite_DB', active: connected },
    { icon: Cpu, label: 'Local_LLM', active: status === 'thinking', state: status },
    { icon: Globe, label: 'WebSocket', active: connected },
  ];

  return (
    <div className="flex h-screen" style={{ background: '#0a0a0a' }}>
      {/* Sidebar */}
      <motion.aside
        initial={{ x: -200, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
        className="w-[200px] shrink-0 flex flex-col"
        style={{ background: '#0d1117', borderRight: '1px solid #003300' }}
      >
        <div className="px-4 pt-5 pb-4 border-b border-[#003300]">
          <h1 className="text-[16px] font-bold tracking-[0.3em]" style={{ color: '#00ff41', textShadow: '0 0 10px rgba(0,255,65,0.5)' }}>
            VEKTOR
          </h1>
          <div className="mt-2 text-[10px]" style={{ color: '#006600' }}>
            {bootText}
            <span className="animate-pulse" style={{ color: '#00ff41' }}>▌</span>
          </div>
        </div>

        <div className="px-3 mt-4 mb-2">
          <span className="text-[9px] tracking-[0.2em]" style={{ color: '#006600' }}>// SYSTEM STATUS</span>
        </div>
        <div className="px-3 space-y-2">
          {sidebarItems.map((item) => (
            <div key={item.label} className="flex items-center gap-2.5 px-2 py-1.5">
              <span className={`w-1.5 h-1.5 rounded-full ${
                item.active ? 'bg-[#00ff41]' : 'bg-[#006600]'
              } ${item.state === 'thinking' ? 'animate-pulse' : ''}`}
                style={{ boxShadow: item.active ? '0 0 6px rgba(0,255,65,0.8)' : 'none' }}
              />
              <item.icon size={11} style={{ color: '#006600' }} />
              <span className="text-[11px]" style={{ color: '#00cc33' }}>{item.label}</span>
            </div>
          ))}
        </div>

        <div className="px-3 mt-4 mb-2">
          <span className="text-[9px] tracking-[0.2em]" style={{ color: '#006600' }}>// ACTIVE_MODEL</span>
        </div>
        <div className="px-4">
          <span className="text-[11px]" style={{ color: '#00ff41' }}>llama3.2:1b</span>
        </div>

        <div className="mt-auto px-4 py-3 border-t border-[#003300]">
          <div className="text-[9px]" style={{ color: '#006600' }}>
            {connected ? '● ONLINE' : '○ OFFLINE'}
          </div>
        </div>
      </motion.aside>

      {/* Main */}
      <div className="flex-1 flex flex-col relative">
        {/* Top bar */}
        <header className="flex items-center justify-between px-6 py-2.5" style={{ borderBottom: '1px solid #003300', background: '#0d1117' }}>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-3"
          >
            <Zap size={12} style={{ color: connected ? '#00ff41' : '#006600' }} />
            <span className="text-[10px] tracking-wider" style={{ color: '#006600' }}>
              {connected ? 'VEKTOR_READY' : 'INITIALIZING...'}
            </span>
          </motion.div>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={triggerVoice}
            disabled={isDisabled}
            className="flex items-center gap-2 px-3 py-1.5 text-[10px] tracking-wider uppercase disabled:opacity-40"
            style={{
              background: '#0a0a0a',
              border: '1px solid #003300',
              color: status === 'listening' ? '#00ff41' : '#006600',
              boxShadow: status === 'listening' ? '0 0 10px rgba(0,255,65,0.3)' : 'none',
            }}
          >
            <Mic size={12} />
            {status === 'listening' ? 'RECEIVING_INPUT...' : 'Voice_Trigger'}
          </motion.button>
        </header>

        {/* Content */}
        <div className="flex-1 flex relative overflow-hidden">
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
                style={{ borderLeft: '1px solid #003300', background: '#0d1117' }}
                className="overflow-hidden shrink-0"
              >
                <div className="flex items-center justify-between px-4 py-2" style={{ borderBottom: '1px solid #003300', color: '#006600' }}>
                  <span className="text-[9px] tracking-wider uppercase">// LIVE_PREVIEW</span>
                </div>
                <iframe
                  src={previewPath}
                  className="w-full"
                  style={{ height: 'calc(100% - 33px)', background: '#0a0a0a' }}
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
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="absolute top-14 right-6 z-50 px-4 py-2"
              style={{ background: '#0d1117', border: '1px solid #00ff41', boxShadow: '0 0 15px rgba(0,255,65,0.2)' }}
            >
              <div className="flex items-center gap-2">
                <BookmarkCheck size={12} style={{ color: '#00ff41' }} />
                <span className="text-[11px]" style={{ color: '#00cc33' }}>
                  MEMORY_WRITTEN: <span style={{ color: '#00ff41' }}>{memoryUpdate.key}</span>
                </span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Terminal overlay */}
        <Terminal output={commandOutput} onClear={clearTerminal} onClose={clearTerminal} />
      </div>

      {/* Jarvis Orb */}
      <motion.div
        className="fixed bottom-6 right-6 z-40"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', stiffness: 200, damping: 15, delay: 0.5 }}
      >
        <JarvisCore status={status} onToggleVoice={triggerVoice} />
      </motion.div>
    </div>
  );
}
