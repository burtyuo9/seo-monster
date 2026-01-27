import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

interface AIProvider {
  name: string;
  display_name: string;
  type: string;
  model: string;
  is_free: boolean;
  rate_limit: number;
  max_tokens: number;
  enabled: boolean;
  priority: number;
  has_api_key: boolean;
}

interface AIAgent {
  name: string;
  role: string;
  provider: string;
  model: string;
  capabilities: string[];
  is_active: boolean;
  success_rate: number;
  total_requests: number;
}

interface ExternalService {
  id: string;
  name: string;
  url: string;
  capabilities: string[];
  is_free: boolean;
  description: string;
  connected: boolean;
}

const AIProvidersManager: React.FC = () => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<'providers' | 'agents' | 'external'>('providers');
  const [providers, setProviders] = useState<AIProvider[]>([]);
  const [agents, setAgents] = useState<AIAgent[]>([]);
  const [externalServices, setExternalServices] = useState<ExternalService[]>([]);
  const [loading, setLoading] = useState(true);
  const [apiKeyModal, setApiKeyModal] = useState<{open: boolean; provider: string}>({open: false, provider: ''});
  const [apiKeyInput, setApiKeyInput] = useState('');
  
  // Главный переключатель AI Agents
  const [aiAgentsEnabled, setAiAgentsEnabled] = useState(true);

  // Демо данные для провайдеров
  const demoProviders: AIProvider[] = [
    { name: 'groq', display_name: 'Groq (Free)', type: 'groq', model: 'llama-3.3-70b-versatile', is_free: true, rate_limit: 30, max_tokens: 8192, enabled: true, priority: 1, has_api_key: true },
    { name: 'together', display_name: 'Together AI (Free Tier)', type: 'together', model: 'meta-llama/Llama-3.3-70B-Instruct-Turbo', is_free: true, rate_limit: 60, max_tokens: 4096, enabled: true, priority: 2, has_api_key: false },
    { name: 'huggingface', display_name: 'HuggingFace (Free)', type: 'huggingface', model: 'mistralai/Mixtral-8x7B-Instruct-v0.1', is_free: true, rate_limit: 30, max_tokens: 4096, enabled: true, priority: 3, has_api_key: false },
    { name: 'ollama', display_name: 'Ollama (Local)', type: 'ollama', model: 'llama3.2', is_free: true, rate_limit: 1000, max_tokens: 8192, enabled: false, priority: 4, has_api_key: false },
    { name: 'cohere', display_name: 'Cohere (Free Tier)', type: 'cohere', model: 'command-r-plus', is_free: true, rate_limit: 20, max_tokens: 4096, enabled: true, priority: 5, has_api_key: false },
    { name: 'mistral', display_name: 'Mistral AI (Free)', type: 'mistral', model: 'mistral-large-latest', is_free: true, rate_limit: 30, max_tokens: 8192, enabled: true, priority: 6, has_api_key: false },
    { name: 'deepseek', display_name: 'DeepSeek (Free Tier)', type: 'deepseek', model: 'deepseek-chat', is_free: true, rate_limit: 60, max_tokens: 8192, enabled: true, priority: 7, has_api_key: false },
    { name: 'openrouter', display_name: 'OpenRouter (Free Models)', type: 'openrouter', model: 'meta-llama/llama-3.2-3b-instruct:free', is_free: true, rate_limit: 20, max_tokens: 4096, enabled: true, priority: 8, has_api_key: false },
    { name: 'google_gemini', display_name: 'Google Gemini (Free)', type: 'google_gemini', model: 'gemini-1.5-flash', is_free: true, rate_limit: 60, max_tokens: 8192, enabled: true, priority: 9, has_api_key: false },
    { name: 'cloudflare', display_name: 'Cloudflare Workers AI (Free)', type: 'cloudflare', model: '@cf/meta/llama-3.1-8b-instruct', is_free: true, rate_limit: 50, max_tokens: 2048, enabled: false, priority: 10, has_api_key: false },
  ];

  // Демо данные для агентов
  const demoAgents: AIAgent[] = [
    { name: 'seo_writer', role: 'content_writer', provider: 'groq', model: 'llama-3.3-70b-versatile', capabilities: ['article_writing', 'meta_tags', 'headlines'], is_active: true, success_rate: 0.98, total_requests: 156 },
    { name: 'keyword_specialist', role: 'keyword_researcher', provider: 'together', model: 'Llama-3.3-70B', capabilities: ['keyword_analysis', 'search_intent', 'long_tail'], is_active: true, success_rate: 0.95, total_requests: 89 },
    { name: 'competitor_analyst', role: 'competitor_analyst', provider: 'groq', model: 'llama-3.3-70b-versatile', capabilities: ['competitor_analysis', 'gap_analysis', 'strategy'], is_active: true, success_rate: 0.97, total_requests: 45 },
    { name: 'tech_seo_expert', role: 'seo_analyst', provider: 'deepseek', model: 'deepseek-chat', capabilities: ['technical_audit', 'schema_markup', 'speed_optimization'], is_active: true, success_rate: 0.99, total_requests: 67 },
    { name: 'content_editor', role: 'editor', provider: 'cohere', model: 'command-r-plus', capabilities: ['proofreading', 'style_editing', 'readability'], is_active: true, success_rate: 0.96, total_requests: 234 },
    { name: 'translator', role: 'translator', provider: 'groq', model: 'llama-3.3-70b-versatile', capabilities: ['translation', 'localization', 'multilingual_seo'], is_active: true, success_rate: 0.94, total_requests: 78 },
    { name: 'data_analyst', role: 'data_analyst', provider: 'together', model: 'Llama-3.3-70B', capabilities: ['analytics', 'reporting', 'forecasting'], is_active: true, success_rate: 0.97, total_requests: 112 },
    { name: 'creative_writer', role: 'creative_writer', provider: 'openrouter', model: 'llama-3.2-3b', capabilities: ['creative_writing', 'storytelling', 'viral_content'], is_active: false, success_rate: 0.91, total_requests: 34 },
    { name: 'fact_checker', role: 'fact_checker', provider: 'huggingface', model: 'Mixtral-8x7B', capabilities: ['fact_checking', 'source_verification', 'accuracy_review'], is_active: true, success_rate: 0.99, total_requests: 189 },
  ];

  // Демо данные для внешних сервисов
  const demoExternalServices: ExternalService[] = [
    { id: 'perplexity', name: 'Perplexity AI', url: 'https://api.perplexity.ai', capabilities: ['search', 'research', 'fact_checking'], is_free: true, description: 'AI-powered search engine with real-time information', connected: true },
    { id: 'you_com', name: 'You.com AI', url: 'https://api.you.com', capabilities: ['search', 'chat', 'code'], is_free: true, description: 'AI search assistant with multiple modes', connected: false },
    { id: 'phind', name: 'Phind', url: 'https://api.phind.com', capabilities: ['code', 'technical_search'], is_free: true, description: 'AI search engine for developers', connected: false },
    { id: 'poe', name: 'Poe by Quora', url: 'https://poe.com/api', capabilities: ['chat', 'multiple_models'], is_free: true, description: 'Access to multiple AI models through one interface', connected: true },
    { id: 'chatgpt_free', name: 'ChatGPT (Free)', url: 'https://chat.openai.com', capabilities: ['chat', 'analysis', 'writing'], is_free: true, description: 'OpenAI\'s ChatGPT free tier', connected: false },
    { id: 'claude_free', name: 'Claude (Free)', url: 'https://claude.ai', capabilities: ['chat', 'analysis', 'coding'], is_free: true, description: 'Anthropic\'s Claude free tier', connected: false },
    { id: 'gemini_free', name: 'Google Gemini (Free)', url: 'https://gemini.google.com', capabilities: ['chat', 'multimodal', 'search'], is_free: true, description: 'Google\'s Gemini AI free tier', connected: true },
    { id: 'copilot_free', name: 'Microsoft Copilot (Free)', url: 'https://copilot.microsoft.com', capabilities: ['chat', 'search', 'image_generation'], is_free: true, description: 'Microsoft\'s AI assistant with Bing integration', connected: false },
    { id: 'huggingchat', name: 'HuggingChat', url: 'https://huggingface.co/chat', capabilities: ['chat', 'open_source_models'], is_free: true, description: 'Free chat interface for open-source models', connected: true },
    { id: 'forefront', name: 'Forefront AI', url: 'https://chat.forefront.ai', capabilities: ['chat', 'personas', 'multiple_models'], is_free: true, description: 'Free access to GPT-4 and Claude with personas', connected: false },
  ];

  useEffect(() => {
    // Загрузка данных
    setProviders(demoProviders);
    setAgents(demoAgents);
    setExternalServices(demoExternalServices);
    setLoading(false);
  }, []);

  const toggleProvider = (name: string) => {
    setProviders(prev => prev.map(p => 
      p.name === name ? {...p, enabled: !p.enabled} : p
    ));
  };

  const toggleAgent = (name: string) => {
    setAgents(prev => prev.map(a => 
      a.name === name ? {...a, is_active: !a.is_active} : a
    ));
  };

  const toggleService = (id: string) => {
    setExternalServices(prev => prev.map(s => 
      s.id === id ? {...s, connected: !s.connected} : s
    ));
  };

  const handleSetApiKey = (provider: string) => {
    setApiKeyModal({open: true, provider});
  };

  const saveApiKey = () => {
    setProviders(prev => prev.map(p => 
      p.name === apiKeyModal.provider ? {...p, has_api_key: true} : p
    ));
    setApiKeyModal({open: false, provider: ''});
    setApiKeyInput('');
  };

  const getRoleIcon = (role: string) => {
    const icons: Record<string, string> = {
      content_writer: '✍️',
      keyword_researcher: '🔍',
      competitor_analyst: '📊',
      seo_analyst: '⚙️',
      editor: '📝',
      translator: '🌐',
      data_analyst: '📈',
      creative_writer: '🎨',
      fact_checker: '✅',
    };
    return icons[role] || '🤖';
  };

  // Переключение модуля AI Agents
  const toggleAiAgents = async () => {
    const newState = !aiAgentsEnabled;
    setAiAgentsEnabled(newState);
    
    // Отправка на сервер
    try {
      await fetch('/api/ai-agents/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: newState })
      });
    } catch (error) {
      console.log('AI Agents toggle saved locally');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-900 min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">🤖 AI Providers & Agents</h1>
            <p className="text-gray-400">Управление AI-провайдерами, агентами и внешними сервисами</p>
          </div>
          
          {/* ГЛАВНЫЙ ПЕРЕКЛЮЧАТЕЛЬ AI AGENTS */}
          <div className={`p-4 rounded-xl border-2 transition-all duration-300 ${
            aiAgentsEnabled 
              ? 'bg-gradient-to-r from-green-600/20 to-emerald-600/20 border-green-500' 
              : 'bg-gradient-to-r from-red-600/20 to-orange-600/20 border-red-500'
          }`}>
            <div className="flex items-center gap-4">
              <div className="text-center">
                <div className="text-sm text-gray-400 mb-1">Модуль AI Agents</div>
                <div className={`text-lg font-bold ${aiAgentsEnabled ? 'text-green-400' : 'text-red-400'}`}>
                  {aiAgentsEnabled ? '✅ ВКЛЮЧЕН' : '❌ ВЫКЛЮЧЕН'}
                </div>
              </div>
              
              {/* Toggle Switch */}
              <button
                onClick={toggleAiAgents}
                className={`relative w-16 h-8 rounded-full transition-all duration-300 ${
                  aiAgentsEnabled ? 'bg-green-500' : 'bg-red-500'
                }`}
              >
                <div className={`absolute top-1 w-6 h-6 bg-white rounded-full shadow-lg transition-all duration-300 ${
                  aiAgentsEnabled ? 'left-9' : 'left-1'
                }`}>
                  <span className="flex items-center justify-center h-full text-sm">
                    {aiAgentsEnabled ? '🤖' : '🚫'}
                  </span>
                </div>
              </button>
            </div>
            
            <div className="mt-2 text-xs text-gray-500">
              {aiAgentsEnabled 
                ? 'Агенты активно участвуют в SEO-задачах' 
                : 'Monster работает в базовом режиме'
              }
            </div>
          </div>
        </div>
      </div>
      
      {/* Предупреждение при выключенном модуле */}
      {!aiAgentsEnabled && (
        <div className="mb-6 p-4 bg-yellow-900/30 border border-yellow-600 rounded-xl">
          <div className="flex items-center gap-3">
            <span className="text-2xl">⚠️</span>
            <div>
              <div className="text-yellow-400 font-semibold">Модуль AI Agents выключен</div>
              <div className="text-yellow-200/70 text-sm">
                SEO Monster работает в базовом режиме без параллельной обработки и самообучения.
                Включите модуль для максимальной эффективности.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-gradient-to-br from-purple-600 to-purple-800 rounded-xl p-4">
          <div className="text-3xl font-bold text-white">{providers.filter(p => p.enabled).length}</div>
          <div className="text-purple-200">Активных провайдеров</div>
        </div>
        <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl p-4">
          <div className="text-3xl font-bold text-white">{agents.filter(a => a.is_active).length}</div>
          <div className="text-blue-200">Активных агентов</div>
        </div>
        <div className="bg-gradient-to-br from-green-600 to-green-800 rounded-xl p-4">
          <div className="text-3xl font-bold text-white">{externalServices.filter(s => s.connected).length}</div>
          <div className="text-green-200">Подключенных сервисов</div>
        </div>
        <div className="bg-gradient-to-br from-orange-600 to-orange-800 rounded-xl p-4">
          <div className="text-3xl font-bold text-white">{providers.filter(p => p.is_free).length}</div>
          <div className="text-orange-200">Бесплатных LLM</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 mb-6">
        <button
          onClick={() => setActiveTab('providers')}
          className={`px-6 py-3 rounded-lg font-medium transition-all ${
            activeTab === 'providers' 
              ? 'bg-purple-600 text-white' 
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
          }`}
        >
          🔌 LLM Провайдеры ({providers.length})
        </button>
        <button
          onClick={() => setActiveTab('agents')}
          className={`px-6 py-3 rounded-lg font-medium transition-all ${
            activeTab === 'agents' 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
          }`}
        >
          🤖 AI Агенты ({agents.length})
        </button>
        <button
          onClick={() => setActiveTab('external')}
          className={`px-6 py-3 rounded-lg font-medium transition-all ${
            activeTab === 'external' 
              ? 'bg-green-600 text-white' 
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
          }`}
        >
          🌐 Внешние AI ({externalServices.length})
        </button>
      </div>

      {/* Content */}
      {activeTab === 'providers' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {providers.map(provider => (
            <div 
              key={provider.name}
              className={`bg-gray-800 rounded-xl p-5 border-2 transition-all ${
                provider.enabled ? 'border-purple-500' : 'border-gray-700'
              }`}
            >
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className="text-lg font-semibold text-white">{provider.display_name}</h3>
                  <p className="text-sm text-gray-400">{provider.model}</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  provider.is_free ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
                }`}>
                  {provider.is_free ? '✓ FREE' : 'PAID'}
                </span>
              </div>
              
              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Rate Limit:</span>
                  <span className="text-white">{provider.rate_limit}/min</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Max Tokens:</span>
                  <span className="text-white">{provider.max_tokens.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Priority:</span>
                  <span className="text-white">#{provider.priority}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">API Key:</span>
                  <span className={provider.has_api_key ? 'text-green-400' : 'text-red-400'}>
                    {provider.has_api_key ? '✓ Set' : '✗ Not set'}
                  </span>
                </div>
              </div>

              <div className="flex space-x-2">
                <button
                  onClick={() => toggleProvider(provider.name)}
                  className={`flex-1 py-2 rounded-lg font-medium transition-all ${
                    provider.enabled 
                      ? 'bg-purple-600 text-white hover:bg-purple-700' 
                      : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                  }`}
                >
                  {provider.enabled ? '✓ Enabled' : 'Enable'}
                </button>
                <button
                  onClick={() => handleSetApiKey(provider.name)}
                  className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-all"
                >
                  🔑
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'agents' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map(agent => (
            <div 
              key={agent.name}
              className={`bg-gray-800 rounded-xl p-5 border-2 transition-all ${
                agent.is_active ? 'border-blue-500' : 'border-gray-700'
              }`}
            >
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center space-x-3">
                  <span className="text-3xl">{getRoleIcon(agent.role)}</span>
                  <div>
                    <h3 className="text-lg font-semibold text-white">{agent.name}</h3>
                    <p className="text-sm text-gray-400">{agent.role.replace('_', ' ')}</p>
                  </div>
                </div>
              </div>
              
              <div className="space-y-2 mb-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Provider:</span>
                  <span className="text-white">{agent.provider}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Success Rate:</span>
                  <span className={`font-medium ${agent.success_rate >= 0.95 ? 'text-green-400' : 'text-yellow-400'}`}>
                    {(agent.success_rate * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Total Requests:</span>
                  <span className="text-white">{agent.total_requests}</span>
                </div>
              </div>

              <div className="flex flex-wrap gap-1 mb-4">
                {agent.capabilities.slice(0, 3).map(cap => (
                  <span key={cap} className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs">
                    {cap}
                  </span>
                ))}
              </div>

              <button
                onClick={() => toggleAgent(agent.name)}
                className={`w-full py-2 rounded-lg font-medium transition-all ${
                  agent.is_active 
                    ? 'bg-blue-600 text-white hover:bg-blue-700' 
                    : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                }`}
              >
                {agent.is_active ? '✓ Active' : 'Activate'}
              </button>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'external' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {externalServices.map(service => (
            <div 
              key={service.id}
              className={`bg-gray-800 rounded-xl p-5 border-2 transition-all ${
                service.connected ? 'border-green-500' : 'border-gray-700'
              }`}
            >
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className="text-lg font-semibold text-white">{service.name}</h3>
                  <p className="text-sm text-gray-400 truncate">{service.url}</p>
                </div>
                <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs font-medium">
                  FREE
                </span>
              </div>
              
              <p className="text-sm text-gray-400 mb-3 line-clamp-2">{service.description}</p>

              <div className="flex flex-wrap gap-1 mb-4">
                {service.capabilities.map(cap => (
                  <span key={cap} className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs">
                    {cap}
                  </span>
                ))}
              </div>

              <button
                onClick={() => toggleService(service.id)}
                className={`w-full py-2 rounded-lg font-medium transition-all ${
                  service.connected 
                    ? 'bg-green-600 text-white hover:bg-green-700' 
                    : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                }`}
              >
                {service.connected ? '✓ Connected' : 'Connect'}
              </button>
            </div>
          ))}
        </div>
      )}

      {/* API Key Modal */}
      {apiKeyModal.open && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-xl p-6 w-full max-w-md">
            <h3 className="text-xl font-semibold text-white mb-4">
              🔑 Set API Key for {apiKeyModal.provider}
            </h3>
            <input
              type="password"
              value={apiKeyInput}
              onChange={(e) => setApiKeyInput(e.target.value)}
              placeholder="Enter your API key..."
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white mb-4 focus:outline-none focus:border-purple-500"
            />
            <div className="flex space-x-3">
              <button
                onClick={() => setApiKeyModal({open: false, provider: ''})}
                className="flex-1 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600"
              >
                Cancel
              </button>
              <button
                onClick={saveApiKey}
                className="flex-1 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                Save Key
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIProvidersManager;
