import { useCallback, useEffect, useRef, useState } from 'react';

export type Message = {
  type: string;
  [key: string]: unknown;
};

export type ChatMessage = {
  role: 'user' | 'assistant';
  content: string;
  id?: number;
};

export type StatusState = 'idle' | 'thinking' | 'listening' | 'executing';

export function useWebSocket(url: string) {
  const ws = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [status, setStatus] = useState<StatusState>('idle');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [commandOutput, setCommandOutput] = useState<string[]>([]);
  const [previewPath, setPreviewPath] = useState<string | null>(null);
  const [memoryUpdate, setMemoryUpdate] = useState<{ key: string; value: string } | null>(null);

  const listeners = useRef(new Set<(msg: Message) => void>());

  useEffect(() => {
    const socket = new WebSocket(url);
    socket.onopen = () => setConnected(true);
    socket.onclose = () => setConnected(false);
    socket.onerror = () => setConnected(false);

    socket.onmessage = (event) => {
      const data: Message = JSON.parse(event.data);
      listeners.current.forEach((fn) => fn(data));

      switch (data.type) {
        case 'status':
          setStatus(data.state as StatusState);
          break;
        case 'message':
          setMessages((prev) => [
            ...prev,
            { role: data.role as 'user' | 'assistant', content: data.content as string, id: data.id as number | undefined },
          ]);
          break;
        case 'history':
          setMessages(data.messages as ChatMessage[]);
          break;
        case 'command':
          setCommandOutput((prev) => [...prev, data.output as string]);
          break;
        case 'preview':
          setPreviewPath(data.path as string);
          break;
        case 'memory':
          setMemoryUpdate({ key: data.key as string, value: data.value as string });
          break;
        case 'voice_text':
          setMessages((prev) => [
            ...prev,
            { role: 'user', content: `[voice] ${data.text as string}` },
          ]);
          break;
      }
    };

    ws.current = socket;
    return () => socket.close();
  }, [url]);

  const send = useCallback((data: Record<string, unknown>) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(data));
    }
  }, []);

  const sendMessage = useCallback(
    (text: string) => send({ type: 'chat', text }),
    [send]
  );

  const triggerVoice = useCallback(
    () => send({ type: 'voice' }),
    [send]
  );

  const executeCommand = useCallback(
    (command: string) => send({ type: 'execute', command }),
    [send]
  );

  const remember = useCallback(
    (key: string, value: string) => send({ type: 'remember', key, value }),
    [send]
  );

  const speak = useCallback(
    (text: string) => send({ type: 'speak', text }),
    [send]
  );

  const clearTerminal = useCallback(() => setCommandOutput([]), []);

  return {
    connected,
    status,
    messages,
    setMessages,
    commandOutput,
    previewPath,
    memoryUpdate,
    sendMessage,
    triggerVoice,
    executeCommand,
    remember,
    speak,
    clearTerminal,
  };
}
