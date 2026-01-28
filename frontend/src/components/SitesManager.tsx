import React, { useState, useEffect, useCallback } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { useTheme } from './ThemeToggle';

interface Site {
  url: string;
  name: string;
  language: string;
  added_at: string;
  status?: string;
  keywords_count?: number;
  articles_count?: number;
}

interface Campaign {
  id: string;
  domain: string;
  status: string;
  stats: {
    content_generated: number;
    content_posted: number;
    urls_indexed: number;
    positions_checked: number;
    average_position: number;
    best_position: number;
    clicks: number;
    impressions: number;
  };
  created_at: string;
  last_activity: string;
  next_action: string;
}

const API_URL = 'http://localhost:8000';

const SitesManager: React.FC = () => {
  const { language } = useLanguage();
  const { theme } = useTheme();

  // Состояния
  const [sites, setSites] = useState<Site[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showCampaignModal, setShowCampaignModal] = useState(false);
  const [selectedSite, setSelectedSite] = useState<Site | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Форма добавления сайта
  const [newSite, setNewSite] = useState({
    url: '',
    name: '',
    language: 'en'
  });

  // Переводы
  const t = {
    title: language === 'ru' ? 'Сайты' : 'Sites',
    addSite: language === 'ru' ? 'Добавить сайт' : 'Add Site',
    noSites: language === 'ru' ? 'Нет добавленных сайтов' : 'No sites added yet',
    noSitesDesc: language === 'ru' ? 'Добавьте сайт для начала продвижения' : 'Add a site to start promotion',
    url: language === 'ru' ? 'URL сайта' : 'Site URL',
    name: language === 'ru' ? 'Название' : 'Name',
    lang: language === 'ru' ? 'Язык' : 'Language',
    cancel: language === 'ru' ? 'Отмена' : 'Cancel',
    add: language === 'ru' ? 'Добавить' : 'Add',
    delete: language === 'ru' ? 'Удалить' : 'Delete',
    startCampaign: language === 'ru' ? 'Запустить кампанию' : 'Start Campaign',
    analyze: language === 'ru' ? 'Анализировать' : 'Analyze',
    status: language === 'ru' ? 'Статус' : 'Status',
    actions: language === 'ru' ? 'Действия' : 'Actions',
    addedAt: language === 'ru' ? 'Добавлен' : 'Added',
    campaigns: language === 'ru' ? 'Кампании' : 'Campaigns',
    noCampaigns: language === 'ru' ? 'Нет активных кампаний' : 'No active campaigns',
    createCampaign: language === 'ru' ? 'Создать кампанию' : 'Create Campaign',
    campaignSettings: language === 'ru' ? 'Настройки кампании' : 'Campaign Settings',
    autoMode: language === 'ru' ? 'Авто-режим' : 'Auto Mode',
    start: language === 'ru' ? 'Запустить' : 'Start',
    pause: language === 'ru' ? 'Пауза' : 'Pause',
    resume: language === 'ru' ? 'Продолжить' : 'Resume',
    running: language === 'ru' ? 'Работает' : 'Running',
    paused: language === 'ru' ? 'На паузе' : 'Paused',
    created: language === 'ru' ? 'Создана' : 'Created',
    contentGenerated: language === 'ru' ? 'Контент создан' : 'Content Generated',
    contentPosted: language === 'ru' ? 'Опубликовано' : 'Posted',
    indexed: language === 'ru' ? 'Проиндексировано' : 'Indexed',
    loading: language === 'ru' ? 'Загрузка...' : 'Loading...',
  };

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'ru', name: 'Русский' },
    { code: 'de', name: 'Deutsch' },
    { code: 'fr', name: 'Français' },
    { code: 'es', name: 'Español' },
    { code: 'it', name: 'Italiano' },
    { code: 'pt', name: 'Português' },
    { code: 'zh', name: '中文' },
    { code: 'ja', name: '日本語' },
    { code: 'ko', name: '한국어' },
  ];

  // Загрузка данных
  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [sitesRes, campaignsRes] = await Promise.all([
        fetch(`${API_URL}/api/autonomous/sites`),
        fetch(`${API_URL}/api/autopilot/campaigns`)
      ]);

      if (sitesRes.ok) {
        const data = await sitesRes.json();
        setSites(data.sites || []);
      }

      if (campaignsRes.ok) {
        const data = await campaignsRes.json();
        setCampaigns(data || []);
      }
    } catch (err) {
      console.error('Error loading data:', err);
      setError(language === 'ru' ? 'Ошибка загрузки данных' : 'Error loading data');
    } finally {
      setLoading(false);
    }
  }, [language]);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [loadData]);

  // Добавление сайта
  const handleAddSite = async () => {
    if (!newSite.url) {
      setError(language === 'ru' ? 'URL обязателен' : 'URL is required');
      return;
    }

    try {
      // Нормализуем URL
      let url = newSite.url.trim();
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'https://' + url;
      }

      const res = await fetch(`${API_URL}/api/autonomous/sites`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: url,
          name: newSite.name || url,
          language: newSite.language
        })
      });

      if (res.ok) {
        setSuccess(language === 'ru' ? 'Сайт добавлен!' : 'Site added!');
        setShowAddModal(false);
        setNewSite({ url: '', name: '', language: 'en' });
        loadData();
        setTimeout(() => setSuccess(null), 3000);
      } else {
        const data = await res.json();
        setError(data.detail || (language === 'ru' ? 'Ошибка добавления' : 'Error adding site'));
      }
    } catch (err) {
      setError(language === 'ru' ? 'Ошибка сети' : 'Network error');
    }
  };

  // Удаление сайта
  const handleDeleteSite = async (url: string) => {
    if (!confirm(language === 'ru' ? 'Удалить этот сайт?' : 'Delete this site?')) return;

    try {
      const res = await fetch(`${API_URL}/api/autonomous/sites?url=${encodeURIComponent(url)}`, {
        method: 'DELETE'
      });

      if (res.ok) {
        setSuccess(language === 'ru' ? 'Сайт удалён' : 'Site deleted');
        loadData();
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      setError(language === 'ru' ? 'Ошибка удаления' : 'Error deleting');
    }
  };

  // Создание кампании
  const handleCreateCampaign = async (site: Site) => {
    try {
      // Извлекаем домен из URL
      const urlObj = new URL(site.url);
      const domain = urlObj.hostname;

      const res = await fetch(`${API_URL}/api/autopilot/campaigns`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          domain: domain,
          settings: { language: site.language }
        })
      });

      if (res.ok) {
        const data = await res.json();
        setSuccess(language === 'ru' ? `Кампания создана: ${data.id}` : `Campaign created: ${data.id}`);
        loadData();
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      setError(language === 'ru' ? 'Ошибка создания кампании' : 'Error creating campaign');
    }
  };

  // Запуск кампании
  const handleStartCampaign = async (campaignId: string) => {
    try {
      const res = await fetch(`${API_URL}/api/autopilot/campaigns/${campaignId}/start`, {
        method: 'POST'
      });

      if (res.ok) {
        setSuccess(language === 'ru' ? 'Кампания запущена!' : 'Campaign started!');
        loadData();
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      setError(language === 'ru' ? 'Ошибка запуска' : 'Error starting');
    }
  };

  // Пауза кампании
  const handlePauseCampaign = async (campaignId: string) => {
    try {
      const res = await fetch(`${API_URL}/api/autopilot/campaigns/${campaignId}/pause`, {
        method: 'POST'
      });

      if (res.ok) {
        setSuccess(language === 'ru' ? 'Кампания приостановлена' : 'Campaign paused');
        loadData();
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      setError(language === 'ru' ? 'Ошибка' : 'Error');
    }
  };

  // Анализ сайта
  const handleAnalyzeSite = async (site: Site) => {
    try {
      const res = await fetch(`${API_URL}/api/autonomous/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: site.url,
          language: site.language
        })
      });

      if (res.ok) {
        setSuccess(language === 'ru' ? 'Анализ запущен!' : 'Analysis started!');
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      setError(language === 'ru' ? 'Ошибка анализа' : 'Analysis error');
    }
  };

  // Стили
  const cardBg = theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow';
  const textPrimary = theme === 'dark' ? 'text-white' : 'text-gray-900';
  const textSecondary = theme === 'dark' ? 'text-gray-400' : 'text-gray-500';
  const borderColor = theme === 'dark' ? 'border-gray-700' : 'border-gray-200';
  const inputBg = theme === 'dark' ? 'bg-gray-700 text-white border-gray-600' : 'bg-white text-gray-900 border-gray-300';

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'bg-green-500';
      case 'paused': return 'bg-yellow-500';
      case 'created': return 'bg-blue-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'running': return t.running;
      case 'paused': return t.paused;
      case 'created': return t.created;
      default: return status;
    }
  };

  if (loading) {
    return (
      <div className={`p-6 rounded-lg ${cardBg}`}>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className={`ml-3 ${textSecondary}`}>{t.loading}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Уведомления */}
      {error && (
        <div className="p-4 bg-red-500/20 border border-red-500 rounded-lg text-red-400">
          {error}
          <button onClick={() => setError(null)} className="float-right">×</button>
        </div>
      )}
      {success && (
        <div className="p-4 bg-green-500/20 border border-green-500 rounded-lg text-green-400">
          {success}
        </div>
      )}

      {/* Заголовок и кнопка добавления */}
      <div className={`p-6 rounded-lg ${cardBg}`}>
        <div className="flex justify-between items-center mb-6">
          <h3 className={`text-xl font-bold ${textPrimary}`}>{t.title}</h3>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <span>+</span> {t.addSite}
          </button>
        </div>

        {/* Список сайтов */}
        {sites.length === 0 ? (
          <div className={`text-center py-12 ${textSecondary}`}>
            <span className="text-6xl">🌐</span>
            <p className="mt-4 text-lg">{t.noSites}</p>
            <p className="mt-2">{t.noSitesDesc}</p>
            <button
              onClick={() => setShowAddModal(true)}
              className="mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              + {t.addSite}
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className={`border-b ${borderColor}`}>
                  <th className={`text-left py-3 px-4 ${textSecondary}`}>{t.name}</th>
                  <th className={`text-left py-3 px-4 ${textSecondary}`}>{t.url}</th>
                  <th className={`text-left py-3 px-4 ${textSecondary}`}>{t.lang}</th>
                  <th className={`text-left py-3 px-4 ${textSecondary}`}>{t.addedAt}</th>
                  <th className={`text-left py-3 px-4 ${textSecondary}`}>{t.actions}</th>
                </tr>
              </thead>
              <tbody>
                {sites.map((site, index) => (
                  <tr key={index} className={`border-b ${borderColor} hover:${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'}`}>
                    <td className={`py-3 px-4 ${textPrimary}`}>{site.name}</td>
                    <td className={`py-3 px-4 ${textSecondary}`}>
                      <a href={site.url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                        {site.url}
                      </a>
                    </td>
                    <td className={`py-3 px-4 ${textSecondary}`}>{site.language.toUpperCase()}</td>
                    <td className={`py-3 px-4 ${textSecondary}`}>
                      {new Date(site.added_at).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleAnalyzeSite(site)}
                          className="px-3 py-1 bg-purple-600 text-white text-sm rounded hover:bg-purple-700"
                        >
                          🔍 {t.analyze}
                        </button>
                        <button
                          onClick={() => handleCreateCampaign(site)}
                          className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                        >
                          🚀 {t.startCampaign}
                        </button>
                        <button
                          onClick={() => handleDeleteSite(site.url)}
                          className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Активные кампании */}
      <div className={`p-6 rounded-lg ${cardBg}`}>
        <h3 className={`text-xl font-bold mb-4 ${textPrimary}`}>{t.campaigns}</h3>
        
        {campaigns.length === 0 ? (
          <div className={`text-center py-8 ${textSecondary}`}>
            <span className="text-4xl">🎯</span>
            <p className="mt-2">{t.noCampaigns}</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {campaigns.map((campaign) => (
              <div key={campaign.id} className={`p-4 rounded-lg border ${borderColor} ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'}`}>
                <div className="flex justify-between items-start">
                  <div>
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full ${getStatusColor(campaign.status)}`}></div>
                      <span className={`font-medium ${textPrimary}`}>{campaign.domain}</span>
                      <span className={`text-sm px-2 py-1 rounded ${theme === 'dark' ? 'bg-gray-600' : 'bg-gray-200'} ${textSecondary}`}>
                        {getStatusText(campaign.status)}
                      </span>
                    </div>
                    <p className={`text-sm mt-1 ${textSecondary}`}>
                      ID: {campaign.id}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    {campaign.status === 'created' && (
                      <button
                        onClick={() => handleStartCampaign(campaign.id)}
                        className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                      >
                        ▶️ {t.start}
                      </button>
                    )}
                    {campaign.status === 'running' && (
                      <button
                        onClick={() => handlePauseCampaign(campaign.id)}
                        className="px-3 py-1 bg-yellow-600 text-white text-sm rounded hover:bg-yellow-700"
                      >
                        ⏸️ {t.pause}
                      </button>
                    )}
                    {campaign.status === 'paused' && (
                      <button
                        onClick={() => handleStartCampaign(campaign.id)}
                        className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                      >
                        ▶️ {t.resume}
                      </button>
                    )}
                  </div>
                </div>
                
                {/* Статистика кампании */}
                <div className="grid grid-cols-4 gap-4 mt-4">
                  <div className={`p-3 rounded ${theme === 'dark' ? 'bg-gray-600' : 'bg-white'}`}>
                    <p className={`text-xs ${textSecondary}`}>{t.contentGenerated}</p>
                    <p className={`text-lg font-bold ${textPrimary}`}>{campaign.stats.content_generated}</p>
                  </div>
                  <div className={`p-3 rounded ${theme === 'dark' ? 'bg-gray-600' : 'bg-white'}`}>
                    <p className={`text-xs ${textSecondary}`}>{t.contentPosted}</p>
                    <p className={`text-lg font-bold ${textPrimary}`}>{campaign.stats.content_posted}</p>
                  </div>
                  <div className={`p-3 rounded ${theme === 'dark' ? 'bg-gray-600' : 'bg-white'}`}>
                    <p className={`text-xs ${textSecondary}`}>{t.indexed}</p>
                    <p className={`text-lg font-bold ${textPrimary}`}>{campaign.stats.urls_indexed}</p>
                  </div>
                  <div className={`p-3 rounded ${theme === 'dark' ? 'bg-gray-600' : 'bg-white'}`}>
                    <p className={`text-xs ${textSecondary}`}>Clicks</p>
                    <p className={`text-lg font-bold ${textPrimary}`}>{campaign.stats.clicks}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Модальное окно добавления сайта */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className={`p-6 rounded-lg w-full max-w-md ${cardBg}`}>
            <h3 className={`text-xl font-bold mb-4 ${textPrimary}`}>{t.addSite}</h3>
            
            <div className="space-y-4">
              <div>
                <label className={`block text-sm mb-1 ${textSecondary}`}>{t.url} *</label>
                <input
                  type="text"
                  value={newSite.url}
                  onChange={(e) => setNewSite({ ...newSite, url: e.target.value })}
                  placeholder="example.com"
                  className={`w-full px-4 py-2 rounded-lg border ${inputBg} focus:outline-none focus:ring-2 focus:ring-blue-500`}
                />
              </div>
              
              <div>
                <label className={`block text-sm mb-1 ${textSecondary}`}>{t.name}</label>
                <input
                  type="text"
                  value={newSite.name}
                  onChange={(e) => setNewSite({ ...newSite, name: e.target.value })}
                  placeholder="My Website"
                  className={`w-full px-4 py-2 rounded-lg border ${inputBg} focus:outline-none focus:ring-2 focus:ring-blue-500`}
                />
              </div>
              
              <div>
                <label className={`block text-sm mb-1 ${textSecondary}`}>{t.lang}</label>
                <select
                  value={newSite.language}
                  onChange={(e) => setNewSite({ ...newSite, language: e.target.value })}
                  className={`w-full px-4 py-2 rounded-lg border ${inputBg} focus:outline-none focus:ring-2 focus:ring-blue-500`}
                >
                  {languages.map((lang) => (
                    <option key={lang.code} value={lang.code}>{lang.name}</option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowAddModal(false)}
                className={`flex-1 px-4 py-2 rounded-lg border ${borderColor} ${textPrimary} hover:bg-gray-700`}
              >
                {t.cancel}
              </button>
              <button
                onClick={handleAddSite}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                {t.add}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SitesManager;
