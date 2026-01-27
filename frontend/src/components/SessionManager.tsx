import { useState, useEffect } from 'react'
import { 
  Users, 
  Key, 
  Plus, 
  Upload, 
  Download, 
  Trash2, 
  CheckCircle, 
  XCircle,
  RefreshCw,
  LogIn,
  Save,
  ExternalLink,
  Search,
  Filter
} from 'lucide-react'
import axios from 'axios'

const API_URL = 'http://localhost:8000/api'

interface Account {
  id: string
  platform: string
  username: string
  status: string
  session_valid: boolean
  created_at: string
  last_login?: string
  login_count: number
}

interface Platform {
  id: string
  name: string
  login_url: string
}

interface SessionStats {
  total_accounts: number
  active_sessions: number
  successful_logins: number
  failed_logins: number
  last_activity?: string
}

export default function SessionManager() {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [platforms, setPlatforms] = useState<Platform[]>([])
  const [stats, setStats] = useState<SessionStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  
  // Filters
  const [filterPlatform, setFilterPlatform] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  
  // Modals
  const [showAddModal, setShowAddModal] = useState(false)
  const [showBulkModal, setShowBulkModal] = useState(false)
  const [showLoginModal, setShowLoginModal] = useState(false)
  
  // Form states
  const [newAccount, setNewAccount] = useState({
    platform: '',
    username: '',
    password: ''
  })
  const [bulkText, setBulkText] = useState('')
  const [bulkPlatform, setBulkPlatform] = useState('auto')
  const [loginAccountId, setLoginAccountId] = useState('')
  const [loginPlatform, setLoginPlatform] = useState('')

  // Fetch data
  useEffect(() => {
    fetchAccounts()
    fetchPlatforms()
    fetchStats()
  }, [filterPlatform, filterStatus])

  const fetchAccounts = async () => {
    try {
      const params = new URLSearchParams()
      if (filterPlatform) params.append('platform', filterPlatform)
      if (filterStatus) params.append('status', filterStatus)
      
      const response = await axios.get(`${API_URL}/sessions/accounts?${params}`)
      setAccounts(response.data.accounts || [])
    } catch (err) {
      console.error('Failed to fetch accounts:', err)
    }
  }

  const fetchPlatforms = async () => {
    try {
      const response = await axios.get(`${API_URL}/sessions/platforms`)
      setPlatforms(response.data.platforms || [])
    } catch (err) {
      console.error('Failed to fetch platforms:', err)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/sessions/stats`)
      setStats(response.data)
    } catch (err) {
      console.error('Failed to fetch stats:', err)
    }
  }

  const addAccount = async () => {
    if (!newAccount.platform || !newAccount.username || !newAccount.password) {
      setError('Заполните все поля')
      return
    }
    
    setLoading(true)
    setError(null)
    
    try {
      await axios.post(`${API_URL}/sessions/accounts`, newAccount)
      setSuccess('Аккаунт добавлен')
      setShowAddModal(false)
      setNewAccount({ platform: '', username: '', password: '' })
      fetchAccounts()
      fetchStats()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка добавления')
    } finally {
      setLoading(false)
    }
  }

  const bulkImport = async () => {
    if (!bulkText.trim()) {
      setError('Введите данные аккаунтов')
      return
    }
    
    setLoading(true)
    setError(null)
    
    try {
      const response = await axios.post(`${API_URL}/sessions/accounts/bulk`, {
        accounts_text: bulkText,
        default_platform: bulkPlatform
      })
      setSuccess(`Импортировано: ${response.data.imported}, пропущено: ${response.data.skipped}`)
      setShowBulkModal(false)
      setBulkText('')
      fetchAccounts()
      fetchStats()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка импорта')
    } finally {
      setLoading(false)
    }
  }

  const deleteAccount = async (accountId: string) => {
    if (!confirm('Удалить аккаунт и его сессию?')) return
    
    try {
      await axios.delete(`${API_URL}/sessions/accounts/${accountId}`)
      setSuccess('Аккаунт удален')
      fetchAccounts()
      fetchStats()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка удаления')
    }
  }

  const openLoginPage = async () => {
    if (!loginAccountId || !loginPlatform) {
      setError('Выберите аккаунт и платформу')
      return
    }
    
    setLoading(true)
    setError(null)
    
    try {
      const response = await axios.post(`${API_URL}/sessions/login/open`, {
        account_id: loginAccountId,
        platform: loginPlatform
      })
      setSuccess(response.data.message)
      setShowLoginModal(false)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка открытия браузера')
    } finally {
      setLoading(false)
    }
  }

  const saveSession = async (accountId: string) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await axios.post(`${API_URL}/sessions/login/save`, {
        account_id: accountId
      })
      setSuccess(response.data.message)
      fetchAccounts()
      fetchStats()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка сохранения сессии')
    } finally {
      setLoading(false)
    }
  }

  const exportSessions = async () => {
    try {
      const response = await axios.post(`${API_URL}/sessions/export`)
      setSuccess(`Экспортировано в: ${response.data.file}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка экспорта')
    }
  }

  // Filter accounts
  const filteredAccounts = accounts.filter(acc => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      return acc.username.toLowerCase().includes(query) || 
             acc.platform.toLowerCase().includes(query)
    }
    return true
  })

  const getStatusBadge = (status: string, sessionValid: boolean) => {
    if (sessionValid) {
      return <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full flex items-center gap-1">
        <CheckCircle className="w-3 h-3" /> Активна
      </span>
    }
    
    switch (status) {
      case 'new':
        return <span className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full">Новый</span>
      case 'expired':
        return <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-700 rounded-full">Истекла</span>
      case 'blocked':
        return <span className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded-full flex items-center gap-1">
          <XCircle className="w-3 h-3" /> Заблокирован
        </span>
      default:
        return <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full">{status}</span>
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Session Manager</h1>
          <p className="text-gray-500">Управление аккаунтами и сессиями</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowBulkModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Upload className="w-4 h-4" />
            Массовый импорт
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Добавить аккаунт
          </button>
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError(null)}><XCircle className="w-5 h-5" /></button>
        </div>
      )}
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg flex items-center justify-between">
          <span>{success}</span>
          <button onClick={() => setSuccess(null)}><XCircle className="w-5 h-5" /></button>
        </div>
      )}

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Всего аккаунтов</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_accounts}</p>
              </div>
              <Users className="w-10 h-10 text-blue-500 opacity-50" />
            </div>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Активных сессий</p>
                <p className="text-2xl font-bold text-green-600">{stats.active_sessions}</p>
              </div>
              <Key className="w-10 h-10 text-green-500 opacity-50" />
            </div>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Успешных входов</p>
                <p className="text-2xl font-bold text-purple-600">{stats.successful_logins}</p>
              </div>
              <CheckCircle className="w-10 h-10 text-purple-500 opacity-50" />
            </div>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Неудачных входов</p>
                <p className="text-2xl font-bold text-red-600">{stats.failed_logins}</p>
              </div>
              <XCircle className="w-10 h-10 text-red-500 opacity-50" />
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Поиск по username или платформе..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
            />
          </div>
          <select
            value={filterPlatform}
            onChange={e => setFilterPlatform(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          >
            <option value="">Все платформы</option>
            {platforms.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
          <select
            value={filterStatus}
            onChange={e => setFilterStatus(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          >
            <option value="">Все статусы</option>
            <option value="new">Новые</option>
            <option value="active">Активные</option>
            <option value="expired">Истекшие</option>
            <option value="blocked">Заблокированные</option>
          </select>
          <button
            onClick={fetchAccounts}
            className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
          <button
            onClick={exportSessions}
            className="flex items-center gap-2 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Download className="w-4 h-4" />
            Экспорт
          </button>
        </div>
      </div>

      {/* Accounts Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Платформа</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Username</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Статус</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Входов</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Последний вход</th>
              <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">Действия</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filteredAccounts.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                  Нет аккаунтов. Добавьте первый аккаунт или импортируйте список.
                </td>
              </tr>
            ) : (
              filteredAccounts.map(account => (
                <tr key={account.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm font-medium">
                      {account.platform}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-medium text-gray-900">{account.username}</td>
                  <td className="px-4 py-3">
                    {getStatusBadge(account.status, account.session_valid)}
                  </td>
                  <td className="px-4 py-3 text-gray-600">{account.login_count}</td>
                  <td className="px-4 py-3 text-gray-500 text-sm">
                    {account.last_login ? new Date(account.last_login).toLocaleString('ru') : '-'}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-2">
                      {!account.session_valid && (
                        <button
                          onClick={() => {
                            setLoginAccountId(account.id)
                            setLoginPlatform(account.platform)
                            setShowLoginModal(true)
                          }}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          title="Войти"
                        >
                          <LogIn className="w-4 h-4" />
                        </button>
                      )}
                      {account.session_valid && (
                        <button
                          onClick={() => saveSession(account.id)}
                          className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                          title="Обновить сессию"
                        >
                          <Save className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => deleteAccount(account.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Удалить"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Add Account Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Добавить аккаунт</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Платформа</label>
                <select
                  value={newAccount.platform}
                  onChange={e => setNewAccount({...newAccount, platform: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                >
                  <option value="">Выберите платформу...</option>
                  {platforms.map(p => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Username / Email</label>
                <input
                  type="text"
                  value={newAccount.username}
                  onChange={e => setNewAccount({...newAccount, username: e.target.value})}
                  placeholder="user@example.com"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
                <input
                  type="password"
                  value={newAccount.password}
                  onChange={e => setNewAccount({...newAccount, password: e.target.value})}
                  placeholder="••••••••"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={addAccount}
                disabled={loading}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Добавление...' : 'Добавить'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Bulk Import Modal */}
      {showBulkModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-2xl">
            <h2 className="text-xl font-bold mb-4">Массовый импорт аккаунтов</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Платформа по умолчанию</label>
                <select
                  value={bulkPlatform}
                  onChange={e => setBulkPlatform(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                >
                  <option value="auto">Автоопределение</option>
                  {platforms.map(p => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Аккаунты (по одному на строку)
                </label>
                <textarea
                  value={bulkText}
                  onChange={e => setBulkText(e.target.value)}
                  placeholder={`Форматы:\nplatform:username:password\nusername:password\nemail:password\n\nПример:\ngoogle:user@gmail.com:mypassword123\nyoutube:channel@gmail.com:pass456\nuser@mail.ru:password789`}
                  rows={10}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 font-mono text-sm"
                />
              </div>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-700">
                <strong>Совет:</strong> Для аккаунтов Google/YouTube используйте формат: 
                <code className="bg-blue-100 px-1 rounded">google:email@gmail.com:password</code>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowBulkModal(false)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={bulkImport}
                disabled={loading}
                className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
              >
                <Upload className="w-4 h-4" />
                {loading ? 'Импорт...' : 'Импортировать'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Login Modal */}
      {showLoginModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Вход в аккаунт</h2>
            <div className="space-y-4">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-sm text-yellow-700">
                <strong>Инструкция:</strong>
                <ol className="list-decimal list-inside mt-2 space-y-1">
                  <li>Нажмите "Открыть браузер"</li>
                  <li>Выполните вход вручную (пройдите капчу если нужно)</li>
                  <li>После успешного входа нажмите "Сохранить сессию"</li>
                </ol>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Платформа</label>
                <select
                  value={loginPlatform}
                  onChange={e => setLoginPlatform(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                >
                  <option value="">Выберите платформу...</option>
                  {platforms.map(p => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowLoginModal(false)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={openLoginPage}
                disabled={loading}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                <ExternalLink className="w-4 h-4" />
                {loading ? 'Открытие...' : 'Открыть браузер'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
