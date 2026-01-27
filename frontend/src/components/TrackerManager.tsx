import React, { useState, useEffect } from 'react';

interface BotStats {
  total_checks: number;
  bots_detected: number;
  humans_passed: number;
  bot_rate: number;
  known_bot_fingerprints: number;
  known_bot_ips: number;
}

interface TrafficStats {
  today: {
    clicks: number;
    unique_clicks: number;
    bots: number;
    conversions: number;
    revenue: number;
    cr: number;
    epc: number;
  };
  week: {
    clicks: number;
    conversions: number;
    revenue: number;
  };
  bot_rate: number;
}

interface RealtimeStats {
  clicks: number;
  unique_clicks: number;
  bots: number;
  conversions: number;
  countries: Record<string, number>;
}

const API_URL = 'http://localhost:8000';

const TrackerManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'bot-detection' | 'stats' | 'filters' | 'routing'>('overview');
  const [botStats, setBotStats] = useState<BotStats | null>(null);
  const [trafficStats, setTrafficStats] = useState<TrafficStats | null>(null);
  const [realtimeStats, setRealtimeStats] = useState<RealtimeStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [botProtectionEnabled, setBotProtectionEnabled] = useState(true);
  const [autoBlockBots, setAutoBlockBots] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchRealtimeStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchBotStats(),
        fetchTrafficStats(),
        fetchRealtimeStats()
      ]);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
    setLoading(false);
  };

  const fetchBotStats = async () => {
    try {
      const res = await fetch(`${API_URL}/api/tds/bot-detection/stats`);
      if (res.ok) {
        const data = await res.json();
        setBotStats(data);
      }
    } catch (error) {
      console.error('Error fetching bot stats:', error);
    }
  };

  const fetchTrafficStats = async () => {
    try {
      const res = await fetch(`${API_URL}/api/tds/stats/overview`);
      if (res.ok) {
        const data = await res.json();
        setTrafficStats(data);
      }
    } catch (error) {
      console.error('Error fetching traffic stats:', error);
    }
  };

  const fetchRealtimeStats = async () => {
    try {
      const res = await fetch(`${API_URL}/api/tds/stats/realtime?minutes=60`);
      if (res.ok) {
        const data = await res.json();
        setRealtimeStats(data);
      }
    } catch (error) {
      console.error('Error fetching realtime stats:', error);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'bot-detection', label: 'Bot Detection', icon: '🤖' },
    { id: 'stats', label: 'Statistics', icon: '📈' },
    { id: 'filters', label: 'Filters', icon: '🔍' },
    { id: 'routing', label: 'Routing', icon: '🔀' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Traffic Tracker</h2>
          <p className="text-gray-400 text-sm">Keitaro-style traffic management system</p>
        </div>
        <div className="flex items-center gap-4
">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400">Bot Protection</span>
            <button
              onClick={() => setBotProtectionEnabled(!botProtectionEnabled)}
              className={`px-3 py-1 rounded text-sm font-medium ${
                botProtectionEnabled ? 'bg-green-600 text-white' : 'bg-gray-700 text-gray-400'
              }`}
            >
              {botProtectionEnabled ? 'ON' : 'OFF'}
            </button>
          </div>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-700 pb-2">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-4 py-2 rounded-t-lg text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'bg-gray-800 text-white border-b-2 border-blue-500'
                : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            }`}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <>
          {activeTab === 'overview' && (
            <OverviewTab 
              botStats={botStats} 
              trafficStats={trafficStats} 
              realtimeStats={realtimeStats}
            />
          )}
          {activeTab === 'bot-detection' && (
            <BotDetectionTab 
              botStats={botStats}
              autoBlockBots={autoBlockBots}
              setAutoBlockBots={setAutoBlockBots}
            />
          )}
          {activeTab === 'stats' && <StatisticsTab />}
          {activeTab === 'filters' && <FiltersTab />}
          {activeTab === 'routing' && <RoutingTab />}
        </>
      )}
    </div>
  );
};

// Overview Tab
const OverviewTab: React.FC<{
  botStats: BotStats | null;
  trafficStats: TrafficStats | null;
  realtimeStats: RealtimeStats | null;
}> = ({ botStats, trafficStats, realtimeStats }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    {/* Today Stats */}
    <div className="bg-gray-800 rounded-lg p-4">
      <h3 className="text-gray-400 text-sm mb-2">Today Clicks</h3>
      <p className="text-3xl font-bold">{trafficStats?.today?.clicks || 0}</p>
      <p className="text-sm text-gray-500">
        Unique: {trafficStats?.today?.unique_clicks || 0}
      </p>
    </div>

    <div className="bg-gray-800 rounded-lg p-4">
      <h3 className="text-gray-400 text-sm mb-2">Conversions</h3>
      <p className="text-3xl font-bold text-green-500">
        {trafficStats?.today?.conversions || 0}
      </p>
      <p className="text-sm text-gray-500">
        CR: {(trafficStats?.today?.cr || 0).toFixed(2)}%
      </p>
    </div>

    <div className="bg-gray-800 rounded-lg p-4">
      <h3 className="text-gray-400 text-sm mb-2">Revenue</h3>
      <p className="text-3xl font-bold text-yellow-500">
        ${(trafficStats?.today?.revenue || 0).toFixed(2)}
      </p>
      <p className="text-sm text-gray-500">
        EPC: ${(trafficStats?.today?.epc || 0).toFixed(3)}
      </p>
    </div>

    <div className="bg-gray-800 rounded-lg p-4">
      <h3 className="text-gray-400 text-sm mb-2">Bots Blocked</h3>
      <p className="text-3xl font-bold text-red-500">
        {botStats?.bots_detected || 0}
      </p>
      <p className="text-sm text-gray-500">
        Rate: {(botStats?.bot_rate || 0).toFixed(1)}%
      </p>
    </div>

    {/* Realtime */}
    <div className="col-span-full bg-gray-800 rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">Last 60 Minutes</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <p className="text-gray-400 text-sm">Clicks</p>
          <p className="text-2xl font-bold">{realtimeStats?.clicks || 0}</p>
        </div>
        <div>
          <p className="text-gray-400 text-sm">Unique</p>
          <p className="text-2xl font-bold">{realtimeStats?.unique_clicks || 0}</p>
        </div>
        <div>
          <p className="text-gray-400 text-sm">Bots</p>
          <p className="text-2xl font-bold text-red-500">{realtimeStats?.bots || 0}</p>
        </div>
        <div>
          <p className="text-gray-400 text-sm">Conversions</p>
          <p className="text-2xl font-bold text-green-500">{realtimeStats?.conversions || 0}</p>
        </div>
      </div>
    </div>

    {/* Top Countries */}
    {realtimeStats?.countries && Object.keys(realtimeStats.countries).length > 0 && (
      <div className="col-span-full bg-gray-800 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">Top Countries (Last Hour)</h3>
        <div className="flex flex-wrap gap-2">
          {Object.entries(realtimeStats.countries)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 10)
            .map(([country, count]) => (
              <span key={country} className="px-3 py-1 bg-gray
-700 rounded text-sm">
                {country}: {count}
              </span>
            ))}
        </div>
      </div>
    )}
  </div>
);

// Bot Detection Tab
const BotDetectionTab: React.FC<{
  botStats: BotStats | null;
  autoBlockBots: boolean;
  setAutoBlockBots: (value: boolean) => void;
}> = ({ botStats, autoBlockBots, setAutoBlockBots }) => (
  <div className="space-y-6">
    {/* Settings */}
    <div className="bg-gray-800 rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">Bot Detection Settings</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="flex items-center justify-between p-3 bg-gray-700 rounded">
          <div>
            <p className="font-medium">Auto Block Bots</p>
            <p className="text-sm text-gray-400">Automatically block detected bots</p>
          </div>
          <button
            onClick={() => setAutoBlockBots(!autoBlockBots)}
            className={`px-4 py-2 rounded font-medium ${
              autoBlockBots ? 'bg-green-600' : 'bg-gray-600'
            }`}
          >
            {autoBlockBots ? 'ON' : 'OFF'}
          </button>
        </div>
        <div className="flex items-center justify-between p-3 bg-gray-700 rounded">
          <div>
            <p className="font-medium">JS Challenge</p>
            <p className="text-sm text-gray-400">Require JavaScript verification</p>
          </div>
          <button className="px-4 py-2 rounded font-medium bg-green-600">ON</button>
        </div>
        <div className="flex items-center justify-between p-3 bg-gray-700 rounded">
          <div>
            <p className="font-medium">Block Datacenters</p>
            <p className="text-sm text-gray-400">Block traffic from known datacenters</p>
          </div>
          <button className="px-4 py-2 rounded font-medium bg-green-600">ON</button>
        </div>
        <div className="flex items-center justify-between p-3 bg-gray-700 rounded">
          <div>
            <p className="font-medium">Block Empty UA</p>
            <p className="text-sm text-gray-400">Block requests without User-Agent</p>
          </div>
          <button className="px-4 py-2 rounded font-medium bg-green-600">ON</button>
        </div>
      </div>
    </div>

    {/* Stats */}
    <div className="bg-gray-800 rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">Detection Statistics</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center p-4 bg-gray-700 rounded">
          <p className="text-3xl font-bold">{botStats?.total_checks || 0}</p>
          <p className="text-sm text-gray-400">Total Checks</p>
        </div>
        <div className="text-center p-4 bg-gray-700 rounded">
          <p className="text-3xl font-bold text-red-500">{botStats?.bots_detected || 0}</p>
          <p className="text-sm text-gray-400">Bots Detected</p>
        </div>
        <div className="text-center p-4 bg-gray-700 rounded">
          <p className="text-3xl font-bold text-green-500">{botStats?.humans_passed || 0}</p>
          <p className="text-sm text-gray-400">Humans Passed</p>
        </div>
        <div className="text-center p-4 bg-gray-700 rounded">
          <p className="text-3xl font-bold text-yellow-500">{(botStats?.bot_rate || 0).toFixed(1)}%</p>
          <p className="text-sm text-gray-400">Bot Rate</p>
        </div>
      </div>
    </div>

    {/* Known Signatures */}
    <div className="bg-gray-800 rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">Known Signatures</h3>
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 bg-gray-700 rounded">
          <p className="text-2xl font-bold">{botStats?.known_bot_fingerprints || 0}</p>
          <p className="text-sm text-gray-400">Bot Fingerprints</p>
        </div>
        <div className="p-4 bg-gray-700 rounded">
          <p className="text-2xl font-bold">{botStats?.known_bot_ips || 0}</p>
          <p className="text-sm text-gray-400">Blocked IPs</p>
        </div>
      </div>
    </div>

    {/* Detection Checks */}
    <div className="bg-gray-800 rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">Detection Checks</h3>
      <div className="space-y-2">
        {[
          { name: 'User-Agent Analysis', desc: 'Check for bot signatures in UA', weight: 100 },
          { name: 'Datacenter IP Detection', desc: 'Identify traffic from datacenters', weight: 60 },
          { name: 'JavaScript Verification', desc: 'Verify JS execution capability', weight: 85 },
          { name: 'Mouse Movement Analysis', desc: 'Detect human-like behavior', weight: 65 },
          { name: 'Canvas Fingerprint', desc: 'Check canvas rendering', weight: 60 },
          { name: 'WebGL Detection', desc: 'Verify WebGL support', weight: 55 },
          { name: 'Page Load Time', desc: 'Detect suspiciously fast loads', weight: 55 },
          { name: 'Known Fingerprints', desc: 'Match against known bot signatures', weight: 95 }
        ].map((check, i) => (
          <div key={i} className="flex items-center justify-between p-3 bg-gray-700 rounded">
            <div>
              <p className="font-medium">{check.name}</p>
              <p className="text-sm text-gray-400">{check.desc}</p>
            </div>
            <span className="px-3 py-1 bg-blue-600 rounded text-sm">
              Weight: {check.weight}
            </span>
          </div>
        ))}
      </div>
    </div>
  </div>
);

// Statistics Tab
const StatisticsTab: React.FC = () => {
  const [period, setPeriod] = useState('today');
  const [stats, setStats] = useState<any>(null);
  const [countryStats, setCountryStats] = useState<any[]>([]);
  const [browserStats, setBrowserStats] = useState<any[]>([]);

  useEffect(() => {
    fetchStats();
  }, [period]);

  const fetchStats = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
      
      const [periodRes, countryRes, browserRes] = await Promise.all([
        fetch(`${API_URL}/api/tds/stats/period?start_date=${weekAgo}&end_date=${today}`),
        fetch(`${API_URL}/api/tds/stats/countries`),
        fetch(`${API_URL}/api/tds/stats/browsers`)
      ]);

      if (periodRes.ok) setStats(await periodRes.json());
      if (countryRes.ok) {
        const data = await countryRes.json();
        setCountryStats(data.countries || []);
      }
      if (browserRes.ok) {
        const data = await browserRes.json();
        setBrowserStats(data.browsers || []);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Period Selector */}
      <div className="flex gap-2">
        {['today', 'yesterday', 'week', 'month'].map(p => (
          <button
            key={p}
            onClick={() => setPeriod(p)}
            className={`px-4 py-2 rounded ${
              period === p ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
            }`}
          >
            {p.charAt(0).toUpperCase() + p.slice(1)}
          </button>
        ))}
      </div>

      {/* Summary */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-800 rounded-lg p-4">
            <p className="text-gray-400 text-sm">Total Clicks</p>
            <p className="text-2xl font-bold">{stats.totals?.clicks || 0}</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <p className="text-gray-400 text-sm">Unique Clicks</p>
            <p className="text-2xl font-bold">{stats.totals?.unique_clicks || 0}</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <p className="text-gray-400 text-sm">Conversions</p>
            <p className="text-2xl font-bold text-green-500">{stats.totals?.conversions || 0}</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <p className="text-gray-400 text-sm">Revenue</p>
            <p className="text-2xl font-bold text-yellow-500">${(stats.totals?.revenue || 0).toFixed(2)}</p>
          </div>
        </div>
      )}

      {/* Country Stats */}
      <div className="bg-gray-800 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">By Country</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-gray-400 text-sm">
                <th className="p-2">Country</th>
                <th className="p-2">Clicks</th>
                <th className="p-2">Unique</th>
                <th className="p-2">Conv</th>
                <th className="p-2">CR</th>
              </tr>
            </thead>
            <tbody>
              {countryStats.slice(0, 10).map((c, i) => (
                <tr key={i} className="border-t border-gray-700">
                  <td className="p-2">{c.country}</td>
                  <td className="p-2">{c.clicks}</td>
                  <td className="p-2">{c.unique}</td>
                  <td className="p-2 text-green-500">{c.conversions}</td>
                  <td className="p-2">{c.cr}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Browser Stats */}
      <div className="bg-gray-800 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">By Browser</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-gray-400 text-sm">
                <th className="p-2">Browser</th>
                <th className="p-2">Clicks</th>
                <th className="p-2">Conv</th>
                <th className="p-2">CR</th>
              </tr>
            </thead>
            <tbody>
              {browserStats.slice(0, 10).map((b, i) => (
                <tr key={i} className="border-t border-gray-700">
                  <td className="p-2">{b.browser}</td>
                  <td className="p-2">{b.clicks}</td>
                  <td className="p-2 text-green-500">{b.conversions}</td>
                  <td className="p-2">{b.cr}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Filters Tab
const FiltersTab: React.FC = () => (
  <div className="space-y-6">
    <div className="flex justify-between items-center">
      <h3 className="text-lg font-semibold">Traffic Filters</h3>
      <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded">
        + Add Filter
      </button>
    </div>
    
    <div className="bg-gray-800 rounded-lg p-4">
      <p className="text-gray-400">
        Create filters to control traffic flow based on country, device, browser, referrer, and more.
      </p>
      
      <div className="mt-4 space-y-2">
        {[
          { name: 'Block Bots', type: 'bot', action: 'block', hits: 1234 },
          { name: 'US Traffic Only', type: 'country', action: 'allow', hits: 5678 },
          { name: 'Mobile Redirect', type: 'device', action: 'redirect', hits: 890 }
        ].map((filter, i) => (
          <div key={i} className="flex items-center justify-between p-3 bg-gray-700 rounded">
            <div>
              <p className="font-medium">{filter.name}</p>
              <p className="text-sm text-gray-400">Type: {filter.type} | Action: {filter.action}</p>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-400">{filter.hits} hits</span>
              <button className="text-blue-400 hover:text-blue-300">Edit</button>
              <button className="text-red-400 hover:text-red-300">Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

// Routing Tab
const RoutingTab: React.FC = () => (
  <div className="space-y-6">
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div className="bg-gray-800 rounded-lg p-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Landings</h3>
          <button className="px-3 py-1 bg-blue-600 rounded text-sm">+ Add</button>
        </div>
        <p className="text-gray-400 text-sm">Manage your landing pages and prelandings</p>
      </div>
      
      <div className="bg-gray-800 rounded-lg p-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Offers</h3>
          <button className="px-3 py-1 bg-blue-600 rounded text-sm">+ Add</button>
        </div>
        <p className="text-gray-400 text-sm">Configure your affiliate offers</p>
      </div>
      
      <div className="bg-gray-800 rounded-lg p-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Rules</h3>
          <button className="px-3 py-1 bg-blue-600 rounded text-sm">+ Add</button>
        </div>
        <p className="text-gray-400 text-sm">Set up routing rules and conditions</p>
      </div>
    </div>

    <div className="bg-gray-800 rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">Traffic Flow</h3>
      <div className="flex items-center justify-center gap-4 p-8 bg-gray-700 rounded">
        <div className="text-center p-4 bg-gray-600 rounded">
          <p className="text-2xl">👤</p>
          <p className="text-sm">Visitor</p>
        </div>
        <span className="text-2xl">→</span>
        <div className="text-center p-4 bg-gray-600 rounded">
          <p className="text-2xl">🔍</p>
          <p className="text-sm">Bot Check</p>
        </div>
        <span className="text-2xl">→</span>
        <div className="text-center p-4 bg-gray-600 rounded">
          <p className="text-2xl">🔀</p>
          <p className="text-sm">Filters</p>
        </div>
        <span className="text-2xl">→</span>
        <div className="text-center p-4 bg-gray-600 rounded">
          <p className="text-2xl">📄</p>
          <p className="text-sm">Landing</p>
        </div>
        <span className="text-2xl">→</span>
        <div className="text-center p-4 bg-green-600 rounded">
          <p className="text-2xl">💰</p>
          <p className="text-sm">Offer</p>
        </div>
      </div>
    </div>
  </div>
);

export default TrackerManager;
