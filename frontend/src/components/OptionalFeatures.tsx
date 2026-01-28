import { useState, useEffect } from 'react'
import axios from 'axios'
import { useLanguage } from '../contexts/LanguageContext'
import { useTheme } from './ThemeToggle'

const API_URL = 'http://144.31.238.16:8000/api'

interface Feature {
  id: string
  name: string
  name_ru: string
  description: string
  description_ru: string
  icon: string
  status: 'configured' | 'not_configured' | 'partially_configured'
  config_url: string
  benefits: string[]
  benefits_ru: string[]
  requirements: Array<{ name: string; configured: boolean }>
  progress: number
}

interface SetupProgress {
  core: {
    components: Array<{ id: string; name: string; name_ru: string; configured: boolean }>
    total: number
    configured: number
    progress: number
  }
  optional: {
    components: Array<{ id: string; name: string; name_ru: string; configured: boolean; icon: string }>
    total: number
    configured: number
    progress: number
  }
  overall: {
    total: number
    configured: number
    progress: number
  }
}

interface Props {
  onNavigate: (page: string) => void
}

export function OptionalFeaturesCard({ onNavigate }: Props) {
  const [features, setFeatures] = useState<Feature[]>([])
  const [loading, setLoading] = useState(true)
  const { language } = useLanguage()
  const { theme } = useTheme()

  useEffect(() => {
    fetchFeatures()
  }, [])

  const fetchFeatures = async () => {
    try {
      const response = await axios.get(`${API_URL}/features/optional`)
      setFeatures(response.data)
    } catch (error) {
      console.error('Error fetching features:', error)
    } finally {
      setLoading(false)
    }
  }

  const notConfigured = features.filter(f => f.status === 'not_configured')
  const configured = features.filter(f => f.status === 'configured')

  if (loading) {
    return (
      <div className={`p-6 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
        <div className="animate-pulse">
          <div className={`h-6 ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-200'} rounded w-1/3 mb-4`}></div>
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className={`h-16 ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-200'} rounded`}></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (notConfigured.length === 0) {
    return (
      <div className={`p-6 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
        <div className="flex items-center gap-3 mb-4">
          <span className="text-2xl">✅</span>
          <h3 className={`text-xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
            {language === 'ru' ? 'Все функции настроены!' : 'All Features Configured!'}
          </h3>
        </div>
        <p className={`${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
          {language === 'ru' 
            ? 'Вы используете все возможности SEO Monster.' 
            : 'You are using all SEO Monster capabilities.'}
        </p>
      </div>
    )
  }

  return (
    <div className={`p-6 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
      <div className="flex items-center gap-3 mb-4">
        <span className="text-2xl">🔓</span>
        <h3 className={`text-xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
          {language === 'ru' ? 'Разблокируйте больше функций' : 'Unlock More Features'}
        </h3>
        <span className={`px-2 py-1 text-xs rounded-full ${theme === 'dark' ? 'bg-blue-900 text-blue-300' : 'bg-blue-100 text-blue-700'}`}>
          {notConfigured.length} {language === 'ru' ? 'доступно' : 'available'}
        </span>
      </div>
      
      <div className="space-y-3">
        {notConfigured.slice(0, 4).map(feature => (
          <div 
            key={feature.id}
            className={`p-4 rounded-lg border transition-all duration-200 cursor-pointer hover:shadow-md ${
              theme === 'dark' 
                ? 'bg-gray-750 border-gray-600 hover:border-blue-500' 
                : 'bg-gray-50 border-gray-200 hover:border-blue-400'
            }`}
            onClick={() => onNavigate(feature.config_url.replace('/', ''))}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{feature.icon}</span>
                <div>
                  <h4 className={`font-semibold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                    {language === 'ru' ? feature.name_ru : feature.name}
                  </h4>
                  <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                    {language === 'ru' ? feature.description_ru : feature.description}
                  </p>
                </div>
              </div>
              <button className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                theme === 'dark'
                  ? 'bg-blue-600 hover:bg-blue-700 text-white'
                  : 'bg-blue-500 hover:bg-blue-600 text-white'
              }`}>
                {language === 'ru' ? 'Настроить' : 'Configure'} →
              </button>
            </div>
          </div>
        ))}
      </div>
      
      {notConfigured.length > 4 && (
        <button 
          onClick={() => onNavigate('settings')}
          className={`mt-4 w-full py-2 text-center text-sm rounded-lg transition-colors ${
            theme === 'dark'
              ? 'text-blue-400 hover:bg-gray-700'
              : 'text-blue-600 hover:bg-gray-100'
          }`}
        >
          {language === 'ru' 
            ? `Показать все ${notConfigured.length} функций` 
            : `Show all ${notConfigured.length} features`}
        </button>
      )}
    </div>
  )
}

export function SetupProgressBar() {
  const [progress, setProgress] = useState<SetupProgress | null>(null)
  const [loading, setLoading] = useState(true)
  const { language } = useLanguage()
  const { theme } = useTheme()

  useEffect(() => {
    fetchProgress()
  }, [])

  const fetchProgress = async () => {
    try {
      const response = await axios.get(`${API_URL}/features/setup-progress`)
      setProgress(response.data)
    } catch (error) {
      console.error('Error fetching progress:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading || !progress) {
    return (
      <div className={`p-6 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
        <div className="animate-pulse">
          <div className={`h-4 ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-200'} rounded w-1/2 mb-4`}></div>
          <div className={`h-3 ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-200'} rounded w-full`}></div>
        </div>
      </div>
    )
  }

  const getProgressColor = (percent: number) => {
    if (percent >= 80) return 'bg-green-500'
    if (percent >= 50) return 'bg-yellow-500'
    return 'bg-blue-500'
  }

  return (
    <div className={`p-6 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className={`text-lg font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
          {language === 'ru' ? 'Настройка системы' : 'System Setup'}
        </h3>
        <span className={`text-2xl font-bold ${
          progress.overall.progress >= 80 ? 'text-green-500' : 
          progress.overall.progress >= 50 ? 'text-yellow-500' : 'text-blue-500'
        }`}>
          {progress.overall.progress}%
        </span>
      </div>
      
      {/* Progress Bar */}
      <div className={`h-3 rounded-full overflow-hidden mb-4 ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-200'}`}>
        <div 
          className={`h-full transition-all duration-500 ${getProgressColor(progress.overall.progress)}`}
          style={{ width: `${progress.overall.progress}%` }}
        />
      </div>
      
      {/* Components Grid */}
      <div className="grid grid-cols-2 gap-4">
        {/* Core Components */}
        <div>
          <h4 className={`text-sm font-medium mb-2 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
            {language === 'ru' ? 'Основные компоненты' : 'Core Components'}
          </h4>
          <div className="space-y-1">
            {progress.core.components.map(comp => (
              <div key={comp.id} className="flex items-center gap-2">
                <span className={comp.configured ? 'text-green-500' : 'text-gray-400'}>
                  {comp.configured ? '✓' : '○'}
                </span>
                <span className={`text-sm ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
                  {language === 'ru' ? comp.name_ru : comp.name}
                </span>
              </div>
            ))}
          </div>
        </div>
        
        {/* Optional Components */}
        <div>
          <h4 className={`text-sm font-medium mb-2 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
            {language === 'ru' ? 'Опциональные функции' : 'Optional Features'}
          </h4>
          <div className="space-y-1">
            {progress.optional.components.map(comp => (
              <div key={comp.id} className="flex items-center gap-2">
                <span className={comp.configured ? 'text-green-500' : 'text-gray-400'}>
                  {comp.configured ? '✓' : '○'}
                </span>
                <span className="text-sm">{comp.icon}</span>
                <span className={`text-sm ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
                  {language === 'ru' ? comp.name_ru : comp.name}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export function FeatureHint({ featureId, onConfigure }: { featureId: string; onConfigure: () => void }) {
  const [feature, setFeature] = useState<Feature | null>(null)
  const [loading, setLoading] = useState(true)
  const [dismissed, setDismissed] = useState(false)
  const { language } = useLanguage()
  const { theme } = useTheme()

  useEffect(() => {
    fetchFeature()
  }, [featureId])

  const fetchFeature = async () => {
    try {
      const response = await axios.get(`${API_URL}/features/optional/${featureId}`)
      setFeature(response.data)
    } catch (error) {
      console.error('Error fetching feature:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading || !feature || feature.status === 'configured' || dismissed) {
    return null
  }

  return (
    <div className={`p-4 rounded-lg border-l-4 border-blue-500 mb-6 ${
      theme === 'dark' ? 'bg-blue-900/20' : 'bg-blue-50'
    }`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <span className="text-2xl">💡</span>
          <div>
            <h4 className={`font-semibold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
              {language === 'ru' ? `${feature.name_ru} не настроен` : `${feature.name} Not Configured`}
            </h4>
            <p className={`text-sm mt-1 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>
              {language === 'ru' 
                ? 'Добавьте учетные данные для разблокировки:'
                : 'Add credentials to unlock:'}
            </p>
            <ul className={`mt-2 space-y-1 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
              {(language === 'ru' ? feature.benefits_ru : feature.benefits).slice(0, 3).map((benefit, i) => (
                <li key={i} className="text-sm flex items-center gap-2">
                  <span className="text-green-500">•</span>
                  {benefit}
                </li>
              ))}
            </ul>
            <div className="flex gap-3 mt-3">
              <button 
                onClick={onConfigure}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
              >
                {language === 'ru' ? 'Настроить сейчас' : 'Configure Now'}
              </button>
              <button 
                onClick={() => setDismissed(true)}
                className={`px-4 py-2 rounded-lg text-sm transition-colors ${
                  theme === 'dark' 
                    ? 'text-gray-400 hover:bg-gray-700' 
                    : 'text-gray-500 hover:bg-gray-100'
                }`}
              >
                {language === 'ru' ? 'Позже' : 'Later'}
              </button>
            </div>
          </div>
        </div>
        <button 
          onClick={() => setDismissed(true)}
          className={`p-1 rounded hover:bg-gray-200 ${theme === 'dark' ? 'text-gray-400 hover:bg-gray-700' : 'text-gray-400'}`}
        >
          ✕
        </button>
      </div>
    </div>
  )
}

export default OptionalFeaturesCard
