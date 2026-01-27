import { useState, useEffect, useCallback } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { useTheme } from './ThemeToggle';

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

interface CategoryInfo {
  name: string;
  display_name: string;
  checks_count: number;
  description: string;
}

const API_URL = 'http://localhost:8000';

// Категории для группировки
const CORE_CATEGORIES = ['api', 'file_system', 'services', 'dependencies', 'performance', 'network', 'security'];
const OPTIONAL_CATEGORIES = ['email', 'integrations', 'configuration'];

const DiagnosticsPanelEnhanced: React.FC = () => {
  const { language } = useLanguage();
  const { theme } = useTheme();
  
  // ==================== СОСТОЯНИЕ ====================
  const [status, setStatus] = useState<DiagnosticsStatus | null>(null);
  const [healthSummary, setHealthSummary] = useState<HealthSummary | null>(null);
  const [results, setResults] = useState<DiagnosticResult[]>([]);
  const [categories, setCategories] = useState<CategoryInfo[]>([]);
  
  const [loading, setLoading] = useState(false);
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  const [activeTab, setActiveTab] = useState<'overview' | 'core' | 'optional' | 'issues' | 'history' | 'settings'>('overview');
  const [expandedChecks, setExpandedChecks] = useState<Set<string>>(new Set());

  // ==================== ПЕРЕВОДЫ ====================
  const t = {
    title: language === 'ru' ? 'Диагностика системы' : 'System Diagnostics',
    runFull: language === 'ru' ? 'Полная проверка' : 'Full Check',
    runQuick: language === 'ru' ? 'Быстрая проверка' : 'Quick Check',
    fixAll: language === 'ru' ? 'Исправить все' : 'Fix All',
    autoMode: language === 'ru' ? 'Авто-режим' : 'Auto Mode',
    autoFix: language === 'ru' ? 'Авто-исправление' : 'Auto-Fix',
    overview: language === 'ru' ? 'Обзор' : 'Overview',
    coreSystems: language === 'ru' ? 'Основные системы' : 'Core Systems',
    optionalFeatures: language === 'ru' ? 'Опциональные функции' : 'Optional Features',
    issues: language === 'ru' ? 'Проблемы' : 'Issues',
    history: language === 'ru' ? 'История' : 'History',
    settings: language === 'ru' ? 'Настройки' : 'Settings',
    healthScore: language === 'ru' ? 'Здоровье системы' : 'Health Score',
    allOperational: language === 'ru' ? 'Все системы работают' : 'All systems operational',
    issuesDetected: language === 'ru' ? 'Обнаружено проблем' : 'Issues detected',
    passed: language === 'ru' ? 'Пройдено' : 'Passed',
    warnings: language === 'ru' ? 'Предупреждения' : 'Warnings',
    errors: language === 'ru' ? 'Ошибки' : 'Errors',
    critical: language === 'ru' ? 'Критические' : 'Critical',
    fixed: language === 'ru' ? 'Исправлено' : 'Fixed',
    notConfigured: language === 'ru' ? 'Не настроено' : 'Not Configured',
    configure: language === 'ru' ? 'Настроить' : 'Configure',
    fix: language === 'ru' ? 'Исправить' : 'Fix',
    lastCheck: language === 'ru' ? 'Последняя проверка' : 'Last check',
  };

  // ==================== API ФУНКЦИИ ====================

  const fetchStatus = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/status`);
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
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

  // ==================== ДЕЙСТВИЯ ====================

  const runAllChecks = async () => {
    setLoading(true);
    setLoadingAction('run-all');
    setError(null);
    setSuccess(null);
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/run-all`, { method: 'POST' });
      if (response.ok) {
        const data = await response.json();
        setResults(data.results || []);
        const msg = language === 'ru' 
          ? `Проверено ${data.summary.total}: ${data.summary.ok} OK, ${data.summary.warnings} предупреждений, ${data.summary.errors} ошибок`
          : `Checked ${data.summary.total}: ${data.summary.ok} OK, ${data.summary.warnings} warnings, ${data.summary.errors} errors`;
        setSuccess(msg);
        await fetchHealthSummary();
      }
    } catch (err) {
      setError(language === 'ru' ? 'Ошибка диагностики' : 'Diagnostics error');
    } finally {
      setLoading(false);
      setLoadingAction(null);
    }
  };

  const runQuickCheck = async () => {
    setLoading(true);
    setLoadingAction('run-quick');
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/run-quick`, { method: 'POST' });
      if (response.ok) {
        const data = await response.json();
        setSuccess(language === 'ru' 
          ? `Быстрая проверка: ${data.summary.ok} OK, ${data.summary.issues} проблем`
          : `Quick check: ${data.summary.ok} OK, ${data.summary.issues} issues`);
        await fetchHealthSummary();
      }
    } catch (err) {
      setError(language === 'ru' ? 'Ошибка' : 'Error');
    } finally {
      setLoading(false);
      setLoadingAction(null);
    }
  };

  const applyAllFixes = async () => {
    setLoading(true);
    setLoadingAction('fix-all');
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/fix-all`, { method: 'POST' });
      if (response.ok) {
        const data = await response.json();
        setSuccess(language === 'ru'
          ? `Исправлено ${data.summary.successful}, не удалось ${data.summary.failed}`
          : `Fixed ${data.summary.successful}, failed ${data.summary.failed}`);
        await runAllChecks();
      }
    } catch (err) {
      setError(language === 'ru' ? 'Ошибка исправления' : 'Fix error');
    } finally {
      setLoading(false);
      setLoadingAction(null);
    }
  };

  const applySingleFix = async (checkId: string) => {
    setLoadingAction(`fix-${checkId}`);
    try {
      const response = await fetch(`${API_URL}/api/diagnostics/fix`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ check_id: checkId })
      });
      if (response.ok) {
        await fetchLastResults();
        await fetchHealthSummary();
      }
    } catch (err) {
      console.error('Error applying fix:', err);
    } finally {
      setLoadingAction(null);
    }
  };

  const toggleAutoMode = async () => {
    if (!status) return;
    try {
      await fetch(`${API_URL}/api/diagnostics/auto-mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !status.auto_mode_enabled })
      });
      await fetchStatus();
    } catch (err) {
      console.error('Error:', err);
    }
  };

  const toggleAutoFix = async () => {
    if (!status) return;
    try {
      await fetch(`${API_URL}/api/diagnostics/auto-fix`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !status.auto_fix_enabled })
      });
      await fetchStatus();
    } catch (err) {
      console.error('Error:', err);
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
    const colors: Record<string, string> = {
      ok: theme === 'dark' ? 'text-green-400' : 'text-green-600',
      fixed: theme === 'dark' ? 'text-green-400' : 'text-green-600',
      healthy: theme === 'dark' ? 'text-green-400' : 'text-green-600',
      warning: theme === 'dark' ? 'text-yellow-400' : 'text-yellow-600',
      error: theme === 'dark' ? 'text-orange-400' : 'text-orange-600',
      critical: theme === 'dark' ? 'text-red-500' : 'text-red-600',
    };
    return colors[status] || (theme === 'dark' ? 'text-gray-400' : 'text-gray-500');
  };

  const getStatusIcon = (status: string) => {
    const icons: Record<string, string> = {
      ok: '✓', fixed: '✓', healthy: '✓',
      warning: '⚠', error: '✗', critical: '🔥',
    };
    return icons[status] || '?';
  };

  const getCategoryIcon = (category: string) => {
    const icons: Record<string, string> = {
      api: '🔌', file_system: '📁', services: '⚙️',
      ai: '🤖', email: '📧', tds: '🔀',
      integrations: '🔗', configuration: '⚙️',
      dependencies: '📦', performance: '⚡',
      network: '🌐', security: '🔒',
    };
    return icons[category] || '📋';
  };

  const getHealthScoreColor = (score: number) => {
    if (score >= 90) return theme === 'dark' ? 'text-green-400' : 'text-green-600';
    if (score >= 70) return theme === 'dark' ? 'text-yellow-400' : 'text-yellow-600';
    if (score >= 50) return theme === 'dark' ? 'text-orange-400' : 'text-orange-600';
    return theme === 'dark' ? 'text-red-400' : 'text-red-600';
  };

  // Группировка результатов
  const coreResults = results.filter(r => CORE_CATEGORIES.includes(r.category));
  const optionalResults = results.filter(r => OPTIONAL_CATEGORIES.includes(r.category) || !CORE_CATEGORIES.includes(r.category));
  const issueResults = results.filter(r => r.status !== 'ok' && r.status !== 'fixed');

  const toggleExpanded = (checkId: string) => {
    const newExpanded = new Set(expandedChecks);
    if (newExpanded.has(checkId)) {
      newExpanded.delete(checkId);
    } else {
      newExpanded.add(checkId);
    }
    setExpandedChecks(newExpanded);
  };

  // ==================== КОМПОНЕНТЫ ====================

  const ResultCard = ({ result }: { result: DiagnosticResult }) => {
    const isExpanded = expandedChecks.has(result.check_id);
    const isOptional = result.details?.note?.includes('optional') || result.details?.configured === false;
    
    return (
      <div className={`p-4 rounded-lg border transition-all ${
        theme === 'dark' 
          ? `bg-gray-800 ${result.status === 'ok' ? 'border-gray-700' : result.status === 'warning' ? 'border-yellow-600/50' : 'border-orange-600/50'}`
          : `bg-white shadow ${result.status === 'ok' ? 'border-gray-200' : result.status === 'warning' ? 'border-yellow-400' : 'border-orange-400'}`
      }`}>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <span className={`text-xl ${getStatusColor(result.status)}`}>
              {getStatusIcon(result.status)}
            </span>
            <div>
              <h4 className={`font-medium ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                {result.name}
              </h4>
              <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                {result.message}
              </p>
              {isOptional && result.status === 'ok' && (
                <span className={`inline-block mt-1 px-2 py-0.5 text-xs rounded-full ${
                  theme === 'dark' ? 'bg-blue-900 text-blue-300' : 'bg-blue-100 text-blue-700'
                }`}>
                  💡 {language === 'ru' ? 'Опциональная функция' : 'Optional Feature'}
                </span>
              )}
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {result.fix_available && result.status !== 'ok' && result.status !== 'fixed' && (
              <button
                onClick={() => applySingleFix(result.check_id)}
                disabled={loadingAction === `fix-${result.check_id}`}
                className={`px-3 py-1 text-sm rounded transition-colors ${
                  theme === 'dark'
                    ? 'bg-green-600 hover:bg-green-700 text-white'
                    : 'bg-green-500 hover:bg-green-600 text-white'
                }`}
              >
                {loadingAction === `fix-${result.check_id}` ? '...' : t.fix}
              </button>
            )}
            <button
              onClick={() => toggleExpanded(result.check_id)}
              className={`p-1 rounded ${theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
            >
              {isExpanded ? '▼' : '▶'}
            </button>
          </div>
        </div>
        
        {isExpanded && (
          <div className={`mt-3 pt-3 border-t ${theme === 'dark' ? 'border-gray-700' : 'border-gray-200'}`}>
            {result.details && (
              <div className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                <pre className="whitespace-pre-wrap overflow-x-auto">
                  {JSON.stringify(result.details, null, 2)}
                </pre>
              </div>
            )}
            {result.recommendations && result.recommendations.length > 0 && (
              <div className="mt-2">
                <h5 className={`text-sm font-medium ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
                  {language === 'ru' ? 'Рекомендации:' : 'Recommendations:'}
                </h5>
                <ul className={`mt-1 text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                  {result.recommendations.map((rec, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-blue-500">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  // ==================== РЕНДЕР ====================

  return (
    <div className="max-w-7xl mx-auto">
      {/* Заголовок */}
      <div className="flex items-center justify-between mb-6">
        <h2 className={`text-2xl font-bold flex items-center gap-2 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
          <span>🔍</span>
          {t.title}
        </h2>
        {status?.last_full_check && (
          <span className={`text-sm ${theme === 'dark' ? 'text-gray-500' : 'text-gray-400'}`}>
            {t.lastCheck}: {new Date(status.last_full_check).toLocaleString()}
          </span>
        )}
      </div>

      {/* Уведомления */}
      {error && (
        <div className={`mb-4 p-3 rounded-lg flex items-center justify-between ${
          theme === 'dark' ? 'bg-red-900/30 border border-red-500 text-red-400' : 'bg-red-50 border border-red-200 text-red-600'
        }`}>
          <span>{error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}
      {success && (
        <div className={`mb-4 p-3 rounded-lg flex items-center justify-between ${
          theme === 'dark' ? 'bg-green-900/30 border border-green-500 text-green-400' : 'bg-green-50 border border-green-200 text-green-600'
        }`}>
          <span>{success}</span>
          <button onClick={() => setSuccess(null)}>✕</button>
        </div>
      )}

      {/* Health Score Card */}
      {healthSummary && (
        <div className={`mb-6 p-5 rounded-xl border-2 ${
          healthSummary.health_score >= 90 
            ? theme === 'dark' ? 'border-green-500 bg-green-900/20' : 'border-green-400 bg-green-50'
            : healthSummary.health_score >= 70 
            ? theme === 'dark' ? 'border-yellow-500 bg-yellow-900/20' : 'border-yellow-400 bg-yellow-50'
            : theme === 'dark' ? 'border-red-500 bg-red-900/20' : 'border-red-400 bg-red-50'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className={`text-5xl font-bold ${getHealthScoreColor(healthSummary.health_score)}`}>
                {healthSummary.health_score}%
              </div>
              <div>
                <h3 className={`text-xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                  {t.healthScore}
                </h3>
                <p className={theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}>
                  {healthSummary.issues_count === 0 ? t.allOperational : `${healthSummary.issues_count} ${t.issuesDetected}`}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="flex flex-col gap-2">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  healthSummary.auto_mode 
                    ? 'bg-green-600 text-white' 
                    : theme === 'dark' ? 'bg-gray-600 text-white' : 'bg-gray-200 text-gray-700'
                }`}>
                  {t.autoMode}: {healthSummary.auto_mode ? 'ON' : 'OFF'}
                </span>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  healthSummary.auto_fix 
                    ? 'bg-green-600 text-white' 
                    : theme === 'dark' ? 'bg-gray-600 text-white' : 'bg-gray-200 text-gray-700'
                }`}>
                  {t.autoFix}: {healthSummary.auto_fix ? 'ON' : 'OFF'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Кнопки управления */}
      <div className="flex flex-wrap gap-3 mb-6">
        <button
          onClick={runAllChecks}
          disabled={loading}
          className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors disabled:opacity-50 ${
            theme === 'dark' ? 'bg-blue-600 hover:bg-blue-700 text-white' : 'bg-blue-500 hover:bg-blue-600 text-white'
          }`}
        >
          {loadingAction === 'run-all' ? <span className="animate-spin">⟳</span> : <span>🔍</span>}
          {t.runFull}
        </button>
        
        <button
          onClick={runQuickCheck}
          disabled={loading}
          className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors disabled:opacity-50 ${
            theme === 'dark' ? 'bg-cyan-600 hover:bg-cyan-700 text-white' : 'bg-cyan-500 hover:bg-cyan-600 text-white'
          }`}
        >
          {loadingAction === 'run-quick' ? <span className="animate-spin">⟳</span> : <span>⚡</span>}
          {t.runQuick}
        </button>
        
        <button
          onClick={applyAllFixes}
          disabled={loading || issueResults.filter(r => r.fix_available).length === 0}
          className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors disabled:opacity-50 ${
            theme === 'dark' ? 'bg-green-600 hover:bg-green-700 text-white' : 'bg-green-500 hover:bg-green-600 text-white'
          }`}
        >
          {loadingAction === 'fix-all' ? <span className="animate-spin">⟳</span> : <span>🔧</span>}
          {t.fixAll} ({issueResults.filter(r => r.fix_available).length})
        </button>
        
        <div className="flex-1" />
        
        <button
          onClick={toggleAutoMode}
          className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors ${
            status?.auto_mode_enabled 
              ? 'bg-green-600 hover:bg-green-700 text-white' 
              : theme === 'dark' ? 'bg-gray-600 hover:bg-gray-700 text-white' : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
          }`}
        >
          ⚡ {t.autoMode}: {status?.auto_mode_enabled ? 'ON' : 'OFF'}
        </button>
        
        <button
          onClick={toggleAutoFix}
          className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors ${
            status?.auto_fix_enabled 
              ? 'bg-green-600 hover:bg-green-700 text-white' 
              : theme === 'dark' ? 'bg-gray-600 hover:bg-gray-700 text-white' : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
          }`}
        >
          🛠 {t.autoFix}: {status?.auto_fix_enabled ? 'ON' : 'OFF'}
        </button>
      </div>

      {/* Табы */}
      <div className={`flex gap-1 mb-6 border-b overflow-x-auto ${theme === 'dark' ? 'border-gray-700' : 'border-gray-200'}`}>
        {[
          { id: 'overview', icon: '📊', label: t.overview },
          { id: 'core', icon: '✅', label: t.coreSystems, count: coreResults.length },
          { id: 'optional', icon: '💡', label: t.optionalFeatures, count: optionalResults.length },
          { id: 'issues', icon: '⚠️', label: t.issues, count: issueResults.length },
          { id: 'settings', icon: '⚙️', label: t.settings },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-4 py-3 font-medium whitespace-nowrap transition-colors flex items-center gap-2 ${
              activeTab === tab.id
                ? theme === 'dark' 
                  ? 'border-b-2 border-blue-500 text-blue-400 bg-blue-900/20'
                  : 'border-b-2 border-blue-500 text-blue-600 bg-blue-50'
                : theme === 'dark'
                  ? 'text-gray-400 hover:text-white hover:bg-gray-800'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            }`}
          >
            {tab.icon} {tab.label}
            {tab.count !== undefined && (
              <span className={`px-2 py-0.5 text-xs rounded-full ${
                tab.id === 'issues' && tab.count > 0
                  ? 'bg-red-500 text-white'
                  : theme === 'dark' ? 'bg-gray-600' : 'bg-gray-200'
              }`}>
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* TAB: OVERVIEW */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Статистика */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {[
              { label: t.passed, count: results.filter(r => r.status === 'ok').length, color: 'green' },
              { label: t.warnings, count: results.filter(r => r.status === 'warning').length, color: 'yellow' },
              { label: t.errors, count: results.filter(r => r.status === 'error').length, color: 'orange' },
              { label: t.critical, count: results.filter(r => r.status === 'critical').length, color: 'red' },
              { label: t.fixed, count: results.filter(r => r.status === 'fixed').length, color: 'blue' },
              { label: t.notConfigured, count: optionalResults.filter(r => r.details?.configured === false).length, color: 'gray' },
            ].map((stat, i) => (
              <div key={i} className={`p-4 rounded-lg text-center ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
                <div className={`text-3xl font-bold text-${stat.color}-${theme === 'dark' ? '400' : '600'}`}>
                  {stat.count}
                </div>
                <div className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>{stat.label}</div>
              </div>
            ))}
          </div>

          {/* Все результаты */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.slice(0, 12).map(result => (
              <ResultCard key={result.check_id} result={result} />
            ))}
          </div>
        </div>
      )}

      {/* TAB: CORE SYSTEMS */}
      {activeTab === 'core' && (
        <div className="space-y-4">
          <p className={`mb-4 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
            {language === 'ru' 
              ? 'Критические компоненты, необходимые для работы системы.'
              : 'Critical components required for system operation.'}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {coreResults.map(result => (
              <ResultCard key={result.check_id} result={result} />
            ))}
          </div>
        </div>
      )}

      {/* TAB: OPTIONAL FEATURES */}
      {activeTab === 'optional' && (
        <div className="space-y-4">
          <p className={`mb-4 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
            {language === 'ru' 
              ? 'Дополнительные функции, которые можно настроить для расширения возможностей.'
              : 'Additional features that can be configured to extend capabilities.'}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {optionalResults.map(result => (
              <ResultCard key={result.check_id} result={result} />
            ))}
          </div>
        </div>
      )}

      {/* TAB: ISSUES */}
      {activeTab === 'issues' && (
        <div className="space-y-4">
          {issueResults.length === 0 ? (
            <div className={`p-8 text-center rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
              <span className="text-4xl">🎉</span>
              <h3 className={`text-xl font-bold mt-4 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                {language === 'ru' ? 'Проблем не обнаружено!' : 'No Issues Found!'}
              </h3>
              <p className={`mt-2 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                {language === 'ru' ? 'Все системы работают нормально.' : 'All systems are operating normally.'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {issueResults.map(result => (
                <ResultCard key={result.check_id} result={result} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB: SETTINGS */}
      {activeTab === 'settings' && (
        <div className={`p-6 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow'}`}>
          <h3 className={`text-lg font-bold mb-4 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
            {language === 'ru' ? 'Настройки диагностики' : 'Diagnostics Settings'}
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className={`font-medium ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>{t.autoMode}</h4>
                <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                  {language === 'ru' ? 'Автоматическая проверка по расписанию' : 'Automatic scheduled checks'}
                </p>
              </div>
              <button
                onClick={toggleAutoMode}
                className={`px-4 py-2 rounded-lg ${
                  status?.auto_mode_enabled ? 'bg-green-600' : theme === 'dark' ? 'bg-gray-600' : 'bg-gray-200'
                } text-white`}
              >
                {status?.auto_mode_enabled ? 'ON' : 'OFF'}
              </button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <h4 className={`font-medium ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>{t.autoFix}</h4>
                <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                  {language === 'ru' ? 'Автоматическое исправление проблем' : 'Automatic problem fixing'}
                </p>
              </div>
              <button
                onClick={toggleAutoFix}
                className={`px-4 py-2 rounded-lg ${
                  status?.auto_fix_enabled ? 'bg-green-600' : theme === 'dark' ? 'bg-gray-600' : 'bg-gray-200'
                } text-white`}
              >
                {status?.auto_fix_enabled ? 'ON' : 'OFF'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DiagnosticsPanelEnhanced;
