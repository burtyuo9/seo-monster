import React, { useState, useEffect, useCallback } from 'react';

interface DiagnosticResult {
  check_id: string;
  category: string;
  name: string;
  status: string;
  message: string;
  details?: Record<string, any>;
  fix_available: boolean;
  fix_applied: boolean;
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
}

interface HealthSummary {
  overall_status: string;
  auto_mode: boolean;
  auto_fix: boolean;
  checks_count: number;
  last_check_results: number;
  issues_count: number;
}

interface FixResult {
  check_id: string;
  success: boolean;
  message: string;
  before_status: string;
  after_status: string;
  timestamp: string;
}

const API_URL = 'http://localhost:8000';

const DiagnosticsPanel: React.FC = () => {
  const [status, setStatus] = useState<DiagnosticsStatus | null>(null);
  const [healthSummary, setHealthSummary] = useState<HealthSummary | null>(null);
  const [results, setResults] = useState<DiagnosticResult[]>([]);
  const [fixResults, setFixResults] = useState<FixResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [checkInterval, setCheckInterval] = useState(300);
  const [activeTab, setActiveTab] = useState<'overview' | 'results' | 'history' | 'settings'>('overview');

  // Загрузка статуса
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

  // Загрузка сводки здоровья
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

  // Загрузка последних результатов
  const fetchLastResults = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/last-results`);
      if (response.ok) {
        const data = await response.json();
        setResults(data.results || []);
      }
    } catch (err) {
      console.error('Failed to fetch results:', err);
    }
  }, []);

  // Запуск всех проверок
  const runAllChecks = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/run-all`, {
        method: 'POST'
      });
      if (response.ok) {
        const data = await response.json();
        setResults(data.results || []);
        await fetchHealthSummary();
      } else {
        setError('Failed to run diagnostics');
      }
    } catch (err) {
      setError('Error running diagnostics');
    } finally {
      setLoading(false);
    }
  };

  // Применение всех исправлений
  const applyAllFixes = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/fix-all`, {
        method: 'POST'
      });
      if (response.ok) {
        const data = await response.json();
        setFixResults(data.results || []);
        await runAllChecks(); // Перезапускаем проверки после исправлений
      } else {
        setError('Failed to apply fixes');
      }
    } catch (err) {
      setError('Error applying fixes');
    } finally {
      setLoading(false);
    }
  };

  // Применение одного исправления
  const applySingleFix = async (checkId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/fix`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ check_id: checkId })
      });
      if (response.ok) {
        await runAllChecks();
      }
    } catch (err) {
      console.error('Error applying fix:', err);
    } finally {
      setLoading(false);
    }
  };

  // Переключение автоматического режима
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
      }
    } catch (err) {
      console.error('Error toggling auto mode:', err);
    }
  };

  // Переключение автоисправления
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
      }
    } catch (err) {
      console.error('Error toggling auto fix:', err);
    }
  };

  // Установка интервала проверок
  const updateCheckInterval = async () => {
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/check-interval`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seconds: checkInterval })
      });
      if (response.ok) {
        await fetchStatus();
      }
    } catch (err) {
      console.error('Error updating interval:', err);
    }
  };

  useEffect(() => {
    fetchStatus();
    fetchHealthSummary();
    fetchLastResults();
  }, [fetchStatus, fetchHealthSummary, fetchLastResults]);

  // Получение цвета статуса
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ok':
      case 'fixed':
      case 'healthy':
        return 'text-green-400';
      case 'warning':
        return 'text-yellow-400';
      case 'error':
        return 'text-red-400';
      case 'critical':
        return 'text-red-600';
      default:
        return 'text-gray-400';
    }
  };

  // Получение иконки статуса
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ok':
      case 'fixed':
      case 'healthy':
        return '✓';
      case 'warning':
        return '⚠';
      case 'error':
      case 'critical':
        return '✗';
      default:
        return '?';
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Diagnostics & Auto-Fix</h2>

      {/* Сводка здоровья */}
      {healthSummary && (
        <div className={`mb-6 p-4 rounded-lg border ${
          healthSummary.overall_status === 'healthy' ? 'border-green-500 bg-green-900/20' :
          healthSummary.overall_status === 'warning' ? 'border-yellow-500 bg-yellow-900/20' :
          'border-red-500 bg-red-900/20'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className={`text-3xl ${getStatusColor(healthSummary.overall_status)}`}>
                {getStatusIcon(healthSummary.overall_status)}
              </span>
              <div>
                <h3 className="text-lg font-semibold capitalize">
                  System Status: {healthSummary.overall_status}
                </h3>
                <p className="text-sm text-gray-400">
                  {healthSummary.issues_count} issues found | {healthSummary.checks_count} checks available
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <span className={`px-2 py-1 rounded text-xs ${healthSummary.auto_mode ? 'bg-green-600' : 'bg-gray-600'}`}>
                Auto: {healthSummary.auto_mode ? 'ON' : 'OFF'}
              </span>
              <span className={`px-2 py-1 rounded text-xs ${healthSummary.auto_fix ? 'bg-green-600' : 'bg-gray-600'}`}>
                Auto-Fix: {healthSummary.auto_fix ? 'ON' : 'OFF'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Кнопки управления */}
      <div className="flex flex-wrap gap-3 mb-6">
        <button
          onClick={runAllChecks}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium disabled:opacity-50 flex items-center gap-2"
        >
          {loading ? (
            <span className="animate-spin">⟳</span>
          ) : (
            <span>🔍</span>
          )}
          Run Diagnostics
        </button>
        
        <button
          onClick={applyAllFixes}
          disabled={loading}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-medium disabled:opacity-50 flex items-center gap-2"
        >
          <span>🔧</span>
          Fix All Issues
        </button>
        
        <button
          onClick={toggleAutoMode}
          className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 ${
            status?.auto_mode_enabled ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-600 hover:bg-gray-700'
          }`}
        >
          <span>⚡</span>
          Auto Mode: {status?.auto_mode_enabled ? 'ON' : 'OFF'}
        </button>
        
        <button
          onClick={toggleAutoFix}
          className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 ${
            status?.auto_fix_enabled ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-600 hover:bg-gray-700'
          }`}
        >
          <span>🛠</span>
          Auto-Fix: {status?.auto_fix_enabled ? 'ON' : 'OFF'}
        </button>
      </div>

      {/* Ошибка */}
      {error && (
        <div className="mb-4 p-3 bg-red-900/30 border border-red-500 rounded-lg text-red-400">
          {error}
        </div>
      )}

      {/* Табы */}
      <div className="flex gap-2 mb-4 border-b border-gray-700">
        {(['overview', 'results', 'history', 'settings'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 font-medium capitalize ${
              activeTab === tab
                ? 'border-b-2 border-blue-500 text-blue-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Контент табов */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {results.map((result) => (
            <div
              key={result.check_id}
              className="p-4 bg-gray-800 rounded-lg border border-gray-700"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className={`text-xl ${getStatusColor(result.status)}`}>
                    {getStatusIcon(result.status)}
                  </span>
                  <span className="font-medium">{result.name}</span>
                </div>
                <span className="text-xs text-gray-500 px-2 py-1 bg-gray-700 rounded">
                  {result.category}
                </span>
              </div>
              <p className="text-sm text-gray-400 mb-3">{result.message}</p>
              {result.fix_available && result.status !== 'ok' && result.status !== 'fixed' && (
                <button
                  onClick={() => applySingleFix(result.check_id)}
                  disabled={loading}
                  className="text-sm px-3 py-1 bg-yellow-600 hover:bg-yellow-700 rounded disabled:opacity-50"
                >
                  🔧 Fix
                </button>
              )}
              {result.fix_applied && (
                <span className="text-sm text-green-400">✓ Fixed</span>
              )}
            </div>
          ))}
        </div>
      )}

      {activeTab === 'results' && (
        <div className="space-y-3">
          {results.map((result) => (
            <div
              key={result.check_id}
              className="p-4 bg-gray-800 rounded-lg border border-gray-700"
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
                  <span className="text-xs text-gray-500 px-2 py-1 bg-gray-700 rounded">
                    {result.category}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded capitalize ${
                    result.status === 'ok' || result.status === 'fixed' ? 'bg-green-600' :
                    result.status === 'warning' ? 'bg-yellow-600' :
                    'bg-red-600'
                  }`}>
                    {result.status}
                  </span>
                </div>
              </div>
              <p className="text-gray-300 mb-2">{result.message}</p>
              {result.details && (
                <details className="mt-2">
                  <summary className="text-sm text-gray-500 cursor-pointer">Details</summary>
                  <pre className="mt-2 p-2 bg-gray-900 rounded text-xs overflow-auto">
                    {JSON.stringify(result.details, null, 2)}
                  </pre>
                </details>
              )}
              <div className="flex items-center justify-between mt-3">
                <span className="text-xs text-gray-500">
                  {new Date(result.timestamp).toLocaleString()}
                </span>
                {result.fix_available && result.status !== 'ok' && result.status !== 'fixed' && (
                  <button
                    onClick={() => applySingleFix(result.check_id)}
                    disabled={loading}
                    className="text-sm px-3 py-1 bg-yellow-600 hover:bg-yellow-700 rounded disabled:opacity-50"
                  >
                    🔧 Apply Fix
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'history' && (
        <div className="space-y-2">
          {fixResults.length > 0 && (
            <div className="mb-4">
              <h3 className="text-lg font-medium mb-2">Recent Fixes</h3>
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
          )}
          <p className="text-gray-500 text-center py-4">
            Run diagnostics to see history
          </p>
        </div>
      )}

      {activeTab === 'settings' && (
        <div className="space-y-6">
          {/* Автоматический режим */}
          <div className="p-4 bg-gray-800 rounded-lg">
            <h3 className="text-lg font-medium mb-3">Automatic Mode</h3>
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="font-medium">Auto Diagnostics</p>
                <p className="text-sm text-gray-400">
                  Automatically run diagnostics at regular intervals
                </p>
              </div>
              <button
                onClick={toggleAutoMode}
                className={`px-4 py-2 rounded-lg font-medium ${
                  status?.auto_mode_enabled
                    ? 'bg-green-600 hover:bg-green-700'
                    : 'bg-gray-600 hover:bg-gray-700'
                }`}
              >
                {status?.auto_mode_enabled ? 'Enabled' : 'Disabled'}
              </button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Auto Fix</p>
                <p className="text-sm text-gray-400">
                  Automatically apply fixes when issues are detected
                </p>
              </div>
              <button
                onClick={toggleAutoFix}
                className={`px-4 py-2 rounded-lg font-medium ${
                  status?.auto_fix_enabled
                    ? 'bg-green-600 hover:bg-green-700'
                    : 'bg-gray-600 hover:bg-gray-700'
                }`}
              >
                {status?.auto_fix_enabled ? 'Enabled' : 'Disabled'}
              </button>
            </div>
          </div>

          {/* Интервал проверок */}
          <div className="p-4 bg-gray-800 rounded-lg">
            <h3 className="text-lg font-medium mb-3">Check Interval</h3>
            <div className="flex items-center gap-4">
              <input
                type="number"
                value={checkInterval}
                onChange={(e) => setCheckInterval(parseInt(e.target.value) || 60)}
                min={60}
                className="w-32 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg"
              />
              <span className="text-gray-400">seconds</span>
              <button
                onClick={updateCheckInterval}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg"
              >
                Update
              </button>
            </div>
            <p className="text-sm text-gray-500 mt-2">
              Current: {status?.check_interval || 300} seconds ({Math.round((status?.check_interval || 300) / 60)} minutes)
            </p>
          </div>

          {/* Статистика */}
          <div className="p-4 bg-gray-800 rounded-lg">
            <h3 className="text-lg font-medium mb-3">Statistics</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-gray-400">Total Checks</p>
                <p className="text-2xl font-bold">{status?.total_checks || 0}</p>
              </div>
              <div>
                <p className="text-gray-400">Available Fixes</p>
                <p className="text-2xl font-bold">{status?.total_fixes || 0}</p>
              </div>
              <div>
                <p className="text-gray-400">History Size</p>
                <p className="text-2xl font-bold">{status?.history_size || 0}</p>
              </div>
              <div>
                <p className="text-gray-400">Fixes Applied</p>
                <p className="text-2xl font-bold">{status?.fixes_history_size || 0}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DiagnosticsPanel;
