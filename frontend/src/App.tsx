import { useState, useEffect } from 'react'
import axios from 'axios'
import DiagnosticsPanel from './components/DiagnosticsPanel'
import AdCampaignsManager from './components/AdCampaignsManager'
import TrackerManager from './components/TrackerManager'
import AdsTrackerIntegration from './components/AdsTrackerIntegration'
import ThemeToggle, { useTheme } from './components/ThemeToggle'
import './theme.css'

const API_URL = 'http://localhost:8000/api'

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [apiConnected, setApiConnected] = useState(false)
  const [stats, setStats] = useState<any>(null)
  const { theme, toggleTheme } = useTheme()

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
  }, [])

  const navigation = [
    { name: 'Dashboard', id: 'dashboard', icon: '📊' },
    { name: 'Autopilot', id: 'autopilot', icon: '🤖' },
    { name: 'Sites', id: 'sites', icon: '🌐' },
    { name: 'Platforms', id: 'platforms', icon: '📱' },
    { name: 'Content', id: 'content', icon: '📝' },
    { name: 'Ad Campaigns', id: 'adcampaigns', icon: '📢' },
    { name: 'Tracker', id: 'tracker', icon: '🎯' },
    { name: 'Ads Integration', id: 'adsintegration', icon: '🔗' },
    { name: 'Diagnostics', id: 'diagnostics', icon: '🔧' },
    { name: 'Settings', id: 'settings', icon: '⚙️' },
  ]

  return (
    <div className={`flex h-screen ${theme === 'dark' ? 'bg-gray-900' : 'bg-gray-100'}`}>
      {/* Sidebar */}
      <div className={`w-64 ${theme === 'dark' ? 'bg-gray-800' : 'bg-white border-r border-gray-200'} p-4 flex flex-col`}>
        <div className="flex items-center justify-between mb-8">
          <h1 className={`text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
            SEO Monster
          </h1>
        </div>
        
        <nav className="space-y-2 flex-1">
          {navigation.map((item) => (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full text-left px-4 py-2 rounded flex items-center gap-2 ${
                currentPage === item.id
                  ? 'bg-blue-600 text-white'
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
        
        {/* Theme Toggle & Status */}
        <div className="space-y-3 mt-auto">
          <div className={`flex items-center justify-between p-3 rounded ${
            theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'
          }`}>
            <span className={`text-sm ${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>
              Theme
            </span>
            <ThemeToggle theme={theme} toggleTheme={toggleTheme} />
          </div>
          
          <div className={`p-3 rounded ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'}`}>
            <div className={`w-3 h-3 rounded-full inline-block mr-2 ${apiConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className={`text-sm ${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>
              {apiConnected ? 'API Connected' : 'API Disconnected'}
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
          <div className="grid grid-cols-4 gap-4">
            <div className={`p-6 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
              <h3 className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>Total Sites</h3>
              <p className={`text-3xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>{stats?.total_sites || 0}</p>
            </div>
            <div className={`p-6 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
              <h3 className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>Total Platforms</h3>
              <p className={`text-3xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>{stats?.total_platforms || 0}</p>
            </div>
            <div className={`p-6 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
              <h3 className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>Total Content</h3>
              <p className={`text-3xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>{stats?.total_content || 0}</p>
            </div>
            <div className={`p-6 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
              <h3 className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>Active Tasks</h3>
              <p className={`text-3xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>{stats?.active_tasks || 0}</p>
            </div>
          </div>
        )}

        {currentPage === 'autopilot' && (
          <div className={`p-6 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
            <p className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>
              Autopilot controls will be displayed here
            </p>
          </div>
        )}

        {currentPage === 'sites' && (
          <div className={`p-6 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
            <p className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>
              Sites management will be displayed here
            </p>
          </div>
        )}

        {currentPage === 'platforms' && (
          <div className={`p-6 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
            <p className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>
              Platforms management will be displayed here
            </p>
          </div>
        )}

        {currentPage === 'content' && (
          <div className={`p-6 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
            <p className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>
              Content management will be displayed here
            </p>
          </div>
        )}

        {currentPage === 'adcampaigns' && (
          <AdCampaignsManager />
        )}

        {currentPage === 'tracker' && (
          <TrackerManager />
        )}

        {currentPage === 'adsintegration' && (
          <AdsTrackerIntegration />
        )}

        {currentPage === 'diagnostics' && (
          <DiagnosticsPanel />
        )}

        {currentPage === 'settings' && (
          <div className={`p-6 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
            <h3 className={`text-xl font-bold mb-4 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
              Application Settings
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className={theme === 'dark' ? 'text-white' : 'text-gray-900'}>Theme</p>
                  <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                    Switch between dark and light mode
                  </p>
                </div>
                <ThemeToggle theme={theme} toggleTheme={toggleTheme} />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
