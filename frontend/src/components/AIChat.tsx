import React, { useState, useEffect, useRef } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  actionResult?: any;
}

const API_BASE = 'http://localhost:8000';

const AIChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    initSession();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initSession = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/chat/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (res.ok) {
        const data = await res.json();
        setSessionId(data.session_id);
        
        // Приветственное сообщение
        setMessages([{
          role: 'assistant',
          content: `👋 Привет! Я AI-ассистент SEO Monster.

Я помогу вам управлять системой через естественный диалог. Вот что я умею:

🎯 **Кампании** — создание и управление автопродвижением
👥 **Аккаунты** — импорт и управление базами
✍️ **Контент** — генерация SEO-статей
🔍 **Индексация** — отправка в поисковики

Просто напишите, что хотите сделать!`,
          timestamp: new Date().toISOString()
        }]);
        
        setSuggestions(['Покажи статистику', 'Создай кампанию', 'Помощь']);
      }
    } catch (error) {
      console.error('Error initializing session:', error);
    }
  };

  const sendMessage = async (text?: string) => {
    const messageText = text || input;
    if (!messageText.trim() || !sessionId) return;

    // Добавляем сообщение пользователя
    const userMessage: Message = {
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setSuggestions([]);

    try {
      const res = await fetch(`${API_BASE}/api/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message: messageText
        })
      });

      if (res.ok) {
        const data = await res.json();
        
        // Добавляем ответ ассистента
        const assistantMessage: Message = {
          role: 'assistant',
          content: data.response,
          timestamp: new Date().toISOString(),
          actionResult: data.action_result
        };
        setMessages(prev => [...prev, assistantMessage]);
        
        // Обновляем предложения
        if (data.suggestions) {
          setSuggestions(data.suggestions);
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '❌ Ошибка соединения с сервером. Попробуйте позже.',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatMessage = (content: string) => {
    // Простое форматирование markdown
    return content
      .split('\n')
      .map((line, i) => {
        // Заголовки
        if (line.startsWith('**') && line.endsWith('**')) {
          return <strong key={i} className="block">{line.slice(2, -2)}</strong>;
        }
        // Жирный текст
        const boldRegex = /\*\*([^*]+)\*\*/g;
        const parts = line.split(boldRegex);
        if (parts.length > 1) {
          return (
            <span key={i} className="block">
              {parts.map((part, j) => 
                j % 2 === 1 ? <strong key={j}>{part}</strong> : part
              )}
            </span>
          );
        }
        return <span key={i} className="block">{line || '\u00A0'}</span>;
      });
  };

  const renderActionResult = (result: any) => {
    if (!result) return null;

    return (
      <div className="mt-2 p-3 bg-gray-100 rounded-lg text-sm">
        {result.campaigns && (
          <div>
            <div className="font-medium mb-2">Кампании:</div>
            {result.campaigns.map((c: any) => (
              <div key={c.id} className="flex justify-between py-1 border-b border-gray-200 last:border-0">
                <span>{c.domain}</span>
                <span className={`px-2 py-0.5 rounded text-xs ${
                  c.status === 'running' ? 'bg-green-100 text-green-700' : 'bg-gray-200'
                }`}>
                  {c.status}
                </span>
              </div>
            ))}
          </div>
        )}
        
        {result.autopilot && (
          <div className="grid grid-cols-2 gap-2">
            <div>Кампаний: <strong>{result.autopilot.total_campaigns}</strong></div>
            <div>Активных: <strong>{result.autopilot.running_campaigns}</strong></div>
            <div>Контента: <strong>{result.autopilot.total_content_generated}</strong></div>
            <div>Индексировано: <strong>{result.autopilot.total_urls_indexed}</strong></div>
          </div>
        )}
        
        {result.accounts && (
          <div className="grid grid-cols-2 gap-2">
            <div>Аккаунтов: <strong>{result.accounts.total_accounts}</strong></div>
            <div>С cookies: <strong>{result.accounts.with_cookies}</strong></div>
          </div>
        )}
        
        {result.content && (
          <div>
            <div className="font-medium">{result.content.title}</div>
            <div className="text-gray-600 text-xs mt-1">{result.content.meta_description}</div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Заголовок */}
      <div className="bg-white border-b px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-xl">
            🤖
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">AI Ассистент</h2>
            <p className="text-xs text-gray-500">Управление через естественный язык</p>
          </div>
        </div>
        <button
          onClick={initSession}
          className="text-gray-500 hover:text-gray-700 p-2"
          title="Новый чат"
        >
          🔄
        </button>
      </div>

      {/* Сообщения */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white rounded-br-md'
                  : 'bg-white shadow-sm border rounded-bl-md'
              }`}
            >
              <div className={message.role === 'user' ? 'text-white' : 'text-gray-800'}>
                {formatMessage(message.content)}
              </div>
              {message.actionResult && renderActionResult(message.actionResult)}
              <div className={`text-xs mt-2 ${message.role === 'user' ? 'text-blue-200' : 'text-gray-400'}`}>
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white shadow-sm border rounded-2xl rounded-bl-md px-4 py-3">
              <div className="flex items-center gap-2">
                <div className="animate-bounce">●</div>
                <div className="animate-bounce" style={{ animationDelay: '0.1s' }}>●</div>
                <div className="animate-bounce" style={{ animationDelay: '0.2s' }}>●</div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Предложения */}
      {suggestions.length > 0 && (
        <div className="px-4 py-2 flex gap-2 flex-wrap">
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => sendMessage(suggestion)}
              className="px-3 py-1.5 bg-white border rounded-full text-sm text-gray-700 hover:bg-gray-50 hover:border-blue-300 transition-colors"
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}

      {/* Поле ввода */}
      <div className="bg-white border-t p-4">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Напишите сообщение... (Enter для отправки)"
            className="flex-1 border rounded-xl px-4 py-3 resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            rows={1}
            disabled={loading}
          />
          <button
            onClick={() => sendMessage()}
            disabled={!input.trim() || loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            ➤
          </button>
        </div>
        <div className="text-xs text-gray-400 mt-2 text-center">
          Примеры: "Создай кампанию для example.com" • "Покажи статистику" • "Сгенерируй контент про SEO"
        </div>
      </div>
    </div>
  );
};

export default AIChat;
