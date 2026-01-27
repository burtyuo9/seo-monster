import { useState, useEffect } from 'react'
import axios from 'axios'
import DiagnosticsPanel from './components/DiagnosticsPanel'

const API_URL = 'http://localhost:8000/api'

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [apiConnected, setApiConnected] = useState(false)
  const [stats, setStats] = useState<any>(null)

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
    { name: 'Dashboard', id: 'dashboard' },
    { name: 'Autopilot', id: 'autopilot' },
    { name: 'Sites', id: 'sites' },
    { name: 'Platforms', id: 'platforms' },
    { name: 'Content', id: 'content' },
    { name: 'Settings', id: 'settings' },
    { name: 'Diagnostics', id: 'diagnostics' },
  ]

  return (
    <div className="flex h-screen bg-gray-900">
      {/* Sidebar */}
      <div className="w-64 bg-gray-800 p-4">
        <h1 className="text-2xl font-bold text-white mb-8">SEO Monster</h1>
        <nav className="space-y-2">
          {navigation.map((item) => (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full text-left px-4 py-2 rounded ${
                currentPage === item.id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700'
              }`}
            >
              {item.name}
            </button>
          ))}
        </nav>
        <div className="mt-8 p-3 rounded bg-gray-700">
          <div className={`w-3 h-3 rounded-full inline-block mr-2 ${apiConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-sm text-gray-300">
            {apiConnected ? 'API Connected' : 'API Disconnected'}
          </span>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 p-8 overflow-auto">
        <h2 className="text-3xl font-bold text-white mb-6">{currentPage.charAt(0).toUpperCase() + currentPage.slice(1)}</h2>
        
        {currentPage === 'dashboard' && (
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-gray-800 p-6 rounded-lg">
              <h3 className="text-gray-400 text-sm">Total Sites</h3>
              <p className="text-3xl font-bold text-white">{stats?.total_sites || 0}</p>
            </div>
            <div className="bg-gray-800 p-6 rounded-lg">
              <h3 className="text-gray-400 text-sm">Total Platforms</h3>
              <p className="text-3xl font-bold text-white">{stats?.total_platforms || 0}</p>
            </div>
            <div className="bg-gray-800 p-6 rounded-lg">
              <h3 className="text-gray-400 text-sm">Total Content</h3>
              <p className="text-3xl font-bold text-white">{stats?.total_content || 0}</p>
            </div>
            <div className="bg-gray-800 p-6 rounded-lg">
              <h3 className="text-gray-400 text-sm">Success Rate</h3>
              <p className="text-3xl font-bold text-white">{stats?.success_rate || 0}%</p>
            </div>
          </div>
        )}

        {currentPage === 'autopilot' && (
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-xl font-bold text-white mb-4">Autopilot Control</h3>
            <button className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg mr-4">
              Start Autopilot
            </button>
            <button className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg">
              Stop Autopilot
            </button>
          </div>
        )}

        {currentPage === 'sites' && (
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-xl font-bold text-white mb-4">Target Sites</h3>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded mb-4">
              + Add Site
            </button>
            <p className="text-gray-400">No sites added yet</p>
          </div>
        )}

        {currentPage === 'platforms' && (
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-xl font-bold text-white mb-4">Platforms</h3>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded mb-4">
              + Add Platform
            </button>
            <p className="text-gray-400">No platforms added yet</p>
          </div>
        )}

        {currentPage === 'content' && (
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-xl font-bold text-white mb-4">Content Generator</h3>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded mb-4">
              Generate Content
            </button>
            <p className="text-gray-400">No content generated yet</p>
          </div>
        )}

        {currentPage === 'settings' && (
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-xl font-bold text-white mb-4">Settings</h3>
            <p className="text-gray-400">Configure your SEO Monster settings here</p>
          </div>
        )}

        {currentPage === 'diagnostics' && (
          <div className="bg-gray-800 rounded-lg">
            <DiagnosticsPanel />
          </div>
        )}
      </div>
    </div>
  )
}

export default App
