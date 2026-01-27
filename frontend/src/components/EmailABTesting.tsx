import React, { useState, useEffect } from 'react';

interface Variant {
  id: string;
  name: string;
  variant_type: string;
  subject: string;
  preheader: string;
  content_id: string;
  sender_name: string;
  sent_count: number;
  delivered_count: number;
  opened_count: number;
  clicked_count: number;
  converted_count: number;
  open_rate: number;
  click_rate: number;
  conversion_rate: number;
}

interface ABTest {
  id: string;
  name: string;
  description: string;
  campaign_id: string;
  variants: Variant[];
  status: string;
  optimization_metric: string;
  test_size_percent: number;
  auto_select_winner: boolean;
  min_sample_size: number;
  confidence_level: number;
  max_test_duration_hours: number;
  winner_variant_id: string | null;
  statistical_significance: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

interface ABTestingStats {
  total_tests: number;
  running_tests: number;
  completed_tests: number;
  draft_tests: number;
  total_variants: number;
  total_opens_tracked: number;
  total_clicks_tracked: number;
  auto_optimization_enabled: boolean;
}

const API_URL = 'http://localhost:8000';

const EmailABTesting: React.FC = () => {
  const [tests, setTests] = useState<ABTest[]>([]);
  const [stats, setStats] = useState<ABTestingStats | null>(null);
  const [selectedTest, setSelectedTest] = useState<ABTest | null>(null);
  const [testResults, setTestResults] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [loading, setLoading] = useState(false);

  // Form state for creating test
  const [newTest, setNewTest] = useState({
    name: '',
    campaign_id: '',
    description: '',
    optimization_metric: 'open_rate',
    test_size_percent: 20,
    auto_select_winner: true,
    min_sample_size: 100,
    confidence_level: 95,
    max_test_duration_hours: 24,
    variants: [
      { name: 'Variant A', variant_type: 'subject', subject: '', preheader: '', content_id: '', sender_name: '' },
      { name: 'Variant B', variant_type: 'subject', subject: '', preheader: '', content_id: '', sender_name: '' }
    ]
  });

  useEffect(() => {
    fetchTests();
    fetchStats();
  }, []);

  const fetchTests = async () => {
    try {
      const res = await fetch(`${API_URL}/api/ses/ab-tests`);
      const data = await res.json();
      setTests(data.tests || []);
    } catch (error) {
      console.error('Error fetching tests:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_URL}/api/ses/ab-tests/stats`);
      const data = await res.json();
      setStats(data.stats);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchTestResults = async (testId: string) => {
    try {
      const res = await fetch(`${API_URL}/api/ses/ab-tests/${testId}/results`);
      const data = await res.json();
      setTestResults(data);
    } catch (error) {
      console.error('Error fetching results:', error);
    }
  };

  const createTest = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/ses/ab-tests`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTest)
      });
      const data = await res.json();
      if (data.success) {
        setShowCreateModal(false);
        fetchTests();
        fetchStats();
      }
    } catch (error) {
      console.error('Error creating test:', error);
    }
    setLoading(false);
  };

  const startTest = async (testId: string) => {
    try {
      await fetch(`${API_URL}/api/ses/ab-tests/${testId}/start`, { method: 'POST' });
      fetchTests();
      fetchStats();
    } catch (error) {
      console.error('Error starting test:', error);
    }
  };

  const pauseTest = async (testId: string) => {
    try {
      await fetch(`${API_URL}/api/ses/ab-tests/${testId}/pause`, { method: 'POST' });
      fetchTests();
    } catch (error) {
      console.error('Error pausing test:', error);
    }
  };

  const completeTest = async (testId: string, winnerId?: string) => {
    try {
      const url = winnerId 
        ? `${API_URL}/api/ses/ab-tests/${testId}/complete?winner_variant_id=${winnerId}`
        : `${API_URL}/api/ses/ab-tests/${testId}/complete`;
      await fetch(url, { method: 'POST' });
      fetchTests();
      fetchStats();
    } catch (error) {
      console.error('Error completing test:', error);
    }
  };

  const deleteTest = async (testId: string) => {
    if (!confirm('Delete this A/B test?')) return;
    try {
      await fetch(`${API_URL}/api/ses/ab-tests/${testId}`, { method: 'DELETE' });
      fetchTests();
      fetchStats();
      setSelectedTest(null);
    } catch (error) {
      console.error('Error deleting test:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'bg-green-500';
      case 'completed': case 'winner_selected': return 'bg-blue-500';
      case 'paused': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'running': return 'Running';
      case 'completed': return 'Completed';
      case 'winner_selected': return 'Winner Selected';
      case 'paused': return 'Paused';
      default: return 'Draft';
    }
  };

  const addVariant = () => {
    const letter = String.fromCharCode(65 + newTest.variants.length);
    setNewTest({
      ...newTest,
      variants: [...newTest.variants, {
        name: `Variant ${letter}`,
        variant_type: 'subject',
        subject: '',
        preheader: '',
        content_id: '',
        sender_name: ''
      }]
    });
  };

  const removeVariant = (index: number) => {
    if (newTest.variants.length <= 2) return;
    setNewTest({
      ...newTest,
      variants: newTest.variants.filter((_, i) => i !== index)
    });
  };

  const updateVariant = (index: number, field: string, value: string) => {
    const updated = [...newTest.variants];
    updated[index] = { ...updated[index], [field]: value };
    setNewTest({ ...newTest, variants: updated });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            🧪 A/B Testing
          </h2>
          <p className="text-gray-400 text-sm mt-1">
            Test email variants and optimize for best performance
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg flex items-center gap-2"
        >
          ➕ New A/B Test
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gray-800 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-purple-400">{stats.total_tests}</div>
            <div className="text-gray-400 text-sm">Total Tests</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-green-400">{stats.running_tests}</div>
            <div className="text-gray-400 text-sm">Running</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-blue-400">{stats.completed_tests}</div>
            <div className="text-gray-400 text-sm">Completed</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-cyan-400">{stats.total_opens_tracked}</div>
            <div className="text-gray-400 text-sm">Opens Tracked</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-700 pb-2">
        {['overview', 'tests', 'results'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-t-lg capitalize ${
              activeTab === tab ? 'bg-purple-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            {tab === 'overview' ? '📊 Overview' : tab === 'tests' ? '🧪 Tests' : '📈 Results'}
          </button>
        ))}
      </div>

      {/* Content */}
      {activeTab === 'overview' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">How A/B Testing Works</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-2xl mb-2">1️⃣</div>
              <h4 className="font-semibold text-purple-400">Create Variants</h4>
              <p className="text-gray-400 text-sm mt-2">
                Create 2+ email variants with different subjects, content, or send times
              </p>
            </div>
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-2xl mb-2">2️⃣</div>
              <h4 className="font-semibold text-green-400">Run Test</h4>
              <p className="text-gray-400 text-sm mt-2">
                Send variants to a test segment and track opens, clicks, conversions
              </p>
            </div>
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-2xl mb-2">3️⃣</div>
              <h4 className="font-semibold text-blue-400">Auto-Optimize</h4>
              <p className="text-gray-400 text-sm mt-2">
                System automatically selects winner based on statistical significance
              </p>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-4 mt-4">
            <h4 className="font-semibold mb-3">Optimization Metrics</h4>
            <div className="grid grid-cols-3 gap-4">
              <div className="flex items-center gap-2">
                <span className="text-2xl">📬</span>
                <div>
                  <div className="font-medium">Open Rate</div>
                  <div className="text-gray-400 text-sm">% of emails opened</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-2xl">🖱️</span>
                <div>
                  <div className="font-medium">Click Rate</div>
                  <div className="text-gray-400 text-sm">% of links clicked</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-2xl">🎯</span>
                <div>
                  <div className="font-medium">Conversion Rate</div>
                  <div className="text-gray-400 text-sm">% of conversions</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'tests' && (
        <div className="space-y-4">
          {tests.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <div className="text-4xl mb-4">🧪</div>
              <p>No A/B tests yet. Create your first test!</p>
            </div>
          ) : (
            tests.map(test => (
              <div
                key={test.id}
                className={`bg-gray-800 rounded-lg p-4 cursor-pointer hover:bg-gray-750 ${
                  selectedTest?.id === test.id ? 'ring-2 ring-purple-500' : ''
                }`}
                onClick={() => {
                  setSelectedTest(test);
                  fetchTestResults(test.id);
                }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className={`w-3 h-3 rounded-full ${getStatusColor(test.status)}`}></span>
                    <div>
                      <h4 className="font-semibold">{test.name}</h4>
                      <p className="text-gray-400 text-sm">{test.variants.length} variants • {test.optimization_metric.replace('_', ' ')}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded text-xs ${getStatusColor(test.status)} bg-opacity-20`}>
                      {getStatusText(test.status)}
                    </span>
                    {test.status === 'draft' && (
                      <button
                        onClick={(e) => { e.stopPropagation(); startTest(test.id); }}
                        className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm"
                      >
                        ▶️ Start
                      </button>
                    )}
                    {test.status === 'running' && (
                      <>
                        <button
                          onClick={(e) => { e.stopPropagation(); pauseTest(test.id); }}
                          className="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 rounded text-sm"
                        >
                          ⏸️ Pause
                        </button>
                        <button
                          onClick={(e) => { e.stopPropagation(); completeTest(test.id); }}
                          className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
                        >
                          ✅ Complete
                        </button>
                      </>
                    )}
                    <button
                      onClick={(e) => { e.stopPropagation(); deleteTest(test.id); }}
                      className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm"
                    >
                      🗑️
                    </button>
                  </div>
                </div>

                {/* Variants Preview */}
                <div className="mt-4 grid grid-cols-2 gap-2">
                  {test.variants.map((variant, idx) => (
                    <div
                      key={variant.id}
                      className={`p-3 rounded ${
                        test.winner_variant_id === variant.id ? 'bg-green-900/30 border border-green-500' : 'bg-gray-700/50'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">{variant.name}</span>
                        {test.winner_variant_id === variant.id && (
                          <span className="text-green-400 text-sm">🏆 Winner</span>
                        )}
                      </div>
                      <div className="grid grid-cols-3 gap-2 text-sm">
                        <div>
                          <div className="text-gray-400">Opens</div>
                          <div className="font-semibold text-purple-400">{variant.open_rate.toFixed(1)}%</div>
                        </div>
                        <div>
                          <div className="text-gray-400">Clicks</div>
                          <div className="font-semibold text-blue-400">{variant.click_rate.toFixed(1)}%</div>
                        </div>
                        <div>
                          <div className="text-gray-400">Sent</div>
                          <div className="font-semibold">{variant.sent_count}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Statistical Significance */}
                {test.statistical_significance > 0 && (
                  <div className="mt-3 flex items-center gap-2">
                    <span className="text-gray-400 text-sm">Statistical Significance:</span>
                    <div className="flex-1 bg-gray-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          test.statistical_significance >= test.confidence_level ? 'bg-green-500' : 'bg-yellow-500'
                        }`}
                        style={{ width: `${Math.min(test.statistical_significance, 100)}%` }}
                      ></div>
                    </div>
                    <span className={`text-sm font-semibold ${
                      test.statistical_significance >= test.confidence_level ? 'text-green-400' : 'text-yellow-400'
                    }`}>
                      {test.statistical_significance.toFixed(1)}%
                    </span>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === 'results' && testResults && (
        <div className="space-y-4">
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">Test Results: {testResults.test?.name}</h3>
            
            {/* Recommendation */}
            <div className="bg-purple-900/30 border border-purple-500 rounded-lg p-4 mb-4">
              <h4 className="font-semibold text-purple-400 mb-2">💡 Recommendation</h4>
              <p>{testResults.recommendation}</p>
            </div>

            {/* Improvement */}
            {testResults.improvement_percent !== 0 && (
              <div className="bg-green-900/30 border border-green-500 rounded-lg p-4 mb-4">
                <h4 className="font-semibold text-green-400 mb-2">📈 Improvement</h4>
                <p className="text-2xl font-bold">
                  {testResults.improvement_percent > 0 ? '+' : ''}{testResults.improvement_percent}%
                </p>
                <p className="text-gray-400 text-sm">Best variant vs worst variant</p>
              </div>
            )}

            {/* Ranked Variants */}
            <h4 className="font-semibold mb-3">Variants Ranked by Performance</h4>
            <div className="space-y-2">
              {testResults.variants_ranked?.map((variant: Variant, idx: number) => (
                <div
                  key={variant.id}
                  className={`p-4 rounded-lg ${
                    idx === 0 ? 'bg-green-900/20 border border-green-500' : 'bg-gray-700/50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{idx === 0 ? '🥇' : idx === 1 ? '🥈' : '🥉'}</span>
                      <div>
                        <h5 className="font-semibold">{variant.name}</h5>
                        <p className="text-gray-400 text-sm">{variant.subject || 'No subject'}</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-4 gap-4 text-center">
                      <div>
                        <div className="text-xl font-bold text-purple-400">{variant.open_rate.toFixed(1)}%</div>
                        <div className="text-gray-400 text-xs">Open Rate</div>
                      </div>
                      <div>
                        <div className="text-xl font-bold text-blue-400">{variant.click_rate.toFixed(1)}%</div>
                        <div className="text-gray-400 text-xs">Click Rate</div>
                      </div>
                      <div>
                        <div className="text-xl font-bold text-green-400">{variant.conversion_rate.toFixed(1)}%</div>
                        <div className="text-gray-400 text-xs">Conv Rate</div>
                      </div>
                      <div>
                        <div className="text-xl font-bold">{variant.sent_count}</div>
                        <div className="text-gray-400 text-xs">Sent</div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Create Test Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-bold mb-4">Create A/B Test</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Test Name *</label>
                <input
                  type="text"
                  value={newTest.name}
                  onChange={(e) => setNewTest({ ...newTest, name: e.target.value })}
                  className="w-full bg-gray-700 rounded px-3 py-2"
                  placeholder="e.g., Subject Line Test - January"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Campaign ID</label>
                <input
                  type="text"
                  value={newTest.campaign_id}
                  onChange={(e) => setNewTest({ ...newTest, campaign_id: e.target.value })}
                  className="w-full bg-gray-700 rounded px-3 py-2"
                  placeholder="campaign_123"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Optimization Metric</label>
                  <select
                    value={newTest.optimization_metric}
                    onChange={(e) => setNewTest({ ...newTest, optimization_metric: e.target.value })}
                    className="w-full bg-gray-700 rounded px-3 py-2"
                  >
                    <option value="open_rate">Open Rate</option>
                    <option value="click_rate">Click Rate</option>
                    <option value="conversion_rate">Conversion Rate</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Test Size (%)</label>
                  <input
                    type="number"
                    value={newTest.test_size_percent}
                    onChange={(e) => setNewTest({ ...newTest, test_size_percent: Number(e.target.value) })}
                    className="w-full bg-gray-700 rounded px-3 py-2"
                    min="5"
                    max="50"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Min Sample Size</label>
                  <input
                    type="number"
                    value={newTest.min_sample_size}
                    onChange={(e) => setNewTest({ ...newTest, min_sample_size: Number(e.target.value) })}
                    className="w-full bg-gray-700 rounded px-3 py-2"
                    min="50"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Confidence Level (%)</label>
                  <input
                    type="number"
                    value={newTest.confidence_level}
                    onChange={(e) => setNewTest({ ...newTest, confidence_level: Number(e.target.value) })}
                    className="w-full bg-gray-700 rounded px-3 py-2"
                    min="80"
                    max="99"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Max Duration (hours)</label>
                  <input
                    type="number"
                    value={newTest.max_test_duration_hours}
                    onChange={(e) => setNewTest({ ...newTest, max_test_duration_hours: Number(e.target.value) })}
                    className="w-full bg-gray-700 rounded px-3 py-2"
                    min="1"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={newTest.auto_select_winner}
                  onChange={(e) => setNewTest({ ...newTest, auto_select_winner: e.target.checked })}
                  className="rounded"
                />
                <label className="text-sm">Auto-select winner when statistical significance is reached</label>
              </div>

              {/* Variants */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm text-gray-400">Variants</label>
                  <button
                    onClick={addVariant}
                    className="text-sm text-purple-400 hover:text-purple-300"
                  >
                    + Add Variant
                  </button>
                </div>
                <div className="space-y-3">
                  {newTest.variants.map((variant, idx) => (
                    <div key={idx} className="bg-gray-700 rounded-lg p-3">
                      <div className="flex items-center justify-between mb-2">
                        <input
                          type="text"
                          value={variant.name}
                          onChange={(e) => updateVariant(idx, 'name', e.target.value)}
                          className="bg-gray-600 rounded px-2 py-1 text-sm font-medium"
                        />
                        {newTest.variants.length > 2 && (
                          <button
                            onClick={() => removeVariant(idx)}
                            className="text-red-400 hover:text-red-300 text-sm"
                          >
                            Remove
                          </button>
                        )}
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <input
                          type="text"
                          value={variant.subject}
                          onChange={(e) => updateVariant(idx, 'subject', e.target.value)}
                          className="bg-gray-600 rounded px-2 py-1 text-sm"
                          placeholder="Subject line"
                        />
                        <input
                          type="text"
                          value={variant.preheader}
                          onChange={(e) => updateVariant(idx, 'preheader', e.target.value)}
                          className="bg-gray-600 rounded px-2 py-1 text-sm"
                          placeholder="Preheader text"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded"
              >
                Cancel
              </button>
              <button
                onClick={createTest}
                disabled={loading || !newTest.name}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded disabled:opacity-50"
              >
                {loading ? 'Creating...' : 'Create Test'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmailABTesting;
