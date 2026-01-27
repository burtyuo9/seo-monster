import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/ad-campaigns';

interface AdAccount {
  id: string;
  platform: string;
  name: string;
  balance: number;
  currency: string;
  status: string;
  is_active: boolean;
  campaigns_count: number;
}

interface AdCampaign {
  id: string;
  account_id: string;
  domain_id: string;
  name: string;
  platform: string;
  campaign_type: string;
  status: string;
  budget: number;
  daily_budget: number;
  spent: number;
  keywords: string[];
  geo_targets: string[];
  stats: {
    impressions: number;
    clicks: number;
    conversions: number;
    ctr: number;
    cpc: number;
  };
}

interface ModuleStatus {
  enabled: boolean;
  auto_mode: boolean;
  total_accounts: number;
  total_campaigns: number;
  active_campaigns: number;
  total_spent: number;
  total_clicks: number;
  blocked_bots: number;
  fraud_prevented: number;
}

const PLATFORMS = [
  { id: 'google_ads', name: 'Google Ads', icon: '🔍' },
  { id: 'bing_ads', name: 'Bing Ads', icon: '🅱️' },
  { id: 'facebook_ads', name: 'Facebook Ads', icon: '📘' },
  { id: 'linkedin_ads', name: 'LinkedIn Ads', icon: '💼' },
  { id: 'tiktok_ads', name: 'TikTok Ads', icon: '🎵' },
  { id: 'yandex_direct', name: 'Yandex Direct', icon: '🔴' },
];

