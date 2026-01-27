import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Image,
  Settings,
  ToggleLeft,
  ToggleRight,
  TrendingUp,
  Search,
  Download,
  BarChart3,
  Zap,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Star,
  AlertCircle,
  CheckCircle2,
  Loader2
} from 'lucide-react';

interface ImageProvider {
  name: string;
  enabled: boolean;
  priority: number;
  rate_limit: number;
  has_api_key: boolean;
  requires_attribution: boolean;
  categories: string[];
}

interface ImageStats {
  total_searches: number;
  total_downloads: number;
  cache_hits: number;
  cache_size: number;
  providers_enabled: number;
  providers_total: number;
  provider_usage: Record<string, number>;
}

interface LearningReport {
  total_samples: number;
  provider_scores: Record<string, number>;
  optimal_params: {
    images_per_article: number;
    hero_image_weight: number;
    inline_image_weight: number;
    preferred_providers: string[];
    optimal_image_positions: number[];
  };
  articles_analyzed: number;
  learning_status: string;
}

interface SearchResult {
  id: string;
  url: string;
  thumbnail_url: string;
  width: number;
  height: number;
  provider: string;
  photographer: string;
  alt_text: string;
  tags: string[];
  relevance_score: number;
}

const ImageProvidersManager: React.FC = () => {
  const { t } = useTranslation();
  const [providers, setProviders] = useState<ImageProvider[]>([]);
  const [stats, setStats] = useState<ImageStats | null>(null);
  const [learningReport, setLearningReport] = useState<LearningReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'providers' | 'search' | 'learning' | 'stats'>('providers');
  const [expandedProvider, setExpandedProvider] = useState<string | null>(null);
  
  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchCategory, setSearchCategory] = useState('inline');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [providersRes, statsRes, learningRes] = await Promise.all([
        fetch('/api/images/providers'),
        fetch('/api/images/stats'),
        fetch('/api/images/learning-report')
      ]);

      const providersData = await providersRes.json();
      const statsData = await statsRes.json();
      const learningData = await learningRes.json();

      if (providersData.success) setProviders(providersData.providers);
      if (statsData.success) setStats(statsData.stats);
      if (learningData.success) setLearningReport(learningData.report?.learning_report);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
    setLoading(false);
  };

  const toggleProvider = async (providerName: string, enabled: boolean) => {
    try {
      await fetch('/api/images/providers/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: providerName, enabled })
      });
      setProviders(providers.map(p => 
        p.name === providerName ? { ...p, enabled } : p
      ));
    } catch (error) {
      console.error('Error toggling provider:', error);
    }
  };

  const setPriority = async (providerName: string, priority: number) => {
    try {
      await fetch('/api/images/providers/priority', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: providerName, priority })
      });
      setProviders(providers.map(p => 
        p.name === providerName ? { ...p, priority } : p
      ));
    } catch (error) {
      console.error('Error setting priority:', error);
    }
  };

  const searchImages = async () => {
    if (!searchQuery.trim()) return;
    
    setSearching(true);
    try {
      const response = await fetch('/api/images/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchQuery,
          category: searchCategory,
          count: 12,
          min_width: 800,
          orientation: 'landscape'
        })
      });
      const data = await response.json();
      if (data.success) {
        setSearchResults(data.images);
      }
    } catch (error) {
      console.error('Error searching images:', error);
    }
    setSearching(false);
  };

  const getProviderIcon = (name: string) => {
    const icons: Record<string, string> = {
      unsplash: '📷',
      pexels: '🎨',
      pixabay: '🖼️',
      pinterest: '📌',
      freepik: '✨',
      stocksnap: '📸',
      burst: '🛒',
      kaboompics: '💥',
      reshot: '🔄',
      picjumbo: '🎯'
    };
    return icons[name] || '🖼️';
  };

  const getProviderColor = (name: string) => {
    const colors: Record<string, string> = {
      unsplash: 'from-gray-800 to-gray-900',
      pexels: 'from-green-500 to-green-600',
      pixabay: 'from-green-400 to-teal-500',
      pinterest: 'from-red-500 to-red-600',
      freepik: 'from-blue-500 to-blue-600',
      stocksnap: 'from-purple-500 to-purple-600',
      burst: 'from-green-600 to-green-700',
      kaboompics: 'from-pink-500 to-pink-600',
      reshot: 'from-orange-500 to-orange-600',
      picjumbo: 'from-indigo-500 to-indigo-600'
    };
    return colors[name] || 'from-gray-500 to-gray-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg">
            <Image className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">
              {t('imageProviders.title', 'Image Providers')}
            </h2>
            <p className="text-sm text-gray-400">
              {t('imageProviders.subtitle', 'Manage image sources for content')}
            </p>
          </div>
        </div>
        <button
          onClick={fetchData}
          className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
        >
          <RefreshCw className="w-5 h-5 text-gray-400" />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-gray-800 pb-4">
        {[
          { id: 'providers', icon: Settings, label: t('imageProviders.tabs.providers', 'Providers') },
          { id: 'search', icon: Search, label: t('imageProviders.tabs.search', 'Search') },
          { id: 'learning', icon: TrendingUp, label: t('imageProviders.tabs.learning', 'Learning') },
          { id: 'stats', icon: BarChart3, label: t('imageProviders.tabs.stats', 'Statistics') }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
              activeTab === tab.id
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Providers Tab */}
      {activeTab === 'providers' && (
        <div className="space-y-3">
          {providers.map(provider => (
            <div
              key={provider.name}
              className="bg-gray-800 rounded-lg overflow-hidden"
            >
              <div
                className="flex items-center justify-between p-4 cursor-pointer"
                onClick={() => setExpandedProvider(
                  expandedProvider === provider.name ? null : provider.name
                )}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${getProviderColor(provider.name)} flex items-center justify-center text-xl`}>
                    {getProviderIcon(provider.name)}
                  </div>
                  <div>
                    <h3 className="font-semibold text-white capitalize">
                      {provider.name}
                    </h3>
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <span>{provider.rate_limit} req/hr</span>
                      {provider.has_api_key && (
                        <span className="flex items-center gap-1 text-green-400">
                          <CheckCircle2 className="w-3 h-3" />
                          API Key
                        </span>
                      )}
                      {provider.requires_attribution && (
                        <span className="text-yellow-400">Attribution</span>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-4">
                  {/* Priority */}
                  <div className="flex items-center gap-2">
                    <Star className="w-4 h-4 text-yellow-500" />
                    <span className="text-white font-medium">{provider.priority}</span>
                  </div>
                  
                  {/* Toggle */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleProvider(provider.name, !provider.enabled);
                    }}
                    className={`p-1 rounded transition-colors ${
                      provider.enabled ? 'text-green-500' : 'text-gray-500'
                    }`}
                  >
                    {provider.enabled ? (
                      <ToggleRight className="w-8 h-8" />
                    ) : (
                      <ToggleLeft className="w-8 h-8" />
                    )}
                  </button>
                  
                  {expandedProvider === provider.name ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </div>
              </div>
              
              {/* Expanded Content */}
              {expandedProvider === provider.name && (
                <div className="px-4 pb-4 border-t border-gray-700 pt-4">
                  <div className="grid grid-cols-2 gap-4">
                    {/* Priority Slider */}
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">
                        {t('imageProviders.priority', 'Priority')} (1-10)
                      </label>
                      <input
                        type="range"
                        min="1"
                        max="10"
                        value={provider.priority}
                        onChange={(e) => setPriority(provider.name, parseInt(e.target.value))}
                        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                      />
                      <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>Low</span>
                        <span>High</span>
                      </div>
                    </div>
                    
                    {/* Categories */}
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">
                        {t('imageProviders.categories', 'Categories')}
                      </label>
                      <div className="flex flex-wrap gap-1">
                        {provider.categories.map(cat => (
                          <span
                            key={cat}
                            className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300"
                          >
                            {cat}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  {/* Usage Stats */}
                  {stats?.provider_usage[provider.name] !== undefined && (
                    <div className="mt-4 p-3 bg-gray-700/50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-400">
                          {t('imageProviders.usage', 'Usage')}
                        </span>
                        <span className="text-white font-medium">
                          {stats.provider_usage[provider.name]} {t('imageProviders.images', 'images')}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Search Tab */}
      {activeTab === 'search' && (
        <div>
          <div className="flex gap-3 mb-6">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && searchImages()}
              placeholder={t('imageProviders.searchPlaceholder', 'Search for images...')}
              className="flex-1 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
            <select
              value={searchCategory}
              onChange={(e) => setSearchCategory(e.target.value)}
              className="px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
            >
              <option value="hero">Hero</option>
              <option value="inline">Inline</option>
              <option value="thumbnail">Thumbnail</option>
              <option value="social">Social</option>
              <option value="background">Background</option>
            </select>
            <button
              onClick={searchImages}
              disabled={searching}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded-lg text-white font-medium transition-colors flex items-center gap-2"
            >
              {searching ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Search className="w-5 h-5" />
              )}
              {t('imageProviders.search', 'Search')}
            </button>
          </div>

          {/* Results Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {searchResults.map(image => (
              <div
                key={image.id}
                className="group relative bg-gray-800 rounded-lg overflow-hidden"
              >
                <img
                  src={image.thumbnail_url}
                  alt={image.alt_text}
                  className="w-full h-40 object-cover"
                />
                <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-between p-3">
                  <div className="flex justify-between">
                    <span className="px-2 py-1 bg-white/20 rounded text-xs text-white capitalize">
                      {image.provider}
                    </span>
                    <span className="px-2 py-1 bg-green-500/20 rounded text-xs text-green-400">
                      {(image.relevance_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div>
                    <p className="text-xs text-gray-300 truncate">
                      {image.photographer}
                    </p>
                    <p className="text-xs text-gray-400">
                      {image.width}x{image.height}
                    </p>
                  </div>
                </div>
                <a
                  href={image.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="absolute top-2 right-2 p-1.5 bg-white/20 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <ExternalLink className="w-4 h-4 text-white" />
                </a>
              </div>
            ))}
          </div>

          {searchResults.length === 0 && searchQuery && !searching && (
            <div className="text-center py-12 text-gray-400">
              <Image className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>{t('imageProviders.noResults', 'No images found')}</p>
            </div>
          )}
        </div>
      )}

      {/* Learning Tab */}
      {activeTab === 'learning' && learningReport && (
        <div className="space-y-6">
          {/* Learning Status */}
          <div className="p-4 bg-gray-800 rounded-lg">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-white">
                {t('imageProviders.learningStatus', 'Learning Status')}
              </h3>
              <span className={`px-3 py-1 rounded-full text-sm ${
                learningReport.learning_status === 'active'
                  ? 'bg-green-500/20 text-green-400'
                  : 'bg-yellow-500/20 text-yellow-400'
              }`}>
                {learningReport.learning_status === 'active' 
                  ? t('imageProviders.active', 'Active')
                  : t('imageProviders.collectingData', 'Collecting Data')
                }
              </span>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-gray-700/50 rounded-lg">
                <p className="text-sm text-gray-400">{t('imageProviders.samples', 'Samples')}</p>
                <p className="text-2xl font-bold text-white">{learningReport.total_samples}</p>
              </div>
              <div className="p-3 bg-gray-700/50 rounded-lg">
                <p className="text-sm text-gray-400">{t('imageProviders.articlesAnalyzed', 'Articles Analyzed')}</p>
                <p className="text-2xl font-bold text-white">{learningReport.articles_analyzed}</p>
              </div>
            </div>
          </div>

          {/* Provider Scores */}
          <div className="p-4 bg-gray-800 rounded-lg">
            <h3 className="font-semibold text-white mb-4">
              {t('imageProviders.providerScores', 'Provider Performance Scores')}
            </h3>
            <div className="space-y-3">
              {Object.entries(learningReport.provider_scores)
                .sort(([,a], [,b]) => b - a)
                .map(([provider, score]) => (
                  <div key={provider} className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded bg-gradient-to-br ${getProviderColor(provider)} flex items-center justify-center text-sm`}>
                      {getProviderIcon(provider)}
                    </div>
                    <span className="text-white capitalize w-24">{provider}</span>
                    <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all"
                        style={{ width: `${score * 100}%` }}
                      />
                    </div>
                    <span className="text-white font-medium w-16 text-right">
                      {(score * 100).toFixed(1)}%
                    </span>
                  </div>
                ))}
            </div>
          </div>

          {/* Optimal Parameters */}
          <div className="p-4 bg-gray-800 rounded-lg">
            <h3 className="font-semibold text-white mb-4">
              {t('imageProviders.optimalParams', 'Learned Optimal Parameters')}
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-gray-700/50 rounded-lg">
                <p className="text-sm text-gray-400">
                  {t('imageProviders.imagesPerArticle', 'Images per Article')}
                </p>
                <p className="text-xl font-bold text-white">
                  {learningReport.optimal_params.images_per_article}
                </p>
              </div>
              <div className="p-3 bg-gray-700/50 rounded-lg">
                <p className="text-sm text-gray-400">
                  {t('imageProviders.preferredProviders', 'Preferred Providers')}
                </p>
                <div className="flex gap-1 mt-1">
                  {learningReport.optimal_params.preferred_providers.map(p => (
                    <span key={p} className="px-2 py-1 bg-blue-500/20 rounded text-xs text-blue-400 capitalize">
                      {p}
                    </span>
                  ))}
                </div>
              </div>
              <div className="p-3 bg-gray-700/50 rounded-lg col-span-2">
                <p className="text-sm text-gray-400">
                  {t('imageProviders.optimalPositions', 'Optimal Image Positions (paragraphs)')}
                </p>
                <div className="flex gap-2 mt-1">
                  {learningReport.optimal_params.optimal_image_positions.map((pos, i) => (
                    <span key={i} className="px-3 py-1 bg-purple-500/20 rounded text-purple-400">
                      #{pos}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stats Tab */}
      {activeTab === 'stats' && stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 bg-gradient-to-br from-blue-500/20 to-blue-600/20 rounded-lg border border-blue-500/30">
            <Search className="w-8 h-8 text-blue-400 mb-2" />
            <p className="text-sm text-gray-400">{t('imageProviders.totalSearches', 'Total Searches')}</p>
            <p className="text-2xl font-bold text-white">{stats.total_searches}</p>
          </div>
          <div className="p-4 bg-gradient-to-br from-green-500/20 to-green-600/20 rounded-lg border border-green-500/30">
            <Download className="w-8 h-8 text-green-400 mb-2" />
            <p className="text-sm text-gray-400">{t('imageProviders.totalDownloads', 'Total Downloads')}</p>
            <p className="text-2xl font-bold text-white">{stats.total_downloads}</p>
          </div>
          <div className="p-4 bg-gradient-to-br from-purple-500/20 to-purple-600/20 rounded-lg border border-purple-500/30">
            <Zap className="w-8 h-8 text-purple-400 mb-2" />
            <p className="text-sm text-gray-400">{t('imageProviders.cacheHits', 'Cache Hits')}</p>
            <p className="text-2xl font-bold text-white">{stats.cache_hits}</p>
          </div>
          <div className="p-4 bg-gradient-to-br from-orange-500/20 to-orange-600/20 rounded-lg border border-orange-500/30">
            <Settings className="w-8 h-8 text-orange-400 mb-2" />
            <p className="text-sm text-gray-400">{t('imageProviders.activeProviders', 'Active Providers')}</p>
            <p className="text-2xl font-bold text-white">
              {stats.providers_enabled}/{stats.providers_total}
            </p>
          </div>

          {/* Provider Usage Chart */}
          <div className="col-span-2 md:col-span-4 p-4 bg-gray-800 rounded-lg">
            <h3 className="font-semibold text-white mb-4">
              {t('imageProviders.usageByProvider', 'Usage by Provider')}
            </h3>
            <div className="space-y-2">
              {Object.entries(stats.provider_usage)
                .sort(([,a], [,b]) => b - a)
                .map(([provider, usage]) => {
                  const maxUsage = Math.max(...Object.values(stats.provider_usage));
                  const percentage = maxUsage > 0 ? (usage / maxUsage) * 100 : 0;
                  return (
                    <div key={provider} className="flex items-center gap-3">
                      <span className="text-white capitalize w-24">{provider}</span>
                      <div className="flex-1 h-6 bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full bg-gradient-to-r ${getProviderColor(provider)} rounded-full transition-all flex items-center justify-end pr-2`}
                          style={{ width: `${percentage}%` }}
                        >
                          <span className="text-xs text-white font-medium">
                            {usage}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageProvidersManager;
