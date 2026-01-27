import React, { useState, useEffect } from 'react';

interface Campaign {
  id: string;
  domain: string;
  status: string;
  stats: {
    content_generated: number;
    content_posted: number;
    urls_indexed: number;
    average_position: number;
  };
  created_at: string;
  last_activity: string;
}

interface AutopilotStats {
  total_campaigns: number;
  running_campaigns: number;
  total_content_generated: number;
  total_urls_indexed: number;
}

const API_BASE = 'http://localhost:8000';

const AutopilotManager: React.FC = () => {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [stats, setStats] = useState<AutopilotStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newDomain, setNewDomain] = useState('');
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);
  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [campaignsRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/api/autopilot/campaigns`),
        fetch(`${API_BASE}/api/autopilot/stats`)
      ]);
      
      if (campaignsRes.ok) {
        setCampaigns(await campaignsRes.json());
      }
      if (statsRes.ok) {
        setStats(await statsRes.json());
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const createCampaign = async () => {
    if (!newDomain) return;
    
    try {
      const res = await fetch(`${API_BASE}/api/autopilot/campaigns`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ domain: newDomain })
      });
      
      if (res.ok) {
        setShowCreateModal(false);
        setNewDomain('');
        loadData();
      }
    } catch (error) {
      console.error('Error creating campaign:', error);
    }
  };

  const startCampaign = async (campaignId: string) => {
    try {
      await fetch(`${API_BASE}/api/autopilot/campaigns/${campaignId}/start`, {
        method: 'POST'
      });
      loadData();
    } catch (error) {
      console.error('Error starting campaign:', error);
    }
  };

  const pauseCampaign = async (campaignId: string) => {
    try {
      await fetch(`${API_BASE}/api/autopilot/campaigns/${campaignId}/pause`, {
        method: 'POST'
      });
      loadData();
    } catch (error) {
      console.error('Error pausing campaign:', error);
    }
  };

  const loadLogs = async (campaignId: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/autopilot/campaigns/${campaignId}/logs`);
      if (res.ok) {
        const data = await res.json();
        setLogs(data.logs || []);
      }
    } catch (error) {
      console.error('Error loading logs:', error);
    }
  };

  const selectCampaign = (campaign: Campaign) => {
    setSelectedCampaign(campaign);
    loadLogs(campaign.id);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'bg-green-100 text-green-800';
      case 'paused': return 'bg-yellow-100 text-yellow-800';
      case 'created': return 'bg-blue-100 text-blue-800';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'running': return '🚀 Работает';
      case 'paused': return '⏸️ Пауза';
      case 'created': return '📝 Создана';
      case 'analyzing': return '🔍 Анализ';
      case 'error': return '❌ Ошибка';
      default: return status;
    }
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
      {/* Заголовок и статистика */}
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">🤖 Автопилот</h2>
          <p className="text-gray-600 mt-1">Автоматическое продвижение сайтов</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <span>➕</span> Новая кампания
        </button>
      </div>

      {/* Статистика */}
      {stats && (
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg shadow border-l-4 border-blue-500">
            <div className="text-2xl font-bold text-blue-600">{stats.total_campaigns}</div>
            <div className="text-gray-600 text-sm">Всего кампаний</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow border-l-4 border-green-500">
            <div className="text-2xl font-bold text-green-600">{stats.running_campaigns}</div>
            <div className="text-gray-600 text-sm">Активных</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow border-l-4 border-purple-500">
            <div className="text-2xl font-bold text-purple-600">{stats.total_content_generated}</div>
            <div className="text-gray-600 text-sm">Контента создано</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow border-l-4 border-orange-500">
            <div className="text-2xl font-bold text-orange-600">{stats.total_urls_indexed}</div>
            <div className="text-gray-600 text-sm">URL проиндексировано</div>
          </div>
        </div>
      )}

      {/* Список кампаний и детали */}
      <div className="grid grid-cols-3 gap-6">
        {/* Список кампаний */}
        <div className="col-span-2 bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h3 className="font-semibold">Кампании продвижения</h3>
          </div>
          <div className="divide-y">
            {campaigns.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <div className="text-4xl mb-2">🎯</div>
                <p>Нет кампаний</p>
                <p className="text-sm">Создайте первую кампанию для начала продвижения</p>
              </div>
            ) : (
              campaigns.map((campaign) => (
                <div
                  key={campaign.id}
                  className={`p-4 hover:bg-gray-50 cursor-pointer ${selectedCampaign?.id === campaign.id ? 'bg-blue-50' : ''}`}
                  onClick={() => selectCampaign(campaign)}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium text-gray-900">{campaign.domain}</div>
                      <div className="text-sm text-gray-500 mt-1">
                        Создано: {new Date(campaign.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(campaign.status)}`}>
                        {getStatusText(campaign.status)}
                      </span>
                      {campaign.status === 'running' ? (
                        <button
                          onClick={(e) => { e.stopPropagation(); pauseCampaign(campaign.id); }}
                          className="p-1 text-yellow-600 hover:bg-yellow-100 rounded"
                          title="Приостановить"
                        >
                          ⏸️
                        </button>
                      ) : (
                        <button
                          onClick={(e) => { e.stopPropagation(); startCampaign(campaign.id); }}
                          className="p-1 text-green-600 hover:bg-green-100 rounded"
                          title="Запустить"
                        >
                          ▶️
                        </button>
                      )}
                    </div>
                  </div>
                  <div className="mt-2 flex gap-4 text-sm text-gray-600">
                    <span>📝 {campaign.stats.content_generated} контента</span>
                    <span>📤 {campaign.stats.content_posted} постов</span>
                    <span>🔗 {campaign.stats.urls_indexed} индексировано</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Детали кампании */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h3 className="font-semibold">
              {selectedCampaign ? `Логи: ${selectedCampaign.domain}` : 'Выберите кампанию'}
            </h3>
          </div>
          <div className="p-4 h-96 overflow-y-auto">
            {selectedCampaign ? (
              logs.length > 0 ? (
                <div className="space-y-2">
                  {logs.slice(-20).reverse().map((log, idx) => (
                    <div key={idx} className={`text-xs p-2 rounded ${log.level === 'error' ? 'bg-red-50 text-red-700' : 'bg-gray-50 text-gray-700'}`}>
                      <div className="text-gray-400">{new Date(log.timestamp).toLocaleTimeString()}</div>
                      <div>{log.message}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <div className="text-2xl mb-2">📋</div>
                  <p>Нет логов</p>
                </div>
              )
            ) : (
              <div className="text-center text-gray-500 py-8">
                <div className="text-2xl mb-2">👈</div>
                <p>Выберите кампанию для просмотра логов</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Модальное окно создания кампании */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
            <div className="p-4 border-b flex justify-between items-center">
              <h3 className="font-semibold">Новая кампания продвижения</h3>
              <button onClick={() => setShowCreateModal(false)} className="text-gray-500 hover:text-gray-700">
                ✕
              </button>
            </div>
            <div className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Домен для продвижения
                </label>
                <input
                  type="text"
                  value={newDomain}
                  onChange={(e) => setNewDomain(e.target.value)}
                  placeholder="example.com"
                  className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="bg-blue-50 p-3 rounded-lg text-sm text-blue-800">
                <strong>Что будет делать автопилот:</strong>
                <ul className="mt-2 space-y-1">
                  <li>✅ Анализировать сайт и конкурентов</li>
                  <li>✅ Генерировать SEO-контент</li>
                  <li>✅ Публиковать на площадках</li>
                  <li>✅ Индексировать в поисковиках</li>
                  <li>✅ Отслеживать позиции</li>
                  <li>✅ Самообучаться на результатах</li>
                </ul>
              </div>
            </div>
            <div className="p-4 border-t flex justify-end gap-2">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                Отмена
              </button>
              <button
                onClick={createCampaign}
                disabled={!newDomain}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                Создать кампанию
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AutopilotManager;
