import React, { useState, useEffect } from 'react';

interface WPSite {
  id: string;
  name: string;
  url: string;
  username: string;
  status: string;
  posts_count: number;
  pages_count: number;
  last_sync: string | null;
}

interface CPanelAccount {
  id: string;
  name: string;
  hostname: string;
  username: string;
  status: string;
  domains: string[];
  last_check: string | null;
}

interface Campaign {
  id: string;
  name: string;
  source_type: string;
  target_urls: string[];
  redirect_type: string;
  rotation_mode: string;
  status: string;
  clicks: number;
}

const HostingManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'wordpress' | 'cpanel' | 'traffic'>('wordpress');
  const [wpSites, setWpSites] = useState<WPSite[]>([]);
  const [cpanelAccounts, setCpanelAccounts] = useState<CPanelAccount[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showCampaignModal, setShowCampaignModal] = useState(false);
  const [importData, setImportData] = useState('');
  const [importType, setImportType] = useState<'wordpress' | 'cpanel'>('wordpress');
  
  // Форма добавления WP сайта
  const [wpForm, setWpForm] = useState({
    name: '',
    url: '',
    username: '',
    password: '',
    app_password: ''
  });
  
  // Форма добавления cPanel
  const [cpanelForm, setCpanelForm] = useState({
    name: '',
    hostname: '',
    username: '',
    password: '',
    port: 2083
  });
  
  // Форма кампании
  const [campaignForm, setCampaignForm] = useState({
    name: '',
    source_type: 'cpanel',
    source_ids: [] as string[],
    target_urls: '',
    redirect_type: '301',
    rotation_mode: 'single'
  });

  const API_BASE = 'http://localhost:8000/api/hosting';

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'wordpress') {
        const res = await fetch(`${API_BASE}/wordpress/sites`);
        const data = await res.json();
        setWpSites(data.sites || []);
      } else if (activeTab === 'cpanel') {
        const res = await fetch(`${API_BASE}/cpanel/accounts`);
        const data = await res.json();
        setCpanelAccounts(data.accounts || []);
      } else {
        const res = await fetch(`${API_BASE}/traffic/campaigns`);
        const data = await res.json();
        setCampaigns(data.campaigns || []);
      }
    } catch (error) {
      console.error('Ошибка загрузки:', error);
    }
    setLoading(false);
  };

  const handleImport = async () => {
    try {
      const endpoint = importType === 'wordpress' 
        ? `${API_BASE}/wordpress/sites/import`
        : `${API_BASE}/cpanel/accounts/import`;
      
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: importData, format_type: 'txt' })
      });
      
      const result = await res.json();
      alert(`Импортировано: ${result.imported}\nОшибок: ${result.errors?.length || 0}`);
      setShowImportModal(false);
      setImportData('');
      loadData();
    } catch (error) {
      alert('Ошибка импорта');
    }
  };

  const handleAddWPSite = async () => {
    try {
      const res = await fetch(`${API_BASE}/wordpress/sites`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(wpForm)
      });
      
      const result = await res.json();
      if (result.success) {
        alert('Сайт добавлен');
        setShowAddModal(false);
        setWpForm({ name: '', url: '', username: '', password: '', app_password: '' });
        loadData();
      } else {
        alert(result.error || 'Ошибка');
      }
    } catch (error) {
      alert('Ошибка добавления');
    }
  };

  const handleAddCPanel = async () => {
    try {
      const res = await fetch(`${API_BASE}/cpanel/accounts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cpanelForm)
      });
      
      const result = await res.json();
      if (result.success) {
        alert('Аккаунт добавлен');
        setShowAddModal(false);
        setCpanelForm({ name: '', hostname: '', username: '', password: '', port: 2083 });
        loadData();
      } else {
        alert(result.error || 'Ошибка');
      }
    } catch (error) {
      alert('Ошибка добавления');
    }
  };

  const handleTestConnection = async (type: 'wordpress' | 'cpanel', id: string) => {
    try {
      const endpoint = type === 'wordpress'
        ? `${API_BASE}/wordpress/sites/${id}/test`
        : `${API_BASE}/cpanel/accounts/${id}/test`;
      
      const res = await fetch(endpoint, { method: 'POST' });
      const result = await res.json();
      
      alert(result.success ? 'Подключение успешно!' : `Ошибка: ${result.error}`);
      loadData();
    } catch (error) {
      alert('Ошибка проверки');
    }
  };

  const handleSetupRedirect = async (accountId: string) => {
    const targetUrl = prompt('Введите целевой URL для редиректа:');
    if (!targetUrl) return;
    
    try {
      const res = await fetch(`${API_BASE}/cpanel/accounts/${accountId}/redirect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_url: targetUrl, redirect_type: '301' })
      });
      
      const result = await res.json();
      alert(result.success ? 'Редирект настроен!' : `Ошибка: ${result.error}`);
    } catch (error) {
      alert('Ошибка настройки редиректа');
    }
  };

  const handleCreateCampaign = async () => {
    try {
      const res = await fetch(`${API_BASE}/traffic/campaigns`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...campaignForm,
          target_urls: campaignForm.target_urls.split('\n').filter(u => u.trim())
        })
      });
      
      const result = await res.json();
      if (result.success) {
        alert('Кампания создана');
        setShowCampaignModal(false);
        setCampaignForm({
          name: '',
          source_type: 'cpanel',
          source_ids: [],
          target_urls: '',
          redirect_type: '301',
          rotation_mode: 'single'
        });
        loadData();
      } else {
        alert(result.error || 'Ошибка');
      }
    } catch (error) {
      alert('Ошибка создания кампании');
    }
  };

  const handleApplyCampaign = async (campaignId: string) => {
    if (!confirm('Применить кампанию ко всем источникам?')) return;
    
    try {
      const res = await fetch(`${API_BASE}/traffic/campaigns/${campaignId}/apply`, {
        method: 'POST'
      });
      
      const result = await res.json();
      alert(result.success 
        ? `Кампания применена!\nУспешно: ${result.results?.cpanel?.success || 0}\nОшибок: ${result.results?.cpanel?.failed || 0}`
        : `Ошибка: ${result.error}`
      );
      loadData();
    } catch (error) {
      alert('Ошибка применения кампании');
    }
  };

  const handleDelete = async (type: 'wordpress' | 'cpanel' | 'campaign', id: string) => {
    if (!confirm('Удалить?')) return;
    
    try {
      let endpoint = '';
      if (type === 'wordpress') endpoint = `${API_BASE}/wordpress/sites/${id}`;
      else if (type === 'cpanel') endpoint = `${API_BASE}/cpanel/accounts/${id}`;
      else endpoint = `${API_BASE}/traffic/campaigns/${id}`;
      
      await fetch(endpoint, { method: 'DELETE' });
      loadData();
    } catch (error) {
      alert('Ошибка удаления');
    }
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">🌐 Хостинг и Редиректы</h1>
        <div className="flex gap-2">
          <button
            onClick={() => { setImportType(activeTab === 'wordpress' ? 'wordpress' : 'cpanel'); setShowImportModal(true); }}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            disabled={activeTab === 'traffic'}
          >
            📥 Импорт
          </button>
          <button
            onClick={() => activeTab === 'traffic' ? setShowCampaignModal(true) : setShowAddModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            ➕ Добавить
          </button>
        </div>
      </div>

      {/* Табы */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setActiveTab('wordpress')}
          className={`px-4 py-2 rounded-lg ${activeTab === 'wordpress' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
        >
          🔵 WordPress ({wpSites.length})
        </button>
        <button
          onClick={() => setActiveTab('cpanel')}
          className={`px-4 py-2 rounded-lg ${activeTab === 'cpanel' ? 'bg-orange-600 text-white' : 'bg-gray-200'}`}
        >
          🟠 cPanel ({cpanelAccounts.length})
        </button>
        <button
          onClick={() => setActiveTab('traffic')}
          className={`px-4 py-2 rounded-lg ${activeTab === 'traffic' ? 'bg-purple-600 text-white' : 'bg-gray-200'}`}
        >
          🔀 Кампании ({campaigns.length})
        </button>
      </div>

      {loading ? (
        <div className="text-center py-8">Загрузка...</div>
      ) : (
        <>
          {/* WordPress Sites */}
          {activeTab === 'wordpress' && (
            <div className="grid gap-4">
              {wpSites.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  Нет WordPress сайтов. Добавьте первый сайт или импортируйте список.
                </div>
              ) : (
                wpSites.map(site => (
                  <div key={site.id} className="bg-white rounded-lg shadow p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold text-lg">{site.name}</h3>
                        <p className="text-gray-500 text-sm">{site.url}</p>
                        <div className="flex gap-4 mt-2 text-sm">
                          <span>👤 {site.username}</span>
                          <span>📝 {site.posts_count} постов</span>
                          <span>📄 {site.pages_count} страниц</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 rounded text-xs ${
                          site.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {site.status === 'active' ? '✅ Активен' : '❌ Ошибка'}
                        </span>
                        <button
                          onClick={() => handleTestConnection('wordpress', site.id)}
                          className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                        >
                          🔗 Тест
                        </button>
                        <button
                          onClick={() => handleDelete('wordpress', site.id)}
                          className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* cPanel Accounts */}
          {activeTab === 'cpanel' && (
            <div className="grid gap-4">
              {cpanelAccounts.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  Нет cPanel аккаунтов. Добавьте первый аккаунт или импортируйте список.
                </div>
              ) : (
                cpanelAccounts.map(acc => (
                  <div key={acc.id} className="bg-white rounded-lg shadow p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold text-lg">{acc.name}</h3>
                        <p className="text-gray-500 text-sm">{acc.hostname}</p>
                        <div className="flex gap-4 mt-2 text-sm">
                          <span>👤 {acc.username}</span>
                          <span>🌐 {acc.domains?.length || 0} доменов</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 rounded text-xs ${
                          acc.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {acc.status === 'active' ? '✅ Активен' : '❌ Ошибка'}
                        </span>
                        <button
                          onClick={() => handleTestConnection('cpanel', acc.id)}
                          className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                        >
                          🔗 Тест
                        </button>
                        <button
                          onClick={() => handleSetupRedirect(acc.id)}
                          className="px-3 py-1 bg-purple-100 text-purple-700 rounded hover:bg-purple-200"
                        >
                          🔀 Редирект
                        </button>
                        <button
                          onClick={() => handleDelete('cpanel', acc.id)}
                          className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Traffic Campaigns */}
          {activeTab === 'traffic' && (
            <div className="grid gap-4">
              {campaigns.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  Нет кампаний редиректов. Создайте первую кампанию.
                </div>
              ) : (
                campaigns.map(camp => (
                  <div key={camp.id} className="bg-white rounded-lg shadow p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold text-lg">{camp.name}</h3>
                        <div className="flex gap-4 mt-2 text-sm text-gray-600">
                          <span>📍 {camp.source_type}</span>
                          <span>🔗 {camp.target_urls?.length || 0} целей</span>
                          <span>🔄 {camp.rotation_mode}</span>
                          <span>📊 {camp.clicks} кликов</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 rounded text-xs ${
                          camp.status === 'applied' ? 'bg-green-100 text-green-800' : 
                          camp.status === 'active' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100'
                        }`}>
                          {camp.status === 'applied' ? '✅ Применена' : 
                           camp.status === 'active' ? '🔵 Активна' : '⏸️ Неактивна'}
                        </span>
                        <button
                          onClick={() => handleApplyCampaign(camp.id)}
                          className="px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200"
                        >
                          🚀 Применить
                        </button>
                        <button
                          onClick={() => handleDelete('campaign', camp.id)}
                          className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </>
      )}

      {/* Модальное окно импорта */}
      {showImportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg">
            <h2 className="text-xl font-bold mb-4">
              📥 Импорт {importType === 'wordpress' ? 'WordPress сайтов' : 'cPanel аккаунтов'}
            </h2>
            <p className="text-gray-600 text-sm mb-4">
              Формат: {importType === 'wordpress' ? 'url:username:password' : 'hostname:username:password'}
              <br />Каждый аккаунт с новой строки
            </p>
            <textarea
              value={importData}
              onChange={(e) => setImportData(e.target.value)}
              placeholder={importType === 'wordpress' 
                ? 'example.com:admin:password123\nsite2.com:user:pass456'
                : 'cpanel.host.com:user:password\n192.168.1.1:admin:pass123'
              }
              className="w-full h-48 p-3 border rounded-lg font-mono text-sm"
            />
            <div className="flex justify-end gap-2 mt-4">
              <button
                onClick={() => setShowImportModal(false)}
                className="px-4 py-2 bg-gray-200 rounded-lg"
              >
                Отмена
              </button>
              <button
                onClick={handleImport}
                className="px-4 py-2 bg-green-600 text-white rounded-lg"
              >
                Импортировать
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Модальное окно добавления */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg">
            <h2 className="text-xl font-bold mb-4">
              ➕ Добавить {activeTab === 'wordpress' ? 'WordPress сайт' : 'cPanel аккаунт'}
            </h2>
            
            {activeTab === 'wordpress' ? (
              <div className="space-y-4">
                <input
                  type="text"
                  placeholder="Название сайта"
                  value={wpForm.name}
                  onChange={(e) => setWpForm({...wpForm, name: e.target.value})}
                  className="w-full p-3 border rounded-lg"
                />
                <input
                  type="text"
                  placeholder="URL сайта (example.com)"
                  value={wpForm.url}
                  onChange={(e) => setWpForm({...wpForm, url: e.target.value})}
                  className="w-full p-3 border rounded-lg"
                />
                <input
                  type="text"
                  placeholder="Логин WordPress"
                  value={wpForm.username}
                  onChange={(e) => setWpForm({...wpForm, username: e.target.value})}
                  className="w-full p-3 border rounded-lg"
                />
                <input
                  type="password"
                  placeholder="Пароль"
                  value={wpForm.password}
                  onChange={(e) => setWpForm({...wpForm, password: e.target.value})}
                  className="w-full p-3 border rounded-lg"
                />
                <input
                  type="password"
                  placeholder="Application Password (опционально)"
                  value={wpForm.app_password}
                  onChange={(e) => setWpForm({...wpForm, app_password: e.target.value})}
                  className="w-full p-3 border rounded-lg"
                />
              </div>
            ) : (
              <div className="space-y-4">
                <input
                  type="text"
                  placeholder="Название"
                  value={cpanelForm.name}
                  onChange={(e) => setCpanelForm({...cpanelForm, name: e.target.value})}
                  className="w-full p-3 border rounded-lg"
                />
                <input
                  type="text"
                  placeholder="Hostname (cpanel.example.com или IP)"
                  value={cpanelForm.hostname}
                  onChange={(e) => setCpanelForm({...cpanelForm, hostname: e.target.value})}
                  className="w-full p-3 border rounded-lg"
                />
                <input
                  type="number"
                  placeholder="Порт (по умолчанию 2083)"
                  value={cpanelForm.port}
                  onChange={(e) => setCpanelForm({...cpanelForm, port: parseInt(e.target.value)})}
                  className="w-full p-3 border rounded-lg"
                />
                <input
                  type="text"
                  placeholder="Логин cPanel"
                  value={cpanelForm.username}
                  onChange={(e) => setCpanelForm({...cpanelForm, username: e.target.value})}
                  className="w-full p-3 border rounded-lg"
                />
                <input
                  type="password"
                  placeholder="Пароль"
                  value={cpanelForm.password}
                  onChange={(e) => setCpanelForm({...cpanelForm, password: e.target.value})}
                  className="w-full p-3 border rounded-lg"
                />
              </div>
            )}
            
            <div className="flex justify-end gap-2 mt-4">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 bg-gray-200 rounded-lg"
              >
                Отмена
              </button>
              <button
                onClick={activeTab === 'wordpress' ? handleAddWPSite : handleAddCPanel}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg"
              >
                Добавить
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Модальное окно создания кампании */}
      {showCampaignModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg">
            <h2 className="text-xl font-bold mb-4">🔀 Создать кампанию редиректов</h2>
            
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Название кампании"
                value={campaignForm.name}
                onChange={(e) => setCampaignForm({...campaignForm, name: e.target.value})}
                className="w-full p-3 border rounded-lg"
              />
              
              <select
                value={campaignForm.source_type}
                onChange={(e) => setCampaignForm({...campaignForm, source_type: e.target.value})}
                className="w-full p-3 border rounded-lg"
              >
                <option value="cpanel">cPanel аккаунты</option>
                <option value="wordpress">WordPress сайты</option>
                <option value="both">Оба типа</option>
              </select>
              
              <div>
                <label className="block text-sm text-gray-600 mb-1">Выберите источники:</label>
                <div className="max-h-32 overflow-y-auto border rounded-lg p-2">
                  {(campaignForm.source_type === 'cpanel' || campaignForm.source_type === 'both') && 
                    cpanelAccounts.map(acc => (
                      <label key={acc.id} className="flex items-center gap-2 p-1">
                        <input
                          type="checkbox"
                          checked={campaignForm.source_ids.includes(acc.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setCampaignForm({...campaignForm, source_ids: [...campaignForm.source_ids, acc.id]});
                            } else {
                              setCampaignForm({...campaignForm, source_ids: campaignForm.source_ids.filter(id => id !== acc.id)});
                            }
                          }}
                        />
                        <span>{acc.name} ({acc.hostname})</span>
                      </label>
                    ))
                  }
                  {(campaignForm.source_type === 'wordpress' || campaignForm.source_type === 'both') && 
                    wpSites.map(site => (
                      <label key={site.id} className="flex items-center gap-2 p-1">
                        <input
                          type="checkbox"
                          checked={campaignForm.source_ids.includes(site.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setCampaignForm({...campaignForm, source_ids: [...campaignForm.source_ids, site.id]});
                            } else {
                              setCampaignForm({...campaignForm, source_ids: campaignForm.source_ids.filter(id => id !== site.id)});
                            }
                          }}
                        />
                        <span>{site.name} ({site.url})</span>
                      </label>
                    ))
                  }
                </div>
              </div>
              
              <textarea
                placeholder="Целевые URL (по одному на строку)"
                value={campaignForm.target_urls}
                onChange={(e) => setCampaignForm({...campaignForm, target_urls: e.target.value})}
                className="w-full h-24 p-3 border rounded-lg"
              />
              
              <div className="grid grid-cols-2 gap-4">
                <select
                  value={campaignForm.redirect_type}
                  onChange={(e) => setCampaignForm({...campaignForm, redirect_type: e.target.value})}
                  className="p-3 border rounded-lg"
                >
                  <option value="301">301 (Постоянный)</option>
                  <option value="302">302 (Временный)</option>
                </select>
                
                <select
                  value={campaignForm.rotation_mode}
                  onChange={(e) => setCampaignForm({...campaignForm, rotation_mode: e.target.value})}
                  className="p-3 border rounded-lg"
                >
                  <option value="single">Один URL</option>
                  <option value="random">Случайный</option>
                  <option value="sequential">По очереди</option>
                </select>
              </div>
            </div>
            
            <div className="flex justify-end gap-2 mt-4">
              <button
                onClick={() => setShowCampaignModal(false)}
                className="px-4 py-2 bg-gray-200 rounded-lg"
              >
                Отмена
              </button>
              <button
                onClick={handleCreateCampaign}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg"
              >
                Создать
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HostingManager;
