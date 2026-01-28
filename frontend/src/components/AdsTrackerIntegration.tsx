import React, { useState, useEffect } from 'react';

const API_URL = 'http://144.31.238.16:8000';

interface CloakingStats {
  integration: {
    tracking_links: number;
    total_clicks: number;
    total_conversions: number;
    total_revenue: number;
    conversion_rate: number;
    postbacks: {
      total: number;
      active: number;
      total_sent: number;
      total_success: number;
      total_failed: number;
    };
    cloaking: {
      total_rules: number;
      active_rules: number;
      total_hits: number;
      total_blocks: number;
      block_rate: number;
    };
  };
  cloaking: {
    safe_pages: { total: number; active: number; total_views: number };
    whitelist: { ips: number; user_agents: number };
    blacklist: { ips: number; user_agents: number };
  };
}

interface CloakingRule {
  id: string;
  name: string;
  mode: string;
  safe_page_url: string;
  enabled: boolean;
  hits: number;
  blocks: number;
}

interface SafePage {
  id: string;
  name: string;
  url: string;
  page_type: string;
  enabled: boolean;
  views: number;
}

interface Postback {
  id: string;
  name: string;
  platform: string;
  event_type: string;
  url_template: string;
  enabled: boolean;
  sent_count: number;
  success_count: number;
  fail_count: number;
}

interface Lists {
  whitelist: { ips: string[]; user_agents: string[] };
  blacklist: { ips: string[]; user_agents: string[] };
}

