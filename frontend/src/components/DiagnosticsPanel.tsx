import React, { useState, useEffect, useCallback } from 'react';

// ==================== ИНТЕРФЕЙСЫ ====================

interface DiagnosticResult {
  check_id: string;
  category: string;
  name: string;
  status: string;
  message: string;
  details?: Record<string, any>;
  fix_available: boolean;
  fix_applied: boolean;
  severity?: string;
  recommendations?: string[];
  duration_ms?: number;
  timestamp: string;
}

interface DiagnosticsStatus {
  auto_mode_enabled: boolean;
  auto_fix_enabled: boolean;
  check_interval: number;
  total_checks: number;
  total_fixes: number;
  history_size: number;
  fixes_history_size: number;
  last_full_check?: string;
}

interface HealthSummary {
  overall_status: string;
  health_score: number;
  auto_mode: boolean;
  auto_fix: boolean;
  checks_count: number;
  fixes_count: number;
  last_check_results: number;
  issues_count: number;
  critical_issues: number;
  issues_by_category: Record<string, number>;
  last_full_check?: string;
}

interface HealthReport {
  overall_status: string;
  health_score: number;
  total_checks: number;
  passed_checks: number;
  warning_checks: number;
  error_checks: number;
  critical_checks: number;
  fixed_checks: number;
  categories_summary: Record<string, any>;
  top_issues: any[];
  recommendations: string[];
  timestamp: string;
}

interface FixResult {
  check_id: string;
  success: boolean;
  message: string;
  before_status: string;
  after_status: string;
  actions_taken?: string[];
  timestamp: string;
}

interface CategoryInfo {
  name: string;
  display_name: string;
  checks_count: number;
  description: string;
}

const API_URL = 'http://144.31.238.16:8000';

