import React, { useState, useEffect } from 'react';

interface Campaign {
  id: string;
  name: string;
  domain: string;
  status: string;
  traffic_source: string;
  total_clicks: number;
  unique_clicks: number;
  conversions: number;
  revenue: number;
  created_at: string;
}

interface Flow {
  id: string;
  name: string;
  campaign_id: string;
  schema: string;
  status: string;
  total_clicks: number;
  paths: any[];
}

interface Landing {
  id: string;
  name: string;
  url: string;
  status: string;
  clicks: number;
  lp_clicks: number;
  lp_ctr: number;
}

interface Offer {
  id: string;
  name: string;
  url: string;
  status: string;
  payout: number;
  clicks: number;
  conversions: number;
  cr: number;
}

interface AntifraudStats {
  total_checks: number;
  blocked: number;
  allowed: number;
  blacklist_size: number;
}

const API_BASE = 'http://localhost:8000/api/tds';

const TDSManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'campaigns' | 'flows' | 'landings' | 'offers' | 'antifraud' | 'stats'>('campaigns');
  
  // Data states
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [flows, setFlows] = useState<Flow[]>([]);
  const [landings, setLandings] = useState<Landing[]>([]);
  const [offers, setOffers] = useState<Offer[]>([]);
  const [antifraudStats, setAntifraudStats] = useState<AntifraudStats | null>(null);
  const [blacklist, setBlacklist] = useState<any[]>([]);
  const [dashboardStats, setDashboardStats] = useState<any>(null);
  
  // Form states
  const [showCampaignForm, setShowCampaignForm] = useState(false);
  const [showFlowForm, setShowFlowForm] = useState(false);
  const [showLandingForm, setShowLandingForm] = useState(false);
  const [showOfferForm, setShowOfferForm] = useState(false);
  const [showBlacklistForm, setShowBlacklistForm] = useState(false);
  
  // Form data
  const [campaignForm, setCampaignForm] = useState({ name: '', domain: '', traffic_source: '' });
  const [flowForm, setFlowForm] = useState({ name: '', campaign_id: '', schema: 'direct' });
  const [landingForm, setLandingForm] = useState({ name: '', url: '', landing_type: 'url' });
  const [offerForm, setOfferForm] = useState({ name: '', url: '', payout: 0, payout_type: 'cpa' });
  const [blacklistForm, setBlacklistForm] = useState({ entry_type: 'ip', value: '', reason: '', hours: 0 });
  
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'campaigns') {
        const res = await fetch(`${API_BASE}/campaigns`);
        const data = await res.json();
        setCampaigns(Array.isArray(data) ? data : []);
      } else if (activeTab === 'flows') {
        const res = await fetch(`${API_BASE}/flows`);
        const data = await res.json();
        setFlows(Array.isArray(data) ? data : []);
      } else if (activeTab === 'landings') {
        const res = await fetch(`${API_BASE}/landings`);
        const data = await res.json();
        setLandings(Array.isArray(data) ? data : []);
      } else if (activeTab === 'offers') {
        const res = await fetch(`${API_BASE}/offers`);
        const data = await res.json();
        setOffers(Array.isArray(data) ? data : []);
      } else if (activeTab === 'antifraud') {
        const [statsRes, listRes] = await Promise.all([
          fetch(`${API_BASE}/antifraud/stats`),
          fetch(`${API_BASE}/antifraud/blacklist`)
        ]);
        setAntifraudStats(await statsRes.json());
        setBlacklist(await listRes.json());
      } else if (activeTab === 'stats') {
        const res = await fetch(`${API_BASE}/stats/dashboard`);
        setDashboardStats(await res.json());
      }
    } catch (error) {
      console.error('Error loading data:', error);
    }
    setLoading(false);
  };

  const createCampaign = async () => {
    try {
      const res = await fetch(`${API_BASE}/campaigns`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(campaignForm)
      });
      const data = await res.json();
      if (data.success) {
        setMessage('Кампания создана!');
        setShowCampaignForm(false);
        setCampaignForm({ name: '', domain: '', traffic_source: '' });
        loadData();
      }
    } catch (error) {
      setMessage('Ошибка создания кампании');
    }
  };

  const createFlow = async () => {
    try {
      const res = await fetch(`${API_BASE}/flows`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(flowForm)
      });
      const data = await res.json();
      if (data.success) {
        setMessage('Поток создан!');
        setShowFlowForm(false);
        setFlowForm({ name: '', campaign_id: '', schema: 'direct' });
        loadData();
      }
    } catch (error) {
      setMessage('Ошибка создания потока');
    }
  };

  const createLanding = async () => {
    try {
      const res = await fetch(`${API_BASE}/landings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(landingForm)
      });
      const data = await res.json();
      if (data.success) {
        setMessage('Лендинг создан!');
        setShowLandingForm(false);
        setLandingForm({ name: '', url: '', landing_type: 'url' });
        loadData();
      }
    } catch (error) {
      setMessage('Ошибка создания лендинга');
    }
  };

  const createOffer = async () => {
    try {
      const res = await fetch(`${API_BASE}/offers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(offerForm)
      });
      const data = await res.json();
      if (data.success) {
        setMessage('Оффер создан!');
        setShowOfferForm(false);
        setOfferForm({ name: '', url: '', payout: 0, payout_type: 'cpa' });
        loadData();
      }
    } catch (error) {
      setMessage('Ошибка создания оффера');
    }
  };

  const addToBlacklist = async () => {
    try {
      const res = await fetch(`${API_BASE}/antifraud/blacklist`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(blacklistForm)
      });
      const data = await res.json();
      if (data.success) {
        setMessage('Добавлено в чёрный список!');
        setShowBlacklistForm(false);
        setBlacklistForm({ entry_type: 'ip', value: '', reason: '', hours: 0 });
        loadData();
      }
    } catch (error) {
      setMessage('Ошибка добавления');
    }
  };

  const deleteCampaign = async (id: string) => {
    if (!confirm('Удалить кампанию?')) return;
    try {
      await fetch(`${API_BASE}/campaigns/${id}`, { method: 'DELETE' });
      loadData();
    } catch (error) {
      setMessage('Ошибка удаления');
    }
  };

  const tabs = [
    { id: 'campaigns', label: '🎯 Кампании', icon: '🎯' },
    { id: 'flows', label: '🔀 Потоки', icon: '🔀' },
    { id: 'landings', label: '📄 Лендинги', icon: '📄' },
    { id: 'offers', label: '💰 Офферы', icon: '💰' },
    { id: 'antifraud', label: '🛡️ Антифрод', icon: '🛡️' },
    { id: 'stats', label: '📊 Статистика', icon: '📊' }
  ];

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">🚀 TDS - Traffic Distribution System</h1>
        <p className="text-gray-600">Система распределения трафика по типу Keitaro</p>
      </div>

      {message && (
        <div className="mb-4 p-3 bg-blue-100 text-blue-800 rounded-lg">
          {message}
          <button onClick={() => setMessage('')} className="ml-2 text-blue-600">✕</button>
        </div>
      )}

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 mb-6 border-b pb-4">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === tab.id
                ? 'bg-purple-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {loading && <div className="text-center py-8">Загрузка...</div>}

      {/* Campaigns Tab */}
      {activeTab === 'campaigns' && !loading && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Кампании</h2>
            <button
              onClick={() => setShowCampaignForm(true)}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              + Создать кампанию
            </button>
          </div>

          {showCampaignForm && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-semibold mb-3">Новая кампания</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <input
                  type="text"
                  placeholder="Название"
                  value={campaignForm.name}
                  onChange={e => setCampaignForm({...campaignForm, name: e.target.value})}
                  className="px-3 py-2 border rounded-lg"
                />
                <input
                  type="text"
                  placeholder="Домен"
                  value={campaignForm.domain}
                  onChange={e => setCampaignForm({...campaignForm, domain: e.target.value})}
                  className="px-3 py-2 border rounded-lg"
                />
                <input
                  type="text"
                  placeholder="Источник трафика"
                  value={campaignForm.traffic_source}
                  onChange={e => setCampaignForm({...campaignForm, traffic_source: e.target.value})}
                  className="px-3 py-2 border rounded-lg"
                />
              </div>
              <div className="mt-4 flex gap-2">
                <button onClick={createCampaign} className="px-4 py-2 bg-green-600 text-white rounded-lg">
                  Создать
                </button>
                <button onClick={() => setShowCampaignForm(false)} className="px-4 py-2 bg-gray-300 rounded-lg">
                  Отмена
                </button>
              </div>
            </div>
          )}

          <div className="overflow-x-auto">
            <table className="w-full bg-white rounded-lg shadow">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left">Название</th>
                  <th className="px-4 py-3 text-left">Домен</th>
                  <th className="px-4 py-3 text-center">Статус</th>
                  <th className="px-4 py-3 text-center">Клики</th>
                  <th className="px-4 py-3 text-center">Конверсии</th>
                  <th className="px-4 py-3 text-center">Доход</th>
                  <th className="px-4 py-3 text-center">Действия</th>
                </tr>
              </thead>
              <tbody>
                {campaigns.map(campaign => (
                  <tr key={campaign.id} className="border-t hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">{campaign.name}</td>
                    <td className="px-4 py-3 text-gray-600">{campaign.domain || '-'}</td>
                    <td className="px-4 py-3 text-center">
                      <span className={`px-2 py-1 rounded text-sm ${
                        campaign.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {campaign.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">{campaign.total_clicks}</td>
                    <td className="px-4 py-3 text-center">{campaign.conversions}</td>
                    <td className="px-4 py-3 text-center">${campaign.revenue?.toFixed(2) || '0.00'}</td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => deleteCampaign(campaign.id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))}
                {campaigns.length === 0 && (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                      Нет кампаний. Создайте первую!
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Flows Tab */}
      {activeTab === 'flows' && !loading && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Потоки</h2>
            <button
              onClick={() => setShowFlowForm(true)}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              + Создать поток
            </button>
          </div>

          {showFlowForm && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-semibold mb-3">Новый поток</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <input
                  type="text"
                  placeholder="Название"
                  value={flowForm.name}
                  onChange={e => setFlowForm({...flowForm, name: e.target.value})}
                  className="px-3 py-2 border rounded-lg"
                />
                <select
                  value={flowForm.campaign_id}
                  onChange={e => setFlowForm({...flowForm, campaign_id: e.target.value})}
                  className="px-3 py-2 border rounded-lg"
                >
                  <option value="">Выберите кампанию</option>
                  {campaigns.map(c => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
                <select
                  value={flowForm.schema}
                  onChange={e => setFlowForm({...flowForm, schema: e.target.value})}
                  className="px-3 py-2 border rounded-lg"
                >
                  <option value="direct">Direct (прямой редирект)</option>
                  <option value="landing_offer">Landing → Offer</option>
                  <option value="multi_landing">Multi Landing</option>
                  <option value="split_test">Split Test</option>
                </select>
              </div>
              <div className="mt-4 flex gap-2">
                <button onClick={createFlow} className="px-4 py-2 bg-green-600 text-white rounded-lg">
                  Создать
                </button>
                <button onClick={() => setShowFlowForm(false)} className="px-4 py-2 bg-gray-300 rounded-lg">
                  Отмена
                </button>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {flows.map(flow => (
              <div key={flow.id} className="bg-white p-4 rounded-lg shadow">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold">{flow.name}</h3>
                  <span className={`px-2 py-1 rounded text-xs ${
                    flow.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100'
                  }`}>
                    {flow.status}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">Схема: {flow.schema}</p>
                <p className="text-sm text-gray-600 mb-2">Путей: {flow.paths?.length || 0}</p>
                <p className="text-sm font-medium">Клики: {flow.total_clicks}</p>
              </div>
            ))}
            {flows.length === 0 && (
              <div className="col-span-full text-center py-8 text-gray-500">
                Нет потоков. Создайте первый!
              </div>
            )}
          </div>
        </div>
      )}

      {/* Landings Tab */}
      {activeTab === 'landings' && !loading && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Лендинги</h2>
            <button
              onClick={() => setShowLandingForm(true)}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              + Добавить лендинг
            </button>
          </div>

          {showLandingForm && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-semibold mb-3">Новый лендинг</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <input
                  type="text"
                  placeholder="Название"
                  value={landingForm.name}
                  onChange={e => setLandingForm({...landingForm, name: e.target.value})}
                  className="px-3 py-2 border rounded-lg"
                />
                <input
                  type="text"
                  placeholder="URL"
                  value={landingForm.url}
                  onChange={e => setLandingForm({...landingForm, url: e.target.value})}
                  className="px-3 py-2 border rounded-lg"
                />
                <select
                  value={landingForm.landing_type}
                  onChange={e => setLandingForm({...landingForm, landing_type: e.target.value})}
                  className="px-3 py-2 border rounded-lg"
                >
                  <option value="url">URL</option>
                  <option value="local">Локальный</option>
                  <option value="html">HTML</option>
                </select>
              </div>
              <div className="mt-4 flex gap-2">
                <button onClick={createLanding} className="px-4 py-2 bg-green-600 text-white rounded-lg">
                  Добавить
                </button>
                <button onClick={() => setShowLandingForm(false)} className="px-4 py-2 bg-gray-300 rounded-lg">
                  Отмена
                </button>
              </div>
            </div>
          )}

          <div className="overflow-x-auto">
            <table className="w-full bg-white rounded-lg shadow">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left">Название</th>
                  <th className="px-4 py-3 text-left">URL</th>
                  <th className="px-4 py-3 text-center">Клики</th>
                  <th className="px-4 py-3 text-center">LP Клики</th>
                  <th className="px-4 py-3 text-center">LP CTR</th>
                  <th className="px-4 py-3 text-center">Статус</th>
                </tr>
              </thead>
              <tbody>
                {landings.map(landing => (
                  <tr key={landing.id} className="border-t hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">{landing.name}</td>
                    <td className="px-4 py-3 text-gray-600 truncate max-w-xs">{landing.url}</td>
                    <td className="px-4 py-3 text-center">{landing.clicks}</td>
                    <td className="px-4 py-3 text-center">{landing.lp_clicks}</td>
                    <td className="px-4 py-3 text-center">{landing.lp_ctr?.toFixed(2)}%</td>
                    <td className="px-4 py-3 text-center">
                      <span className={`px-2 py-1 rounded text-sm ${
                        landing.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100'
                      }`}>
                        {landing.status}
                      </span>
                    </td>
                  </tr>
                ))}
                {landings.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                      Нет лендингов
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Offers Tab */}
      {activeTab === 'offers' && !loading && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Офферы</h2>
            <button
              onClick={() => setShowOfferForm(true)}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              + Добавить оффер
            </button>
          </div>

          {showOfferForm && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-semibold mb-3">Новый оффер</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <input
                  type="text"
                  placeholder="Название"
                  value={offerForm.name}
                  onChange={e => setOfferForm({...offerForm, name: e.target.value})}
                  className="px-3 py-2 border rounded-lg"
                />
                <input
                  type="text"
                  placeholder="URL"
                  value={offerForm.url}
                  onChange={e => setOfferForm({...offerForm, url: e.target.value})}
                  className="px-3 py-2 border rounded-lg"
                />
                <input
                  type="number"
                  placeholder="Выплата"
                  value={offerForm.payout}
                  onChange={e => setOfferForm({...offerForm, payout: parseFloat(e.target.value)})}
                  className="px-3 py-2 border rounded-lg"
                />
                <select
                  value={offerForm.payout_type}
                  onChange={e => setOfferForm({...offerForm, payout_type: e.target.value})}
                  className="px-3 py-2 border rounded-lg"
                >
                  <option value="cpa">CPA</option>
                  <option value="cpl">CPL</option>
                  <option value="cps">CPS</option>
                  <option value="revshare">RevShare</option>
                </select>
              </div>
              <div className="mt-4 flex gap-2">
                <button onClick={createOffer} className="px-4 py-2 bg-green-600 text-white rounded-lg">
                  Добавить
                </button>
                <button onClick={() => setShowOfferForm(false)} className="px-4 py-2 bg-gray-300 rounded-lg">
                  Отмена
                </button>
              </div>
            </div>
          )}

          <div className="overflow-x-auto">
            <table className="w-full bg-white rounded-lg shadow">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left">Название</th>
                  <th className="px-4 py-3 text-left">URL</th>
                  <th className="px-4 py-3 text-center">Выплата</th>
                  <th className="px-4 py-3 text-center">Клики</th>
                  <th className="px-4 py-3 text-center">Конверсии</th>
                  <th className="px-4 py-3 text-center">CR</th>
                  <th className="px-4 py-3 text-center">Статус</th>
                </tr>
              </thead>
              <tbody>
                {offers.map(offer => (
                  <tr key={offer.id} className="border-t hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">{offer.name}</td>
                    <td className="px-4 py-3 text-gray-600 truncate max-w-xs">{offer.url}</td>
                    <td className="px-4 py-3 text-center">${offer.payout}</td>
                    <td className="px-4 py-3 text-center">{offer.clicks}</td>
                    <td className="px-4 py-3 text-center">{offer.conversions}</td>
                    <td className="px-4 py-3 text-center">{offer.cr?.toFixed(2)}%</td>
                    <td className="px-4 py-3 text-center">
                      <span className={`px-2 py-1 rounded text-sm ${
                        offer.status === 'active' ? 'bg-green-100 text-green-800' :
                        offer.status === 'capped' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100'
                      }`}>
                        {offer.status}
                      </span>
                    </td>
                  </tr>
                ))}
                {offers.length === 0 && (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                      Нет офферов
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Antifraud Tab */}
      {activeTab === 'antifraud' && !loading && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Антифрод система</h2>
            <button
              onClick={() => setShowBlacklistForm(true)}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              + Добавить в чёрный список
            </button>
          </div>

          {/* Stats */}
          {antifraudStats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white p-4 rounded-lg shadow">
                <p className="text-sm text-gray-600">Проверок (24ч)</p>
                <p className="text-2xl font-bold">{antifraudStats.total_checks}</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <p className="text-sm text-gray-600">Заблокировано</p>
                <p className="text-2xl font-bold text-red-600">{antifraudStats.blocked}</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <p className="text-sm text-gray-600">Пропущено</p>
                <p className="text-2xl font-bold text-green-600">{antifraudStats.allowed}</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <p className="text-sm text-gray-600">В чёрном списке</p>
                <p className="text-2xl font-bold">{antifraudStats.blacklist_size}</p>
              </div>
            </div>
          )}

          {showBlacklistForm && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-semibold mb-3">Добавить в чёрный список</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <select
                  value={blacklistForm.entry_type}
                  onChange={e => setBlacklistForm({...blacklistForm, entry_type: e.target.value})}
                  className="px-3 py-2 border rounded-lg"
                >
                  <option value="ip">IP адрес</option>
                  <option value="ip_range">IP диапазон</option>
                  <option value="ua">User-Agent</option>
                  <option value="referrer">Реферер</option>
                </select>
                <input
                  type="text"
                  placeholder="Значение"
                  value={blacklistForm.value}
                  onChange={e => setBlacklistForm({...blacklistForm, value: e.target.value})}
                  className="px-3 py-2 border rounded-lg"
                />
                <input
                  type="text"
                  placeholder="Причина"
                  value={blacklistForm.reason}
                  onChange={e => setBlacklistForm({...blacklistForm, reason: e.target.value})}
                  className="px-3 py-2 border rounded-lg"
                />
                <input
                  type="number"
                  placeholder="Часов (0 = навсегда)"
                  value={blacklistForm.hours}
                  onChange={e => setBlacklistForm({...blacklistForm, hours: parseInt(e.target.value)})}
                  className="px-3 py-2 border rounded-lg"
                />
              </div>
              <div className="mt-4 flex gap-2">
                <button onClick={addToBlacklist} className="px-4 py-2 bg-red-600 text-white rounded-lg">
                  Добавить
                </button>
                <button onClick={() => setShowBlacklistForm(false)} className="px-4 py-2 bg-gray-300 rounded-lg">
                  Отмена
                </button>
              </div>
            </div>
          )}

          {/* Blacklist */}
          <div className="bg-white rounded-lg shadow">
            <h3 className="px-4 py-3 font-semibold border-b">Чёрный список</h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left">Тип</th>
                    <th className="px-4 py-3 text-left">Значение</th>
                    <th className="px-4 py-3 text-left">Причина</th>
                    <th className="px-4 py-3 text-center">Попаданий</th>
                    <th className="px-4 py-3 text-center">Истекает</th>
                  </tr>
                </thead>
                <tbody>
                  {blacklist.map((entry: any) => (
                    <tr key={entry.id} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-sm">
                          {entry.entry_type}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-mono text-sm">{entry.value}</td>
                      <td className="px-4 py-3 text-gray-600">{entry.reason || '-'}</td>
                      <td className="px-4 py-3 text-center">{entry.hits}</td>
                      <td className="px-4 py-3 text-center text-sm">
                        {entry.expires_at ? new Date(entry.expires_at).toLocaleString() : 'Навсегда'}
                      </td>
                    </tr>
                  ))}
                  {blacklist.length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                        Чёрный список пуст
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Stats Tab */}
      {activeTab === 'stats' && !loading && dashboardStats && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Общая статистика</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white p-4 rounded-lg">
              <p className="text-sm opacity-80">Всего кампаний</p>
              <p className="text-3xl font-bold">{dashboardStats.campaigns?.total_campaigns || 0}</p>
            </div>
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 rounded-lg">
              <p className="text-sm opacity-80">Всего кликов</p>
              <p className="text-3xl font-bold">{dashboardStats.campaigns?.total_clicks || 0}</p>
            </div>
            <div className="bg-gradient-to-r from-green-500 to-green-600 text-white p-4 rounded-lg">
              <p className="text-sm opacity-80">Конверсии</p>
              <p className="text-3xl font-bold">{dashboardStats.campaigns?.total_conversions || 0}</p>
            </div>
            <div className="bg-gradient-to-r from-yellow-500 to-yellow-600 text-white p-4 rounded-lg">
              <p className="text-sm opacity-80">Доход</p>
              <p className="text-3xl font-bold">${dashboardStats.campaigns?.total_revenue?.toFixed(2) || '0.00'}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Landings Stats */}
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-semibold mb-3">📄 Лендинги</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Всего:</span>
                  <span className="font-medium">{dashboardStats.landings?.total_landings || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Активных:</span>
                  <span className="font-medium">{dashboardStats.landings?.active_landings || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Средний LP CTR:</span>
                  <span className="font-medium">{dashboardStats.landings?.avg_lp_ctr?.toFixed(2) || 0}%</span>
                </div>
              </div>
            </div>

            {/* Offers Stats */}
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-semibold mb-3">💰 Офферы</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Всего:</span>
                  <span className="font-medium">{dashboardStats.offers?.total_offers || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Активных:</span>
                  <span className="font-medium">{dashboardStats.offers?.active_offers || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Средний CR:</span>
                  <span className="font-medium">{dashboardStats.offers?.avg_cr?.toFixed(2) || 0}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Средний EPC:</span>
                  <span className="font-medium">${dashboardStats.offers?.avg_epc?.toFixed(4) || 0}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TDSManager;
