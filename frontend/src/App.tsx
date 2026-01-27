import { useState, useEffect } from 'react'
import { 
  Globe, 
  FileText, 
  Send, 
  Settings, 
  BarChart3, 
  Plus,
  Search,
  Trash2,
  RefreshCw,
  Upload,
  Download,
  CheckCircle,
  XCircle,
  Clock,
  Zap,
  Target,
  TrendingUp,
  Activity,
  Database,
  Bot,
  Users
} from 'lucide-react'
import SessionManager from './components/SessionManager'
import IndexingManager from './components/IndexingManager'
import AutopilotManager from './components/AutopilotManager'
import AIChat from './components/AIChat'
import TelegramSettings from './components/TelegramSettings'
import HostingManager from './components/HostingManager'
import TDSManager from './components/TDSManager'
import axios from 'axios'
import './index.css'

// API base URL
const API_URL = 'http://localhost:8000/api'

// Types
interface TargetSite {
  id: number
  name: string
  url: string
  description?: string
  keywords: string[]
  niche?: string
  target_geos: string[]
  target_languages: string[]
  is_active: boolean
  created_at: string
  last_analyzed_at?: string
}

interface Platform {
  id: number
  name: string
  url: string
  platform_type?: string
  login?: string
  has_captcha: boolean
  is_active: boolean
  is_verified: boolean
  posts_count: number
  successful_posts: number
}

interface ContentItem {
  id: number
  title?: string
  content: string
  content_type: string
  language: string
  is_published: boolean
  created_at: string
}

interface Task {
  id: number
  task_type: string
  status: string
  progress: number
  created_at: string
}

interface DashboardStats {
  total_sites: number
  total_platforms: number
  total_content: number
  published_content: number
  pending_tasks: number
  running_tasks: number
  success_rate: number
}

// Sidebar Navigation
const navigation = [
  { name: 'Дашборд', icon: BarChart3, id: 'dashboard' },
  { name: 'AI Чат', icon: Bot, id: 'chat' },
  { name: 'Автопилот', icon: Zap, id: 'autopilot' },
  { name: 'Сайты', icon: Globe, id: 'sites' },
  { name: 'Площадки', icon: Target, id: 'platforms' },
  { name: 'Контент', icon: FileText, id: 'content' },
  { name: 'Аккаунты', icon: Users, id: 'sessions' },
  { name: 'Индексация', icon: Search, id: 'indexing' },
  { name: 'Задачи', icon: Activity, id: 'tasks' },
  { name: 'Telegram', icon: Send, id: 'telegram' },
  { name: 'Хостинг', icon: Database, id: 'hosting' },
  { name: 'TDS', icon: Target, id: 'tds' },
  { name: 'Настройки', icon: Settings, id: 'settings' },
]

