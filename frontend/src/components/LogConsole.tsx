import React, { useEffect, useRef, useState } from 'react';
import { Terminal, ShieldCheck, AlertTriangle, Info, Terminal as TerminalIcon } from 'lucide-react';
import './LogConsole.css';

interface LogEntry {
  level: string;
  message: string;
  timestamp: string;
}

export const LogConsole: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout;

    const connect = () => {
      const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const wsUrl = apiBase.replace(/^http/, 'ws') + '/ws/logs';
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setIsConnected(true);
        console.log('LogConsole: WebSocket connected');
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log('LogConsole: WebSocket disconnected, retrying...');
        reconnectTimeout = setTimeout(connect, 3000);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'log') {
            setLogs((prev) => [...prev, data].slice(-100));
          }
        } catch (e) {
          console.error('Error parsing log:', e);
        }
      };

      ws.onerror = (err) => {
        console.error('LogConsole: WebSocket error', err);
      };
    };

    connect();

    return () => {
      if (ws) {
        // Only close if it's not already in a closing or closed state
        if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
          ws.onclose = null; // Prevent the retry loop during unmount
          ws.close();
        }
      }
      clearTimeout(reconnectTimeout);
    };
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const getIcon = (level: string) => {
    switch (level.toUpperCase()) {
      case 'SUCCESS': return <ShieldCheck size={14} className="log-icon success" />;
      case 'ERROR': return <AlertTriangle size={14} className="log-icon error" />;
      case 'WARNING': return <AlertTriangle size={14} className="log-icon warning" />;
      default: return <Info size={14} className="log-icon info" />;
    }
  };

  return (
    <div className="log-console-container">
      <div className="log-console-header">
        <div className="header-left">
          <TerminalIcon size={16} />
          <span>Agent Cogitation Console</span>
        </div>
        <div className={`connection-status ${isConnected ? 'online' : 'offline'}`}>
          {isConnected ? 'LIVE' : 'RECONNECTING'}
        </div>
      </div>
      <div className="log-viewport" ref={scrollRef}>
        {logs.length === 0 ? (
          <div className="empty-logs">
            <Terminal size={32} opacity={0.2} />
            <p>Awaiting agent activity...</p>
          </div>
        ) : (
          logs.map((log, i) => (
            <div key={i} className={`log-entry ${log.level.toLowerCase()}`}>
              <span className="log-time">{new Date(log.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
              <span className="log-level-badge">{log.level}</span>
              {getIcon(log.level)}
              <span className="log-msg">{log.message}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
