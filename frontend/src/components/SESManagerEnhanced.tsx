import { useState, useEffect } from 'react';
import EmailABTesting from './EmailABTesting';
import SESWarmup from './SESWarmup';
import { useLanguage } from '../contexts/LanguageContext';
import { useTheme } from './ThemeToggle';
import { FeatureHint } from './OptionalFeatures';

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

const SESManagerEnhanced: React.FC = () => {
  const { language } = useLanguage();
  const { theme } = useTheme();
  
  const [activeTab, setActiveTab] = useState('overview');
  const [keys, setKeys] = useState<AWSKey[]>([]);
  const [contents, setContents] = useState<EmailContent[]>([]);
  const [lists, setLists] = useState<RecipientList[]>([]);
  const [showAddKey, setShowAddKey] = useState(false);
  const [showGenerateContent, setShowGenerateContent] = useState(false);
  const [showUploadList, setShowUploadList] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showHint, setShowHint] = useState(true);

  // Form states
  const [newKey, setNewKey] = useState({ access_key_id: '', secret_access_key: '', region: 'us-east-1', name: '' });
  const [contentTask, setContentTask] = useState({ task: '', format_type: 'html', language: 'ru', tone: 'professional' });

  // Переводы
  const t = {
    title: language === 'ru' ? 'AWS SES Менеджер' : 'AWS SES Manager',
    overview: language === 'ru' ? 'Обзор' : 'Overview',
    keys: language === 'ru' ? 'AWS Ключи' : 'AWS Keys',
    content: language === 'ru' ? 'Контент' : 'Content',
    recipients: language === 'ru' ? 'Получатели' : 'Recipients',
    campaigns: language === 'ru' ? 'Кампании' : 'Campaigns',
    abTesting: language === 'ru' ? 'A/B Тестирование' : 'A/B Testing',
    warmup: language === 'ru' ? 'Прогрев' : 'Warm-up',
    addKey: language === 'ru' ? 'Добавить ключ' : 'Add Key',
    generateContent: language === 'ru' ? 'Создать контент' : 'Generate Content',
    uploadList: language === 'ru' ? 'Загрузить список' : 'Upload List',
    noKeys: language === 'ru' ? 'Нет AWS ключей' : 'No AWS Keys',
    noKeysDesc: language === 'ru' ? 'Добавьте AWS SES ключ для начала работы' : 'Add an AWS SES key to get started',
    quickActions: language === 'ru' ? 'Быстрые действия' : 'Quick Actions',
    totalRecipients: language === 'ru' ? 'Всего получателей' : 'Total Recipients',
    emailContents: language === 'ru' ? 'Email контент' : 'Email Contents',
    recipientLists: language === 'ru' ? 'Списки получателей' : 'Recipient Lists',
    delete: language === 'ru' ? 'Удалить' : 'Delete',
    cancel: language === 'ru' ? 'Отмена' : 'Cancel',
    save: language === 'ru' ? 'Сохранить' : 'Save',
    generate: language === 'ru' ? 'Создать' : 'Generate',
    keyName: language === 'ru' ? 'Название ключа' : 'Key Name',
    accessKeyId: language === 'ru' ? 'Access Key ID' : 'Access Key ID',
    secretKey: language === 'ru' ? 'Secret Access Key' : 'Secret Access Key',
    region: language === 'ru' ? 'Регион' : 'Region',
    gettingStarted: language === 'ru' ? 'Начало работы' : 'Getting Started',
    step1: language === 'ru' ? 'Добавьте AWS SES ключ' : 'Add AWS SES key',
    step2: language === 'ru' ? 'Загрузите список получателей' : 'Upload recipient list',
    step3: language === 'ru' ? 'Создайте email контент' : 'Create email content',
    step4: language === 'ru' ? 'Запустите прогрев или кампанию' : 'Start warm-up or campaign',
  };

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
    if (!confirm(language === 'ru' ? 'Удалить этот AWS ключ?' : 'Delete this AWS key?')) return;
    try {
      await fetch(`${API_URL}/api/ses/keys/${keyId}`, { method: 'DELETE' });
      fetchData();
    } catch (e) {
      console.error('Error deleting key:', e);
    }
  };

  const tabs = [
    { id: 'overview', label: t.overview, icon: '📊' },
    { id: 'keys', label: t.keys, icon: '🔑' },
    { id: 'content', label: t.content, icon: '✉️' },
    { id: 'lists', label: t.recipients, icon: '👥' },
    { id: 'campaigns', label: t.campaigns, icon: '🚀' },
    { id: 'abtesting', label: t.abTesting, icon: '🧪' },
    { id: 'warmup', label: t.warmup, icon: '🔥' }
  ];

  const cardBg = theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow';
  const textPrimary = theme === 'dark' ? 'text-white' : 'text-gray-900';
  const textSecondary = theme === 'dark' ? 'text-gray-400' : 'text-gray-500';
  const borderColor = theme === 'dark' ? 'border-gray-700' : 'border-gray-200';

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className={`text-2xl font-bold flex items-center gap-3 ${textPrimary}`}>
          <span className="text-3xl">📧</span>
          {t.title}
        </h2>
        <div className="flex gap-3">
          <span className={`px-4 py-2 rounded-full text-sm ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'} ${textSecondary}`}>
            {keys.length} {t.keys}
          </span>
          <span className={`px-4 py-2 rounded-full text-sm ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'} ${textSecondary}`}>
            {contents.length} {t.content}
          </span>
          <span className={`px-4 py-2 rounded-full text-sm ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'} ${textSecondary}`}>
            {lists.reduce((sum, l) => sum + l.valid_count, 0)} {t.recipients}
          </span>
        </div>
      </div>

      {/* Контекстная подсказка если нет ключей */}
      {keys.length === 0 && showHint && (
        <div className={`mb-6 p-4 rounded-lg border-l-4 border-blue-500 ${
          theme === 'dark' ? 'bg-blue-900/20' : 'bg-blue-50'
        }`}>
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3">
              <span className="text-2xl">💡</span>
              <div>
                <h4 className={`font-semibold ${textPrimary}`}>
                  {t.gettingStarted}
                </h4>
                <p className={`text-sm mt-1 ${textSecondary}`}>
                  {language === 'ru' 
                    ? 'Для начала работы с Email Marketing выполните следующие шаги:'
                    : 'To get started with Email Marketing, follow these steps:'}
                </p>
                <ol className={`mt-3 space-y-2 ${textSecondary}`}>
                  <li className="flex items-center gap-2">
                    <span className={`w-6 h-6 rounded-full flex items-center justify-center text-sm ${
                      keys.length > 0 ? 'bg-green-500 text-white' : theme === 'dark' ? 'bg-gray-600' : 'bg-gray-200'
                    }`}>
                      {keys.length > 0 ? '✓' : '1'}
                    </span>
                    {t.step1}
                  </li>
                  <li className="flex items-center gap-2">
                    <span className={`w-6 h-6 rounded-full flex items-center justify-center text-sm ${
                      lists.length > 0 ? 'bg-green-500 text-white' : theme === 'dark' ? 'bg-gray-600' : 'bg-gray-200'
                    }`}>
                      {lists.length > 0 ? '✓' : '2'}
                    </span>
                    {t.step2}
                  </li>
                  <li className="flex items-center gap-2">
                    <span className={`w-6 h-6 rounded-full flex items-center justify-center text-sm ${
                      contents.length > 0 ? 'bg-green-500 text-white' : theme === 'dark' ? 'bg-gray-600' : 'bg-gray-200'
                    }`}>
                      {contents.length > 0 ? '✓' : '3'}
                    </span>
                    {t.step3}
                  </li>
                  <li className="flex items-center gap-2">
                    <span className={`w-6 h-6 rounded-full flex items-center justify-center text-sm ${theme === 'dark' ? 'bg-gray-600' : 'bg-gray-200'}`}>
                      4
                    </span>
                    {t.step4}
                  </li>
                </ol>
                <button 
                  onClick={() => setShowAddKey(true)}
                  className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
                >
                  🔑 {t.addKey}
                </button>
              </div>
            </div>
            <button 
              onClick={() => setShowHint(false)}
              className={`p-1 rounded hover:bg-gray-200 ${theme === 'dark' ? 'text-gray-400 hover:bg-gray-700' : 'text-gray-400'}`}
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className={`flex gap-1 mb-6 border-b ${borderColor} overflow-x-auto`}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-3 font-medium whitespace-nowrap transition-colors flex items-center gap-2 ${
              activeTab === tab.id
                ? theme === 'dark' 
                  ? 'border-b-2 border-green-500 text-green-400 bg-green-900/20'
                  : 'border-b-2 border-green-500 text-green-600 bg-green-50'
                : theme === 'dark'
                  ? 'text-gray-400 hover:text-white hover:bg-gray-800'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            }`}
          >
            <span>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Stats */}
          <div className="grid grid-cols-4 gap-4">
            <div className={`p-6 rounded-lg text-center ${cardBg}`}>
              <div className="text-4xl font-bold text-green-500">{keys.length}</div>
              <div className={textSecondary}>{t.keys}</div>
            </div>
            <div className={`p-6 rounded-lg text-center ${cardBg}`}>
              <div className="text-4xl font-bold text-blue-500">{contents.length}</div>
              <div className={textSecondary}>{t.emailContents}</div>
            </div>
            <div className={`p-6 rounded-lg text-center ${cardBg}`}>
              <div className="text-4xl font-bold text-orange-500">{lists.length}</div>
              <div className={textSecondary}>{t.recipientLists}</div>
            </div>
            <div className={`p-6 rounded-lg text-center ${cardBg}`}>
              <div className="text-4xl font-bold text-purple-500">
                {lists.reduce((sum, l) => sum + l.valid_count, 0)}
              </div>
              <div className={textSecondary}>{t.totalRecipients}</div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className={`p-6 rounded-lg ${cardBg}`}>
            <h3 className={`text-lg font-bold mb-4 ${textPrimary}`}>{t.quickActions}</h3>
            <div className="flex gap-3">
              <button 
                onClick={() => setShowAddKey(true)} 
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
              >
                🔑 {t.addKey}
              </button>
              <button 
                onClick={() => setShowGenerateContent(true)} 
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                ✨ {t.generateContent}
              </button>
              <button 
                onClick={() => setShowUploadList(true)} 
                className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors flex items-center gap-2"
              >
                📤 {t.uploadList}
              </button>
            </div>
          </div>

          {/* Recent Keys */}
          {keys.length > 0 && (
            <div className={`p-6 rounded-lg ${cardBg}`}>
              <h3 className={`text-lg font-bold mb-4 ${textPrimary}`}>{t.keys}</h3>
              <div className="space-y-3">
                {keys.slice(0, 3).map(key => (
                  <div key={key.id} className={`p-4 rounded-lg border ${borderColor} flex items-center justify-between`}>
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">🔑</span>
                      <div>
                        <h4 className={`font-medium ${textPrimary}`}>{key.name}</h4>
                        <p className={`text-sm ${textSecondary}`}>{key.region} • {key.access_key_id.slice(0, 8)}...</p>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm ${
                      key.status === 'active' ? 'bg-green-500/20 text-green-500' : 'bg-gray-500/20 text-gray-500'
                    }`}>
                      {key.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* AWS Keys Tab */}
      {activeTab === 'keys' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className={`text-lg font-bold ${textPrimary}`}>{t.keys}</h3>
            <button 
              onClick={() => setShowAddKey(true)} 
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              + {t.addKey}
            </button>
          </div>

          {keys.length === 0 ? (
            <div className={`p-12 rounded-lg text-center ${cardBg}`}>
              <span className="text-6xl">🔑</span>
              <h3 className={`text-xl font-bold mt-4 ${textPrimary}`}>{t.noKeys}</h3>
              <p className={`mt-2 ${textSecondary}`}>{t.noKeysDesc}</p>
              <button 
                onClick={() => setShowAddKey(true)} 
                className="mt-4 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                + {t.addKey}
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {keys.map(key => (
                <div key={key.id} className={`p-6 rounded-lg ${cardBg}`}>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-3xl">🔑</span>
                      <div>
                        <h4 className={`font-bold ${textPrimary}`}>{key.name}</h4>
                        <p className={`text-sm ${textSecondary}`}>{key.access_key_id}</p>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm ${
                      key.status === 'active' ? 'bg-green-500/20 text-green-500' : 'bg-gray-500/20 text-gray-500'
                    }`}>
                      {key.status}
                    </span>
                  </div>
                  <div className={`mt-4 pt-4 border-t ${borderColor} grid grid-cols-2 gap-4`}>
                    <div>
                      <p className={`text-sm ${textSecondary}`}>{t.region}</p>
                      <p className={textPrimary}>{key.region}</p>
                    </div>
                    <div>
                      <p className={`text-sm ${textSecondary}`}>{language === 'ru' ? 'Лимит' : 'Limit'}</p>
                      <p className={textPrimary}>{key.sent_today} / {key.daily_limit}</p>
                    </div>
                  </div>
                  <div className="mt-4 flex gap-2">
                    <button 
                      onClick={() => deleteKey(key.id)}
                      className="px-3 py-1 bg-red-600/20 text-red-500 rounded hover:bg-red-600/30 transition-colors"
                    >
                      {t.delete}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* A/B Testing Tab */}
      {activeTab === 'abtesting' && <EmailABTesting />}

      {/* Warm-up Tab */}
      {activeTab === 'warmup' && <SESWarmup />}

      {/* Add Key Modal */}
      {showAddKey && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className={`p-6 rounded-lg w-full max-w-md ${theme === 'dark' ? 'bg-gray-800' : 'bg-white'}`}>
            <h3 className={`text-xl font-bold mb-4 ${textPrimary}`}>{t.addKey}</h3>
            <div className="space-y-4">
              <div>
                <label className={`block text-sm mb-1 ${textSecondary}`}>{t.keyName}</label>
                <input
                  type="text"
                  value={newKey.name}
                  onChange={(e) => setNewKey({...newKey, name: e.target.value})}
                  className={`w-full p-3 rounded-lg border ${
                    theme === 'dark' ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300'
                  }`}
                  placeholder="My AWS Key"
                />
              </div>
              <div>
                <label className={`block text-sm mb-1 ${textSecondary}`}>{t.accessKeyId}</label>
                <input
                  type="text"
                  value={newKey.access_key_id}
                  onChange={(e) => setNewKey({...newKey, access_key_id: e.target.value})}
                  className={`w-full p-3 rounded-lg border ${
                    theme === 'dark' ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300'
                  }`}
                  placeholder="AKIAIOSFODNN7EXAMPLE"
                />
              </div>
              <div>
                <label className={`block text-sm mb-1 ${textSecondary}`}>{t.secretKey}</label>
                <input
                  type="password"
                  value={newKey.secret_access_key}
                  onChange={(e) => setNewKey({...newKey, secret_access_key: e.target.value})}
                  className={`w-full p-3 rounded-lg border ${
                    theme === 'dark' ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300'
                  }`}
                  placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                />
              </div>
              <div>
                <label className={`block text-sm mb-1 ${textSecondary}`}>{t.region}</label>
                <select
                  value={newKey.region}
                  onChange={(e) => setNewKey({...newKey, region: e.target.value})}
                  className={`w-full p-3 rounded-lg border ${
                    theme === 'dark' ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300'
                  }`}
                >
                  <option value="us-east-1">US East (N. Virginia)</option>
                  <option value="us-west-2">US West (Oregon)</option>
                  <option value="eu-west-1">EU (Ireland)</option>
                  <option value="eu-central-1">EU (Frankfurt)</option>
                  <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
                </select>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button 
                onClick={() => setShowAddKey(false)}
                className={`flex-1 px-4 py-2 rounded-lg ${
                  theme === 'dark' ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-200 hover:bg-gray-300'
                } transition-colors`}
              >
                {t.cancel}
              </button>
              <button 
                onClick={addKey}
                disabled={loading || !newKey.access_key_id || !newKey.secret_access_key}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
              >
                {loading ? '...' : t.save}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SESManagerEnhanced;
