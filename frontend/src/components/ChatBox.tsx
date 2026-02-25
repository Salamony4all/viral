import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader, Trash2 } from 'lucide-react';
import type { Message } from '@/types';
import './ChatBox.css';

interface ChatBoxProps {
  agent: string;
  onSendMessage: (message: string) => Promise<string>;
  isLoading?: boolean;
}

const QUICK_PROMPTS: Record<string, string[]> = {
  'Agent Alpha': [
    'What trends are rising right now?',
    'Best niches with low competition?',
    'YouTube formats to bring to TikTok?',
  ],
  'Agent Beta': [
    'Write a hook for a productivity video',
    'Give me 3 pattern interrupt ideas',
    'How do I keep viewers past 3 seconds?',
  ],
  'Agent Gamma': [
    'Best visual style for viral TikToks?',
    'How to add captions that pop?',
    'Tips for audio mixing in short-form?',
  ],
  'Agent Delta': [
    'Best monetization for a new account?',
    'Affiliate vs TikTok Shop — which first?',
    'How to add CTAs without being salesy?',
  ],
};

export const ChatBox: React.FC<ChatBoxProps> = ({
  agent,
  onSendMessage,
  isLoading = false,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (overrideText?: string) => {
    const text = overrideText || input;
    if (!text.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now(),
      role: 'user',
      content: text,
      timestamp: new Date(),
      agent,
    };

    setMessages((prev) => [...prev, userMessage]);
    if (!overrideText) setInput('');
    setLoading(true);

    try {
      const responseContent = await onSendMessage(text);
      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: responseContent,
        timestamp: new Date(),
        agent,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant' as const,
          content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
          timestamp: new Date(),
          agent,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = () => setMessages([]);
  const prompts = QUICK_PROMPTS[agent] || QUICK_PROMPTS['Agent Beta'];

  return (
    <div className="chat-box">
      <div className="chat-header">
        <h3>Brainstorm with {agent}</h3>
        {messages.length > 0 && (
          <button className="chat-clear-btn" onClick={clearHistory} title="Clear chat">
            <Trash2 size={14} />
          </button>
        )}
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty-state">
            <p className="chat-empty-title">Ask {agent.replace('Agent ', '')} anything</p>
            <p className="chat-empty-sub">Quick suggestions:</p>
            <div className="quick-prompts">
              {prompts.map((p) => (
                <button
                  key={p}
                  className="quick-prompt-chip"
                  onClick={() => handleSend(p)}
                  disabled={loading}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`chat-message ${msg.role}`}>
            <div className="message-avatar">
              {msg.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              <pre className="message-text">{msg.content}</pre>
              <small>{new Date(msg.timestamp).toLocaleTimeString()}</small>
            </div>
          </div>
        ))}

        {loading && (
          <div className="chat-message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content typing-indicator">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
          placeholder={`Message ${agent}...`}
          disabled={loading || isLoading}
          className="chat-input"
        />
        <button
          onClick={() => handleSend()}
          disabled={!input.trim() || loading || isLoading}
          className="chat-send-btn"
        >
          {loading ? <Loader size={16} className="spinner" /> : <Send size={16} />}
        </button>
      </div>
    </div>
  );
};
