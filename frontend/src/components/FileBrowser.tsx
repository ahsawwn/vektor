import { useCallback, useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { File, Folder, ArrowLeft, Trash2, Plus } from 'lucide-react';

const BASE = `http://${window.location.hostname}:8000`;

interface FileEntry {
  name: string;
  is_dir: boolean;
  size: number;
  modified: number;
}

export default function FileBrowser() {
  const [path, setPath] = useState('');
  const [entries, setEntries] = useState<FileEntry[]>([]);
  const [content, setContent] = useState('');
  const [editing, setEditing] = useState<string | null>(null);
  const [newFileName, setNewFileName] = useState('');

  const loadDir = useCallback(async (dir: string) => {
    const res = await fetch(`${BASE}/api/files?path=${encodeURIComponent(dir)}`);
    const data = await res.json();
    if (data.entries) setEntries(data.entries);
  }, []);

  useEffect(() => { loadDir(path); }, [path, loadDir]);

  const openFile = async (name: string) => {
    const p = path ? `${path}/${name}` : name;
    const res = await fetch(`${BASE}/api/files/read`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: p }),
    });
    const data = await res.json();
    if (data.content) { setContent(data.content); setEditing(p); }
  };

  const saveFile = async () => {
    if (!editing) return;
    await fetch(`${BASE}/api/files/write`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: editing, content }),
    });
    setEditing(null);
  };

  const deleteEntry = async (name: string) => {
    const p = path ? `${path}/${name}` : name;
    await fetch(`${BASE}/api/files/delete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: p }),
    });
    loadDir(path);
  };

  const createFile = async () => {
    if (!newFileName) return;
    const p = path ? `${path}/${newFileName}` : newFileName;
    await fetch(`${BASE}/api/files/write`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: p, content: '' }),
    });
    setNewFileName('');
    loadDir(path);
  };

  const createDir = async () => {
    if (!newFileName) return;
    const p = path ? `${path}/${newFileName}` : newFileName;
    await fetch(`${BASE}/api/files/mkdir`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: p }),
    });
    setNewFileName('');
    loadDir(path);
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)}KB`;
    return `${(bytes / 1048576).toFixed(1)}MB`;
  };

  if (editing) {
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col h-full p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <button onClick={() => setEditing(null)} className="text-[#8b949e] hover:text-[#e6edf3]"><ArrowLeft size={14} /></button>
            <span className="text-sm font-mono text-[#3fb950]">{editing}</span>
          </div>
          <button onClick={saveFile}
            className="px-3 py-1.5 text-xs font-medium rounded"
            style={{ background: '#238636', color: '#fff' }}>
            Save
          </button>
        </div>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="flex-1 p-4 text-sm font-mono leading-relaxed rounded border outline-none resize-none"
          style={{ background: '#050505', borderColor: '#21262d', color: '#e6edf3' }}
        />
      </motion.div>
    );
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col h-full p-4">
      {/* Path bar */}
      <div className="flex items-center gap-2 mb-3">
        {path && (
          <button onClick={() => setPath(path.includes('/') ? path.split('/').slice(0, -1).join('/') : '')}
            className="text-[#8b949e] hover:text-[#e6edf3]">
            <ArrowLeft size={14} />
          </button>
        )}
        <span className="text-sm font-mono text-[#3fb950]">~/{path}</span>
        <div className="flex-1" />
        <input
          value={newFileName}
          onChange={(e) => setNewFileName(e.target.value)}
          placeholder="new name..."
          className="w-32 px-2 py-1 text-xs rounded border outline-none"
          style={{ background: '#0d1117', borderColor: '#21262d', color: '#e6edf3' }}
          onKeyDown={(e) => e.key === 'Enter' && (createFile())}
        />
        <button onClick={createFile} title="Create file"
          className="p-1.5 rounded text-[#8b949e] hover:text-[#3fb950] border border-[#21262d]">
          <Plus size={12} />
        </button>
        <button onClick={createDir} title="Create folder"
          className="p-1.5 rounded text-[#8b949e] hover:text-[#3fb950] border border-[#21262d]">
          <Folder size={12} />
        </button>
      </div>

      {/* File list */}
      <div className="flex-1 overflow-y-auto space-y-0.5">
        {entries.length === 0 && (
          <div className="text-center py-8 text-sm text-[#8b949e]">Empty directory</div>
        )}
        {entries.map((entry) => (
          <div
            key={entry.name}
            className="flex items-center gap-2 px-3 py-1.5 rounded text-sm cursor-pointer hover:bg-[#161b22] group"
            onClick={() => entry.is_dir ? setPath(path ? `${path}/${entry.name}` : entry.name) : openFile(entry.name)}
          >
            {entry.is_dir
              ? <Folder size={14} className="text-[#3fb950] shrink-0" />
              : <File size={14} className="text-[#8b949e] shrink-0" />
            }
            <span className="flex-1 truncate text-[#e6edf3]">{entry.name}</span>
            <span className="text-xs text-[#8b949e]">{entry.is_dir ? '--' : formatSize(entry.size)}</span>
            <button onClick={(e) => { e.stopPropagation(); deleteEntry(entry.name); }}
              className="opacity-0 group-hover:opacity-100 p-0.5 rounded text-[#8b949e] hover:text-[#f85149] transition-all">
              <Trash2 size={11} />
            </button>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