// Language options
const languages = [
  { code: 'ru', name: 'Русский', flag: '🇷🇺' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'it', name: 'Italiano', flag: '🇮🇹' },
  { code: 'pt', name: 'Português', flag: '🇵🇹' },
  { code: 'zh', name: '中文', flag: '🇨🇳' },
  { code: 'ja', name: '日本語', flag: '🇯🇵' },
  { code: 'ko', name: '한국어', flag: '🇰🇷' },
  { code: 'ar', name: 'العربية', flag: '🇸🇦' },
  { code: 'tr', name: 'Türkçe', flag: '🇹🇷' },
]

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [sites, setSites] = useState<TargetSite[]>([])
  const [platforms, setPlatforms] = useState<Platform[]>([])
  const [content, setContent] = useState<ContentItem[]>([])
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [apiConnected, setApiConnected] = useState(false)
  
  // Modal states
  const [showAddSiteModal, setShowAddSiteModal] = useState(false)
  const [showAddPlatformModal, setShowAddPlatformModal] = useState(false)
  const [showGenerateModal, setShowGenerateModal] = useState(false)
  
  // Form states
  const [newSite, setNewSite] = useState({ name: '', url: '', description: '' })
  const [newPlatform, setNewPlatform] = useState({ name: '', url: '', login: '', password: '' })
  const [generateParams, setGenerateParams] = useState({
    target_site_id: 0,
    content_type: 'article',
    language: 'ru',
    topic: '',
    length: 'medium',
    style: 'informative'
  })

  // Check API connection
  useEffect(() => {
    const checkApi = async () => {
      try {
        await axios.get(`${API_URL.replace('/api', '')}/health`)
        setApiConnected(true)
        fetchAll()
      } catch {
        setApiConnected(false)
      }
    }
    checkApi()
    const interval = setInterval(checkApi, 10000)
    return () => clearInterval(interval)
  }, [])

  const fetchAll = () => {
    fetchStats()
    fetchSites()
    fetchPlatforms()
    fetchContent()
    fetchTasks()
  }

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/system/stats`)
      setStats(response.data)
    } catch (err) {
      console.error('Error fetching stats:', err)
    }
  }

  const fetchSites = async () => {
    try {
      const response = await axios.get(`${API_URL}/sites/`)
      setSites(response.data)
    } catch (err) {
      console.error('Error fetching sites:', err)
    }
  }

  const fetchPlatforms = async () => {
    try {
      const response = await axios.get(`${API_URL}/platforms/`)
      setPlatforms(response.data)
    } catch (err) {
      console.error('Error fetching platforms:', err)
    }
  }

  const fetchContent = async () => {
    try {
      const response = await axios.get(`${API_URL}/content/`)
      setContent(response.data)
    } catch (err) {
      console.error('Error fetching content:', err)
    }
  }

  const fetchTasks = async () => {
    try {
      const response = await axios.get(`${API_URL}/tasks/`)
      setTasks(response.data)
    } catch (err) {
      console.error('Error fetching tasks:', err)
    }
  }

  // Actions
  const addSite = async () => {
    try {
      setLoading(true)
      await axios.post(`${API_URL}/sites/`, newSite)
      setShowAddSiteModal(false)
      setNewSite({ name: '', url: '', description: '' })
      fetchSites()
      fetchStats()
    } catch {
      setError('Ошибка при добавлении сайта')
    } finally {
      setLoading(false)
    }
  }

  const analyzeSite = async (siteId: number) => {
    try {
      await axios.post(`${API_URL}/sites/${siteId}/analyze`)
      fetchTasks()
    } catch {
      setError('Ошибка при запуске анализа')
    }
  }

  const deleteSite = async (siteId: number) => {
    if (!confirm('Удалить этот сайт?')) return
    try {
      await axios.delete(`${API_URL}/sites/${siteId}`)
      fetchSites()
      fetchStats()
    } catch {
      setError('Ошибка при удалении сайта')
    }
  }

  const addPlatform = async () => {
    try {
      setLoading(true)
      await axios.post(`${API_URL}/platforms/`, newPlatform)
      setShowAddPlatformModal(false)
      setNewPlatform({ name: '', url: '', login: '', password: '' })
      fetchPlatforms()
      fetchStats()
    } catch {
      setError('Ошибка при добавлении площадки')
    } finally {
      setLoading(false)
    }
  }

  const generateContent = async () => {
    try {
      setLoading(true)
      await axios.post(`${API_URL}/content/generate`, generateParams)
      setShowGenerateModal(false)
      fetchTasks()
      fetchContent()
    } catch {
      setError('Ошибка при генерации контента')
    } finally {
      setLoading(false)
    }
  }

  // Render Dashboard
  const renderDashboard = () => (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold gradient-text">SEO Monster</h1>
        <div className="flex items-center gap-2 text-sm">
          {apiConnected ? (
            <>
              <Bot className="w-5 h-5 text-green-500" />
              <span className="text-green-600">Система активна</span>
            </>
          ) : (
            <>
              <Bot className="w-5 h-5 text-red-500" />
              <span className="text-red-600">API недоступен</span>
            </>
          )}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-6 shadow-sm card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Сайты</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.total_sites || 0}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Globe className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Площадки</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.total_platforms || 0}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <Target className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Контент</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.total_content || 0}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <FileText className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Успешность</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.success_rate?.toFixed(1) || 0}%</p>
            </div>
            <div className="p-3 bg-yellow-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-yellow-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Быстрые действия</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button 
            onClick={() => setShowAddSiteModal(true)}
            className="flex items-center gap-3 p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
          >
            <Plus className="w-5 h-5 text-blue-600" />
            <span className="font-medium text-blue-900">Добавить сайт</span>
          </button>
          <button 
            onClick={() => setShowAddPlatformModal(true)}
            className="flex items-center gap-3 p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
          >
            <Upload className="w-5 h-5 text-purple-600" />
            <span className="font-medium text-purple-900">Добавить площадку</span>
          </button>
          <button 
            onClick={() => setShowGenerateModal(true)}
            className="flex items-center gap-3 p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
          >
            <Zap className="w-5 h-5 text-green-600" />
            <span className="font-medium text-green-900">Генерировать контент</span>
          </button>
        </div>
      </div>

      {/* Recent Tasks */}
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Последние задачи</h2>
        {tasks.length === 0 ? (
          <p className="text-gray-500 text-center py-8">Нет активных задач</p>
        ) : (
          <div className="space-y-3">
            {tasks.slice(0, 5).map(task => (
              <div key={task.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  {task.status === 'completed' && <CheckCircle className="w-5 h-5 text-green-500" />}
                  {task.status === 'running' && <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />}
                  {task.status === 'pending' && <Clock className="w-5 h-5 text-yellow-500" />}
                  {task.status === 'failed' && <XCircle className="w-5 h-5 text-red-500" />}
                  <span className="font-medium">{task.task_type}</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full transition-all"
                      style={{ width: `${task.progress}%` }}
                    />
                  </div>
                  <span className="text-sm text-gray-500">{task.progress}%</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )

  // Render Sites
  const renderSites = () => (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Целевые сайты</h1>
        <button 
          onClick={() => setShowAddSiteModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Добавить сайт
        </button>
      </div>

      {sites.length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center">
          <Globe className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">Нет добавленных сайтов</p>
          <button 
            onClick={() => setShowAddSiteModal(true)}
            className="mt-4 text-blue-600 hover:underline"
          >
            Добавить первый сайт
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {sites.map(site => (
            <div key={site.id} className="bg-white rounded-xl p-6 shadow-sm card-hover">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold">{site.name}</h3>
                    {site.is_active ? (
                      <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">Активен</span>
                    ) : (
                      <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">Неактивен</span>
                    )}
                  </div>
                  <a href={site.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline text-sm">{site.url}</a>
                  {site.niche && (
                    <p className="mt-2 text-sm text-gray-600">Ниша: <span className="font-medium">{site.niche}</span></p>
                  )}
                  {site.keywords && site.keywords.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {site.keywords.slice(0, 5).map((kw, i) => (
                        <span key={i} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">{kw}</span>
                      ))}
                      {site.keywords.length > 5 && (
                        <span className="px-2 py-1 text-gray-400 text-xs">+{site.keywords.length - 5}</span>
                      )}
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <button 
                    onClick={() => analyzeSite(site.id)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Анализировать"
                  >
                    <Search className="w-5 h-5" />
                  </button>
                  <button 
                    onClick={() => deleteSite(site.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Удалить"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )

  // Render Platforms
  const renderPlatforms = () => (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Площадки</h1>
        <button 
          onClick={() => setShowAddPlatformModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Добавить площадку
        </button>
      </div>

      {platforms.length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center">
          <Target className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">Нет добавленных площадок</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Площадка</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Тип</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Статус</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Посты</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Действия</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {platforms.map(platform => (
                <tr key={platform.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-medium">{platform.name}</p>
                      <a href={platform.url} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:underline">{platform.url}</a>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">{platform.platform_type || 'Не определен'}</span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {platform.is_verified ? (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      ) : (
                        <Clock className="w-4 h-4 text-yellow-500" />
                      )}
                      {platform.has_captcha && (
                        <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded">Капча</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-green-600">{platform.successful_posts}</span>
                    <span className="text-gray-400"> / {platform.posts_count}</span>
                  </td>
                  <td className="px-6 py-4">
                    <button className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )

  // Render Content
  const renderContent = () => (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Контент</h1>
        <button 
          onClick={() => setShowGenerateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          <Zap className="w-4 h-4" />
          Генерировать
        </button>
      </div>

      {content.length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center">
          <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">Нет созданного контента</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {content.map(item => (
            <div key={item.id} className="bg-white rounded-xl p-6 shadow-sm card-hover">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold">{item.title || 'Без заголовка'}</h3>
                    <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">{item.content_type}</span>
                    <span className="text-lg">{languages.find(l => l.code === item.language)?.flag}</span>
                  </div>
                  <p className="mt-2 text-gray-600 text-sm line-clamp-2">{item.content.substring(0, 200)}...</p>
                </div>
                <div className="flex items-center gap-2">
                  {item.is_published ? (
                    <span className="px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full">Опубликован</span>
                  ) : (
                    <button className="flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full hover:bg-blue-200">
                      <Send className="w-3 h-3" />
                      Опубликовать
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )

  // Render Tasks
  const renderTasks = () => (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Задачи</h1>
        <button 
          onClick={fetchTasks}
          className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Обновить
        </button>
      </div>

      {tasks.length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center">
          <Activity className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">Нет задач</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Тип</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Статус</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Прогресс</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Создана</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {tasks.map(task => (
                <tr key={task.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-mono text-sm">#{task.id}</td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">{task.task_type}</span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {task.status === 'completed' && <CheckCircle className="w-4 h-4 text-green-500" />}
                      {task.status === 'running' && <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />}
                      {task.status === 'pending' && <Clock className="w-4 h-4 text-yellow-500" />}
                      {task.status === 'failed' && <XCircle className="w-4 h-4 text-red-500" />}
                      <span className="capitalize">{task.status}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all ${
                            task.status === 'completed' ? 'bg-green-500' :
                            task.status === 'failed' ? 'bg-red-500' : 'bg-blue-500'
                          }`}
                          style={{ width: `${task.progress}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-500">{task.progress}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(task.created_at).toLocaleString('ru-RU')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )

  // Render Sessions
  const renderSessions = () => <SessionManager />

  // Render Settings
  const renderSettings = () => (
    <div className="space-y-6 animate-fadeIn">
      <h1 className="text-2xl font-bold">Настройки</h1>
      
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Подключение ИИ</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">OpenAI API Key</label>
            <input 
              type="password" 
              placeholder="sk-..." 
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Модель</label>
            <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
              <option value="gpt-4.1-mini">GPT-4.1 Mini</option>
              <option value="gpt-4.1-nano">GPT-4.1 Nano</option>
              <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
            </select>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Бэкап и восстановление</h2>
        <div className="flex gap-4">
          <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
            <Download className="w-4 h-4" />
            Создать бэкап
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            <Upload className="w-4 h-4" />
            Восстановить
          </button>
        </div>
      </div>
    </div>
  )

  // Render Indexing
  const renderIndexing = () => <IndexingManager />

  // Render current page
  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard': return renderDashboard()
      case 'chat': return <AIChat />
      case 'autopilot': return <AutopilotManager />
      case 'sites': return renderSites()
      case 'platforms': return renderPlatforms()
      case 'content': return renderContent()
      case 'sessions': return renderSessions()
      case 'indexing': return renderIndexing()
      case 'tasks': return renderTasks()
      case 'telegram': return <TelegramSettings />
      case 'hosting': return <HostingManager />
      case 'tds': return <TDSManager />
      case 'settings': return renderSettings()
      default: return renderDashboard()
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 text-white flex flex-col">
        <div className="p-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-blue-500 rounded-lg flex items-center justify-center">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-bold text-lg">SEO Monster</h1>
              <p className="text-xs text-gray-400">v1.0.0</p>
            </div>
          </div>
        </div>
        
        <nav className="flex-1 px-4">
          {navigation.map(item => (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-1 transition-colors ${
                currentPage === item.id 
                  ? 'bg-gray-800 text-white' 
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <item.icon className="w-5 h-5" />
              {item.name}
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-800">
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <Database className="w-4 h-4" />
            <span>SQLite</span>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-auto">
        {error && (
          <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-lg flex items-center justify-between">
            <span>{error}</span>
            <button onClick={() => setError(null)}><XCircle className="w-5 h-5" /></button>
          </div>
        )}
        {renderPage()}
      </main>

      {/* Add Site Modal */}
      {showAddSiteModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md animate-fadeIn">
            <h2 className="text-xl font-bold mb-4">Добавить сайт</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Название</label>
                <input 
                  type="text"
                  value={newSite.name}
                  onChange={e => setNewSite({...newSite, name: e.target.value})}
                  placeholder="Мой сайт"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">URL</label>
                <input 
                  type="url"
                  value={newSite.url}
                  onChange={e => setNewSite({...newSite, url: e.target.value})}
                  placeholder="https://example.com"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Описание</label>
                <textarea 
                  value={newSite.description}
                  onChange={e => setNewSite({...newSite, description: e.target.value})}
                  placeholder="Краткое описание сайта..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={3}
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button 
                onClick={() => setShowAddSiteModal(false)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Отмена
              </button>
              <button 
                onClick={addSite}
                disabled={loading || !newSite.name || !newSite.url}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Добавление...' : 'Добавить'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Platform Modal */}
      {showAddPlatformModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md animate-fadeIn">
            <h2 className="text-xl font-bold mb-4">Добавить площадку</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Название</label>
                <input 
                  type="text"
                  value={newPlatform.name}
                  onChange={e => setNewPlatform({...newPlatform, name: e.target.value})}
                  placeholder="Форум XYZ"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">URL</label>
                <input 
                  type="url"
                  value={newPlatform.url}
                  onChange={e => setNewPlatform({...newPlatform, url: e.target.value})}
                  placeholder="https://forum.example.com"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Логин</label>
                <input 
                  type="text"
                  value={newPlatform.login}
                  onChange={e => setNewPlatform({...newPlatform, login: e.target.value})}
                  placeholder="username"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
                <input 
                  type="password"
                  value={newPlatform.password}
                  onChange={e => setNewPlatform({...newPlatform, password: e.target.value})}
                  placeholder="••••••••"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button 
                onClick={() => setShowAddPlatformModal(false)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Отмена
              </button>
              <button 
                onClick={addPlatform}
                disabled={loading || !newPlatform.name || !newPlatform.url}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Добавление...' : 'Добавить'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Generate Content Modal */}
      {showGenerateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-lg animate-fadeIn">
            <h2 className="text-xl font-bold mb-4">Генерация контента</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Целевой сайт</label>
                <select 
                  value={generateParams.target_site_id}
                  onChange={e => setGenerateParams({...generateParams, target_site_id: Number(e.target.value)})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                >
                  <option value={0}>Выберите сайт...</option>
                  {sites.map(site => (
                    <option key={site.id} value={site.id}>{site.name}</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Тип контента</label>
                  <select 
                    value={generateParams.content_type}
                    onChange={e => setGenerateParams({...generateParams, content_type: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  >
                    <option value="article">Статья</option>
                    <option value="comment">Комментарий</option>
                    <option value="review">Обзор</option>
                    <option value="news">Новость</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Язык</label>
                  <select 
                    value={generateParams.language}
                    onChange={e => setGenerateParams({...generateParams, language: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  >
                    {languages.map(lang => (
                      <option key={lang.code} value={lang.code}>{lang.flag} {lang.name}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Тема (опционально)</label>
                <input 
                  type="text"
                  value={generateParams.topic}
                  onChange={e => setGenerateParams({...generateParams, topic: e.target.value})}
                  placeholder="Оставьте пустым для автоматического определения"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Длина</label>
                  <select 
                    value={generateParams.length}
                    onChange={e => setGenerateParams({...generateParams, length: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  >
                    <option value="short">Короткая (200-400 слов)</option>
                    <option value="medium">Средняя (500-800 слов)</option>
                    <option value="long">Длинная (1000-1500 слов)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Стиль</label>
                  <select 
                    value={generateParams.style}
                    onChange={e => setGenerateParams({...generateParams, style: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  >
                    <option value="informative">Информативный</option>
                    <option value="promotional">Рекламный</option>
                    <option value="news">Новостной</option>
                    <option value="review">Обзорный</option>
                  </select>
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button 
                onClick={() => setShowGenerateModal(false)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Отмена
              </button>
              <button 
                onClick={generateContent}
                disabled={loading || !generateParams.target_site_id}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
              >
                <Zap className="w-4 h-4" />
                {loading ? 'Генерация...' : 'Сгенерировать'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
