import { useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Database, Cpu, Globe, BookmarkCheck, Zap, Volume2, FolderOpen } from 'lucide-react';
import ChatPanel from './components/ChatPanel';
import JarvisCore from './components/JarvisCore';
import Terminal from './components/Terminal';
import FileBrowser from './components/FileBrowser';
import { useWebSocket } from './hooks/useWebSocket';

const WS_URL = `ws://${window.location.hostname}:8000/ws`;

type Tab = 'chat' | 'files';

export default function App() {
  const [tab, setTab] = useState<Tab>('chat');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const {
    connected, status, messages, commandOutput, memoryUpdate,
    sendMessage, triggerVoice, speak, clearTerminal,
  } = useWebSocket(WS_URL);

  const isDisabled = status !== 'idle';

  const sidebarItems = [
    { icon: Database, label: 'SQLite', active: connected },
    { icon: Cpu, label: 'DeepSeek', active: status === 'thinking', state: status },
    { icon: Globe, label: 'WebSocket', active: connected },
  ];

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const form = new FormData();
    form.append('file', file);
    const res = await fetch(`http://${window.location.hostname}:8000/api/upload`, { method: 'POST', body: form });
    const data = await res.json();
    if (data.url) {
      sendMessage(`[image](${window.location.origin}${data.url})`);
    }
  };

  return (
    <div className="flex h-screen" style={{ background: '#0a0a0a' }}>
      {/* Sidebar */}
      <motion.aside
        initial={{ x: -200, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        className="w-48 shrink-0 flex flex-col"
        style={{ background: '#0d1117', borderRight: '1px solid #21262d' }}
      >
        <div className="px-4 pt-5 pb-4 border-b border-[#21262d]">
          <h1 className="text-base font-bold tracking-widest text-[#3fb950]" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
            VEKTOR
          </h1>
          <div className="mt-1.5 text-[11px] text-[#8b949e] font-mono">
            {connected ? '● ONLINE' : '○ OFFLINE'}
          </div>
        </div>

        {/* Tabs */}
        <div className="px-3 mt-3 space-y-1">
          <button onClick={() => setTab('chat')}
            className="w-full flex items-center gap-2.5 px-3 py-2 text-xs rounded-md transition-colors"
            style={{ background: tab === 'chat' ? '#161b22' : 'transparent', color: tab === 'chat' ? '#3fb950' : '#8b949e' }}>
            <Zap size={13} /> Chat
          </button>
          <button onClick={() => setTab('files')}
            className="w-full flex items-center gap-2.5 px-3 py-2 text-xs rounded-md transition-colors"
            style={{ background: tab === 'files' ? '#161b22' : 'transparent', color: tab === 'files' ? '#3fb950' : '#8b949e' }}>
            <FolderOpen size={13} /> Files
          </button>
        </div>

        <div className="px-3 mt-4 mb-2">
          <span className="text-[10px] font-semibold tracking-wider text-[#8b949e]">STATUS</span>
        </div>
        <div className="px-3 space-y-2">
          {sidebarItems.map((item) => (
            <div key={item.label} className="flex items-center gap-2.5 px-2 py-1">
              <span className={`w-1.5 h-1.5 rounded-full ${item.active ? 'bg-[#3fb950]' : 'bg-[#8b949e]'} ${item.state === 'thinking' ? 'animate-pulse' : ''}`} />
              <item.icon size={11} className="text-[#8b949e]" />
              <span className="text-xs text-[#8b949e]">{item.label}</span>
            </div>
          ))}
        </div>

        <div className="mt-auto px-4 py-3 border-t border-[#21262d]">
          <div className="text-[10px] text-[#8b949e] font-mono">deepseek-chat</div>
        </div>
      </motion.aside>

      {/* Main */}
      <div className="flex-1 flex flex-col relative">
        {/* Top bar */}
        <header className="flex items-center justify-between px-5 py-2.5 border-b border-[#21262d]" style={{ background: '#0d1117' }}>
          <div className="flex items-center gap-3">
            <Zap size={13} className={connected ? 'text-[#3fb950]' : 'text-[#8b949e]'} />
            <span className="text-xs font-mono text-[#8b949e]">
              {connected ? '/vektor/ready' : '/vektor/connecting'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            {/* TTS Toggle */}
            <button onClick={() => speak('Test voice')}
              className="flex items-center gap-1.5 px-2 py-1 rounded text-xs border border-[#21262d] text-[#8b949e] hover:text-[#3fb950] transition-colors">
              <Volume2 size={12} /> Speak
            </button>
            {/* Voice Trigger */}
            <button onClick={triggerVoice} disabled={isDisabled}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs border disabled:opacity-40 transition-colors"
              style={{ borderColor: status === 'listening' ? '#3fb950' : '#21262d', color: status === 'listening' ? '#3fb950' : '#8b949e' }}>
              <Mic size={12} />
              {status === 'listening' ? 'Listening...' : 'Voice'}
            </button>
          </div>
        </header>

        {/* Content */}
        <div className="flex-1 flex relative overflow-hidden">
          {tab === 'chat' && (
            <div className="flex-1 flex flex-col">
              <ChatPanel messages={messages} onSend={sendMessage} disabled={isDisabled} />
              {/* Hidden file input */}
              <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleImageUpload} />
            </div>
          )}
          {tab === 'files' && <FileBrowser />}
        </div>

        {/* Memory notification */}
        <AnimatePresence>
          {memoryUpdate && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="absolute top-14 right-6 z-50 px-4 py-2 rounded border"
              style={{ background: '#0d1117', borderColor: '#3fb950' }}
            >
              <div className="flex items-center gap-2">
                <BookmarkCheck size={13} className="text-[#3fb950]" />
                <span className="text-xs text-[#8b949e]">
                  Memory: <span className="text-[#3fb950] font-mono">{memoryUpdate.key}</span>
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
        className="fixed bottom-5 right-5 z-40"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', stiffness: 200, damping: 15 }}
      >
        <JarvisCore status={status} onToggleVoice={triggerVoice} />
      </motion.div>
    </div>
  );
}