export default function AdCampaignsManager() {
  const [status, setStatus] = useState<ModuleStatus | null>(null);
  const [accounts, setAccounts] = useState<AdAccount[]>([]);
  const [campaigns, setCampaigns] = useState<AdCampaign[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'accounts' | 'campaigns' | 'stats' | 'settings'>('overview');
  const [loading, setLoading] = useState(false);
  const [showAddAccount, setShowAddAccount] = useState(false);
  const [showAddCampaign, setShowAddCampaign] = useState(false);
  
  // Form states
  const [newAccount, setNewAccount] = useState({
    platform: 'google_ads',
    name: '',
    api_key: '',
    client_id: '',
    client_secret: '',
    currency: 'USD',
    daily_budget_limit: 100
  });
  
  const [newCampaign, setNewCampaign] = useState({
    account_id: '',
    domain_id: '',
    name: '',
    campaign_type: 'ads_only',
    budget: 1000,
    daily_budget: 50,
    keywords: '',
    geo_targets: 'US,GB,DE',
    language_targets: 'en',
    landing_url: '',
    cloaking_enabled: true,
    auto_keywords: true
  });

  useEffect(() => {
    fetchStatus();
    fetchAccounts();
    fetchCampaigns();
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/status`);
      setStatus(response.data);
    } catch (error) {
      console.error('Error fetching status:', error);
    }
  };

  const fetchAccounts = async () => {
    try {
      const response = await axios.get(`${API_URL}/accounts`);
      setAccounts(response.data);
    } catch (error) {
      console.error('Error fetching accounts:', error);
    }
  };

  const fetchCampaigns = async () => {
    try {
      const response = await axios.get(`${API_URL}/campaigns`);
      setCampaigns(response.data);
    } catch (error) {
      console.error('Error fetching campaigns:', error);
    }
  };

  const toggleModule = async () => {
    setLoading(true);
    try {
      if (status?.enabled) {
        await axios.post(`${API_URL}/disable`);
      } else {
        await axios.post(`${API_URL}/enable`);
      }
      await fetchStatus();
    } catch (error) {
      console.error('Error toggling module:', error);
    }
    setLoading(false);
  };

  const toggleAutoMode = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_URL}/auto-mode`, { enabled: !status?.auto_mode });
      await fetchStatus();
    } catch (error) {
      console.error('Error toggling auto mode:', error);
    }
    setLoading(false);
  };

  const addAccount = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_URL}/accounts`, {
        platform: newAccount.platform,
        name: newAccount.name,
        credentials: {
          api_key: newAccount.api_key,
          client_id: newAccount.client_id,
          client_secret: newAccount.client_secret
        },
        currency: newAccount.currency,
        daily_budget_limit: newAccount.daily_budget_limit
      });
      await fetchAccounts();
      setShowAddAccount(false);
      setNewAccount({
        platform: 'google_ads',
        name: '',
        api_key: '',
        client_id: '',
        client_secret: '',
        currency: 'USD',
        daily_budget_limit: 100
      });
    } catch (error) {
      console.error('Error adding account:', error);
    }
    setLoading(false);
  };

  const deleteAccount = async (accountId: string) => {
    if (!confirm('Are you sure you want to delete this account?')) return;
    try {
      await axios.delete(`${API_URL}/accounts/${accountId}`);
      await fetchAccounts();
    } catch (error) {
      console.error('Error deleting account:', error);
    }
  };

  const createCampaign = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_URL}/campaigns`, {
        account_id: newCampaign.account_id,
        domain_id: newCampaign.domain_id || 'default',
        name: newCampaign.name,
        campaign_type: newCampaign.campaign_type,
        budget: newCampaign.budget,
        daily_budget: newCampaign.daily_budget,
        keywords: newCampaign.keywords.split(',').map(k => k.trim()).filter(k => k),
        geo_targets: newCampaign.geo_targets.split(',').map(g => g.trim()),
        language_targets: newCampaign.language_targets.split(',').map(l => l.trim()),
        landing_url: newCampaign.landing_url,
        cloaking_enabled: newCampaign.cloaking_enabled,
        auto_keywords: newCampaign.auto_keywords
      });
      await fetchCampaigns();
      setShowAddCampaign(false);
    } catch (error) {
      console.error('Error creating campaign:', error);
    }
    setLoading(false);
  };

  const startCampaign = async (campaignId: string) => {
    try {
      await axios.post(`${API_URL}/campaigns/${campaignId}/start`);
      await fetchCampaigns();
    } catch (error) {
      console.error('Error starting campaign:', error);
    }
  };

  const pauseCampaign = async (campaignId: string) => {
    try {
      await axios.post(`${API_URL}/campaigns/${campaignId}/pause`);
      await fetchCampaigns();
    } catch (error) {
      console.error('Error pausing campaign:', error);
    }
  };

  const getStatusColor = (s: string) => {
    switch (s) {
      case 'active': return 'bg-green-500';
      case 'paused': return 'bg-yellow-500';
      case 'draft': return 'bg-gray-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white">Ad Campaigns Manager</h2>
          <p className="text-gray-400">Manage your advertising campaigns across platforms</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={toggleModule}
            disabled={loading}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              status?.enabled
                ? 'bg-green-600 hover:bg-green-700 text-white'
                : 'bg-gray-600 hover:bg-gray-700 text-white'
            }`}
          >
            {status?.enabled ? '✓ Module ON' : '○ Module OFF'}
          </button>
          <button
            onClick={toggleAutoMode}
            disabled={loading || !status?.enabled}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              status?.auto_mode
                ? 'bg-blue-600 hover:bg-blue-700 text-white'
                : 'bg-gray-600 hover:bg-gray-700 text-white'
            }`}
          >
            {status?.auto_mode ? '⚡ Auto Mode ON' : '○ Auto Mode OFF'}
          </button>
        </div>
      </div>

      {/* Status Cards */}
      {status && (
        <div className="grid grid-cols-5 gap-4 mb-6">
          <div className="bg-gray-700 p-4 rounded-lg">
            <p className="text-gray-400 text-sm">Accounts</p>
            <p className="text-2xl font-bold text-white">{status.total_accounts}</p>
          </div>
          <div className="bg-gray-700 p-4 rounded-lg">
            <p className="text-gray-400 text-sm">Campaigns</p>
            <p className="text-2xl font-bold text-white">{status.total_campaigns}</p>
            <p className="text-green-400 text-xs">{status.active_campaigns} active</p>
          </div>
          <div className="bg-gray-700 p-4 rounded-lg">
            <p className="text-gray-400 text-sm">Total Spent</p>
            <p className="text-2xl font-bold text-white">${status.total_spent.toFixed(2)}</p>
          </div>
          <div className="bg-gray-700 p-4 rounded-lg">
            <p className="text-gray-400 text-sm">Total Clicks</p>
            <p className="text-2xl font-bold text-white">{status.total_clicks}</p>
          </div>
          <div className="bg-gray-700 p-4 rounded-lg">
            <p className="text-gray-400 text-sm">Fraud Blocked</p>
            <p className="text-2xl font-bold text-red-400">{status.blocked_bots}</p>
            <p className="text-green-400 text-xs">${status.fraud_prevented.toFixed(2)} saved</p>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-gray-700 pb-2">
        {['overview', 'accounts', 'campaigns', 'stats', 'settings'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as any)}
            className={`px-4 py-2 rounded-t-lg capitalize ${
              activeTab === tab
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-700'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-2 gap-6">
          {/* Platforms */}
          <div className="bg-gray-700 p-4 rounded-lg">
            <h3 className="text-lg font-bold text-white mb-4">Supported Platforms</h3>
            <div className="grid grid-cols-2 gap-3">
              {PLATFORMS.map((platform) => (
                <div key={platform.id} className="flex items-center gap-2 p-2 bg-gray-600 rounded">
                  <span className="text-2xl">{platform.icon}</span>
                  <span className="text-white">{platform.name}</span>
                </div>
              ))}
            </div>
          </div>
          
          {/* Quick Actions */}
          <div className="bg-gray-700 p-4 rounded-lg">
            <h3 className="text-lg font-bold text-white mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button
                onClick={() => setShowAddAccount(true)}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded"
              >
                + Add Ad Account
              </button>
              <button
                onClick={() => setShowAddCampaign(true)}
                disabled={accounts.length === 0}
                className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded disabled:opacity-50"
              >
                + Create Campaign
              </button>
              <button
                onClick={fetchStatus}
                className="w-full bg-gray-600 hover:bg-gray-500 text-white py-2 rounded"
              >
                🔄 Refresh Data
              </button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'accounts' && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-bold text-white">Ad Accounts</h3>
            <button
              onClick={() => setShowAddAccount(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
            >
              + Add Account
            </button>
          </div>
          
          {accounts.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              No accounts added yet. Click "Add Account" to get started.
            </div>
          ) : (
            <div className="grid gap-4">
              {accounts.map((account) => (
                <div key={account.id} className="bg-gray-700 p-4 rounded-lg flex justify-between items-center">
                  <div className="flex items-center gap-4">
                    <span className="text-2xl">
                      {PLATFORMS.find(p => p.id === account.platform)?.icon || '📊'}
                    </span>
                    <div>
                      <p className="text-white font-medium">{account.name}</p>
                      <p className="text-gray-400 text-sm">{account.platform}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <p className="text-white font-bold">{account.currency} {account.balance.toFixed(2)}</p>
                      <p className="text-gray-400 text-sm">{account.campaigns_count} campaigns</p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs text-white ${
                      account.is_active ? 'bg-green-600' : 'bg-gray-600'
                    }`}>
                      {account.status}
                    </span>
                    <button
                      onClick={() => deleteAccount(account.id)}
                      className="text-red-400 hover:text-red-300"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'campaigns' && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-bold text-white">Campaigns</h3>
            <button
              onClick={() => setShowAddCampaign(true)}
              disabled={accounts.length === 0}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded disabled:opacity-50"
            >
              + Create Campaign
            </button>
          </div>
          
          {campaigns.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              No campaigns created yet.
            </div>
          ) : (
            <div className="space-y-4">
              {campaigns.map((campaign) => (
                <div key={campaign.id} className="bg-gray-700 p-4 rounded-lg">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounde
d-full ${getStatusColor(campaign.status)}`}></span>
                        <h4 className="text-white font-medium">{campaign.name}</h4>
                      </div>
                      <p className="text-gray-400 text-sm">
                        {campaign.platform} | {campaign.campaign_type}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      {campaign.status === 'active' ? (
                        <button
                          onClick={() => pauseCampaign(campaign.id)}
                          className="bg-yellow-600 hover:bg-yellow-700 text-white px-3 py-1 rounded text-sm"
                        >
                          Pause
                        </button>
                      ) : (
                        <button
                          onClick={() => startCampaign(campaign.id)}
                          className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm"
                        >
                          Start
                        </button>
                      )}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-6 gap-4 text-sm">
                    <div>
                      <p className="text-gray-400">Budget</p>
                      <p className="text-white">${campaign.budget}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Daily</p>
                      <p className="text-white">${campaign.daily_budget}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Spent</p>
                      <p className="text-white">${campaign.spent.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Impressions</p>
                      <p className="text-white">{campaign.stats.impressions}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Clicks</p>
                      <p className="text-white">{campaign.stats.clicks}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">CTR</p>
                      <p className="text-white">{campaign.stats.ctr.toFixed(2)}%</p>
                    </div>
                  </div>
                  
                  {campaign.keywords.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-1">
                      {campaign.keywords.slice(0, 5).map((kw, i) => (
                        <span key={i} className="bg-gray-600 text-gray-300 px-2 py-0.5 rounded text-xs">
                          {kw}
                        </span>
                      ))}
                      {campaign.keywords.length > 5 && (
                        <span className="text-gray-400 text-xs">+{campaign.keywords.length - 5} more</span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'stats' && (
        <div className="grid grid-cols-2 gap-6">
          <div className="bg-gray-700 p-4 rounded-lg">
            <h3 className="text-lg font-bold text-white mb-4">Performance Overview</h3>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-400">Total Impressions</span>
                <span className="text-white font-bold">
                  {campaigns.reduce((sum, c) => sum + c.stats.impressions, 0)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Total Clicks</span>
                <span className="text-white font-bold">
                  {campaigns.reduce((sum, c) => sum + c.stats.clicks, 0)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Total Conversions</span>
                <span className="text-white font-bold">
                  {campaigns.reduce((sum, c) => sum + c.stats.conversions, 0)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Average CPC</span>
                <span className="text-white font-bold">
                  ${(campaigns.reduce((sum, c) => sum + c.stats.cpc, 0) / Math.max(campaigns.length, 1)).toFixed(2)}
                </span>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-700 p-4 rounded-lg">
            <h3 className="text-lg font-bold text-white mb-4">Fraud Protection</h3>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-400">Bots Blocked</span>
                <span className="text-red-400 font-bold">{status?.blocked_bots || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Money Saved</span>
                <span className="text-green-400 font-bold">${status?.fraud_prevented?.toFixed(2) || '0.00'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Protection Status</span>
                <span className="text-green-400 font-bold">Active</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'settings' && (
        <div className="bg-gray-700 p-4 rounded-lg max-w-2xl">
          <h3 className="text-lg font-bold text-white mb-4">Module Settings</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-white">Auto Mode</p>
                <p className="text-gray-400 text-sm">Automatically manage campaigns based on performance</p>
              </div>
              <button
                onClick={toggleAutoMode}
                className={`px-4 py-2 rounded ${
                  status?.auto_mode ? 'bg-green-600' : 'bg-gray-600'
                }`}
              >
                {status?.auto_mode ? 'ON' : 'OFF'}
              </button>
            </div>
            <div className="flex justify-between items-center">
              <div>
                <p className="text-white">Fraud Protection</p>
                <p className="text-gray-400 text-sm">Block bots and fraudulent clicks</p>
              </div>
              <span className="px-4 py-2 rounded bg-green-600 text-white">Always ON</span>
            </div>
            <div className="flex justify-between items-center">
              <div>
                <p className="text-white">Auto Keywords</p>
                <p className="text-gray-400 text-sm">Automatically discover and add keywords</p>
              </div>
              <span className="px-4 py-2 rounded bg-green-600 text-white">Enabled</span>
            </div>
          </div>
        </div>
      )}

      {/* Add Account Modal */}
      {showAddAccount && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-lg w-full max-w-md">
            <h3 className="text-xl font-bold text-white mb-4">Add Ad Account</h3>
            
            <div className="space-y-4">
              <div>
                <label className="text-gray-400 text-sm">Platform</label>
                <select
                  value={newAccount.platform}
                  onChange={(e) => setNewAccount({...newAccount, platform: e.target.value})}
                  className="w-full bg-gray-700 text-white p-2 rounded mt-1"
                >
                  {PLATFORMS.map((p) => (
                    <option key={p.id} value={p.id}>{p.icon} {p.name}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="text-gray-400 text-sm">Account Name</label>
                <input
                  type="text"
                  value={newAccount.name}
                  onChange={(e) => setNewAccount({...newAccount, name: e.target.value})}
                  className="w-full bg-gray-700 text-white p-2 rounded mt-1"
                  placeholder="My Google Ads Account"
                />
              </div>
              
              <div>
                <label className="text-gray-400 text-sm">API Key / Token</label>
                <input
                  type="password"
                  value={newAccount.api_key}
                  onChange={(e) => setNewAccount({...newAccount, api_key: e.target.value})}
                  className="w-full bg-gray-700 text-white p-2 rounded mt-1"
                  placeholder="••••••••"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-gray-400 text-sm">Currency</label>
                  <select
                    value={newAccount.currency}
                    onChange={(e) => setNewAccount({...newAccount, currency: e.target.value})}
                    className="w-full bg-gray-700 text-white p-2 rounded mt-1"
                  >
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                    <option value="GBP">GBP</option>
                    <option value="RUB">RUB</option>
                  </select>
                </div>
                <div>
                  <label className="text-gray-400 text-sm">Daily Limit</label>
                  <input
                    type="number"
                    value={newAccount.daily_budget_limit}
                    onChange={(e) => setNewAccount({...newAccount, daily_budget_limit: Number(e.target.value)})}
                    className="w-full bg-gray-700 text-white p-2 rounded mt-1"
                  />
                </div>
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowAddAccount(false)}
                className="flex-1 bg-gray-600 hover:bg-gray-500 text-white py-2 rounded"
              >
                Cancel
              </button>
              <button
                onClick={addAccount}
                disabled={!newAccount.name || loading}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded disabled:opacity-50"
              >
                {loading ? 'Adding...' : 'Add Account'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Campaign Modal */}
      {showAddCampaign && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-lg w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-bold text-white mb-4">Create Campaign</h3>
            
            <div className="space-y-4">
              <div>
                <label className="text-gray-400 text-sm">Account</label>
                <select
                  value={newCampaign.account_id}
                  onChange={(e) => setNewCampaign({...newCampaign, account_id: e.target.value})}
                  className="w-full bg-gray-700 text-white p-2 rounded mt-1"
                >
                  <option value="">Select account...</option>
                  {accounts.map((a) => (
                    <option key={a.id} value={a.id}>{a.name} ({a.platform})</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="text-gray-400 text-sm">Campaign Name</label>
                <input
                  type="text"
                  value={newCampaign.name}
                  onChange={(e) => setNewCampaign({...newCampaign, name: e.target.value})}
                  className="w-full bg-gray-700 text-white p-2 rounded mt-1"
                  placeholder="My Campaign"
                />
              </div>
              
              <div>
                <label className="text-gray-400 text-sm">Campaign Type</label>
                <select
                  value={newCampaign.campaign_type}
                  onChange={(e) => setNewCampaign({...newCampaign, campaign_type: e.target.value})}
                  className="w-full bg-gray-700 text-white p-2 rounded mt-1"
                >
                  <option value="ads_only">Ads Only</option>
                  <option value="seo_plus_ads">SEO + Ads (Complex)</option>
                </select>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-gray-400 text-sm">Total Budget</label>
                  <input
                    type="number"
                    value={newCampaign.budget}
                    onChange={(e) => setNewCampaign({...newCampaign, budget: Number(e.target.value)})}
                    className="w-full bg-gray-700 text-white p-2 rounded mt-1"
                  />
                </div>
                <div>
                  <label className="text-gray-400 text-sm">Daily Budget</label>
                  <input
                    type="number"
                    value={newCampaign.daily_budget}
                    onChange={(e) => setNewCampaign({...newCampaign, daily_budget: Number(e.target.value)})}
                    className="w-full bg-gray-700 text-white p-2 rounded mt-1"
                  />
                </div>
              </div>
              
              <div>
                <label className="text-gray-400 text-sm">Landing URL</label>
                <input
                  type="url"
                  value={newCampaign.landing_url}
                  onChange={(e) => setNewCampaign({...newCampaign, landing_url: e.target.value})}
                  className="w-full bg-gray-700 text-white p-2 rounded mt-1"
                  placeholder="https://example.com/landing"
                />
              </div>
              
              <div>
                <label className="text-gray-400 text-sm">Keywords (comma separated)</label>
                <textarea
                  value={newCampaign.keywords}
                  onChange={(e) => setNewCampaign({...newCampaign, keywords: e.target.value})}
                  className="w-full bg-gray-700 text-white p-2 rounded mt-1"
                  rows={2}
                  placeholder="keyword1, keyword2, keyword3"
                />
              </div>
              
              <div>
                <label className="text-gray-400 text-sm">Geo Targets (comma separated)</label>
                <input
                  type="text"
                  value={newCampaign.geo_targets}
                  onChange={(e) => setNewCampaign({...newCampaign, geo_targets: e.target.value})}
                  className="w-full bg-gray-700 text-white p-2 rounded mt-1"
                  placeholder="US, GB, DE"
                />
              </div>
              
              <div className="flex gap-4">
                <label className="flex items-center gap-2 text-white">
                  <input
                    type="checkbox"
                    checked={newCampaign.cloaking_enabled}
                    onChange={(e) => setNewCampaign({...newCampaign, cloaking_enabled: e.target.checked})}
                    className="rounded"
                  />
                  Cloaking
                </label>
                <label className="flex items-center gap-2 text-white">
                  <input
                    type="checkbox"
                    checked={newCampaign.auto_keywords}
                    onChange={(e) => setNewCampaign({...newCampaign, auto_keywords: e.target.checked})}
                    className="rounded"
                  />
                  Auto Keywords
                </label>
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowAddCampaign(false)}
                className="flex-1 bg-gray-600 hover:bg-gray-500 text-white py-2 rounded"
              >
                Cancel
              </button>
              <button
                onClick={createCampaign}
                disabled={!newCampaign.account_id || !newCampaign.name || loading}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded disabled:opacity-50"
              >
                {loading ? 'Creating...' : 'Create Campaign'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