export const AdsTrackerIntegration: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'cloaking' | 'postbacks' | 'lists' | 'test'>('overview');
  const [stats, setStats] = useState<CloakingStats | null>(null);
  const [rules, setRules] = useState<CloakingRule[]>([]);
  const [safePages, setSafePages] = useState<SafePage[]>([]);
  const [postbacks, setPostbacks] = useState<Postback[]>([]);
  const [lists, setLists] = useState<Lists | null>(null);
  const [loading, setLoading] = useState(true);
  const [testResult, setTestResult] = useState<any>(null);
  
  // Test form
  const [testIp, setTestIp] = useState('66.249.66.1');
  const [testUa, setTestUa] = useState('Googlebot/2.1');
  const [testRef, setTestRef] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsRes, rulesRes, pagesRes, postbacksRes, listsRes] = await Promise.all([
        fetch(`${API_URL}/api/ads-tracker/cloaking/stats`),
        fetch(`${API_URL}/api/ads-tracker/cloaking/rules`),
        fetch(`${API_URL}/api/ads-tracker/safe-pages`),
        fetch(`${API_URL}/api/ads-tracker/postbacks`),
        fetch(`${API_URL}/api/ads-tracker/lists`)
      ]);
      
      if (statsRes.ok) setStats(await statsRes.json());
      if (rulesRes.ok) {
        const data = await rulesRes.json();
        setRules(data.rules || []);
      }
      if (pagesRes.ok) {
        const data = await pagesRes.json();
        setSafePages(data.pages || []);
      }
      if (postbacksRes.ok) {
        const data = await postbacksRes.json();
        setPostbacks(data.postbacks || []);
      }
      if (listsRes.ok) setLists(await listsRes.json());
    } catch (error) {
      console.error('Error fetching data:', error);
    }
    setLoading(false);
  };

  const testCloaking = async () => {
    try {
      // Определяем заголовки в зависимости от типа посетителя
      const isRealUser = !testUa.toLowerCase().includes('bot') && 
                         !testUa.toLowerCase().includes('spider') &&
                         !testUa.toLowerCase().includes('crawler');
      
      const headers = isRealUser ? {
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
      } : {};
      
      const res = await fetch(`${API_URL}/api/ads-tracker/cloaking/check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ip: testIp,
          user_agent: testUa,
          referrer: testRef,
          headers: headers
        })
      });
      if (res.ok) {
        setTestResult(await res.json());
      }
    } catch (error) {
      console.error('Error testing cloaking:', error);
    }
  };

  const addToList = async (listType: 'whitelist' | 'blacklist', ip?: string, ua?: string) => {
    try {
      await fetch(`${API_URL}/api/ads-tracker/${listType}/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip, user_agent: ua })
      });
      fetchData();
    } catch (error) {
      console.error('Error adding to list:', error);
    }
  };

  const removeFromList = async (listType: 'whitelist' | 'blacklist', ip?: string, ua?: string) => {
    try {
      await fetch(`${API_URL}/api/ads-tracker/${listType}/remove`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip, user_agent: ua })
      });
      fetchData();
    } catch (error) {
      console.error('Error removing from list:', error);
    }
  };

  const setPreset = (preset: 'google' | 'facebook' | 'real') => {
    if (preset === 'google') {
      setTestIp('66.249.66.1');
      setTestUa('Googlebot/2.1');
      setTestRef('');
    } else if (preset === 'facebook') {
      setTestIp('157.240.1.1');
      setTestUa('facebookexternalhit/1.1');
      setTestRef('');
    } else {
      setTestIp('192.168.1.1');
      setTestUa('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0');
      setTestRef('https://google.com');
    }
    setTestResult(null);
  };

  const tabs = [
    { id: 'overview', label: '📊 Overview', icon: '📊' },
    { id: 'cloaking', label: '🎭 Cloaking', icon: '🎭' },
    { id: 'postbacks', label: '📤 Postbacks', icon: '📤' },
    { id: 'lists', label: '📋 Lists', icon: '📋' },
    { id: 'test', label: '🧪 Test', icon: '🧪' }
  ];

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2 style={{ margin: 0, color: '#fff' }}>🔗 Ads-Tracker Integration</h2>
          <p style={{ margin: '5px 0 0', color: '#888', fontSize: '14px' }}>
            Cloaking, postbacks, and fraud protection for ad campaigns
          </p>
        </div>
        <button
          onClick={fetchData}
          style={{
            padding: '8px 16px',
            background: '#3b82f6',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer'
          }}
        >
          Refresh
        </button>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            style={{
              padding: '10px 20px',
              background: activeTab === tab.id ? '#3b82f6' : '#1e293b',
              color: activeTab === tab.id ? '#fff' : '#94a3b8',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div>
          {/* Stats Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '15px', marginBottom: '20px' }}>
            <div style={{ background: '#1e293b', padding: '20px', borderRadius: '8px' }}>
              <div style={{ color: '#94a3b8', fontSize: '12px' }}>Tracking Links</div>
              <div style={{ color: '#fff', fontSize: '24px', fontWeight: 'bold' }}>
                {stats?.integration.tracking_links || 0}
              </div>
            </div>
            <div style={{ background: '#1e293b', padding: '20px', borderRadius: '8px' }}>
              <div style={{ color: '#94a3b8', fontSize: '12px' }}>Total Clicks</div>
              <div style={{ color: '#3b82f6', fontSize: '24px', fontWeight: 'bold' }}>
                {stats?.integration.total_clicks || 0}
              </div>
            </div>
            <div style={{ background: '#1e293b', padding: '20px', borderRadius: '8px' }}>
              <div style={{ color: '#94a3b8', fontSize: '12px' }}>Conversions</div>
              <div style={{ color: '#10b981', fontSize: '24px', fontWeight: 'bold' }}>
                {stats?.integration.total_conversions || 0}
              </div>
            </div>
            <div style={{ background: '#1e293b', padding: '20px', borderRadius: '8px' }}>
              <div style={{ color: '#94a3b8', fontSize: '12px' }}>CR%</div>
              <div style={{ color: '#f59e0b', fontSize: '24px', fontWeight: 'bold' }}>
                {stats?.integration.conversion_rate?.toFixed(1) || 0}%
              </div>
            </div>
          </div>

          {/* Cloaking Protection */}
          <div style={{ background: '#1e293b', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
            <h3 style={{ margin: '0 0 15px', color: '#fff' }}>🎭 Cloaking Protection</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '15px' }}>
              <div>
                <div style={{ color: '#94a3b8', fontSize: '12px' }}>Active Rules</div>
                <div style={{ color: '#fff', fontSize: '20px' }}>{stats?.integration.cloaking.active_rules || 0}</div>
              </div>
              <div>
                <div style={{ color: '#94a3b8', fontSize: '12px' }}>Total Hits</div>
                <div style={{ color: '#3b82f6', fontSize: '20px' }}>{stats?.integration.cloaking.total_hits || 0}</div>
              </div>
              <div>
                <div style={{ color: '#94a3b8', fontSize: '12px' }}>Blocked</div>
                <div style={{ color: '#ef4444', fontSize: '20px' }}>{stats?.integration.cloaking.total_blocks || 0}</div>
              </div>
              <div>
                <div style={{ color: '#94a3b8', fontSize: '12px' }}>Block Rate</div>
                <div style={{ color: '#f59e0b', fontSize: '20px' }}>{stats?.integration.cloaking.block_rate?.toFixed(1) || 0}%</div>
              </div>
            </div>
          </div>

          {/* Postback Stats */}
          <div style={{ background: '#1e293b', padding: '20px', borderRadius: '8px' }}>
            <h3 style={{ margin: '0 0 15px', color: '#fff' }}>📤 Postback Stats</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '15px' }}>
              <div>
                <div style={{ color: '#94a3b8', fontSize: '12px' }}>Active</div>
                <div style={{ color: '#fff', fontSize: '20px' }}>{stats?.integration.postbacks.active || 0}</div>
              </div>
              <div>
                <div style={{ color: '#94a3b8', fontSize: '12px' }}>Total Sent</div>
                <div style={{ color: '#3b82f6', fontSize: '20px' }}>{stats?.integration.postbacks.total_sent || 0}</div>
              </div>
              <div>
                <div style={{ color: '#94a3b8', fontSize: '12px' }}>Success</div>
                <div style={{ color: '#10b981', fontSize: '20px' }}>{stats?.integration.postbacks.total_success || 0}</div>
              </div>
              <div>
                <div style={{ color: '#94a3b8', fontSize: '12px' }}>Failed</div>
                <div style={{ color: '#ef4444', fontSize: '20px' }}>{stats?.integration.postbacks.total_failed || 0}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Cloaking Tab */}
      {activeTab === 'cloaking' && (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            {/* Rules */}
            <div style={{ background: '#1e293b', padding: '20px', borderRadius: '8px' }}>
              <h3 style={{ margin: '0 0 15px', color: '#fff' }}>Cloaking Rules</h3>
              {rules.length === 0 ? (
                <p style={{ color: '#94a3b8' }}>No rules configured</p>
              ) : (
                rules.map(rule => (
                  <div key={rule.id} style={{ padding: '10px', background: '#0f172a', borderRadius: '6px', marginBottom: '10px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#fff' }}>{rule.name}</span>
                      <span style={{ color: rule.enabled ? '#10b981' : '#ef4444' }}>
                        {rule.enabled ? 'Active' : 'Disabled'}
                      </span>
                    </div>
                    <div style={{ color: '#94a3b8', fontSize: '12px', marginTop: '5px' }}>
                      Mode: {rule.mode} | Hits: {rule.hits} | Blocks: {rule.blocks}
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Safe Pages */}
            <div style={{ background: '#1e293b', padding: '20px', borderRadius: '8px' }}>
              <h3 style={{ margin: '0 0 15px', color: '#fff' }}>Safe Pages</h3>
              {safePages.length === 0 ? (
                <p style={{ color: '#94a3b8' }}>No safe pages configured</p>
              ) : (
                safePages.map(page => (
                  <div key={page.id} style={{ padding: '10px', background: '#0f172a', borderRadius: '6px', marginBottom: '10px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#fff' }}>{page.name}</span>
                      <span style={{ color: page.enabled ? '#10b981' : '#ef4444' }}>
                        {page.enabled ? 'Active' : 'Disabled'}
                      </span>
                    </div>
                    <div style={{ color: '#94a3b8', fontSize: '12px', marginTop: '5px' }}>
                      Type: {page.page_type} | Views: {page.views}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Postbacks Tab */}
      {activeTab === 'postbacks' && (
        <div style={{ background: '#1e293b', padding: '20px', borderRadius: '8px' }}>
          <h3 style={{ margin: '0 0 15px', color: '#fff' }}>Postbacks</h3>
          {postbacks.length === 0 ? (
            <p style={{ color: '#94a3b8' }}>No postbacks configured</p>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #334155' }}>
                  <th style={{ padding: '10px', textAlign: 'left', color: '#94a3b8' }}>Name</th>
                  <th style={{ padding: '10px', textAlign: 'left', color: '#94a3b8' }}>Platform</th>
                  <th style={{ padding: '10px', textAlign: 'left', color: '#94a3b8' }}>Event</th>
                  <th style={{ padding: '10px', textAlign: 'left', color: '#94a3b8' }}>Sent</th>
                  <th style={{ padding: '10px', textAlign: 'left', color: '#94a3b8' }}>Success</th>
                  <th style={{ padding: '10px', textAlign: 'left', color: '#94a3b8' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {postbacks.map(pb => (
                  <tr key={pb.id} style={{ borderBottom: '1px solid #1e293b' }}>
                    <td style={{ padding: '10px', color: '#fff' }}>{pb.name}</td>
                    <td style={{ padding: '10px', color: '#3b82f6' }}>{pb.platform}</td>
                    <td style={{ padding: '10px', color: '#94a3b8' }}>{pb.event_type}</td>
                    <td style={{ padding: '10px', color: '#fff' }}>{pb.sent_count}</td>
                    <td style={{ padding: '10px', color: '#10b981' }}>{pb.success_count}</td>
                    <td style={{ padding: '10px' }}>
                      <span style={{ color: pb.enabled ? '#10b981' : '#ef4444' }}>
                        {pb.enabled ? '● Active' : '○ Disabled'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Lists Tab */}
      {activeTab === 'lists' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          {/* Whitelist */}
          <div style={{ background: '#1e293b', padding: '20px', borderRadius: '8px' }}>
            <h3 style={{ margin: '0 0 15px', color: '#10b981' }}>✅ Whitelist</h3>
            <div style={{ marginBottom: '15px' }}>
              <h4 style={{ color: '#94a3b8', margin: '0 0 10px' }}>IPs ({lists?.whitelist.ips.length || 0})</h4>

              {lists?.whitelist.ips.map((ip, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 10px', background: '#0f172a', borderRadius: '4px', marginBottom: '5px' }}>
                  <span style={{ color: '#fff' }}>{ip}</span>
                  <button onClick={() => removeFromList('whitelist', ip)} style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}>×</button>
                </div>
              ))}
            </div>
            <div>
              <h4 style={{ color: '#94a3b8', margin: '0 0 10px' }}>User Agents ({lists?.whitelist.user_agents.length || 0})</h4>
              {lists?.whitelist.user_agents.map((ua, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 10px', background: '#0f172a', borderRadius: '4px', marginBottom: '5px' }}>
                  <span style={{ color: '#fff', fontSize: '12px' }}>{ua}</span>
                  <button onClick={() => removeFromList('whitelist', undefined, ua)} style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}>×</button>
                </div>
              ))}
            </div>
          </div>

          {/* Blacklist */}
          <div style={{ background: '#1e293b', padding: '20px', borderRadius: '8px' }}>
            <h3 style={{ margin: '0 0 15px', color: '#ef4444' }}>🚫 Blacklist</h3>
            <div style={{ marginBottom: '15px' }}>
              <h4 style={{ color: '#94a3b8', margin: '0 0 10px' }}>IPs ({lists?.blacklist.ips.length || 0})</h4>
              {lists?.blacklist.ips.map((ip, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 10px', background: '#0f172a', borderRadius: '4px', marginBottom: '5px' }}>
                  <span style={{ color: '#fff' }}>{ip}</span>
                  <button onClick={() => removeFromList('blacklist', ip)} style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}>×</button>
                </div>
              ))}
            </div>
            <div>
              <h4 style={{ color: '#94a3b8', margin: '0 0 10px' }}>User Agents ({lists?.blacklist.user_agents.length || 0})</h4>
              {lists?.blacklist.user_agents.map((ua, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 10px', background: '#0f172a', borderRadius: '4px', marginBottom: '5px' }}>
                  <span style={{ color: '#fff', fontSize: '12px' }}>{ua}</span>
                  <button onClick={() => removeFromList('blacklist', undefined, ua)} style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}>×</button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Test Tab */}
      {activeTab === 'test' && (
        <div style={{ background: '#1e293b', padding: '20px', borderRadius: '8px' }}>
          <h3 style={{ margin: '0 0 15px', color: '#fff' }}>🧪 Test Cloaking</h3>
          <p style={{ color: '#94a3b8', marginBottom: '20px' }}>Test how the cloaking system will handle a specific visitor</p>
          
          <div style={{ display: 'grid', gap: '15px', marginBottom: '20px' }}>
            <div>
              <label style={{ color: '#94a3b8', display: 'block', marginBottom: '5px' }}>IP Address</label>
              <input
                type="text"
                value={testIp}
                onChange={(e) => setTestIp(e.target.value)}
                placeholder="e.g., 66.249.66.1 (Googlebot)"
                style={{ width: '100%', padding: '10px', background: '#0f172a', border: '1px solid #334155', borderRadius: '6px', color: '#fff' }}
              />
            </div>
            <div>
              <label style={{ color: '#94a3b8', display: 'block', marginBottom: '5px' }}>User-Agent</label>
              <input
                type="text"
                value={testUa}
                onChange={(e) => setTestUa(e.target.value)}
                placeholder="e.g., Googlebot/2.1"
                style={{ width: '100%', padding: '10px', background: '#0f172a', border: '1px solid #334155', borderRadius: '6px', color: '#fff' }}
              />
            </div>
            <div>
              <label style={{ color: '#94a3b8', display: 'block', marginBottom: '5px' }}>Referrer (optional)</label>
              <input
                type="text"
                value={testRef}
                onChange={(e) => setTestRef(e.target.value)}
                placeholder="e.g., https://google.com"
                style={{ width: '100%', padding: '10px', background: '#0f172a', border: '1px solid #334155', borderRadius: '6px', color: '#fff' }}
              />
            </div>
          </div>

          <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
            <button
              onClick={testCloaking}
              style={{ padding: '10px 20px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
            >
              Test Visitor
            </button>
            <button
              onClick={() => setPreset('google')}
              style={{ padding: '10px 20px', background: '#1e293b', color: '#fff', border: '1px solid #334155', borderRadius: '6px', cursor: 'pointer' }}
            >
              Google Bot
            </button>
            <button
              onClick={() => setPreset('facebook')}
              style={{ padding: '10px 20px', background: '#1e293b', color: '#fff', border: '1px solid #334155', borderRadius: '6px', cursor: 'pointer' }}
            >
              Facebook Bot
            </button>
            <button
              onClick={() => setPreset('real')}
              style={{ padding: '10px 20px', background: '#1e293b', color: '#fff', border: '1px solid #334155', borderRadius: '6px', cursor: 'pointer' }}
            >
              Real User
            </button>
          </div>

          {testResult && (
            <div style={{ background: '#0f172a', padding: '20px', borderRadius: '8px' }}>
              <h4 style={{ margin: '0 0 15px', color: '#fff' }}>Result:</h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div>
                  <span style={{ color: '#94a3b8' }}>Is Bot: </span>
                  <span style={{ color: testResult.is_bot ? '#ef4444' : '#10b981', fontWeight: 'bold' }}>
                    {testResult.is_bot ? 'YES' : 'NO'}
                  </span>
                </div>
                <div>
                  <span style={{ color: '#94a3b8' }}>Is Moderator: </span>
                  <span style={{ color: testResult.is_moderator ? '#f59e0b' : '#10b981', fontWeight: 'bold' }}>
                    {testResult.is_moderator ? 'YES' : 'NO'}
                  </span>
                </div>
                <div>
                  <span style={{ color: '#94a3b8' }}>Action: </span>
                  <span style={{ color: '#fff' }}>{testResult.action}</span>
                </div>
                <div>
                  <span style={{ color: '#94a3b8' }}>Confidence: </span>
                  <span style={{ color: '#fff' }}>{(testResult.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
              <div style={{ marginTop: '15px' }}>
                <span style={{ color: '#94a3b8' }}>Reason: </span>
                <span style={{ color: '#fff' }}>{testResult.reason}</span>
              </div>
              {testResult.moderator_type && (
                <div style={{ marginTop: '10px' }}>
                  <span style={{ color: '#94a3b8' }}>Moderator Type: </span>
                  <span style={{ color: '#f59e0b' }}>{testResult.moderator_type}</span>
                </div>
              )}
              <div style={{ marginTop: '15px' }}>
                <span style={{ color: '#94a3b8' }}>Checks: </span>
                <span style={{ color: '#64748b', fontSize: '12px' }}>{testResult.checks_performed?.join(', ')}</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AdsTrackerIntegration;
