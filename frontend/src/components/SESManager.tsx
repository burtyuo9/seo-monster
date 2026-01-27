import React, { useState, useEffect } from 'react';
import EmailABTesting from './EmailABTesting';
import SESWarmup from './SESWarmup';

const API_URL = 'http://localhost:8000';

interface AWSKey {
  id: string;
  name: string;
  access_key_id: string;
  region: string;
  status: string;
  inbox_region: string;
  daily_limit: number;
  sent_today: number;
  verified_emails: string[];
  verified_domains: string[];
  created_at: string;
}

interface EmailContent {
  id: string;
  name: string;
  subject: string;
  preheader: string;
  format: string;
  generated_by: string;
  created_at: string;
}

interface RecipientList {
  id: string;
  name: string;
  description: string;
  file_type: string;
  total_count: number;
  valid_count: number;
  invalid_count: number;
  status: string;
}

const SESManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [keys, setKeys] = useState<AWSKey[]>([]);
  const [contents, setContents] = useState<EmailContent[]>([]);
  const [lists, setLists] = useState<RecipientList[]>([]);
  const [showAddKey, setShowAddKey] = useState(false);
  const [showGenerateContent, setShowGenerateContent] = useState(false);
  const [showUploadList, setShowUploadList] = useState(false);
  const [loading, setLoading] = useState(false);

  // Form states
  const [newKey, setNewKey] = useState({ access_key_id: '', secret_access_key: '', region: 'us-east-1', name: '' });
  const [contentTask, setContentTask] = useState({ task: '', format_type: 'html', language: 'ru', tone: 'professional' });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [keysRes, contentsRes, listsRes] = await Promise.all([
        fetch(`${API_URL}/api/ses/keys`),
        fetch(`${API_URL}/api/ses/content`),
        fetch(`${API_URL}/api/ses/lists`)
      ]);
      
      if (keysRes.ok) setKeys((await keysRes.json()).keys || []);
      if (contentsRes.ok) setContents((await contentsRes.json()).contents || []);
      if (listsRes.ok) setLists((await listsRes.json()).lists || []);
    } catch (e) {
      console.error('Error fetching data:', e);
    }
  };

  const addKey = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/ses/keys`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newKey)
      });
      if (res.ok) {
        setShowAddKey(false);
        setNewKey({ access_key_id: '', secret_access_key: '', region: 'us-east-1', name: '' });
        fetchData();
      }
    } catch (e) {
      console.error('Error adding key:', e);
    }
    setLoading(false);
  };

  const generateContent = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/ses/content/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(contentTask)
      });
      if (res.ok) {
        setShowGenerateContent(false);
        setContentTask({ task: '', format_type: 'html', language: 'ru', tone: 'professional' });
        fetchData();
      }
    } catch (e) {
      console.error('Error generating content:', e);
    }
    setLoading(false);
  };

  const deleteKey = async (keyId: string) => {
    if (!confirm('Delete this AWS key?')) return;
    try {
      await fetch(`${API_URL}/api/ses/keys/${keyId}`, { method: 'DELETE' });
      fetchData();
    } catch (e) {
      console.error('Error deleting key:', e);
    }
  };

  const deleteContent = async (contentId: string) => {
    if (!confirm('Delete this content?')) return;
    try {
      await fetch(`${API_URL}/api/ses/content/${contentId}`, { method: 'DELETE' });
      fetchData();
    } catch (e) {
      console.error('Error deleting content:', e);
    }
  };

  const deleteList = async (listId: string) => {
    if (!confirm('Delete this list?')) return;
    try {
      await fetch(`${API_URL}/api/ses/lists/${listId}`, { method: 'DELETE' });
      fetchData();
    } catch (e) {
      console.error('Error deleting list:', e);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'keys', label: 'AWS Keys', icon: '🔑' },
    { id: 'content', label: 'Content', icon: '✉️' },
    { id: 'lists', label: 'Recipients', icon: '👥' },
    { id: 'campaigns', label: 'Campaigns', icon: '🚀' },
    { id: 'abtesting', label: 'A/B Testing', icon: '🧪' },
    { id: 'warmup', label: 'Warm-up', icon: '🔥' }
  ];

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '28px' }}>📧</span>
          AWS SES Manager
        </h2>
        <div style={{ display: 'flex', gap: '10px' }}>
          <span style={{ padding: '5px 15px', background: '#2d2d2d', borderRadius: '20px', fontSize: '14px' }}>
            {keys.length} Keys
          </span>
          <span style={{ padding: '5px 15px', background: '#2d2d2d', borderRadius: '20px', fontSize: '14px' }}>
            {contents.length} Contents
          </span>
          <span style={{ padding: '5px 15px', background: '#2d2d2d', borderRadius: '20px', fontSize: '14px' }}>
            {lists.reduce((sum, l) => sum + l.valid_count, 0)} Recipients
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '5px', marginBottom: '20px', borderBottom: '1px solid #333', paddingBottom: '10px' }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '10px 20px',
              background: activeTab === tab.id ? '#4CAF50' : 'transparent',
              border: 'none',
              borderRadius: '5px',
              color: 'white',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <span>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px' }}>
          <div style={{ background: '#1e1e1e', padding: '20px', borderRadius: '10px', textAlign: 'center' }}>
            <div style={{ fontSize: '36px', color: '#4CAF50', fontWeight: 'bold' }}>{keys.length}</div>
            <div style={{ color: '#888' }}>AWS Keys</div>
          </div>
          <div style={{ background: '#1e1e1e', padding: '20px', borderRadius: '10px', textAlign: 'center' }}>
            <div style={{ fontSize: '36px', color: '#2196F3', fontWeight: 'bold' }}>{contents.length}</div>
            <div style={{ color: '#888' }}>Email Contents</div>
          </div>
          <div style={{ background: '#1e1e1e', padding: '20px', borderRadius: '10px', textAlign: 'center' }}>
            <div style={{ fontSize: '36px', color: '#FF9800', fontWeight: 'bold' }}>{lists.length}</div>
            <div style={{ color: '#888' }}>Recipient Lists</div>
          </div>
          <div style={{ background: '#1e1e1e', padding: '20px', borderRadius: '10px', textAlign: 'center' }}>
            <div style={{ fontSize: '36px', color: '#9C27B0', fontWeight: 'bold' }}>
              {lists.reduce((sum, l) => sum + l.valid_count, 0)}
            </div>
            <div style={{ color: '#888' }}>Total Recipients</div>
          </div>

          {/* Quick Actions */}
          <div style={{ gridColumn: 'span 4', background: '#1e1e1e', padding: '20px', borderRadius: '10px' }}>
            <h3 style={{ marginTop: 0 }}>Quick Actions</h3>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button onClick={() => setShowAddKey(true)} style={{ padding: '10px 20px', background: '#4CAF50', border: 'none', borderRadius: '5px', color: 'white', cursor: 'pointer' }}>
                🔑 Add AWS Key
              </button>
              <button onClick={() => setShowGenerateContent(true)} style={{ padding: '10px 20px', background: '#2196F3', border: 'none', borderRadius: '5px', color: 'white', cursor: 'pointer' }}>
                ✨ Generate Content
              </button>
              <button onClick={() => setShowUploadList(true)} style={{ padding: '10px 20px', background: '#FF9800', border: 'none', borderRadius: '5px', color: 'white', cursor: 'pointer' }}>
                📤 Upload List
              </button>
            </div>
          </div>
        </div>
      )}

      {/* AWS Keys Tab */}
      {activeTab === 'keys' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
            <h3 style={{ margin: 0 }}>AWS SES Keys</h3>
            <button onClick={() => setShowAddKey(true)} style={{ padding: '10px 20px', background: '#4CAF50', border: 'none', borderRadius: '5px', color: 'white', cursor: 'pointer' }}>
              + Add Key
            </button>
          </div>

          {keys.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', background: '#1e1e1e', borderRadius: '10px' }}>
              <div style={{ fontSize: '48px', marginBottom: '10px' }}>🔑</div>
              <p style={{ color: '#888' }}>No AWS keys added yet</p>
              <button onClick={() => setShowAddKey(true)} style={{ padding: '10px 20px', background: '#4CAF50', border: 'none', borderRadius: '5px', color: 'white', cursor: 'pointer' }}>
                Add Your First Key
              </button>
            </div>
          ) : (
            <div style={{ display: 'grid', gap: '15px' }}>
              {keys.map(key => (
                <div key={key.id} style={{ background: '#1e1e1e', padding: '20px', borderRadius: '10px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>

                      <h4 style={{ margin: '0 0 10px 0' }}>{key.name || key.access_key_id}</h4>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '15px', fontSize: '14px' }}>
                        <div>
                          <span style={{ color: '#888' }}>Region:</span> {key.region}
                        </div>
                        <div>
                          <span style={{ color: '#888' }}>Inbox Region:</span> {key.inbox_region || 'N/A'}
                        </div>
                        <div>
                          <span style={{ color: '#888' }}>Status:</span>{' '}
                          <span style={{ color: key.status === 'active' ? '#4CAF50' : '#f44336' }}>
                            {key.status}
                          </span>
                        </div>
                        <div>
                          <span style={{ color: '#888' }}>Daily Limit:</span> {key.daily_limit?.toLocaleString() || 'N/A'}
                        </div>
                        <div>
                          <span style={{ color: '#888' }}>Sent Today:</span> {key.sent_today || 0}
                        </div>
                        <div>
                          <span style={{ color: '#888' }}>Verified Emails:</span> {key.verified_emails?.length || 0}
                        </div>
                      </div>
                    </div>
                    <button onClick={() => deleteKey(key.id)} style={{ background: '#f44336', border: 'none', padding: '5px 10px', borderRadius: '5px', color: 'white', cursor: 'pointer' }}>
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Content Tab */}
      {activeTab === 'content' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
            <h3 style={{ margin: 0 }}>Email Content</h3>
            <button onClick={() => setShowGenerateContent(true)} style={{ padding: '10px 20px', background: '#2196F3', border: 'none', borderRadius: '5px', color: 'white', cursor: 'pointer' }}>
              ✨ Generate with AI
            </button>
          </div>

          {contents.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', background: '#1e1e1e', borderRadius: '10px' }}>
              <div style={{ fontSize: '48px', marginBottom: '10px' }}>✉️</div>
              <p style={{ color: '#888' }}>No email content created yet</p>
              <button onClick={() => setShowGenerateContent(true)} style={{ padding: '10px 20px', background: '#2196F3', border: 'none', borderRadius: '5px', color: 'white', cursor: 'pointer' }}>
                Generate Your First Email
              </button>
            </div>
          ) : (
            <div style={{ display: 'grid', gap: '15px' }}>
              {contents.map(content => (
                <div key={content.id} style={{ background: '#1e1e1e', padding: '20px', borderRadius: '10px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <h4 style={{ margin: '0 0 5px 0' }}>{content.name}</h4>
                      <p style={{ margin: '0 0 10px 0', color: '#888' }}>Subject: {content.subject}</p>
                      <div style={{ display: 'flex', gap: '10px', fontSize: '12px' }}>
                        <span style={{ background: '#333', padding: '3px 8px', borderRadius: '3px' }}>
                          {content.format}
                        </span>
                        <span style={{ background: '#333', padding: '3px 8px', borderRadius: '3px' }}>
                          {content.generated_by}
                        </span>
                      </div>
                    </div>
                    <button onClick={() => deleteContent(content.id)} style={{ background: '#f44336', border: 'none', padding: '5px 10px', borderRadius: '5px', color: 'white', cursor: 'pointer' }}>
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Recipients Tab */}
      {activeTab === 'lists' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
            <h3 style={{ margin: 0 }}>Recipient Lists</h3>
            <button onClick={() => setShowUploadList(true)} style={{ padding: '10px 20px', background: '#FF9800', border: 'none', borderRadius: '5px', color: 'white', cursor: 'pointer' }}>
              📤 Upload List
            </button>
          </div>

          <div style={{ background: '#1e1e1e', padding: '15px', borderRadius: '10px', marginBottom: '20px' }}>
            <p style={{ margin: 0, color: '#888' }}>
              Supported formats: <strong>CSV, TXT, XLSX, JSON</strong>
            </p>
          </div>

          {lists.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', background: '#1e1e1e', borderRadius: '10px' }}>
              <div style={{ fontSize: '48px', marginBottom: '10px' }}>👥</div>
              <p style={{ color: '#888' }}>No recipient lists uploaded yet</p>
            </div>
          ) : (
            <div style={{ display: 'grid', gap: '15px' }}>
              {lists.map(list => (
                <div key={list.id} style={{ background: '#1e1e1e', padding: '20px', borderRadius: '10px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <h4 style={{ margin: '0 0 5px 0' }}>{list.name}</h4>
                      <p style={{ margin: '0 0 10px 0', color: '#888' }}>{list.description}</p>
                      <div style={{ display: 'flex', gap: '15px', fontSize: '14px' }}>
                        <span><span style={{ color: '#4CAF50' }}>✓</span> {list.valid_count} valid</span>
                        <span><span style={{ color: '#f44336' }}>✗</span> {list.invalid_count} invalid</span>
                        <span style={{ color: '#888' }}>Total: {list.total_count}</span>
                      </div>
                    </div>
                    <button onClick={() => deleteList(list.id)} style={{ background: '#f44336', border: 'none', padding: '5px 10px', borderRadius: '5px', color: 'white', cursor: 'pointer' }}>
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Campaigns Tab */}
      {activeTab === 'campaigns' && (
        <div style={{ textAlign: 'center', padding: '40px', background: '#1e1e1e', borderRadius: '10px' }}>
          <div style={{ fontSize: '48px', marginBottom: '10px' }}>🚀</div>
          <h3>Campaign Management</h3>
          <p style={{ color: '#888' }}>Create and manage email campaigns</p>
          <p style={{ color: '#666', fontSize: '14px' }}>Add AWS key, create content, and upload recipients first</p>
        </div>
      )}

      {/* A/B Testing Tab */}
      {activeTab === 'abtesting' && (
        <EmailABTesting />
      )}

      {/* Warm-up Tab */}
      {activeTab === 'warmup' && (
        <SESWarmup />
      )}

      {/* Add Key Modal */}
      {showAddKey && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#1e1e1e', padding: '30px', borderRadius: '10px', width: '500px' }}>
            <h3 style={{ marginTop: 0 }}>Add AWS SES Key</h3>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px', color: '#888' }}>Name (optional)</label>
              <input
                type="text"
                value={newKey.name}
                onChange={e => setNewKey({ ...newKey, name: e.target.value })}
                placeholder="My SES Key"
                style={{ width: '100%', padding: '10px', background: '#2d2d2d', border: '1px solid #444', borderRadius: '5px', color: 'white' }}
              />
            </div>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px', color: '#888' }}>Access Key ID *</label>
              <input
                type="text"
                value={newKey.access_key_id}
                onChange={e => setNewKey({ ...newKey, access_key_id: e.target.value })}
                placeholder="AKIAIOSFODNN7EXAMPLE"
                style={{ width: '100%', padding: '10px', background: '#2d2d2d', border: '1px solid #444', borderRadius: '5px', color: 'white' }}
              />
            </div>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px', color: '#888' }}>Secret Access Key *</label>
              <input
                type="password"
                value={newKey.secret_access_key}
                onChange={e => setNewKey({ ...newKey, secret_access_key: e.target.value })}
                placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                style={{ width: '100%', padding: '10px', background: '#2d2d2d', border: '1px solid #444', borderRadius: '5px', color: 'white' }}
              />
            </div>
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '5px', color: '#888' }}>Region</label>
              <select
                value={newKey.region}
                onChange={e => setNewKey({ ...newKey, region: e.target.value })}
                style={{ width: '100%', padding: '10px', background: '#2d2d2d', border: '1px solid #444', borderRadius: '5px', color: 'white' }}
              >
                <option value="us-east-1">US East (N. Virginia)</option>
                <option value="us-west-2">US West (Oregon)</option>
                <option value="eu-west-1">EU (Ireland)</option>
                <option value="eu-central-1">EU (Frankfurt)</option>
                <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
                <option value="ap-northeast-1">Asia Pacific (Tokyo)</option>
              </select>
            </div>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button onClick={() => setShowAddKey(false)} style={{ padding: '10px 20px', background: '#444', border: 'none', borderRadius: '5px', color: 'white', cursor: 'pointer' }}>
                Cancel
              </button>
              <button onClick={addKey} disabled={loading} style={{ padding: '10px 20px', background: '#4CAF50', border: 'none', borderRadius: '5px', color: 'white', cursor: 'pointer' }}>
                {loading ? 'Adding...' : 'Add Key'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Generate Content Modal */}
      {showGenerateContent && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#1e1e1e', padding: '30px', borderRadius: '10px', width: '600px' }}>
            <h3 style={{ marginTop: 0 }}>✨ Generate Email Content with AI</h3>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px', color: '#888' }}>Task / Description *</label>
              <textarea
                value={contentTask.task}
                onChange={e => setContentTask({ ...contentTask, task: e.target.value })}
                placeholder="Describe what kind of email you want to create. E.g.: 'Promotional email for Black Friday sale with 50% discount on all products'"
                rows={4}
                style={{ width: '100%', padding: '10px', background: '#2d2d2d', border: '1px solid #444', borderRadius: '5px', color: 'white', resize: 'vertical' }}
              />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '15px', marginBottom: '20px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', color: '#888' }}>Format</label>
                <select
                  value={contentTask.format_type}
                  onChange={e => setContentTask({ ...contentTask, format_type: e.target.value })}
                  style={{ width: '100%', padding: '10px', background: '#2d2d2d', border: '1px solid #444', borderRadius: '5px', color: 'white' }}
                >
                  <option value="html">HTML</option>
                  <option value="text">Plain Text</option>
                  <option value="mixed">Mixed</option>
                </select>
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', color: '#888' }}>Language</label>
                <select
                  value={contentTask.language}
                  onChange={e => setContentTask({ ...contentTask, language: e.target.value })}
                  style={{ width: '100%', padding: '10px', background: '#2d2d2d', border: '1px solid #444', borderRadius: '5px', color: 'white' }}
                >
                  <option value="ru">Russian</option>
                  <option value="en">English</option>
                  <option value="de">German</option>
                  <option value="fr">French</option>
                  <option value="es">Spanish</option>
                </select>
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', color: '#888' }}>Tone</label>
                <select
                  value={contentTask.tone}
                  onChange={e => setContentTask({ ...contentTask, tone: e.target.value })}
                  style={{ width: '100%', padding: '10px', background: '#2d2d2d', border: '1px solid #444', borderRadius: '5px', color: 'white' }}
                >
                  <option value="professional">Professional</option>
                  <option value="friendly">Friendly</option>
                  <option value="casual">Casual</option>
                  <option value="formal">Formal</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button onClick={() => setShowGenerateContent(false)} style={{ padding: '10px 20px', background: '#444', border: 'none', borderRadius: '5px', color: 'white', cursor: 'pointer' }}>
                Cancel
              </button>
              <button onClick={generateContent} disabled={loading || !contentTask.task} style={{ padding: '10px 20px', background: '#2196F3', border: 'none', borderRadius: '5px', color: 'white', cursor: 'pointer' }}>
                {loading ? 'Generating...' : '✨ Generate'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// A/B Testing Tab is handled by EmailABTesting component
// Added to tabs array above

export default SESManager;
