import { useState, useEffect } from 'react'
import axios from 'axios'
import DiagnosticsPanelEnhanced from './components/DiagnosticsPanelEnhanced'
import AdCampaignsManager from './components/AdCampaignsManager'
import TrackerManager from './components/TrackerManager'
import AdsTrackerIntegration from './components/AdsTrackerIntegration'
import SESManagerEnhanced from './components/SESManagerEnhanced'
import SitesManager from './components/SitesManager'
import ContentManager from './components/ContentManager'
import AutopilotManager from './components/AutopilotManager'
import ThemeToggle, { useTheme } from './components/ThemeToggle'
import { LanguageProvider, useLanguage, LanguageSwitcher } from './contexts/LanguageContext'
import { OptionalFeaturesCard, SetupProgressBar } from './components/OptionalFeatures'
import './theme.css'

const API_URL = 'http://144.31.238.16:8000/api'

function AppContent() {
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [apiConnected, setApiConnected] = useState(false)
  const [stats, setStats] = useState<any>(null)
  const { theme, toggleTheme } = useTheme()
  const { t, language } = useLanguage()

  useEffect(() => {
    const checkApi = async () => {
      try {
        await axios.get(`${API_URL.replace('/api', '')}/health`)
        setApiConnected(true)
        const response = await axios.get(`${API_URL}/system/stats`)
        setStats(response.data)
      } catch {
        setApiConnected(false)
      }
    }
    checkApi()
    const interval = setInterval(checkApi, 30000)
    return () => clearInterval(interval)
  }, [])

  const navigation = [
    { name: t('nav.dashboard'), id: 'dashboard', icon: '📊' },
    { name: t('nav.autopilot'), id: 'autopilot', icon: '🤖' },
    { name: t('nav.sites'), id: 'sites', icon: '🌐' },
    { name: t('nav.platforms'), id: 'platforms', icon: '📱' },
    { name: t('nav.content'), id: 'content', icon: '📝' },
    { name: t('nav.adCampaigns'), id: 'adcampaigns', icon: '📢' },
    { name: t('nav.tracker'), id: 'tracker', icon: '🎯' },
    { name: t('nav.adsIntegration'), id: 'adsintegration', icon: '🔗' },
    { name: t('nav.emailSes'), id: 'ses', icon: '📧' },
    { name: t('nav.diagnostics'), id: 'diagnostics', icon: '🔧' },
    { name: t('nav.settings'), id: 'settings', icon: '⚙️' },
  ]

  return (
    <div className={`flex h-screen ${theme === 'dark' ? 'bg-gray-900' : 'bg-gray-100'}`}>
      {/* Sidebar */}
      <div className={`w-64 ${theme === 'dark' ? 'bg-gray-800' : 'bg-white border-r border-gray-200'} p-4 flex flex-col`}>
        <div className="flex items-center justify-between mb-8">
          <h1 className={`text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
            {t('app.name')}
          </h1>
        </div>
        
        <nav className="space-y-2 flex-1">
          {navigation.map((item) => (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full text-left px-4 py-2 rounded flex items-center gap-2 transition-all duration-200 ${
                currentPage === item.id
                  ? 'bg-blue-600 text-white shadow-md'
                  : theme === 'dark' 
                    ? 'text-gray-300 hover:bg-gray-700' 
                    : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <span>{item.icon}</span>
              {item.name}
            </button>
          ))}
        </nav>
        
        {/* Language Switcher */}
        <div className={`p-3 rounded mb-3 ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'}`}>
          <div className={`text-sm mb-2 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>
            {t('settings.language')}
          </div>
          <LanguageSwitcher />
        </div>
        
        {/* Theme Toggle & Status */}
        <div className="space-y-3">
          <div className={`flex items-center justify-between p-3 rounded ${
            theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'
          }`}>
            <span className={`text-sm ${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>
              {t('settings.theme')}
            </span>
            <ThemeToggle theme={theme} toggleTheme={toggleTheme} />
          </div>
          
          <div className={`p-3 rounded ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'}`}>
            <div className={`w-3 h-3 rounded-full inline-block mr-2 ${apiConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
            <span className={`text-sm ${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>
              {apiConnected ? t('msg.apiConnected') : t('msg.apiDisconnected')}
            </span>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 p-8 overflow-auto">
        <h2 className={`text-3xl font-bold mb-6 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
          {navigation.find(n => n.id === currentPage)?.name || currentPage}
        </h2>
        
        {currentPage === 'dashboard' && (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-4 gap-4">
              <div className={`p-6 rounded-lg transition-all duration-200 hover:shadow-lg ${theme === 'dark' ? 'bg-gray-800 hover:bg-gray-750' : 'bg-white shadow hover:shadow-md'}`}>
                <h3 className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>{t('dashboard.totalSites')}</h3>
                <p className={`text-3xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>{stats?.total_sites || 0}</p>
              </div>
              <div className={`p-6 rounded-lg transition-all duration-200 hover:shadow-lg ${theme === 'dark' ? 'bg-gray-800 hover:bg-gray-750' : 'bg-white shadow hover:shadow-md'}`}>
                <h3 className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>{t('dashboard.totalPlatforms')}</h3>
                <p className={`text-3xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>{stats?.total_platforms || 0}</p>
              </div>
              <div className={`p-6 rounded-lg transition-all duration-200 hover:shadow-lg ${theme === 'dark' ? 'bg-gray-800 hover:bg-gray-750' : 'bg-white shadow hover:shadow-md'}`}>
                <h3 className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>{t('dashboard.totalContent')}</h3>
                <p className={`text-3xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>{stats?.total_content || 0}</p>
              </div>
              <div className={`p-6 rounded-lg transition-all duration-200 hover:shadow-lg ${theme === 'dark' ? 'bg-gray-800 hover:bg-gray-750' : 'bg-white shadow hover:shadow-md'}`}>
                <h3 className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>{t('dashboard.activeTasks')}</h3>
                <p className={`text-3xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>{stats?.active_tasks || 0}</p>
              </div>
            </div>

            {/* Setup Progress Bar */}
            <SetupProgressBar />
            
            {/* Quick Actions */}
            <div className={`p-6 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
              <h3 className={`text-xl font-bold mb-4 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                {t('dashboard.quickActions')}
              </h3>
              <div className="grid grid-cols-4 gap-4">
                <button 
                  onClick={() => setCurrentPage('autopilot')}
                  className="p-4 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors flex flex-col items-center gap-2"
                >
                  <span className="text-2xl">🤖</span>
                  <span>{t('autopilot.start')}</span>
                </button>
                <button 
                  onClick={() => setCurrentPage('sites')}
                  className="p-4 rounded-lg bg-green-600 text-white hover:bg-green-700 transition-colors flex flex-col items-center gap-2"
                >
                  <span className="text-2xl">🌐</span>
                  <span>{t('sites.addSite')}</span>
                </button>
                <button 
                  onClick={() => setCurrentPage('content')}
                  className="p-4 rounded-lg bg-purple-600 text-white hover:bg-purple-700 transition-colors flex flex-col items-center gap-2"
                >
                  <span className="text-2xl">📝</span>
                  <span>{t('content.generate')}</span>
                </button>
                <button 
                  onClick={() => setCurrentPage('diagnostics')}
                  className="p-4 rounded-lg bg-orange-600 text-white hover:bg-orange-700 transition-colors flex flex-col items-center gap-2"
                >
                  <span className="text-2xl">🔧</span>
                  <span>{t('diagnostics.runDiagnostics')}</span>
                </button>
              </div>
            </div>

            {/* Optional Features Card */}
            <OptionalFeaturesCard onNavigate={setCurrentPage} />
            
            {/* System Status */}
            <div className={`p-6 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
              <h3 className={`text-xl font-bold mb-4 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                {t('dashboard.systemStatus')}
              </h3>
              <div className="grid grid-cols-3 gap-4">
                <div className={`p-4 rounded-lg ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'}`}>
                  <div className="flex items-center gap-2 mb-2">
                    <div className={`w-3 h-3 rounded-full ${apiConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span className={theme === 'dark' ? 'text-white' : 'text-gray-900'}>API</span>
                  </div>
                  <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                    {apiConnected ? t('common.connected') : t('common.disconnected')}
                  </p>
                </div>
                <div className={`p-4 rounded-lg ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'}`}>
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span className={theme === 'dark' ? 'text-white' : 'text-gray-900'}>{t('nav.autopilot')}</span>
                  </div>
                  <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                    {t('common.active')}
                  </p>
                </div>
                <div className={`p-4 rounded-lg ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'}`}>
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span className={theme === 'dark' ? 'text-white' : 'text-gray-900'}>{t('nav.emailSes')}</span>
                  </div>
                  <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                    {t('common.active')}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Autopilot - использует полнофункциональный компонент */}
        {currentPage === 'autopilot' && <AutopilotManager />}

        {/* Sites - использует полнофункциональный компонент */}
        {currentPage === 'sites' && <SitesManager />}

        {/* Platforms - заглушка с TODO */}
        {currentPage === 'platforms' && (
          <div className={`p-6 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
            <div className="flex justify-between items-center mb-6">
              <h3 className={`text-xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                {t('platforms.title')}
              </h3>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                + {t('platforms.addPlatform')}
              </button>
            </div>
            <div className={`text-center py-12 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
              <span className="text-4xl">📱</span>
              <p className="mt-4">{language === 'ru' ? 'Платформы управляются через раздел Сайты' : 'Platforms are managed through Sites section'}</p>
              <button 
                onClick={() => setCurrentPage('sites')}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                {language === 'ru' ? 'Перейти к Сайтам' : 'Go to Sites'}
              </button>
            </div>
          </div>
        )}

        {/* Content - использует полнофункциональный компонент */}
        {currentPage === 'content' && <ContentManager />}

        {currentPage === 'adcampaigns' && <AdCampaignsManager />}
        {currentPage === 'tracker' && <TrackerManager />}
        {currentPage === 'adsintegration' && <AdsTrackerIntegration />}
        {currentPage === 'ses' && <SESManagerEnhanced />}
        {currentPage === 'diagnostics' && <DiagnosticsPanelEnhanced />}

        {currentPage === 'settings' && (
          <div className="space-y-6">
            <div className={`p-6 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
              <h3 className={`text-xl font-bold mb-4 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                {t('settings.title')}
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className={`font-medium ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                      {t('settings.language')}
                    </h4>
                    <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                      {language === 'ru' ? 'Выберите язык интерфейса' : 'Select interface language'}
                    </p>
                  </div>
                  <LanguageSwitcher />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className={`font-medium ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                      {t('settings.theme')}
                    </h4>
                    <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                      {language === 'ru' ? 'Светлая или темная тема' : 'Light or dark theme'}
                    </p>
                  </div>
                  <ThemeToggle theme={theme} toggleTheme={toggleTheme} />
                </div>
              </div>
            </div>

            {/* Setup Progress in Settings */}
            <SetupProgressBar />

            {/* Optional Features in Settings */}
            <OptionalFeaturesCard onNavigate={setCurrentPage} />
          </div>
        )}
      </div>
    </div>
  )
}

function App() {
  return (
    <LanguageProvider>
      <AppContent />
    </LanguageProvider>
  )
}

export default App