const DiagnosticsPanel: React.FC = () => {
  // ==================== СОСТОЯНИЕ ====================
  const [status, setStatus] = useState<DiagnosticsStatus | null>(null);
  const [healthSummary, setHealthSummary] = useState<HealthSummary | null>(null);
  const [healthReport, setHealthReport] = useState<HealthReport | null>(null);
  const [results, setResults] = useState<DiagnosticResult[]>([]);
  const [resultsByCategory, setResultsByCategory] = useState<Record<string, DiagnosticResult[]>>({});
  const [fixResults, setFixResults] = useState<FixResult[]>([]);
  const [categories, setCategories] = useState<CategoryInfo[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [fixesHistory, setFixesHistory] = useState<any[]>([]);
  
  const [loading, setLoading] = useState(false);
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  const [checkInterval, setCheckInterval] = useState(300);
  const [activeTab, setActiveTab] = useState<'overview' | 'results' | 'categories' | 'history' | 'settings'>('overview');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [expandedChecks, setExpandedChecks] = useState<Set<string>>(new Set());

  // ==================== API ФУНКЦИИ ====================

  const fetchStatus = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/status`);
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
        setCheckInterval(data.check_interval);
      }
    } catch (err) {
      console.error('Failed to fetch status:', err);
    }
  }, []);

  const fetchHealthSummary = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/health-summary`);
      if (response.ok) {
        const data = await response.json();
        setHealthSummary(data);
      }
    } catch (err) {
      console.error('Failed to fetch health summary:', err);
    }
  }, []);

  const fetchHealthReport = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/health-report`);
      if (response.ok) {
        const data = await response.json();
        setHealthReport(data);
      }
    } catch (err) {
      console.error('Failed to fetch health report:', err);
    }
  }, []);

  const fetchLastResults = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/last-results`);
      if (response.ok) {
        const data = await response.json();
        setResults(data.results || []);
        setResultsByCategory(data.by_category || {});
      }
    } catch (err) {
      console.error('Failed to fetch results:', err);
    }
  }, []);

  const fetchCategories = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/categories`);
      if (response.ok) {
        const data = await response.json();
        setCategories(data.categories || []);
      }
    } catch (err) {
      console.error('Failed to fetch categories:', err);
    }
  }, []);

  const fetchHistory = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/history?limit=100`);
      if (response.ok) {
        const data = await response.json();
        setHistory(data.history || []);
      }
    } catch (err) {
      console.error('Failed to fetch history:', err);
    }
  }, []);

  const fetchFixesHistory = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/fixes-history?limit=50`);
      if (response.ok) {
        const data = await response.json();
        setFixesHistory(data.history || []);
      }
    } catch (err) {
      console.error('Failed to fetch fixes history:', err);
    }
  }, []);

  // ==================== ДЕЙСТВИЯ ====================

  const runAllChecks = async () => {
    setLoading(true);
    setLoadingAction('run-all');
    setError(null);
    setSuccess(null);
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/run-all`, {
        method: 'POST'
      });
      if (response.ok) {
        const data = await response.json();
        setResults(data.results || []);
        setSuccess(`Completed ${data.summary.total} checks: ${data.summary.ok} OK, ${data.summary.warnings} warnings, ${data.summary.errors} errors`);
        await fetchHealthSummary();
        await fetchHealthReport();
      } else {
        setError('Failed to run diagnostics');
      }
    } catch (err) {
      setError('Error running diagnostics');
    } finally {
      setLoading(false);
      setLoadingAction(null);
    }
  };

  const runQuickCheck = async () => {
    setLoading(true);
    setLoadingAction('run-quick');
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/run-quick`, {
        method: 'POST'
      });
      if (response.ok) {
        const data = await response.json();
        setSuccess(`Quick check: ${data.summary.ok} OK, ${data.summary.issues} issues`);
        await fetchHealthSummary();
      } else {
        setError('Failed to run quick check');
      }
    } catch (err) {
      setError('Error running quick check');
    } finally {
      setLoading(false);
      setLoadingAction(null);
    }
  };

  const runCategoryCheck = async (category: string) => {
    setLoading(true);
    setLoadingAction(`run-category-${category}`);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/run-category`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category })
      });
      if (response.ok) {
        const data = await response.json();
        setSuccess(`Category "${category}": ${data.summary.ok} OK, ${data.summary.issues} issues`);
        await fetchLastResults();
      } else {
        setError(`Failed to run ${category} checks`);
      }
    } catch (err) {
      setError('Error running category check');
    } finally {
      setLoading(false);
      setLoadingAction(null);
    }
  };

  const applyAllFixes = async () => {
    setLoading(true);
    setLoadingAction('fix-all');
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/fix-all`, {
        method: 'POST'
      });
      if (response.ok) {
        const data = await response.json();
        setFixResults(data.results || []);
        setSuccess(`Applied ${data.summary.successful} fixes, ${data.summary.failed} failed`);
        await runAllChecks();
      } else {
        setError('Failed to apply fixes');
      }
    } catch (err) {
      setError('Error applying fixes');
    } finally {
      setLoading(false);
      setLoadingAction(null);
    }
  };

  const applySingleFix = async (checkId: string) => {
    setLoading(true);
    setLoadingAction(`fix-${checkId}`);
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/fix`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ check_id: checkId })
      });
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setSuccess(`Fixed: ${checkId}`);
        } else {
          setError(`Fix failed: ${data.message}`);
        }
        await fetchLastResults();
        await fetchHealthSummary();
      }
    } catch (err) {
      console.error('Error applying fix:', err);
    } finally {
      setLoading(false);
      setLoadingAction(null);
    }
  };

  const toggleAutoMode = async () => {
    if (!status) return;
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/auto-mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !status.auto_mode_enabled })
      });
      if (response.ok) {
        await fetchStatus();
        setSuccess(`Auto mode ${!status.auto_mode_enabled ? 'enabled' : 'disabled'}`);
      }
    } catch (err) {
      console.error('Error toggling auto mode:', err);
    }
  };

  const toggleAutoFix = async () => {
    if (!status) return;
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/auto-fix`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !status.auto_fix_enabled })
      });
      if (response.ok) {
        await fetchStatus();
        setSuccess(`Auto-fix ${!status.auto_fix_enabled ? 'enabled' : 'disabled'}`);
      }
    } catch (err) {
      console.error('Error toggling auto fix:', err);
    }
  };

  const updateCheckInterval = async () => {
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/check-interval`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seconds: checkInterval })
      });
      if (response.ok) {
        await fetchStatus();
        setSuccess(`Check interval updated to ${checkInterval} seconds`);
      }
    } catch (err) {
      console.error('Error updating interval:', err);
    }
  };

  // ==================== ЭФФЕКТЫ ====================

  useEffect(() => {
    fetchStatus();
    fetchHealthSummary();
    fetchLastResults();
    fetchCategories();
  }, [fetchStatus, fetchHealthSummary, fetchLastResults, fetchCategories]);

  useEffect(() => {
    if (activeTab === 'history') {
      fetchHistory();
      fetchFixesHistory();
    }
  }, [activeTab, fetchHistory, fetchFixesHistory]);

  // Автоочистка сообщений
  useEffect(() => {
    if (success || error) {
      const timer = setTimeout(() => {
        setSuccess(null);
        setError(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [success, error]);

  // ==================== УТИЛИТЫ ====================

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ok':
      case 'fixed':
      case 'healthy':
        return 'text-green-400';
      case 'warning':
        return 'text-yellow-400';
      case 'error':
        return 'text-orange-400';
      case 'critical':
        return 'text-red-500';
      case 'skipped':
        return 'text-gray-500';
      default:
        return 'text-gray-400';
    }
  };

  const getStatusBg = (status: string) => {
    switch (status) {
      case 'ok':
      case 'fixed':
      case 'healthy':
        return 'bg-green-600';
      case 'warning':
        return 'bg-yellow-600';
      case 'error':
        return 'bg-orange-600';
      case 'critical':
        return 'bg-red-600';
      case 'skipped':
        return 'bg-gray-600';
      default:
        return 'bg-gray-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ok':
      case 'fixed':
      case 'healthy':
        return '✓';
      case 'warning':
        return '⚠';
      case 'error':
        return '✗';
      case 'critical':
        return '🔥';
      case 'skipped':
        return '⊘';
      default:
        return '?';
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-600 text-white';
      case 'high':
        return 'bg-orange-600 text-white';
      case 'medium':
        return 'bg-yellow-600 text-black';
      case 'low':
        return 'bg-blue-600 text-white';
      default:
        return 'bg-gray-600 text-white';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'database':
        return '🗄️';
      case 'api':
        return '🔌';
      case 'email':
        return '📧';
      case 'ses':
        return '📨';
      case 'storage':
        return '💾';
      case 'security':
        return '🔒';
      case 'performance':
        return '⚡';
      case 'network':
        return '🌐';
      case 'scheduler':
        return '⏰';
      case 'warmup':
        return '🔥';
      case 'recipients':
        return '👥';
      case 'templates':
        return '📝';
      case 'campaigns':
        return '📊';
      default:
        return '📋';
    }
  };

  const getHealthScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 70) return 'text-yellow-400';
    if (score >= 50) return 'text-orange-400';
    return 'text-red-400';
  };

  const toggleExpanded = (checkId: string) => {
    const newExpanded = new Set(expandedChecks);
    if (newExpanded.has(checkId)) {
      newExpanded.delete(checkId);
    } else {
      newExpanded.add(checkId);
    }
    setExpandedChecks(newExpanded);
  };

  // ==================== РЕНДЕР ====================

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <span>🔍</span>
          Diagnostics & Auto-Fix
        </h2>
        {status?.last_full_check && (
          <span className="text-sm text-gray-500">
            Last check: {new Date(status.last_full_check).toLocaleString()}
          </span>
        )}
      </div>

      {/* Уведомления */}
      {error && (
        <div className="mb-4 p-3 bg-red-900/30 border border-red-500 rounded-lg text-red-400 flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-red-300">✕</button>
        </div>
      )}
      {success && (
        <div className="mb-4 p-3 bg-green-900/30 border border-green-500 rounded-lg text-green-400 flex items-center justify-between">
          <span>{success}</span>
          <button onClick={() => setSuccess(null)} className="text-green-400 hover:text-green-300">✕</button>
        </div>
      )}

      {/* Сводка здоровья */}
      {healthSummary && (
        <div className={`mb-6 p-5 rounded-xl border-2 ${
          healthSummary.overall_status === 'healthy' ? 'border-green-500 bg-green-900/20' :
          healthSummary.overall_status === 'warning' ? 'border-yellow-500 bg-yellow-900/20' :
          healthSummary.overall_status === 'error' ? 'border-orange-500 bg-orange-900/20' :
          'border-red-500 bg-red-900/20'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className={`text-5xl ${getStatusColor(healthSummary.overall_status)}`}>
                {getStatusIcon(healthSummary.overall_status)}
              </div>
              <div>
                <h3 className="text-xl font-bold capitalize">
                  System Status: {healthSummary.overall_status}
                </h3>
                <p className="text-gray-400">
                  {healthSummary.issues_count === 0 
                    ? 'All systems operational' 
                    : `${healthSummary.issues_count} issues detected${healthSummary.critical_issues > 0 ? ` (${healthSummary.critical_issues} critical)` : ''}`}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-6">
              {/* Health Score */}
              <div className="text-center">
                <div className={`text-4xl font-bold ${getHealthScoreColor(healthSummary.health_score)}`}>
                  {healthSummary.health_score}
                </div>
                <div className="text-xs text-gray-500">Health Score</div>
              </div>
              
              {/* Status badges */}
              <div className="flex flex-col gap-2">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  healthSummary.auto_mode ? 'bg-green-600' : 'bg-gray-600'
                }`}>
                  Auto Mode: {healthSummary.auto_mode ? 'ON' : 'OFF'}
                </span>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  healthSummary.auto_fix ? 'bg-green-600' : 'bg-gray-600'
                }`}>
                  Auto-Fix: {healthSummary.auto_fix ? 'ON' : 'OFF'}
                </span>
              </div>
            </div>
          </div>

          {/* Issues by category */}
          {Object.keys(healthSummary.issues_by_category).length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-700">
              <div className="flex flex-wrap gap-2">
                {Object.entries(healthSummary.issues_by_category).map(([cat, count]) => (
                  <span key={cat} className="px-2 py-1 bg-gray-700 rounded text-sm">
                    {getCategoryIcon(cat)} {cat}: {count}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Кнопки управления */}
      <div className="flex flex-wrap gap-3 mb-6">
        <button
          onClick={runAllChecks}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium disabled:opacity-50 flex items-center gap-2 transition-colors"
        >
          {loadingAction === 'run-all' ? (
            <span className="animate-spin">⟳</span>
          ) : (
            <span>🔍</span>
          )}
          Run Full Diagnostics
        </button>
        
        <button
          onClick={runQuickCheck}
          disabled={loading}
          className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg font-medium disabled:opacity-50 flex items-center gap-2 transition-colors"
        >
          {loadingAction === 'run-quick' ? (
            <span className="animate-spin">⟳</span>
          ) : (
            <span>⚡</span>
          )}
          Quick Check
        </button>
        
        <button
          onClick={applyAllFixes}
          disabled={loading || results.filter(r => r.fix_available && r.status !== 'ok' && r.status !== 'fixed').length === 0}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-medium disabled:opacity-50 flex items-center gap-2 transition-colors"
        >
          {loadingAction === 'fix-all' ? (
            <span className="animate-spin">⟳</span>
          ) : (
            <span>🔧</span>
          )}
          Fix All Issues ({results.filter(r => r.fix_available && r.status !== 'ok' && r.status !== 'fixed').length})
        </button>
        
        <div className="flex-1" />
        
        <button
          onClick={toggleAutoMode}
          className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors ${
            status?.auto_mode_enabled ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-600 hover:bg-gray-700'
          }`}
        >
          <span>⚡</span>
          Auto: {status?.auto_mode_enabled ? 'ON' : 'OFF'}
        </button>
        
        <button
          onClick={toggleAutoFix}
          className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors ${
            status?.auto_fix_enabled ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-600 hover:bg-gray-700'
          }`}
        >
          <span>🛠</span>
          Auto-Fix: {status?.auto_fix_enabled ? 'ON' : 'OFF'}
        </button>
      </div>

      {/* Табы */}
      <div className="flex gap-1 mb-6 border-b border-gray-700 overflow-x-auto">
        {(['overview', 'results', 'categories', 'history', 'settings'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-3 font-medium capitalize whitespace-nowrap transition-colors ${
              activeTab === tab
                ? 'border-b-2 border-blue-500 text-blue-400 bg-blue-900/20'
                : 'text-gray-400 hover:text-white hover:bg-gray-800'
            }`}
          >
            {tab === 'overview' && '📊 '}
            {tab === 'results' && '📋 '}
            {tab === 'categories' && '📁 '}
            {tab === 'history' && '📜 '}
            {tab === 'settings' && '⚙️ '}
            {tab}
          </button>
        ))}
      </div>

      {/* ==================== TAB: OVERVIEW ==================== */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Статистика */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <div className="p-4 bg-gray-800 rounded-lg text-center">
              <div className="text-3xl font-bold text-green-400">
                {results.filter(r => r.status === 'ok').length}
              </div>
              <div className="text-sm text-gray-400">Passed</div>
            </div>
            <div className="p-4 bg-gray-800 rounded-lg text-center">
              <div className="text-3xl font-bold text-yellow-400">
                {results.filter(r => r.status === 'warning').length}
              </div>
              <div className="text-sm text-gray-400">Warnings</div>
            </div>
            <div className="p-4 bg-gray-800 rounded-lg text-center">
              <div className="text-3xl font-bold text-orange-400">
                {results.filter(r => r.status === 'error').length}
              </div>
              <div className="text-sm text-gray-400">Errors</div>
            </div>
            <div className="p-4 bg-gray-800 rounded-lg text-center">
              <div className="text-3xl font-bold text-red-500">
                {results.filter(r => r.status === 'critical').length}
              </div>
              <div className="text-sm text-gray-400">Critical</div>
            </div>
            <div className="p-4 bg-gray-800 rounded-lg text-center">
              <div className="text-3xl font-bold text-blue-400">
                {results.filter(r => r.status === 'fixed').length}
              </div>
              <div className="text-sm text-gray-400">Fixed</div>
            </div>
            <div className="p-4 bg-gray-800 rounded-lg text-center">
              <div className="text-3xl font-bold text-gray-400">
                {results.filter(r => r.status === 'skipped').length}
              </div>
              <div className="text-sm text-gray-400">Skipped</div>
            </div>
          </div>

          {/* Карточки проверок */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.map((result) => (
              <div
                key={result.check_id}
                className={`p-4 bg-gray-800 rounded-lg border transition-all hover:shadow-lg ${
                  result.status === 'ok' || result.status === 'fixed' ? 'border-gray-700' :
                  result.status === 'warning' ? 'border-yellow-600/50' :
                  result.status === 'critical' ? 'border-red-600' :
                  'border-orange-600/50'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={`text-2xl ${getStatusColor(result.status)}`}>
                      {getStatusIcon(result.status)}
                    </span>
                    <div>
                      <span className="font-medium">{result.name}</span>
                      {result.severity && (
                        <span className={`ml-2 text-xs px-1.5 py-0.5 rounded ${getSeverityBadge(result.severity)}`}>
                          {result.severity}
                        </span>
                      )}
                    </div>
                  </div>
                  <span className="text-xs text-gray-500 px-2 py-1 bg-gray-700 rounded flex items-center gap-1">
                    {getCategoryIcon(result.category)}
                    {result.category}
                  </span>
                </div>
                
                <p className="text-sm text-gray-400 mb-3 line-clamp-2">{result.message}</p>
                
                {result.duration_ms !== undefined && (
                  <p className="text-xs text-gray-500 mb-2">Duration: {result.duration_ms}ms</p>
                )}
                
                <div className="flex items-center justify-between">
                  {result.fix_available && result.status !== 'ok' && result.status !== 'fixed' ? (
                    <button
                      onClick={() => applySingleFix(result.check_id)}
                      disabled={loading}
                      className="text-sm px-3 py-1 bg-yellow-600 hover:bg-yellow-700 rounded disabled:opacity-50 flex items-center gap-1 transition-colors"
                    >
                      {loadingAction === `fix-${result.check_id}` ? (
                        <span className="animate-spin">⟳</span>
                      ) : (
                        <span>🔧</span>
                      )}
                      Fix
                    </button>
                  ) : result.fix_applied ? (
                    <span className="text-sm text-green-400 flex items-center gap-1">
                      <span>✓</span> Fixed
                    </span>
                  ) : (
                    <span />
                  )}
                  
                  <button
                    onClick={() => toggleExpanded(result.check_id)}
                    className="text-xs text-gray-500 hover:text-gray-300"
                  >
                    {expandedChecks.has(result.check_id) ? '▼ Less' : '▶ More'}
                  </button>
                </div>
                
                {expandedChecks.has(result.check_id) && (
                  <div className="mt-3 pt-3 border-t border-gray-700">
                    {result.recommendations && result.recommendations.length > 0 && (
                      <div className="mb-2">
                        <p className="text-xs text-gray-500 mb-1">Recommendations:</p>
                        <ul className="text-xs text-gray-400 list-disc list-inside">
                          {result.recommendations.map((rec, i) => (
                            <li key={i}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {result.details && (
                      <details className="mt-2">
                        <summary className="text-xs text-gray-500 cursor-pointer">Technical Details</summary>
                        <pre className="mt-1 p-2 bg-gray-900 rounded text-xs overflow-auto max-h-32">
                          {JSON.stringify(result.details, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>

          {results.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <span className="text-4xl mb-4 block">🔍</span>
              <p>No diagnostic results yet. Click "Run Full Diagnostics" to start.</p>
            </div>
          )}
        </div>
      )}

      {/* ==================== TAB: RESULTS ==================== */}
      {activeTab === 'results' && (
        <div className="space-y-3">
          {results.map((result) => (
            <div
              key={result.check_id}
              className={`p-4 bg-gray-800 rounded-lg border transition-all ${
                result.status === 'critical' ? 'border-red-600' :
                result.status === 'error' ? 'border-orange-600/50' :
                result.status === 'warning' ? 'border-yellow-600/50' :
                'border-gray-700'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <span className={`text-2xl ${getStatusColor(result.status)}`}>
                    {getStatusIcon(result.status)}
                  </span>
                  <div>
                    <h4 className="font-medium">{result.name}</h4>
                    <p className="text-sm text-gray-500">{result.check_id}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {result.severity && (
                    <span className={`text-xs px-2 py-1 rounded ${getSeverityBadge(result.severity)}`}>
                      {result.severity}
                    </span>
                  )}
                  <span className="text-xs text-gray-500 px-2 py-1 bg-gray-700 rounded flex items-center gap-1">
                    {getCategoryIcon(result.category)} {result.category}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded capitalize ${getStatusBg(result.status)}`}>
                    {result.status}
                  </span>
                </div>
              </div>
              
              <p className="text-gray-300 mb-2">{result.message}</p>
              
              {result.recommendations && result.recommendations.length > 0 && (
                <div className="mb-2 p-2 bg-blue-900/20 rounded border border-blue-600/30">
                  <p className="text-xs text-blue-400 mb-1">💡 Recommendations:</p>
                  <ul className="text-sm text-gray-300 list-disc list-inside">
                    {result.recommendations.map((rec, i) => (
                      <li key={i}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {result.details && (
                <details className="mt-2">
                  <summary className="text-sm text-gray-500 cursor-pointer hover:text-gray-300">
                    View Technical Details
                  </summary>
                  <pre className="mt-2 p-3 bg-gray-900 rounded text-xs overflow-auto max-h-48">
                    {JSON.stringify(result.details, null, 2)}
                  </pre>
                </details>
              )}
              
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-700">
                <span className="text-xs text-gray-500">
                  {new Date(result.timestamp).toLocaleString()}
                  {result.duration_ms !== undefined && ` • ${result.duration_ms}ms`}
                </span>
                {result.fix_available && result.status !== 'ok' && result.status !== 'fixed' && (
                  <button
                    onClick={() => applySingleFix(result.check_id)}
                    disabled={loading}
                    className="text-sm px-4 py-1.5 bg-yellow-600 hover:bg-yellow-700 rounded disabled:opacity-50 flex items-center gap-2 transition-colors"
                  >
                    {loadingAction === `fix-${result.check_id}` ? (
                      <span className="animate-spin">⟳</span>
                    ) : (
                      <span>🔧</span>
                    )}
                    Apply Fix
                  </button>
                )}
              </div>
            </div>
          ))}
          
          {results.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <p>Run diagnostics to see detailed results</p>
            </div>
          )}
        </div>
      )}

      {/* ==================== TAB: CATEGORIES ==================== */}
      {activeTab === 'categories' && (
        <div className="space-y-6">
          {/* Категории */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {categories.map((cat) => {
              const catResults = resultsByCategory[cat.name] || [];
              const issues = catResults.filter(r => r.status !== 'ok' && r.status !== 'fixed' && r.status !== 'skipped').length;
              
              return (
                <div
                  key={cat.name}
                  className={`p-4 bg-gray-800 rounded-lg border cursor-pointer transition-all hover:shadow-lg ${
                    selectedCategory === cat.name ? 'border-blue-500 ring-2 ring-blue-500/30' :
                    issues > 0 ? 'border-orange-600/50' : 'border-gray-700'
                  }`}
                  onClick={() => setSelectedCategory(selectedCategory === cat.name ? null : cat.name)}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">{getCategoryIcon(cat.name)}</span>
                    <span className="font-medium capitalize">{cat.display_name}</span>
                  </div>
                  <p className="text-xs text-gray-500 mb-3">{cat.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">{cat.checks_count} checks</span>
                    {issues > 0 && (
                      <span className="text-xs px-2 py-1 bg-orange-600 rounded-full">
                        {issues} issues
                      </span>
                    )}
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      runCategoryCheck(cat.name);
                    }}
                    disabled={loading}
                    className="mt-3 w-full text-sm px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded disabled:opacity-50 transition-colors"
                  >
                    {loadingAction === `run-category-${cat.name}` ? 'Running...' : 'Run Checks'}
                  </button>
                </div>
              );
            })}
          </div>

          {/* Результаты выбранной категории */}
          {selectedCategory && resultsByCategory[selectedCategory] && (
            <div className="mt-6">
              <h3 className="text-lg font-medium mb-4 flex items-center gap-2">
                {getCategoryIcon(selectedCategory)}
                {selectedCategory} Results
              </h3>
              <div className="space-y-2">
                {resultsByCategory[selectedCategory].map((result) => (
                  <div
                    key={result.check_id}
                    className="p-3 bg-gray-800 rounded-lg border border-gray-700 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <span className={`text-xl ${getStatusColor(result.status)}`}>
                        {getStatusIcon(result.status)}
                      </span>
                      <div>
                        <span className="font-medium">{result.name}</span>
                        <p className="text-sm text-gray-500">{result.message}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-2 py-1 rounded ${getStatusBg(result.status)}`}>
                        {result.status}
                      </span>
                      {result.fix_available && result.status !== 'ok' && result.status !== 'fixed' && (
                        <button
                          onClick={() => applySingleFix(result.check_id)}
                          disabled={loading}
                          className="text-xs px-2 py-1 bg-yellow-600 hover:bg-yellow-700 rounded"
                        >
                          Fix
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ==================== TAB: HISTORY ==================== */}
      {activeTab === 'history' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* История проверок */}
          <div>
            <h3 className="text-lg font-medium mb-4">📋 Check History</h3>
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {history.map((item, index) => (
                <div
                  key={index}
                  className="p-3 bg-gray-800 rounded-lg border border-gray-700"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-sm">{item.name || item.check_id}</span>
                    <span className={`text-xs px-2 py-0.5 rounded ${getStatusBg(item.status)}`}>
                      {item.status}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">{item.message}</p>
                  <p className="text-xs text-gray-600 mt-1">
                    {new Date(item.timestamp).toLocaleString()}
                  </p>
                </div>
              ))}
              {history.length === 0 && (
                <p className="text-gray-500 text-center py-4">No history yet</p>
              )}
            </div>
          </div>

          {/* История исправлений */}
          <div>
            <h3 className="text-lg font-medium mb-4">🔧 Fix History</h3>
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {fixesHistory.map((item, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg border ${
                    item.success ? 'border-green-600/50 bg-green-900/20' : 'border-red-600/50 bg-red-900/20'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-sm">{item.check_id}</span>
                    <span className={item.success ? 'text-green-400' : 'text-red-400'}>
                      {item.success ? '✓ Success' : '✗ Failed'}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400">{item.message}</p>
                  <p className="text-xs text-gray-500">
                    {item.before_status} → {item.after_status}
                  </p>
                  {item.actions_taken && item.actions_taken.length > 0 && (
                    <div className="mt-1">
                      <p className="text-xs text-gray-500">Actions:</p>
                      <ul className="text-xs text-gray-400 list-disc list-inside">
                        {item.actions_taken.map((action: string, i: number) => (
                          <li key={i}>{action}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <p className="text-xs text-gray-600 mt-1">
                    {new Date(item.timestamp).toLocaleString()}
                  </p>
                </div>
              ))}
              {fixesHistory.length === 0 && (
                <p className="text-gray-500 text-center py-4">No fixes applied yet</p>
              )}
            </div>
          </div>

          {/* Последние исправления из текущей сессии */}
          {fixResults.length > 0 && (
            <div className="lg:col-span-2">
              <h3 className="text-lg font-medium mb-4">🔄 Recent Session Fixes</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {fixResults.map((fix, index) => (
                  <div
                    key={index}
                    className={`p-3 rounded-lg border ${
                      fix.success ? 'border-green-600 bg-green-900/20' : 'border-red-600 bg-red-900/20'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{fix.check_id}</span>
                      <span className={fix.success ? 'text-green-400' : 'text-red-400'}>
                        {fix.success ? '✓ Success' : '✗ Failed'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-400">{fix.message}</p>
                    <p className="text-xs text-gray-500">
                      {fix.before_status} → {fix.after_status}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ==================== TAB: SETTINGS ==================== */}
      {activeTab === 'settings' && (
        <div className="space-y-6 max-w-3xl">
          {/* Автоматический режим */}
          <div className="p-5 bg-gray-800 rounded-lg">
            <h3 className="text-lg font-medium mb-4 flex items-center gap-2">
              <span>⚡</span> Automatic Mode
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                <div>
                  <p className="font-medium">Auto Diagnostics</p>
                  <p className="text-sm text-gray-400">
                    Automatically run diagnostics at regular intervals
                  </p>
                </div>
                <button
                  onClick={toggleAutoMode}
                  className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                    status?.auto_mode_enabled
                      ? 'bg-green-600 hover:bg-green-700'
                      : 'bg-gray-600 hover:bg-gray-700'
                  }`}
                >
                  {status?.auto_mode_enabled ? 'Enabled' : 'Disabled'}
                </button>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                <div>
                  <p className="font-medium">Auto Fix</p>
                  <p className="text-sm text-gray-400">
                    Automatically apply safe fixes when issues are detected
                  </p>
                </div>
                <button
                  onClick={toggleAutoFix}
                  className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                    status?.auto_fix_enabled
                      ? 'bg-green-600 hover:bg-green-700'
                      : 'bg-gray-600 hover:bg-gray-700'
                  }`}
                >
                  {status?.auto_fix_enabled ? 'Enabled' : 'Disabled'}
                </button>
              </div>
            </div>
          </div>

          {/* Интервал проверок */}
          <div className="p-5 bg-gray-800 rounded-lg">
            <h3 className="text-lg font-medium mb-4 flex items-center gap-2">
              <span>⏱️</span> Check Interval
            </h3>
            <div className="flex items-center gap-4">
              <input
                type="number"
                value={checkInterval}
                onChange={(e) => setCheckInterval(Math.max(60, parseInt(e.target.value) || 60))}
                min={60}
                className="w-32 px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              />
              <span className="text-gray-400">seconds</span>
              <button
                onClick={updateCheckInterval}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
              >
                Update
              </button>
            </div>
            <p className="text-sm text-gray-500 mt-3">
              Current: {status?.check_interval || 300} seconds ({Math.round((status?.check_interval || 300) / 60)} minutes)
            </p>
            <p className="text-xs text-gray-600 mt-1">
              Minimum interval: 60 seconds
            </p>
          </div>

          {/* Статистика */}
          <div className="p-5 bg-gray-800 rounded-lg">
            <h3 className="text-lg font-medium mb-4 flex items-center gap-2">
              <span>📊</span> Statistics
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-gray-700/50 rounded-lg text-center">
                <p className="text-3xl font-bold text-blue-400">{status?.total_checks || 0}</p>
                <p className="text-sm text-gray-400">Total Checks</p>
              </div>
              <div className="p-4 bg-gray-700/50 rounded-lg text-center">
                <p className="text-3xl font-bold text-green-400">{status?.total_fixes || 0}</p>
                <p className="text-sm text-gray-400">Available Fixes</p>
              </div>
              <div className="p-4 bg-gray-700/50 rounded-lg text-center">
                <p className="text-3xl font-bold text-purple-400">{status?.history_size || 0}</p>
                <p className="text-sm text-gray-400">History Records</p>
              </div>
              <div className="p-4 bg-gray-700/50 rounded-lg text-center">
                <p className="text-3xl font-bold text-yellow-400">{status?.fixes_history_size || 0}</p>
                <p className="text-sm text-gray-400">Fixes Applied</p>
              </div>
            </div>
          </div>

          {/* Категории проверок */}
          <div className="p-5 bg-gray-800 rounded-lg">
            <h3 className="text-lg font-medium mb-4 flex items-center gap-2">
              <span>📁</span> Check Categories
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {categories.map((cat) => (
                <div key={cat.name} className="p-3 bg-gray-700/50 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <span>{getCategoryIcon(cat.name)}</span>
                    <span className="font-medium capitalize">{cat.display_name}</span>
                  </div>
                  <p className="text-xs text-gray-500">{cat.checks_count} checks</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DiagnosticsPanel;
