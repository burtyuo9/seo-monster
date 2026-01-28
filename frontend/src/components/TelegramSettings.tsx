import React, { useState, useEffect } from 'react';

interface TelegramStatus {
  enabled: boolean;
  token_configured: boolean;
  subscribers_count: number;
  notifications: {
    campaign_started: boolean;
    campaign_completed: boolean;
    campaign_error: boolean;
    content_generated: boolean;
    content_posted: boolean;
    indexing_completed: boolean;
    daily_report: boolean;
  };
  recent_notifications: any[];
}

interface Subscriber {
  chat_id: string;
  username: string;
  subscribed_at: string;
  is_admin: boolean;
}

const API_BASE = 'http://144.31.238.16:8000';

const TelegramSettings: React.FC = () => {
  const [status, setStatus] = useState<TelegramStatus | null>(null);
  const [subscribers, setSubscribers] = useState<Subscriber[]>([]);
  const [loading, setLoading] = useState(true);
  const [botToken, setBotToken] = useState('');
  const [adminChatId, setAdminChatId] = useState('');
  const [showTokenInput, setShowTokenInput] = useState(false);
  const [testMessage, setTestMessage] = useState('');
  const [broadcastMessage, setBroadcastMessage] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statusRes, subscribersRes] = await Promise.all([
        fetch(`${API_BASE}/api/telegram/status`),
        fetch(`${API_BASE}/api/telegram/subscribers`)
      ]);

      if (statusRes.ok) {
        setStatus(await statusRes.json());
      }
      if (subscribersRes.ok) {
        const data = await subscribersRes.json();
        setSubscribers(data.subscribers || []);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const configurBot = async () => {
    if (!botToken) return;

    try {
      const res = await fetch(`${API_BASE}/api/telegram/configure`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          bot_token: botToken,
          admin_chat_id: adminChatId || undefined
        })
      });

      if (res.ok) {
        setShowTokenInput(false);
        setBotToken('');
        loadData();
      }
    } catch (error) {
      console.error('Error configuring bot:', error);
    }
  };

  const toggleBot = async () => {
    const endpoint = status?.enabled ? 'disable' : 'enable';
    try {
      await fetch(`${API_BASE}/api/telegram/${endpoint}`, { method: 'POST' });
      loadData();
    } catch (error) {
      console.error('Error toggling bot:', error);
    }
  };

  const updateNotification = async (key: string, value: boolean) => {
    try {
      await fetch(`${API_BASE}/api/telegram/notifications`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ [key]: value })
      });
      loadData();
    } catch (error) {
      console.error('Error updating notification:', error);
    }
  };

  const sendTestNotification = async (type: string) => {
    try {
      await fetch(`${API_BASE}/api/telegram/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notification_type: type })
      });
      setTestMessage(`✅ Тестовое уведомление "${type}" отправлено!`);
      setTimeout(() => setTestMessage(''), 3000);
    } catch (error) {
      setTestMessage('❌ Ошибка отправки');
      console.error('Error sending test:', error);
    }
  };

  const sendBroadcast = async () => {
    if (!broadcastMessage) return;

    try {
      const res = await fetch(`${API_BASE}/api/telegram/broadcast`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: broadcastMessage })
      });

      if (res.ok) {
        const data = await res.json();
        setTestMessage(`✅ Отправлено: ${data.sent}, Ошибок: ${data.failed}`);
        setBroadcastMessage('');
        setTimeout(() => setTestMessage(''), 3000);
      }
    } catch (error) {
      setTestMessage('❌ Ошибка рассылки');
      console.error('Error broadcasting:', error);
    }
  };

  const removeSubscriber = async (chatId: string) => {
    try {
      await fetch(`${API_BASE}/api/telegram/subscribers/${chatId}`, {
        method: 'DELETE'
      });
      loadData();
    } catch (error) {
      console.error('Error removing subscriber:', error);
    }
  };

  const notificationLabels: Record<string, string> = {
    campaign_started: '🚀 Запуск кампании',
    campaign_completed: '✅ Завершение цикла',
    campaign_error: '❌ Ошибки кампании',
    content_generated: '✍️ Генерация контента',
    content_posted: '📤 Публикация контента',
    indexing_completed: '🔍 Индексация URL',
    daily_report: '📊 Ежедневный отчёт'
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">📱 Telegram интеграция</h2>
          <p className="text-gray-600 mt-1">Управление и уведомления через Telegram бота</p>
        </div>
      </div>

      {/* Статус и настройка */}
      <div className="grid grid-cols-2 gap-6">
        {/* Статус бота */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-lg mb-4">Статус бота</h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span>Токен настроен:</span>
              <span className={`px-2 py-1 rounded text-sm ${status?.token_configured ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                {status?.token_configured ? '✅ Да' : '❌ Нет'}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span>Бот активен:</span>
              <button
                onClick={toggleBot}
                disabled={!status?.token_configured}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                  status?.enabled 
                    ? 'bg-green-500 text-white hover:bg-green-600' 
                    : 'bg-gray-300 text-gray-700 hover:bg-gray-400'
                } disabled:opacity-50`}
              >
                {status?.enabled ? '🟢 Включен' : '⚪ Выключен'}
              </button>
            </div>
            
            <div className="flex items-center justify-between">
              <span>Подписчиков:</span>
              <span className="font-medium">{status?.subscribers_count || 0}</span>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t">
            {!showTokenInput ? (
              <button
                onClick={() => setShowTokenInput(true)}
                className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                {status?.token_configured ? '🔄 Изменить токен' : '⚙️ Настроить бота'}
              </button>
            ) : (
              <div className="space-y-3">
                <input
                  type="password"
                  value={botToken}
                  onChange={(e) => setBotToken(e.target.value)}
                  placeholder="Bot Token от @BotFather"
                  className="w-full border rounded-lg px-3 py-2"
                />
                <input
                  type="text"
                  value={adminChatId}
                  onChange={(e) => setAdminChatId(e.target.value)}
                  placeholder="Ваш Chat ID (опционально)"
                  className="w-full border rounded-lg px-3 py-2"
                />
                <div className="flex gap-2">
                  <button
                    onClick={configurBot}
                    className="flex-1 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    Сохранить
                  </button>
                  <button
                    onClick={() => setShowTokenInput(false)}
                    className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
                  >
                    Отмена
                  </button>
                </div>
                <p className="text-xs text-gray-500">
                  Получите токен у @BotFather в Telegram. Chat ID можно узнать у @userinfobot
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Настройки уведомлений */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-lg mb-4">Уведомления</h3>
          
          <div className="space-y-3">
            {status?.notifications && Object.entries(status.notifications).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between">
                <span className="text-sm">{notificationLabels[key] || key}</span>
                <button
                  onClick={() => updateNotification(key, !value)}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    value ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full shadow transform transition-transform ${
                    value ? 'translate-x-6' : 'translate-x-0.5'
                  }`} />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Тестирование и рассылка */}
      <div className="grid grid-cols-2 gap-6">
        {/* Тестовые уведомления */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-lg mb-4">Тестовые уведомления</h3>
          
          {testMessage && (
            <div className={`mb-4 p-3 rounded-lg ${testMessage.startsWith('✅') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
              {testMessage}
            </div>
          )}
          
          <div className="grid grid-cols-2 gap-2">
            {Object.keys(notificationLabels).map((type) => (
              <button
                key={type}
                onClick={() => sendTestNotification(type)}
                disabled={!status?.enabled}
                className="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg disabled:opacity-50 text-left"
              >
                {notificationLabels[type]}
              </button>
            ))}
          </div>
        </div>

        {/* Рассылка */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-lg mb-4">Рассылка сообщения</h3>
          
          <textarea
            value={broadcastMessage}
            onChange={(e) => setBroadcastMessage(e.target.value)}
            placeholder="Введите сообщение для рассылки всем подписчикам..."
            className="w-full border rounded-lg px-3 py-2 h-24 resize-none"
          />
          
          <button
            onClick={sendBroadcast}
            disabled={!broadcastMessage || !status?.enabled}
            className="mt-3 w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            📤 Отправить всем ({status?.subscribers_count || 0})
          </button>
        </div>
      </div>

      {/* Подписчики */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b flex justify-between items-center">
          <h3 className="font-semibold">Подписчики ({subscribers.length})</h3>
        </div>
        
        <div className="divide-y max-h-64 overflow-y-auto">
          {subscribers.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <div className="text-4xl mb-2">👥</div>
              <p>Нет подписчиков</p>
              <p className="text-sm mt-1">Пользователи автоматически добавляются при отправке /start боту</p>
            </div>
          ) : (
            subscribers.map((sub) => (
              <div key={sub.chat_id} className="p-4 flex justify-between items-center hover:bg-gray-50">
                <div>
                  <div className="font-medium">
                    {sub.username ? `@${sub.username}` : `Chat ID: ${sub.chat_id}`}
                    {sub.is_admin && <span className="ml-2 text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">Admin</span>}
                  </div>
                  <div className="text-sm text-gray-500">
                    Подписан: {new Date(sub.subscribed_at).toLocaleDateString()}
                  </div>
                </div>
                <button
                  onClick={() => removeSubscriber(sub.chat_id)}
                  className="text-red-500 hover:bg-red-50 p-2 rounded"
                >
                  🗑️
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Инструкция */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-3">📋 Как настроить Telegram бота</h3>
        <ol className="list-decimal list-inside space-y-2 text-blue-800">
          <li>Откройте Telegram и найдите <strong>@BotFather</strong></li>
          <li>Отправьте команду <code className="bg-blue-100 px-1 rounded">/newbot</code></li>
          <li>Следуйте инструкциям и получите токен</li>
          <li>Вставьте токен в поле выше и нажмите "Сохранить"</li>
          <li>Включите бота и напишите ему <code className="bg-blue-100 px-1 rounded">/start</code></li>
          <li>Готово! Вы будете получать уведомления</li>
        </ol>
        
        <div className="mt-4 pt-4 border-t border-blue-200">
          <h4 className="font-medium text-blue-900 mb-2">Команды бота:</h4>
          <div className="grid grid-cols-2 gap-2 text-sm text-blue-700">
            <div><code>/start</code> — Начать работу</div>
            <div><code>/status</code> — Статус системы</div>
            <div><code>/campaigns</code> — Список кампаний</div>
            <div><code>/stats</code> — Статистика</div>
            <div><code>/help</code> — Справка</div>
            <div><code>/stop</code> — Отписаться</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TelegramSettings;
