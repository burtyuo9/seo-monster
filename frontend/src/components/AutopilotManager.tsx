import React, { useState, useEffect, useCallback } from 'react';
import { useLanguage } from '../contexts/LanguageContext';

interface AutopilotStatus {
  status: string;
  current_task: {
    id: string;
    type: string;
    status: string;
  } | null;
  queue_length: number;
  completed_tasks: number;
  sites_count: number;
  settings: {
    auto_analyze: boolean;
    auto_generate: boolean;
    articles_per_day: number;
    external_ai_enabled: boolean;
  };
}

interface Site {
  url: string;
  name: string;
  language: string;
  added_at: string;
}

interface Article {
  id: string;
  topic: string;
  title: string;
  content?: string;
  content_type: string;
  language: string;
  word_count: number;
  generated_at: string;
}

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  details: Record<string, any>;
}

const API_BASE = 'http://localhost:8000';

const AutopilotManager: React.FC = () => {
  const { t } = useLanguage();
  
  const [status, setStatus] = useState<AutopilotStatus | null>(null);
  const [sites, setSites] = useState<Site[]>([]);
  const [articles, setArticles] = useState<Article[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'sites' | 'articles' | 'logs' | 'settings'>('dashboard');
  
  // Формы
  const [newSiteUrl, setNewSiteUrl] = useState('');
  const [newSiteName, setNewSiteName] = useState('');
  const [newSiteLanguage, setNewSiteLanguage] = useState('en');
  const [showAddSiteModal, setShowAddSiteModal] = useState(false);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [showArticleModal, setShowArticleModal] = useState(false);
  const [loadingArticle, setLoadingArticle] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [publishedUrl, setPublishedUrl] = useState<string | null>(null);
  const [publishedLandings, setPublishedLandings] = useState<any[]>([]);
  
  // Быстрая генерация
  const [quickGenTopic, setQuickGenTopic] = useState('');
  const [quickGenLanguage, setQuickGenLanguage] = useState('en');
  const [quickGenType, setQuickGenType] = useState('guide');
  const [generating, setGenerating] = useState(false);
  
  // Настройки
  const [settings, setSettings] = useState({
    auto_analyze: true,
    auto_generate: true,
    articles_per_day: 5,
    min_word_count: 800,
    max_word_count: 2000,
    external_ai_enabled: false
  });

  const loadData = useCallback(async () => {
    try {
      const [statusRes, sitesRes, articlesRes, logsRes] = await Promise.all([
        fetch(`${API_BASE}/api/autonomous/status`),
        fetch(`${API_BASE}/api/autonomous/sites`),
        fetch(`${API_BASE}/api/autonomous/articles`),
        fetch(`${API_BASE}/api/autonomous/logs?limit=50`)
      ]);
      
      if (statusRes.ok) {
        const data = await statusRes.json();
        setStatus(data);
        setSettings(prev => ({
          ...prev,
          ...data.settings
        }));
      }
      if (sitesRes.ok) {
        const data = await sitesRes.json();
        setSites(data.sites || []);
      }
      if (articlesRes.ok) {
        const data = await articlesRes.json();
        setArticles(data.articles || []);
      }
      if (logsRes.ok) {
        const data = await logsRes.json();
        setLogs(data.logs || []);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000); // Обновляем каждые 10 секунд
    return () => clearInterval(interval);
  }, [loadData]);

  const startAutopilot = async () => {
    try {
      await fetch(`${API_BASE}/api/autonomous/start`, { method: 'POST' });
      loadData();
    } catch (error) {
      console.error('Error starting autopilot:', error);
    }
  };

  const stopAutopilot = async () => {
    try {
      await fetch(`${API_BASE}/api/autonomous/stop`, { method: 'POST' });
      loadData();
    } catch (error) {
      console.error('Error stopping autopilot:', error);
    }
  };

  const pauseAutopilot = async () => {
    try {
      await fetch(`${API_BASE}/api/autonomous/pause`, { method: 'POST' });
      loadData();
    } catch (error) {
      console.error('Error pausing autopilot:', error);
    }
  };

  const resumeAutopilot = async () => {
    try {
      await fetch(`${API_BASE}/api/autonomous/resume`, { method: 'POST' });
      loadData();
    } catch (error) {
      console.error('Error resuming autopilot:', error);
    }
  };

  const addSite = async () => {
    if (!newSiteUrl) return;
    
    try {
      const res = await fetch(`${API_BASE}/api/autonomous/sites`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: newSiteUrl,
          name: newSiteName || newSiteUrl,
          language: newSiteLanguage
        })
      });
      
      if (res.ok) {
        setShowAddSiteModal(false);
        setNewSiteUrl('');
        setNewSiteName('');
        loadData();
      }
    } catch (error) {
      console.error('Error adding site:', error);
    }
  };

  const removeSite = async (url: string) => {
    try {
      await fetch(`${API_BASE}/api/autonomous/sites?url=${encodeURIComponent(url)}`, {
        method: 'DELETE'
      });
      loadData();
    } catch (error) {
      console.error('Error removing site:', error);
    }
  };

  const runNow = async (url: string, language: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/autonomous/run-now`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, language, articles_count: 3 })
      });
      
      if (res.ok) {
        loadData();
      }
    } catch (error) {
      console.error('Error running now:', error);
    }
  };

  const generateContent = async () => {
    if (!quickGenTopic) return;
    
    setGenerating(true);
    try {
      const res = await fetch(`${API_BASE}/api/autonomous/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: quickGenTopic,
          language: quickGenLanguage,
          content_type: quickGenType,
          word_count: 1000
        })
      });
      
      if (res.ok) {
        setQuickGenTopic('');
        loadData();
      }
    } catch (error) {
      console.error('Error generating content:', error);
    } finally {
      setGenerating(false);
    }
  };

  const updateSettings = async () => {
    try {
      await fetch(`${API_BASE}/api/autonomous/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });
      loadData();
    } catch (error) {
      console.error('Error updating settings:', error);
    }
  };

  const viewArticle = async (article: Article) => {
    setLoadingArticle(true);
    setShowArticleModal(true);
    try {
      const res = await fetch(`${API_BASE}/api/autonomous/articles/${article.id}`);
      if (res.ok) {
        const fullArticle = await res.json();
        setSelectedArticle(fullArticle);
      } else {
        // Если API не вернул контент, используем заглушку
        setSelectedArticle({
          ...article,
          content: `# ${article.title}\n\n${t('content_loading_failed')}\n\nТема: ${article.topic}\nТип: ${article.content_type}\nСлов: ${article.word_count}`
        });
      }
    } catch (error) {
      console.error('Error loading article:', error);
      setSelectedArticle({
        ...article,
        content: `# ${article.title}\n\nОшибка загрузки контента.\n\nТема: ${article.topic}\nТип: ${article.content_type}\nСлов: ${article.word_count}`
      });
    } finally {
      setLoadingArticle(false);
    }
  };

  const copyArticleContent = () => {
    if (selectedArticle?.content) {
      navigator.clipboard.writeText(selectedArticle.content);
    }
  };

  const downloadArticle = () => {
    if (selectedArticle) {
      const blob = new Blob([selectedArticle.content || ''], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedArticle.title.replace(/[^a-zA-Z0-9]/g, '_')}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const publishToManus = async () => {
    if (!selectedArticle) return;
    
    setPublishing(true);
    setPublishedUrl(null);
    try {
      const res = await fetch(`${API_BASE}/api/publishing/publish`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: selectedArticle.title,
          content: selectedArticle.content || '',
          language: selectedArticle.language,
          style: 'glassmorphism_dark',
          keywords: [selectedArticle.topic],
          author: 'SEO Monster'
        })
      });
      
      if (res.ok) {
        const data = await res.json();
        setPublishedUrl(data.url);
        // Refresh landings list
        loadPublishedLandings();
      } else {
        console.error('Failed to publish');
      }
    } catch (error) {
      console.error('Error publishing to MANUS:', error);
    } finally {
      setPublishing(false);
    }
  };

  const loadPublishedLandings = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/publishing/list`);
      if (res.ok) {
        const data = await res.json();
        setPublishedLandings(data);
      }
    } catch (error) {
      console.error('Error loading published landings:', error);
    }
  };

  const previewLanding = (slug: string) => {
    window.open(`${API_BASE}/api/publishing/preview/${slug}`, '_blank');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'paused': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'stopped': return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
      case 'error': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'running': return '🚀 ' + t('running');
      case 'paused': return '⏸️ ' + t('paused');
      case 'stopped': return '⏹️ ' + t('stopped');
      case 'error': return '❌ ' + t('error');
      default: return status;
    }
  };

  const getLogLevelColor = (level: string) => {
    switch (level) {
      case 'error': return 'bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-300';
      case 'success': return 'bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300';
      case 'warning': return 'bg-yellow-50 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300';
      default: return 'bg-gray-50 text-gray-700 dark:bg-gray-800 dark:text-gray-300';
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
      {/* Заголовок */}
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">🤖 {t('autopilot')}</h2>
          <p className="text-gray-600 dark:text-gray-400 mt-1">{t('autopilot_description')}</p>
        </div>
        <div className="flex items-center gap-2">
          {status?.status === 'running' ? (
            <>
              <button
                onClick={pauseAutopilot}
                className="bg-yellow-500 text-white px-4 py-2 rounded-lg hover:bg-yellow-600 flex items-center gap-2"
              >
                ⏸️ {t('pause')}
              </button>
              <button
                onClick={stopAutopilot}
                className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 flex items-center gap-2"
              >
                ⏹️ {t('stop')}
              </button>
            </>
          ) : status?.status === 'paused' ? (
            <>
              <button
                onClick={resumeAutopilot}
                className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 flex items-center gap-2"
              >
                ▶️ {t('resume')}
              </button>
              <button
                onClick={stopAutopilot}
                className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 flex items-center gap-2"
              >
                ⏹️ {t('stop')}
              </button>
            </>
          ) : (
            <button
              onClick={startAutopilot}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center gap-2"
            >
              🚀 {t('start_autopilot')}
            </button>
          )}
        </div>
      </div>

      {/* Статус */}
      {status && (
        <div className="grid grid-cols-5 gap-4">
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border-l-4 border-blue-500">
            <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(status.status)}`}>
              {getStatusText(status.status)}
            </div>
            <div className="text-gray-600 dark:text-gray-400 text-sm mt-2">{t('status')}</div>
          </div>
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border-l-4 border-green-500">
            <div className="text-2xl font-bold text-green-600">{status.sites_count}</div>
            <div className="text-gray-600 dark:text-gray-400 text-sm">{t('sites')}</div>
          </div>
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border-l-4 border-purple-500">
            <div className="text-2xl font-bold text-purple-600">{status.queue_length}</div>
            <div className="text-gray-600 dark:text-gray-400 text-sm">{t('tasks_in_queue')}</div>
          </div>
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border-l-4 border-orange-500">
            <div className="text-2xl font-bold text-orange-600">{status.completed_tasks}</div>
            <div className="text-gray-600 dark:text-gray-400 text-sm">{t('completed_tasks')}</div>
          </div>
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border-l-4 border-cyan-500">
            <div className="text-2xl font-bold text-cyan-600">{articles.length}</div>
            <div className="text-gray-600 dark:text-gray-400 text-sm">{t('articles_generated')}</div>
          </div>
        </div>
      )}

      {/* Текущая задача */}
      {status?.current_task && (
        <div className="bg-blue-50 dark:bg-blue-900/30 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
          <div className="flex items-center gap-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            <span className="font-medium text-blue-800 dark:text-blue-200">
              {t('current_task')}: {status.current_task.type}
            </span>
            <span className="text-blue-600 dark:text-blue-300">({status.current_task.status})</span>
          </div>
        </div>
      )}

      {/* Табы */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="flex gap-4">
          {(['dashboard', 'sites', 'articles', 'logs', 'settings'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-2 px-4 border-b-2 font-medium text-sm ${
                activeTab === tab
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              {tab === 'dashboard' && '📊 '}
              {tab === 'sites' && '🌐 '}
              {tab === 'articles' && '📝 '}
              {tab === 'logs' && '📋 '}
              {tab === 'settings' && '⚙️ '}
              {t(tab)}
            </button>
          ))}
        </nav>
      </div>

      {/* Контент табов */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        {/* Dashboard */}
        {activeTab === 'dashboard' && (
          <div className="p-6 space-y-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">🚀 {t('quick_generate')}</h3>
            
            <div className="grid grid-cols-4 gap-4">
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {t('topic')}
                </label>
                <input
                  type="text"
                  value={quickGenTopic}
                  onChange={(e) => setQuickGenTopic(e.target.value)}
                  placeholder={t('enter_topic')}
                  className="w-full border dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {t('language')}
                </label>
                <select
                  value={quickGenLanguage}
                  onChange={(e) => setQuickGenLanguage(e.target.value)}
                  className="w-full border dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="en">🇺🇸 English</option>
                  <option value="ru">🇷🇺 Русский</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {t('content_type')}
                </label>
                <select
                  value={quickGenType}
                  onChange={(e) => setQuickGenType(e.target.value)}
                  className="w-full border dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="guide">{t('guide')}</option>
                  <option value="how_to">{t('how_to')}</option>
                  <option value="listicle">{t('listicle')}</option>
                  <option value="comparison">{t('comparison')}</option>
                </select>
              </div>
            </div>
            
            <button
              onClick={generateContent}
              disabled={!quickGenTopic || generating}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              {generating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  {t('generating')}...
                </>
              ) : (
                <>✨ {t('generate_article')}</>
              )}
            </button>

            {/* Последние статьи */}
            <div className="mt-8">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">📝 {t('recent_articles')}</h3>
              <div className="space-y-2">
                {articles.slice(0, 5).map((article) => (
                  <div 
                    key={article.id} 
                    onClick={() => viewArticle(article)}
                    className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg flex justify-between items-center cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                  >
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">{article.title}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {article.content_type} • {article.word_count} {t('words')} • {article.language.toUpperCase()}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-400">
                        {new Date(article.generated_at).toLocaleString()}
                      </span>
                      <span className="text-blue-500">👁️</span>
                    </div>
                  </div>
                ))}
                {articles.length === 0 && (
                  <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                    {t('no_articles_yet')}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Sites */}
        {activeTab === 'sites' && (
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">🌐 {t('monitored_sites')}</h3>
              <button
                onClick={() => setShowAddSiteModal(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
              >
                ➕ {t('add_site')}
              </button>
            </div>
            
            <div className="space-y-3">
              {sites.map((site) => (
                <div key={site.url} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg flex justify-between items-center">
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">{site.name}</div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">{site.url}</div>
                    <div className="text-xs text-gray-400 mt-1">
                      {site.language.toUpperCase()} • {t('added')}: {new Date(site.added_at).toLocaleDateString()}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => runNow(site.url, site.language)}
                      className="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600 text-sm"
                    >
                      ▶️ {t('run_now')}
                    </button>
                    <button
                      onClick={() => removeSite(site.url)}
                      className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600 text-sm"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              ))}
              {sites.length === 0 && (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  <div className="text-4xl mb-2">🌐</div>
                  <p>{t('no_sites_added')}</p>
                  <p className="text-sm">{t('add_site_to_start')}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Articles */}
        {activeTab === 'articles' && (
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">📝 {t('generated_articles')}</h3>
            
            <div className="space-y-3">
              {articles.map((article) => (
                <div 
                  key={article.id} 
                  className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                  onClick={() => viewArticle(article)}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">{article.title}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        {t('topic')}: {article.topic}
                      </div>
                    </div>
                    <div className="flex gap-2 items-center">
                      <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs">
                        {article.content_type}
                      </span>
                      <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-xs">
                        {article.language.toUpperCase()}
                      </span>
                      <span className="text-blue-500 text-lg">👁️</span>
                    </div>
                  </div>
                  <div className="flex gap-4 mt-2 text-sm text-gray-500 dark:text-gray-400">
                    <span>📊 {article.word_count} {t('words')}</span>
                    <span>📅 {new Date(article.generated_at).toLocaleString()}</span>
                  </div>
                </div>
              ))}
              {articles.length === 0 && (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  <div className="text-4xl mb-2">📝</div>
                  <p>{t('no_articles_yet')}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Logs */}
        {activeTab === 'logs' && (
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">📋 {t('autopilot_logs')}</h3>
            
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {logs.slice().reverse().map((log, idx) => (
                <div key={idx} className={`p-3 rounded-lg text-sm ${getLogLevelColor(log.level)}`}>
                  <div className="flex justify-between items-start">
                    <span className="font-medium">{log.message}</span>
                    <span className="text-xs opacity-70">
                      {new Date(log.timestamp).toLocaleString()}
                    </span>
                  </div>
                  {Object.keys(log.details).length > 0 && (
                    <div className="mt-1 text-xs opacity-70">
                      {JSON.stringify(log.details)}
                    </div>
                  )}
                </div>
              ))}
              {logs.length === 0 && (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  <div className="text-4xl mb-2">📋</div>
                  <p>{t('no_logs_yet')}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Settings */}
        {activeTab === 'settings' && (
          <div className="p-6 space-y-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">⚙️ {t('autopilot_settings')}</h3>
            
            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.auto_analyze}
                    onChange={(e) => setSettings({ ...settings, auto_analyze: e.target.checked })}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <span className="text-gray-700 dark:text-gray-300">{t('auto_analyze_sites')}</span>
                </label>
              </div>
              
              <div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.auto_generate}
                    onChange={(e) => setSettings({ ...settings, auto_generate: e.target.checked })}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <span className="text-gray-700 dark:text-gray-300">{t('auto_generate_content')}</span>
                </label>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {t('articles_per_day')}
                </label>
                <input
                  type="number"
                  value={settings.articles_per_day}
                  onChange={(e) => setSettings({ ...settings, articles_per_day: parseInt(e.target.value) })}
                  min={1}
                  max={20}
                  className="w-full border dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {t('min_word_count')}
                </label>
                <input
                  type="number"
                  value={settings.min_word_count}
                  onChange={(e) => setSettings({ ...settings, min_word_count: parseInt(e.target.value) })}
                  min={300}
                  max={5000}
                  className="w-full border dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>
            
            <div className="bg-yellow-50 dark:bg-yellow-900/30 p-4 rounded-lg border border-yellow-200 dark:border-yellow-800">
              <div className="flex items-start gap-2">
                <span className="text-yellow-600">⚠️</span>
                <div>
                  <div className="font-medium text-yellow-800 dark:text-yellow-200">{t('external_ai_optional')}</div>
                  <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                    {t('external_ai_description')}
                  </p>
                  <label className="flex items-center gap-2 mt-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.external_ai_enabled}
                      onChange={(e) => setSettings({ ...settings, external_ai_enabled: e.target.checked })}
                      className="w-4 h-4 text-yellow-600 rounded"
                    />
                    <span className="text-yellow-800 dark:text-yellow-200">{t('enable_external_ai')}</span>
                  </label>
                </div>
              </div>
            </div>
            
            <button
              onClick={updateSettings}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
            >
              💾 {t('save_settings')}
            </button>
          </div>
        )}
      </div>

      {/* Модальное окно добавления сайта */}
      {showAddSiteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md">
            <div className="p-4 border-b dark:border-gray-700 flex justify-between items-center">
              <h3 className="font-semibold text-gray-900 dark:text-white">{t('add_site')}</h3>
              <button 
                onClick={() => setShowAddSiteModal(false)} 
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                ✕
              </button>
            </div>
            <div className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  URL *
                </label>
                <input
                  type="text"
                  value={newSiteUrl}
                  onChange={(e) => setNewSiteUrl(e.target.value)}
                  placeholder="https://example.com"
                  className="w-full border dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {t('name')}
                </label>
                <input
                  type="text"
                  value={newSiteName}
                  onChange={(e) => setNewSiteName(e.target.value)}
                  placeholder={t('site_name')}
                  className="w-full border dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {t('language')}
                </label>
                <select
                  value={newSiteLanguage}
                  onChange={(e) => setNewSiteLanguage(e.target.value)}
                  className="w-full border dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="en">🇺🇸 English</option>
                  <option value="ru">🇷🇺 Русский</option>
                </select>
              </div>
            </div>
            <div className="p-4 border-t dark:border-gray-700 flex justify-end gap-2">
              <button
                onClick={() => setShowAddSiteModal(false)}
                className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                {t('cancel')}
              </button>
              <button
                onClick={addSite}
                disabled={!newSiteUrl}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {t('add')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Модальное окно просмотра статьи */}
      {showArticleModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
            <div className="p-4 border-b dark:border-gray-700 flex justify-between items-center">
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white text-lg">
                  {selectedArticle?.title || t('loading')}
                </h3>
                {selectedArticle && (
                  <div className="flex gap-2 mt-1">
                    <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs">
                      {selectedArticle.content_type}
                    </span>
                    <span className="px-2 py-0.5 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-xs">
                      {selectedArticle.language.toUpperCase()}
                    </span>
                    <span className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded text-xs">
                      {selectedArticle.word_count} {t('words')}
                    </span>
                  </div>
                )}
              </div>
              <button 
                onClick={() => {
                  setShowArticleModal(false);
                  setSelectedArticle(null);
                }} 
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-2xl"
              >
                ✕
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6">
              {loadingArticle ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-3 text-gray-500 dark:text-gray-400">{t('loading')}...</span>
                </div>
              ) : selectedArticle?.content ? (
                <div className="prose dark:prose-invert max-w-none">
                  <pre className="whitespace-pre-wrap font-sans text-gray-800 dark:text-gray-200 text-base leading-relaxed">
                    {selectedArticle.content}
                  </pre>
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                  <div className="text-4xl mb-2">📝</div>
                  <p>{t('no_content_available')}</p>
                </div>
              )}
            </div>
            
            {/* Отображение опубликованной ссылки */}
            {publishedUrl && (
              <div className="mx-6 mb-4 p-4 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-green-800 dark:text-green-200 font-medium">✅ Статья опубликована!</p>
                    <a 
                      href={publishedUrl} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 dark:text-blue-400 hover:underline text-sm"
                    >
                      {publishedUrl}
                    </a>
                  </div>
                  <button
                    onClick={() => navigator.clipboard.writeText(publishedUrl)}
                    className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
                  >
                    📋 Копировать
                  </button>
                </div>
              </div>
            )}
            
            <div className="p-4 border-t dark:border-gray-700 flex justify-between items-center">
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {selectedArticle && (
                  <>
                    {t('topic')}: {selectedArticle.topic} • 
                    {new Date(selectedArticle.generated_at).toLocaleString()}
                  </>
                )}
              </div>             <div className="flex gap-2">
                <button
                  onClick={copyArticleContent}
                  className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 flex items-center gap-2"
                >
                  📋 {t('copy')}
                </button>
                <button
                  onClick={downloadArticle}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
                >
                  ⬇️ {t('download')}
                </button>
                <button
                  onClick={publishToManus}
                  disabled={publishing || !selectedArticle?.content}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {publishing ? (
                    <>
                      <span className="animate-spin">⏳</span> Публикация...
                    </>
                  ) : (
                    <>
                      🚀 Опубликовать на MANUS.im
                    </>
                  )}
                </button>
                <button
                  onClick={() => {
                    setShowArticleModal(false);
                    setSelectedArticle(null);
                    setPublishedUrl(null);
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  {t('close')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AutopilotManager;
