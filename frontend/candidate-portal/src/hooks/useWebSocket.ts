import { useState, useEffect, useCallback, useRef } from 'react';
import { WS_BASE_URL } from '../utils/constants';

interface WebSocketHook {
  sendMessage: (msg: any) => void;
  lastMessage: any;
  isConnected: boolean;
}

export const useWebSocket = (interviewId: string | undefined): WebSocketHook => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!interviewId) return;

    const url = `${WS_BASE_URL}/interview/${interviewId}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastMessage(data);
      } catch (e) {
        setLastMessage(event.data);
      }
    };

    return () => {
      ws.close();
    };
  }, [interviewId]);

  const sendMessage = useCallback((msg: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(typeof msg === 'string' ? msg : JSON.stringify(msg));
    }
  }, []);

  return { sendMessage, lastMessage, isConnected };
};
