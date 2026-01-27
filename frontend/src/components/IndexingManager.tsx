import React, { useState, useEffect } from 'react'
import { 
  Search, 
  Globe, 
  Send, 
  RefreshCw, 
  CheckCircle, 
  XCircle, 
  Clock,
  FileText,
  Download,
  Upload,
  Trash2,
  Play,
  List,
  BarChart3,
  AlertCircle
} from 'lucide-react'

interface IndexingStats {
  total_requests: number
  submitted: number
  indexed: number
  not_indexed: number
  errors: number
  queue_pending: number
  queue_total: number
  unique_domains: number
}

interface HistoryItem {
  url: string
  status: string
  message: string
  timestamp: string
  source: string
}

interface QueueItem {
  url: string
  added_at: string
  status: string
  processed_at?: string
}

const API_BASE = 'http://localhost:8000/api/indexing'

export default function IndexingManager() {
  const [activeTab, setActiveTab] = useState<'submit' | 'check' | 'sitemap' | 'history' | 'queue'>('submit')
  const [stats, setStats] = useState<IndexingStats | null>(null)
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [queue, setQueue] = useState<QueueItem[]>([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{type: 'success' | 'error', text: string} | null>(null)
  
  // Form states
  const [submitUrl, setSubmitUrl] = useState('')
  const [bulkUrls, setBulkUrls] = useState('')
  const [checkUrl, setCheckUrl] = useState('')
  const [sitemapBaseUrl, setSitemapBaseUrl] = useState('')
  const [sitemapUrls, setSitemapUrls] = useState('')
  const [crawlUrl, setCrawlUrl] = useState('')
  const [crawlMaxPages, setCrawlMaxPages] = useState(100)
  const [generatedSitemap, setGeneratedSitemap] = useState('')
  const [crawledUrls, setCrawledUrls] = useState<string[]>([])

  // Load data
  useEffect(() => {
    loadStats()
    loadHistory()
    loadQueue()
  }, [])

  const loadStats = async () => {
    try {
      const res = await fetch(`${API_BASE}/stats`)
      if (res.ok) {
        setStats(await res.json())
      }
    } catch (e) {
      console.error('Error loading stats:', e)
    }
  }

  const loadHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/history?limit=50`)
      if (res.ok) {
        setHistory(await res.json())
      }
    } catch (e) {
      console.error('Error loading history:', e)
    }
  }

  const loadQueue = async () => {
    try {
      const res = await fetch(`${API_BASE}/queue`)
      if (res.ok) {
        setQueue(await res.json())
      }
    } catch (e) {
      console.error('Error loading queue:', e)
    }
  }

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text })
    setTimeout(() => setMessage(null), 5000)
  }

  // Submit single URL
  const handleSubmitUrl = async () => {
    if (!submitUrl) return
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: submitUrl })
      })
      const data = await res.json()
      if (res.ok) {
        showMessage('success', `URL отправлен: ${data.message}`)
        setSubmitUrl('')
        loadStats()
        loadHistory()
      } else {
        showMessage('error', data.detail || 'Ошибка отправки')
      }
    } catch (e) {
      showMessage('error', 'Ошибка соединения')
    }
    setLoading(false)
  }

  // Submit bulk URLs
  const handleSubmitBulk = async () => {
    const urls = bulkUrls.split('\n').map(u => u.trim()).filter(u => u)
    if (urls.length === 0) return
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/submit-bulk`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ urls })
      })
      const data = await res.json()
      if (res.ok) {
        showMessage('success', data.message)
        setBulkUrls('')
        loadStats()
        loadQueue()
      } else {
        showMessage('error', data.detail || 'Ошибка отправки')
      }
    } catch (e) {
      showMessage('error', 'Ошибка соединения')
    }
    setLoading(false)
  }

  // Check indexing status
  const handleCheckUrl = async () => {
    if (!checkUrl) return
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: checkUrl })
      })
      const data = await res.json()
      if (res.ok) {
        const statusText = data.status === 'indexed' ? '✅ Проиндексирован' : '❌ Не проиндексирован'
        showMessage(data.status === 'indexed' ? 'success' : 'error', `${statusText}: ${data.message}`)
        loadHistory()
      } else {
        showMessage('error', data.detail || 'Ошибка проверки')
      }
    } catch (e) {
      showMessage('error', 'Ошибка соединения')
    }
    setLoading(false)
  }

  // Generate sitemap
  const handleGenerateSitemap = async () => {
    const urls = sitemapUrls.split('\n').map(u => u.trim()).filter(u => u)
    if (!sitemapBaseUrl || urls.length === 0) return
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/generate-sitemap`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ base_url: sitemapBaseUrl, urls })
      })
      const data = await res.json()
      if (res.ok) {
        setGeneratedSitemap(data.sitemap_xml)
        showMessage('success', `Sitemap сгенерирован для ${data.urls_count} URL`)
      } else {
        showMessage('error', data.detail || 'Ошибка генерации')
      }
    } catch (e) {
      showMessage('error', 'Ошибка соединения')
    }
    setLoading(false)
  }

  // Crawl site
  const handleCrawlSite = async () => {
    if (!crawlUrl) return
    setLoading(true)
    setCrawledUrls([])
    try {
      const res = await fetch(`${API_BASE}/crawl-site`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ base_url: crawlUrl, max_pages: crawlMaxPages })
      })
      const data = await res.json()
      if (res.ok) {
        setCrawledUrls(data.urls)
        showMessage('success', `Найдено ${data.urls_found} URL`)
      } else {
        showMessage('error', data.detail || 'Ошибка сканирования')
      }
    } catch (e) {
      showMessage('error', 'Ошибка соединения')
    }
    setLoading(false)
  }

  // Ping sitemap
  const handlePingSitemap = async (sitemapUrl: string) => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/ping-sitemap`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sitemap_url: sitemapUrl })
      })
      const data = await res.json()
      if (res.ok) {
        showMessage('success', `Ping отправлен: ${data.success_count} успешно, ${data.error_count} ошибок`)
        loadHistory()
      } else {
        showMessage('error', data.detail || 'Ошибка ping')
      }
    } catch (e) {
      showMessage('error', 'Ошибка соединения')
    }
    setLoading(false)
  }

  // Process queue
  const handleProcessQueue = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/process-queue?batch_size=10`, {
        method: 'POST'
      })
      const data = await res.json()
      if (res.ok) {
        showMessage('success', `Обработано ${data.processed} URL`)
        loadStats()
        loadQueue()
        loadHistory()
      } else {
        showMessage('error', data.detail || 'Ошибка обработки')
      }
    } catch (e) {
      showMessage('error', 'Ошибка соединения')
    }
    setLoading(false)
  }

  // Clear queue
  const handleClearQueue = async () => {
    if (!confirm('Очистить очередь индексации?')) return
    try {
      const res = await fetch(`${API_BASE}/queue/clear`, { method: 'DELETE' })
      const data = await res.json()
      if (res.ok) {
        showMessage('success', data.message)
        loadQueue()
        loadStats()
      }
    } catch (e) {
      showMessage('error', 'Ошибка очистки')
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'indexed':
      case 'submitted':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'not_indexed':
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />
      default:
        return <AlertCircle className="w-4 h-4 text-gray-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      indexed: 'bg-green-100 text-green-800',
      submitted: 'bg-blue-100 text-blue-800',
      not_indexed: 'bg-red-100 text-red-800',
      error: 'bg-red-100 text-red-800',
      pending: 'bg-yellow-100 text-yellow-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Индексация сайтов</h1>
          <p className="text-gray-500">Управление индексацией в поисковых системах</p>
        </div>
        <button
          onClick={() => { loadStats(); loadHistory(); loadQueue() }}
          className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Обновить
        </button>
      </div>

      {/* Message */}
      {message && (
        <div className={`p-4 rounded-lg ${message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
          {message.text}
        </div>
      )}

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-gray-500 text-sm">Всего запросов</span>
              <BarChart3 className="w-5 h-5 text-blue-500" />
            </div>
            <p className="text-2xl font-bold mt-1">{stats.total_requests}</p>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-gray-500 text-sm">Отправлено</span>
              <Send className="w-5 h-5 text-green-500" />
            </div>
            <p className="text-2xl font-bold mt-1 text-green-600">{stats.submitted}</p>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-gray-500 text-sm">В очереди</span>
              <Clock className="w-5 h-5 text-yellow-500" />
            </div>
            <p className="text-2xl font-bold mt-1 text-yellow-600">{stats.queue_pending}</p>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-gray-500 text-sm">Уникальных доменов</span>
              <Globe className="w-5 h-5 text-purple-500" />
            </div>
            <p className="text-2xl font-bold mt-1 text-purple-600">{stats.unique_domains}</p>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="flex border-b">
          {[
            { id: 'submit', label: 'Отправить на индексацию', icon: Send },
            { id: 'check', label: 'Проверить индексацию', icon: Search },
            { id: 'sitemap', label: 'Sitemap', icon: FileText },
            { id: 'history', label: 'История', icon: List },
            { id: 'queue', label: 'Очередь', icon: Clock }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === tab.id 
                  ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        <div className="p-6">
          {/* Submit Tab */}
          {activeTab === 'submit' && (
            <div className="space-y-6">
              {/* Single URL */}
              <div>
                <h3 className="font-semibold mb-3">Отправить один URL</h3>
                <div className="flex gap-2">
                  <input
                    type="url"
                    value={submitUrl}
                    onChange={e => setSubmitUrl(e.target.value)}
                    placeholder="https://example.com/page"
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button
                    onClick={handleSubmitUrl}
                    disabled={loading || !submitUrl}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                  >
                    <Send className="w-4 h-4" />
                    Отправить
                  </button>
                </div>
              </div>

              {/* Bulk URLs */}
              <div>
                <h3 className="font-semibold mb-3">Массовая отправка</h3>
                <textarea
                  value={bulkUrls}
                  onChange={e => setBulkUrls(e.target.value)}
                  placeholder="Введите URL (по одному на строку)&#10;https://example.com/page1&#10;https://example.com/page2"
                  rows={6}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <div className="flex justify-between items-center mt-2">
                  <span className="text-sm text-gray-500">
                    {bulkUrls.split('\n').filter(u => u.trim()).length} URL
                  </span>
                  <button
                    onClick={handleSubmitBulk}
                    disabled={loading || !bulkUrls.trim()}
                    className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
                  >
                    <Upload className="w-4 h-4" />
                    Добавить в очередь
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Check Tab */}
          {activeTab === 'check' && (
            <div className="space-y-6">
              <div>
                <h3 className="font-semibold mb-3">Проверить статус индексации</h3>
                <div className="flex gap-2">
                  <input
                    type="url"
                    value={checkUrl}
                    onChange={e => setCheckUrl(e.target.value)}
                    placeholder="https://example.com/page"
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button
                    onClick={handleCheckUrl}
                    disabled={loading || !checkUrl}
                    className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
                  >
                    <Search className="w-4 h-4" />
                    Проверить
                  </button>
                </div>
                <p className="text-sm text-gray-500 mt-2">
                  Проверяет наличие URL в индексе Google через поиск site:
                </p>
              </div>
            </div>
          )}

          {/* Sitemap Tab */}
          {activeTab === 'sitemap' && (
            <div className="space-y-6">
              {/* Crawl site */}
              <div>
                <h3 className="font-semibold mb-3">Сканировать сайт</h3>
                <div className="flex gap-2">
                  <input
                    type="url"
                    value={crawlUrl}
                    onChange={e => setCrawlUrl(e.target.value)}
                    placeholder="https://example.com"
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <input
                    type="number"
                    value={crawlMaxPages}
                    onChange={e => setCrawlMaxPages(parseInt(e.target.value) || 100)}
                    placeholder="Max pages"
                    className="w-24 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button
                    onClick={handleCrawlSite}
                    disabled={loading || !crawlUrl}
                    className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                  >
                    <Globe className="w-4 h-4" />
                    Сканировать
                  </button>
                </div>
              </div>

              {/* Crawled URLs */}
              {crawledUrls.length > 0 && (
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <h4 className="font-medium">Найденные URL ({crawledUrls.length})</h4>
                    <button
                      onClick={() => {
                        setSitemapBaseUrl(crawlUrl)
                        setSitemapUrls(crawledUrls.join('\n'))
                      }}
                      className="text-sm text-blue-600 hover:underline"
                    >
                      Использовать для sitemap
                    </button>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3 max-h-40 overflow-y-auto text-sm">
                    {crawledUrls.map((url, i) => (
                      <div key={i} className="truncate">{url}</div>
                    ))}
                  </div>
                </div>
              )}

              {/* Generate Sitemap */}
              <div className="border-t pt-6">
                <h3 className="font-semibold mb-3">Генерация Sitemap</h3>
                <div className="space-y-3">
                  <input
                    type="url"
                    value={sitemapBaseUrl}
                    onChange={e => setSitemapBaseUrl(e.target.value)}
                    placeholder="Базовый URL (https://example.com)"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <textarea
                    value={sitemapUrls}
                    onChange={e => setSitemapUrls(e.target.value)}
                    placeholder="URL для включения в sitemap (по одному на строку)"
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button
                    onClick={handleGenerateSitemap}
                    disabled={loading || !sitemapBaseUrl || !sitemapUrls.trim()}
                    className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
                  >
                    <FileText className="w-4 h-4" />
                    Сгенерировать Sitemap
                  </button>
                </div>
              </div>

              {/* Generated Sitemap */}
              {generatedSitemap && (
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <h4 className="font-medium">Сгенерированный Sitemap</h4>
                    <div className="flex gap-2">
                      <button
                        onClick={() => {
                          const blob = new Blob([generatedSitemap], { type: 'application/xml' })
                          const url = URL.createObjectURL(blob)
                          const a = document.createElement('a')
                          a.href = url
                          a.download = 'sitemap.xml'
                          a.click()
                        }}
                        className="text-sm text-blue-600 hover:underline flex items-center gap-1"
                      >
                        <Download className="w-4 h-4" />
                        Скачать
                      </button>
                      <button
                        onClick={() => navigator.clipboard.writeText(generatedSitemap)}
                        className="text-sm text-gray-600 hover:underline"
                      >
                        Копировать
                      </button>
                    </div>
                  </div>
                  <pre className="bg-gray-900 text-green-400 rounded-lg p-4 text-xs overflow-x-auto max-h-60">
                    {generatedSitemap}
                  </pre>
                </div>
              )}
            </div>
          )}

          {/* History Tab */}
          {activeTab === 'history' && (
            <div>
              {history.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <List className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>История пуста</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="text-left text-sm text-gray-500 border-b">
                        <th className="pb-3">URL</th>
                        <th className="pb-3">Статус</th>
                        <th className="pb-3">Источник</th>
                        <th className="pb-3">Время</th>
                      </tr>
                    </thead>
                    <tbody>
                      {history.map((item, i) => (
                        <tr key={i} className="border-b last:border-0">
                          <td className="py-3">
                            <div className="flex items-center gap-2">
                              {getStatusIcon(item.status)}
                              <span className="truncate max-w-xs" title={item.url}>{item.url}</span>
                            </div>
                          </td>
                          <td className="py-3">
                            <span className={`px-2 py-1 rounded-full text-xs ${getStatusBadge(item.status)}`}>
                              {item.status}
                            </span>
                          </td>
                          <td className="py-3 text-sm text-gray-500">{item.source}</td>
                          <td className="py-3 text-sm text-gray-500">
                            {new Date(item.timestamp).toLocaleString('ru-RU')}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Queue Tab */}
          {activeTab === 'queue' && (
            <div>
              <div className="flex justify-between items-center mb-4">
                <span className="text-sm text-gray-500">
                  {queue.filter(q => q.status === 'pending').length} ожидают обработки
                </span>
                <div className="flex gap-2">
                  <button
                    onClick={handleProcessQueue}
                    disabled={loading || queue.filter(q => q.status === 'pending').length === 0}
                    className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm transition-colors"
                  >
                    <Play className="w-4 h-4" />
                    Обработать
                  </button>
                  <button
                    onClick={handleClearQueue}
                    disabled={queue.length === 0}
                    className="flex items-center gap-2 px-3 py-1.5 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 text-sm transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                    Очистить
                  </button>
                </div>
              </div>

              {queue.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Clock className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Очередь пуста</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {queue.map((item, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        {getStatusIcon(item.status)}
                        <span className="truncate max-w-md" title={item.url}>{item.url}</span>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs ${getStatusBadge(item.status)}`}>
                        {item.status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
