import React, { useState, useEffect } from 'react';

interface WarmupDay {
  day: number;
  target_volume: number;
  actual_sent: number;
  delivered: number;
  bounced: number;
  complaints: number;
  opens: number;
  clicks: number;
  date: string;
  completed: boolean;
  status: string;
  delivery_rate: number;
  bounce_rate: number;
  complaint_rate: number;
  open_rate: number;
  click_rate: number;
}

interface WarmupPlan {
  id: string;
  key_id: string;
  name: string;
  strategy: string;
  status: string;
  start_date: string;
  target_daily_volume: number;
  current_day: number;
  total_days: number;
  schedule: WarmupDay[];
  max_bounce_rate: number;
  max_complaint_rate: number;
  auto_pause_on_issues: boolean;
  total_sent: number;
  total_delivered: number;
  total_bounced: number;
  total_complaints: number;
  total_opens: number;
  total_clicks: number;
  // New fields
  auto_mode: boolean;
  send_hour: number;
  send_minute: number;
  recipient_list_id: string;
  content_id: string;
  from_email: string;
  from_name: string;
  last_auto_run: string;
  next_scheduled_run: string;
  pause_reason: string;
  health_score: number;
  reputation_trend: string;
  alerts: string[];
  progress_percent: number;
  avg_delivery_rate: number;
  avg_bounce_rate: number;
  avg_complaint_rate: number;
  avg_open_rate: number;
}

interface WarmupStats {
  total_plans: number;
  in_progress: number;
  completed: number;
  paused: number;
  failed: number;
  not_started: number;
  total_emails_sent: number;
  total_delivered: number;
  total_bounced: number;
  overall_delivery_rate: number;
  scheduler_running: boolean;
}

interface Strategy {
  id: string;
  name: string;
  description: string;
  days: number;
  risk: string;
}

interface Recommendation {
  type: string;
  title: string;
  message: string;
  action: string;
}

interface ExecutorStatus {
  is_running: boolean;
  active_plans: number;
  auto_mode_plans: number;
  check_interval_seconds: number;
  total_log_entries: number;
}

const API_URL = 'http://localhost:8000';

const SESWarmup: React.FC = () => {
  const [stats, setStats] = useState<WarmupStats>({ 
    total_plans: 0, in_progress: 0, completed: 0, paused: 0, failed: 0, not_started: 0,
    total_emails_sent: 0, total_delivered: 0, total_bounced: 0, overall_delivery_rate: 0, scheduler_running: false
  });
  const [plans, setPlans] = useState<WarmupPlan[]>([]);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<WarmupPlan | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [timeline, setTimeline] = useState<WarmupDay[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [executorStatus, setExecutorStatus] = useState<ExecutorStatus | null>(null);
  const [executionLog, setExecutionLog] = useState<any[]>([]);
  const [activeView, setActiveView] = useState<'list' | 'details' | 'timeline' | 'log'>('list');
  
  const [newPlan, setNewPlan] = useState({
    key_id: '', name: '', strategy: 'moderate', target_volume: 10000,
    auto_mode: true, send_hour: 10, send_minute: 0,
    recipient_list_id: '', content_id: '', from_email: '', from_name: ''
  });
  
  const [planSettings, setPlanSettings] = useState({
    auto_mode: true, send_hour: 10, send_minute: 0,
    recipient_list_id: '', content_id: '', from_email: '', from_name: '',
    max_bounce_rate: 5.0, max_complaint_rate: 0.1, auto_pause_on_issues: true
  });
  
  const [keys, setKeys] = useState<any[]>([]);
  const [lists, setLists] = useState<any[]>([]);
  const [contents, setContents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData();
    fetchExecutorStatus();
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, plansRes, strategiesRes, keysRes, listsRes, contentsRes] = await Promise.all([
        fetch(`${API_URL}/api/ses/warmup/stats`),
        fetch(`${API_URL}/api/ses/warmup/plans`),
        fetch(`${API_URL}/api/ses/warmup/strategies`),
        fetch(`${API_URL}/api/ses/keys`),
        fetch(`${API_URL}/api/ses/lists`),
        fetch(`${API_URL}/api/ses/content`)
      ]);
      
      if (statsRes.ok) setStats(await statsRes.json());
      if (plansRes.ok) {
        const data = await plansRes.json();
        setPlans(data.plans || []);
      }
      if (strategiesRes.ok) {
        const data = await strategiesRes.json();
        setStrategies(data.strategies || []);
      }
      if (keysRes.ok) {
        const data = await keysRes.json();
        setKeys(data.keys || []);
      }
      if (listsRes.ok) {
        const data = await listsRes.json();
        setLists(data.lists || []);
      }
      if (contentsRes.ok) {
        const data = await contentsRes.json();
        setContents(data.contents || []);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const fetchExecutorStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/api/ses/warmup/executor/status`);
      if (res.ok) {
        setExecutorStatus(await res.json());
      }
    } catch (error) {
      console.error('Error fetching executor status:', error);
    }
  };

  const fetchRecommendations = async (planId: string) => {
    try {
      const res = await fetch(`${API_URL}/api/ses/warmup/plans/${planId}/recommendations`);
      if (res.ok) {
        const data = await res.json();
        setRecommendations(data.recommendations || []);
      }
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    }
  };

  const fetchTimeline = async (planId: string) => {
    try {
      const res = await fetch(`${API_URL}/api/ses/warmup/plans/${planId}/timeline`);
      if (res.ok) {
        const data = await res.json();
        setTimeline(data.timeline || []);
      }
    } catch (error) {
      console.error('Error fetching timeline:', error);
    }
  };

  const fetchExecutionLog = async (planId?: string) => {
    try {
      const url = planId 
        ? `${API_URL}/api/ses/warmup/executor/log?plan_id=${planId}&limit=50`
        : `${API_URL}/api/ses/warmup/executor/log?limit=50`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setExecutionLog(data.log || []);
      }
    } catch (error) {
      console.error('Error fetching execution log:', error);
    }
  };

  const createPlan = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/ses/warmup/plans`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newPlan)
      });
      if (res.ok) {
        setShowCreateModal(false);
        setNewPlan({ 
          key_id: '', name: '', strategy: 'moderate', target_volume: 10000,
          auto_mode: true, send_hour: 10, send_minute: 0,
          recipient_list_id: '', content_id: '', from_email: '', from_name: ''
        });
        fetchData();
      }
    } catch (error) {
      console.error('Error creating plan:', error);
    }
    setLoading(false);
  };

  const updatePlanSettings = async () => {
    if (!selectedPlan) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/ses/warmup/plans/${selectedPlan.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(planSettings)
      });
      if (res.ok) {
        setShowSettingsModal(false);
        fetchData();
        const data = await res.json();
        setSelectedPlan(data.plan);
      }
    } catch (error) {
      console.error('Error updating plan:', error);
    }
    setLoading(false);
  };

  const startPlan = async (planId: string) => {
    try {
      await fetch(`${API_URL}/api/ses/warmup/plans/${planId}/start`, { method: 'POST' });
      fetchData();
    } catch (error) {
      console.error('Error starting plan:', error);
    }
  };

  const pausePlan = async (planId: string, reason: string = '') => {
    try {
      await fetch(`${API_URL}/api/ses/warmup/plans/${planId}/pause`, { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason })
      });
      fetchData();
    } catch (error) {
      console.error('Error pausing plan:', error);
    }
  };

  const resumePlan = async (planId: string) => {
    try {
      await fetch(`${API_URL}/api/ses/warmup/plans/${planId}/resume`, { method: 'POST' });
      fetchData();
    } catch (error) {
      console.error('Error resuming plan:', error);
    }
  };

  const deletePlan = async (planId: string) => {
    if (!confirm('Are you sure you want to delete this warmup plan?')) return;
    try {
      await fetch(`${API_URL}/api/ses/warmup/plans/${planId}`, { method: 'DELETE' });
      setSelectedPlan(null);
      setActiveView('list');
      fetchData();
    } catch (error) {
      console.error('Error deleting plan:', error);
    }
  };

  const executeWarmup = async (planId: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/ses/warmup/execute/${planId}`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        alert(`Warmup executed! Sent: ${data.sent}, Delivered: ${data.delivered}`);
        fetchData();
        if (selectedPlan) {
          fetchTimeline(selectedPlan.id);
          fetchRecommendations(selectedPlan.id);
        }
      } else {
        alert(`Error: ${data.error}`);
      }
    } catch (error) {
      console.error('Error executing warmup:', error);
    }
    setLoading(false);
  };

  const simulateWarmup = async (planId: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/ses/warmup/simulate/${planId}`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        alert(`Simulation completed! Day ${data.day}: Sent ${data.sent}, Delivered ${data.delivered}, Opens ${data.opens}`);
        fetchData();
        if (selectedPlan) {
          fetchTimeline(selectedPlan.id);
          fetchRecommendations(selectedPlan.id);
        }
      }
    } catch (error) {
      console.error('Error simulating warmup:', error);
    }
    setLoading(false);
  };

  const toggleExecutor = async () => {
    try {
      const action = executorStatus?.is_running ? 'stop' : 'start';
      await fetch(`${API_URL}/api/ses/warmup/executor/${action}`, { method: 'POST' });
      fetchExecutorStatus();
    } catch (error) {
      console.error('Error toggling executor:', error);
    }
  };

  const selectPlan = (plan: WarmupPlan) => {
    setSelectedPlan(plan);
    setPlanSettings({
      auto_mode: plan.auto_mode,
      send_hour: plan.send_hour,
      send_minute: plan.send_minute,
      recipient_list_id: plan.recipient_list_id,
      content_id: plan.content_id,
      from_email: plan.from_email,
      from_name: plan.from_name,
      max_bounce_rate: plan.max_bounce_rate,
      max_complaint_rate: plan.max_complaint_rate,
      auto_pause_on_issues: plan.auto_pause_on_issues
    });
    fetchRecommendations(plan.id);
    fetchTimeline(plan.id);
    fetchExecutionLog(plan.id);
    setActiveView('details');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'in_progress': return '#10b981';
      case 'completed': return '#3b82f6';
      case 'paused': return '#f59e0b';
      case 'failed': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getHealthColor = (score: number) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return '📈';
      case 'declining': return '📉';
      default: return '➡️';
    }
  };

  const getRecommendationColor = (type: string) => {
    switch (type) {
      case 'critical': return '#ef4444';
      case 'warning': return '#f59e0b';
      case 'info': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  const getRiskBadge = (risk: string) => {
    const colors: Record<string, string> = { low: '#10b981', medium: '#f59e0b', high: '#ef4444' };
    return (
      <span style={{ background: colors[risk] || '#6b7280', color: 'white', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', textTransform: 'uppercase' }}>
        {risk} risk
      </span>
    );
  };

  const formatTime = (hour: number, minute: number) => {
    return `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
  };

  return (
    <div style={{ padding: '20px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ margin: 0, color: '#f0f0f0' }}>🔥 Warm-up Manager</h2>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          {/* Executor Status */}
          <div style={{ 
            display: 'flex', alignItems: 'center', gap: '8px', 
            padding: '8px 15px', background: '#1e293b', borderRadius: '6px'
          }}>
            <div style={{ 
              width: '10px', height: '10px', borderRadius: '50%', 
              background: executorStatus?.is_running ? '#10b981' : '#ef4444',
              animation: executorStatus?.is_running ? 'pulse 2s infinite' : 'none'
            }} />
            <span style={{ color: '#94a3b8', fontSize: '13px' }}>
              Auto-Executor: {executorStatus?.is_running ? 'Running' : 'Stopped'}
            </span>
            <button 
              onClick={toggleExecutor}
              style={{ 
                background: executorStatus?.is_running ? '#ef4444' : '#10b981', 
                color: 'white', border: 'none', padding: '4px 10px', 
                borderRadius: '4px', cursor: 'pointer', fontSize: '11px'
              }}
            >
              {executorStatus?.is_running ? 'Stop' : 'Start'}
            </button>
          </div>
          
          <button 
            onClick={() => setShowCreateModal(true)} 
            style={{ 
              background: '#10b981', color: 'white', border: 'none', 
              padding: '10px 20px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold'
            }}
          >
            + New Warm-up Plan
          </button>
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '15px', marginBottom: '20px' }}>
        <div style={{ background: '#1e293b', padding: '15px', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f0f0f0' }}>{stats.total_plans}</div>
          <div style={{ color: '#94a3b8', fontSize: '12px' }}>Total Plans</div>
        </div>
        <div style={{ background: '#1e293b', padding: '15px', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981' }}>{stats.in_progress}</div>
          <div style={{ color: '#94a3b8', fontSize: '12px' }}>In Progress</div>
        </div>
        <div style={{ background: '#1e293b', padding: '15px', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#3b82f6' }}>{stats.completed}</div>
          <div style={{ color: '#94a3b8', fontSize: '12px' }}>Completed</div>
        </div>
        <div style={{ background: '#1e293b', padding: '15px', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f59e0b' }}>{stats.paused}</div>
          <div style={{ color: '#94a3b8', fontSize: '12px' }}>Paused</div>
        </div>
        <div style={{ background: '#1e293b', padding: '15px', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f0f0f0' }}>{stats.total_emails_sent?.toLocaleString() || 0}</div>
          <div style={{ color: '#94a3b8', fontSize: '12px' }}>Emails Sent</div>
        </div>
        <div style={{ background: '#1e293b', padding: '15px', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981' }}>{stats.overall_delivery_rate || 0}%</div>
          <div style={{ color: '#94a3b8', fontSize: '12px' }}>Delivery Rate</div>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ display: 'grid', gridTemplateColumns: selectedPlan ? '350px 1fr' : '1fr', gap: '20px' }}>
        {/* Plans List */}
        <div style={{ background: '#1e293b', borderRadius: '8px', padding: '15px' }}>
          <h3 style={{ margin: '0 0 15px 0', color: '#f0f0f0' }}>Warm-up Plans</h3>
          {plans.length === 0 ? (
            <div style={{ color: '#94a3b8', textAlign: 'center', padding: '40px' }}>
              No warm-up plans yet. Create one to start building sender reputation.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '600px', overflowY: 'auto' }}>
              {plans.map(plan => (
                <div 
                  key={plan.id} 
                  onClick={() => selectPlan(plan)} 
                  style={{ 
                    background: selectedPlan?.id === plan.id ? '#334155' : '#0f172a', 
                    padding: '15px', borderRadius: '6px', cursor: 'pointer', 
                    border: selectedPlan?.id === plan.id ? '1px solid #3b82f6' : '1px solid transparent'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontWeight: 'bold', color: '#f0f0f0' }}>{plan.name}</span>
                    <span style={{ 
                      background: getStatusColor(plan.status), color: 'white', 
                      padding: '2px 8px', borderRadius: '4px', fontSize: '11px', textTransform: 'uppercase'
                    }}>
                      {plan.status.replace('_', ' ')}
                    </span>
                  </div>
                  
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ color: '#94a3b8', fontSize: '12px' }}>
                      Day {plan.current_day}/{plan.total_days}
                    </span>
                    <span style={{ color: '#94a3b8', fontSize: '12px' }}>
                      {plan.auto_mode ? '🤖 Auto' : '👤 Manual'}
                    </span>
                  </div>
                  
                  {/* Progress Bar */}
                  <div style={{ background: '#0f172a', borderRadius: '4px', height: '6px', overflow: 'hidden', marginBottom: '8px' }}>
                    <div style={{ 
                      background: getStatusColor(plan.status), height: '100%', 
                      width: `${plan.progress_percent || 0}%`, transition: 'width 0.3s'
                    }} />
                  </div>
                  
                  {/* Health Score */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: '#94a3b8', fontSize: '11px' }}>
                      Health: <span style={{ color: getHealthColor(plan.health_score || 100) }}>{plan.health_score || 100}%</span>
                    </span>
                    <span style={{ fontSize: '11px' }}>
                      {getTrendIcon(plan.reputation_trend || 'stable')}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Plan Details */}
        {selectedPlan && (
          <div style={{ background: '#1e293b', borderRadius: '8px', padding: '15px' }}>
            {/* Tabs */}
            <div style={{ display: 'flex', gap: '5px', marginBottom: '15px', borderBottom: '1px solid #334155', paddingBottom: '10px' }}>
              {[
                { id: 'details', label: 'Details', icon: '📊' },
                { id: 'timeline', label: 'Timeline', icon: '📅' },
                { id: 'log', label: 'Execution Log', icon: '📜' }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveView(tab.id as any)}
                  style={{
                    padding: '8px 15px', background: activeView === tab.id ? '#334155' : 'transparent',
                    border: 'none', borderRadius: '4px', color: activeView === tab.id ? '#f0f0f0' : '#94a3b8',
                    cursor: 'pointer', fontSize: '13px'
                  }}
                >
                  {tab.icon} {tab.label}
                </button>
              ))}
            </div>

            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
              <div>
                <h3 style={{ margin: '0 0 5px 0', color: '#f0f0f0' }}>{selectedPlan.name}</h3>
                <span style={{ color: '#94a3b8', fontSize: '12px' }}>
                  Strategy: {selectedPlan.strategy} • Target: {selectedPlan.target_daily_volume.toLocaleString()}/day
                </span>
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                {selectedPlan.status === 'not_started' && (
                  <button onClick={() => startPlan(selectedPlan.id)} style={{ background: '#10b981', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>▶ Start</button>
                )}
                {selectedPlan.status === 'in_progress' && (
                  <>
                    <button onClick={() => simulateWarmup(selectedPlan.id)} disabled={loading} style={{ background: '#8b5cf6', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px', opacity: loading ? 0.5 : 1 }}>🎲 Simulate Day</button>
                    <button onClick={() => executeWarmup(selectedPlan.id)} disabled={loading} style={{ background: '#3b82f6', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px', opacity: loading ? 0.5 : 1 }}>⚡ Execute Now</button>
                    <button onClick={() => pausePlan(selectedPlan.id)} style={{ background: '#f59e0b', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>⏸ Pause</button>
                  </>
                )}
                {selectedPlan.status === 'paused' && (
                  <button onClick={() => resumePlan(selectedPlan.id)} style={{ background: '#10b981', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>▶ Resume</button>
                )}
                <button onClick={() => setShowSettingsModal(true)} style={{ background: '#334155', color: '#f0f0f0', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>⚙️ Settings</button>
                <button onClick={() => deletePlan(selectedPlan.id)} style={{ background: '#ef4444', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>🗑</button>
              </div>
            </div>

            {/* Details View */}
            {activeView === 'details' && (
              <>
                {/* Stats Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '10px', marginBottom: '15px' }}>
                  <div style={{ background: '#0f172a', padding: '12px', borderRadius: '6px', textAlign: 'center' }}>
                    <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#f0f0f0' }}>{selectedPlan.total_sent.toLocaleString()}</div>
                    <div style={{ color: '#94a3b8', fontSize: '11px' }}>Total Sent</div>
                  </div>
                  <div style={{ background: '#0f172a', padding: '12px', borderRadius: '6px', textAlign: 'center' }}>
                    <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#10b981' }}>{selectedPlan.avg_delivery_rate || 0}%</div>
                    <div style={{ color: '#94a3b8', fontSize: '11px' }}>Delivery Rate</div>
                  </div>
                  <div style={{ background: '#0f172a', padding: '12px', borderRadius: '6px', textAlign: 'center' }}>
                    <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#ef4444' }}>{selectedPlan.avg_bounce_rate || 0}%</div>
                    <div style={{ color: '#94a3b8', fontSize: '11px' }}>Bounce Rate</div>
                  </div>
                  <div style={{ background: '#0f172a', padding: '12px', borderRadius: '6px', textAlign: 'center' }}>
                    <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#3b82f6' }}>{selectedPlan.avg_open_rate || 0}%</div>
                    <div style={{ color: '#94a3b8', fontSize: '11px' }}>Open Rate</div>
                  </div>
                  <div style={{ background: '#0f172a', padding: '12px', borderRadius: '6px', textAlign: 'center' }}>
                    <div style={{ fontSize: '20px', fontWeight: 'bold', color: getHealthColor(selectedPlan.health_score || 100) }}>{selectedPlan.health_score || 100}</div>
                    <div style={{ color: '#94a3b8', fontSize: '11px' }}>Health Score</div>
                  </div>
                </div>

                {/* Auto Mode Info */}
                {selectedPlan.auto_mode && (
                  <div style={{ background: '#0f172a', padding: '12px', borderRadius: '6px', marginBottom: '15px', borderLeft: '3px solid #3b82f6' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <span style={{ color: '#3b82f6', fontWeight: 'bold', fontSize: '13px' }}>🤖 Auto Mode Enabled</span>
                        <div style={{ color: '#94a3b8', fontSize: '12px', marginTop: '4px' }}>
                          Scheduled: {formatTime(selectedPlan.send_hour, selectedPlan.send_minute)} daily
                          {selectedPlan.next_scheduled_run && (
                            <span> • Next run: {new Date(selectedPlan.next_scheduled_run).toLocaleString()}</span>
                          )}
                        </div>
                      </div>
                      <div style={{ textAlign: 'right', fontSize: '11px', color: '#94a3b8' }}>
                        {selectedPlan.from_email && <div>From: {selectedPlan.from_email}</div>}
                        {selectedPlan.last_auto_run && <div>Last run: {new Date(selectedPlan.last_auto_run).toLocaleString()}</div>}
                      </div>
                    </div>
                  </div>
                )}

                {/* Pause Reason */}
                {selectedPlan.pause_reason && (
                  <div style={{ background: '#0f172a', padding: '12px', borderRadius: '6px', marginBottom: '15px', borderLeft: '3px solid #ef4444' }}>
                    <span style={{ color: '#ef4444', fontWeight: 'bold', fontSize: '13px' }}>⚠️ Paused: </span>
                    <span style={{ color: '#f0f0f0', fontSize: '13px' }}>{selectedPlan.pause_reason}</span>
                  </div>
                )}

                {/* Recommendations */}
                {recommendations.length > 0 && (
                  <div style={{ marginBottom: '15px' }}>
                    <h4 style={{ margin: '0 0 10px 0', color: '#f0f0f0', fontSize: '14px' }}>💡 Recommendations</h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {recommendations.map((rec, i) => (
                        <div key={i} style={{ 
                          background: '#0f172a', padding: '12px', borderRadius: '6px', 
                          borderLeft: `3px solid ${getRecommendationColor(rec.type)}`
                        }}>
                          <div style={{ color: getRecommendationColor(rec.type), fontWeight: 'bold', fontSize: '12px', marginBottom: '4px' }}>
                            {rec.title}
                          </div>
                          <div style={{ color: '#94a3b8', fontSize: '12px', marginBottom: '4px' }}>{rec.message}</div>
                          <div style={{ color: '#f0f0f0', fontSize: '11px' }}>→ {rec.action}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Alerts */}
                {selectedPlan.alerts && selectedPlan.alerts.length > 0 && (
                  <div style={{ marginBottom: '15px' }}>
                    <h4 style={{ margin: '0 0 10px 0', color: '#f0f0f0', fontSize: '14px' }}>🔔 Recent Alerts</h4>
                    <div style={{ background: '#0f172a', padding: '10px', borderRadius: '6px', maxHeight: '100px', overflowY: 'auto' }}>
                      {selectedPlan.alerts.slice(-5).reverse().map((alert, i) => (
                        <div key={i} style={{ color: '#94a3b8', fontSize: '11px', marginBottom: '4px' }}>• {alert}</div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}

            {/* Timeline View */}
            {activeView === 'timeline' && (
              <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                  <thead>
                    <tr style={{ background: '#0f172a', position: 'sticky', top: 0 }}>
                      <th style={{ padding: '10px', textAlign: 'left', color: '#94a3b8' }}>Day</th>
                      <th style={{ padding: '10px', textAlign: 'left', color: '#94a3b8' }}>Date</th>
                      <th style={{ padding: '10px', textAlign: 'right', color: '#94a3b8' }}>Target</th>
                      <th style={{ padding: '10px', textAlign: 'right', color: '#94a3b8' }}>Sent</th>
                      <th style={{ padding: '10px', textAlign: 'right', color: '#94a3b8' }}>Delivered</th>
                      <th style={{ padding: '10px', textAlign: 'right', color: '#94a3b8' }}>Bounce %</th>
                      <th style={{ padding: '10px', textAlign: 'right', color: '#94a3b8' }}>Open %</th>
                      <th style={{ padding: '10px', textAlign: 'center', color: '#94a3b8' }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {timeline.map(day => (
                      <tr key={day.day} style={{ 
                        borderBottom: '1px solid #334155',
                        background: day.status === 'current' ? '#1e3a5f' : 'transparent'
                      }}>
                        <td style={{ padding: '10px', color: '#f0f0f0', fontWeight: day.status === 'current' ? 'bold' : 'normal' }}>
                          Day {day.day}
                        </td>
                        <td style={{ padding: '10px', color: '#94a3b8' }}>{day.date || '-'}</td>
                        <td style={{ padding: '10px', textAlign: 'right', color: '#94a3b8' }}>{day.target_volume.toLocaleString()}</td>
                        <td style={{ padding: '10px', textAlign: 'right', color: '#f0f0f0' }}>{day.actual_sent.toLocaleString()}</td>
                        <td style={{ padding: '10px', textAlign: 'right', color: '#10b981' }}>{day.delivered.toLocaleString()}</td>
                        <td style={{ padding: '10px', textAlign: 'right', color: day.bounce_rate > 3 ? '#ef4444' : '#94a3b8' }}>
                          {day.bounce_rate.toFixed(2)}%
                        </td>
                        <td style={{ padding: '10px', textAlign: 'right', color: day.open_rate > 20 ? '#10b981' : '#94a3b8' }}>
                          {day.open_rate.toFixed(1)}%
                        </td>
                        <td style={{ padding: '10px', textAlign: 'center' }}>
                          {day.status === 'completed' ? (
                            <span style={{ color: '#10b981' }}>✓</span>
                          ) : day.status === 'current' ? (
                            <span style={{ color: '#3b82f6' }}>●</span>
                          ) : (
                            <span style={{ color: '#6b7280' }}>○</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Execution Log View */}
            {activeView === 'log' && (
              <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
                {executionLog.length === 0 ? (
                  <div style={{ color: '#94a3b8', textAlign: 'center', padding: '40px' }}>
                    No execution logs yet
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {executionLog.map((entry, i) => (
                      <div key={i} style={{ 
                        background: '#0f172a', padding: '10px', borderRadius: '6px',
                        borderLeft: `3px solid ${entry.status === 'success' ? '#10b981' : entry.status === 'failed' ? '#ef4444' : '#f59e0b'}`
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                          <span style={{ color: '#f0f0f0', fontSize: '12px', fontWeight: 'bold' }}>{entry.action}</span>
                          <span style={{ color: '#94a3b8', fontSize: '11px' }}>{new Date(entry.timestamp).toLocaleString()}</span>
                        </div>
                        <div style={{ color: entry.status === 'success' ? '#10b981' : '#ef4444', fontSize: '11px' }}>
                          Status: {entry.status}
                        </div>
                        {entry.details && Object.keys(entry.details).length > 0 && (
                          <div style={{ color: '#94a3b8', fontSize: '11px', marginTop: '4px' }}>
                            {Object.entries(entry.details).map(([k, v]) => `${k}: ${v}`).join(' • ')}
                          </div>
                        )}
                        {entry.error && (
                          <div style={{ color: '#ef4444', fontSize: '11px', marginTop: '4px' }}>Error: {entry.error}</div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#1e293b', padding: '25px', borderRadius: '12px', width: '600px', maxWidth: '90%', maxHeight: '90vh', overflowY: 'auto' }}>
            <h3 style={{ margin: '0 0 20px 0', color: '#f0f0f0' }}>Create Warm-up Plan</h3>
            
            {/* Basic Settings */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '15px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', color: '#94a3b8', fontSize: '12px' }}>AWS Key *</label>
                <select value={newPlan.key_id} onChange={e => setNewPlan({...newPlan, key_id: e.target.value})} style={{ width: '100%', padding: '10px', background: '#0f172a', border: '1px solid #334155', borderRadius: '6px', color: '#f0f0f0' }}>
                  <option value="">Select AWS Key</option>
                  {keys.map(key => (
                    <option key={key.id} value={key.id}>{key.name || key.id} ({key.region})</option>
                  ))}
                </select>
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', color: '#94a3b8', fontSize: '12px' }}>Plan Name *</label>
                <input type="text" value={newPlan.name} onChange={e => setNewPlan({...newPlan, name: e.target.value})} placeholder="My Warmup Plan" style={{ width: '100%', padding: '10px', background: '#0f172a', border: '1px solid #334155', borderRadius: '6px', color: '#f0f0f0', boxSizing: 'border-box' }} />
              </div>
            </div>

            {/* Strategy */}
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px', color: '#94a3b8', fontSize: '12px' }}>Strategy</label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {strategies.map(s => (
                  <label key={s.id} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px', background: newPlan.strategy === s.id ? '#334155' : '#0f172a', borderRadius: '6px', cursor: 'pointer', border: newPlan.strategy === s.id ? '1px solid #3b82f6' : '1px solid transparent' }}>
                    <input type="radio" name="strategy" value={s.id} checked={newPlan.strategy === s.id} onChange={e => setNewPlan({...newPlan, strategy: e.target.value})} style={{ display: 'none' }} />
                    <div style={{ flex: 1 }}>
                      <div style={{ color: '#f0f0f0', fontWeight: 'bold', marginBottom: '2px' }}>{s.name} <span style={{ color: '#94a3b8', fontWeight: 'normal' }}>({s.days} days)</span></div>
                      <div style={{ color: '#94a3b8', fontSize: '11px' }}>{s.description}</div>
                    </div>
                    {getRiskBadge(s.risk)}
                  </label>
                ))}
              </div>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px', color: '#94a3b8', fontSize: '12px' }}>Target Daily Volume (after warmup)</label>
              <input type="number" value={newPlan.target_volume} onChange={e => setNewPlan({...newPlan, target_volume: parseInt(e.target.value) || 0})} style={{ width: '100%', padding: '10px', background: '#0f172a', border: '1px solid #334155', borderRadius: '6px', color: '#f0f0f0', boxSizing: 'border-box' }} />
            </div>

            {/* Auto Mode Settings */}
            <div style={{ background: '#0f172a', padding: '15px', borderRadius: '8px', marginBottom: '15px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px' }}>
                <input type="checkbox" id="autoMode" checked={newPlan.auto_mode} onChange={e => setNewPlan({...newPlan, auto_mode: e.target.checked})} />
                <label htmlFor="autoMode" style={{ color: '#f0f0f0', fontWeight: 'bold' }}>🤖 Enable Auto Mode</label>
              </div>
              
              {newPlan.auto_mode && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', color: '#94a3b8', fontSize: '12px' }}>Send Time</label>
                    <div style={{ display: 'flex', gap: '10px' }}>
                      <input type="number" min="0" max="23" value={newPlan.send_hour} onChange={e => setNewPlan({...newPlan, send_hour: parseInt(e.target.value) || 0})} placeholder="Hour" style={{ width: '50%', padding: '10px', background: '#1e293b', border: '1px solid #334155', borderRadius: '6px', color: '#f0f0f0' }} />
                      <input type="number" min="0" max="59" value={newPlan.send_minute} onChange={e => setNewPlan({...newPlan, send_minute: parseInt(e.target.value) || 0})} placeholder="Min" style={{ width: '50%', padding: '10px', background: '#1e293b', border: '1px solid #334155', borderRadius: '6px', color: '#f0f0f0' }} />
                    </div>
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', color: '#94a3b8', fontSize: '12px' }}>Recipient List</label>
                    <select value={newPlan.recipient_list_id} onChange={e => setNewPlan({...newPlan, recipient_list_id: e.target.value})} style={{ width: '100%', padding: '10px', background: '#1e293b', border: '1px solid #334155', borderRadius: '6px', color: '#f0f0f0' }}>
                      <option value="">Select List</option>
                      {lists.map(list => (
                        <option key={list.id} value={list.id}>{list.name} ({list.valid_count} emails)</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', color: '#94a3b8', fontSize: '12px' }}>Email Content</label>
                    <select value={newPlan.content_id} onChange={e => setNewPlan({...newPlan, content_id: e.target.value})} style={{ width: '100%', padding: '10px', background: '#1e293b', border: '1px solid #334155', borderRadius: '6px', color: '#f0f0f0' }}>
                      <option value="">Select Content</option>
                      {contents.map(content => (
                        <option key={content.id} value={content.id}>{content.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', color: '#94a3b8', fontSize: '12px' }}>From Email</label>
                    <input type="email" value={newPlan.from_email} onChange={e => setNewPlan({...newPlan, from_email: e.target.value})} placeholder="sender@domain.com" style={{ width: '100%', padding: '10px', background: '#1e293b', border: '1px solid #334155', borderRadius: '6px', color: '#f0f0f0', boxSizing: 'border-box' }} />
                  </div>
                  <div style={{ gridColumn: 'span 2' }}>
                    <label style={{ display: 'block', marginBottom: '5px', color: '#94a3b8', fontSize: '12px' }}>From Name</label>
                    <input type="text" value={newPlan.from_name} onChange={e => setNewPlan({...newPlan, from_name: e.target.value})} placeholder="Sender Name" style={{ width: '100%', padding: '10px', background: '#1e293b', border: '1px solid #334155', borderRadius: '6px', color: '#f0f0f0', boxSizing: 'border-box' }} />
                  </div>
                </div>
              )}
            </div>

            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button onClick={() => setShowCreateModal(false)} style={{ background: '#334155', color: '#f0f0f0', border: 'none', padding: '10px 20px', borderRadius: '6px', cursor: 'pointer' }}>Cancel</button>
              <button onClick={createPlan} disabled={!newPlan.key_id || !newPlan.name || loading} style={{ background: '#10b981', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '6px', cursor: 'pointer', opacity: (!newPlan.key_id || !newPlan.name || loading) ? 0.5 : 1 }}>
                {loading ? 'Creating...' : 'Create Plan'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Settings Modal */}
      {showSettingsModal && selectedPlan && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#1e293b', padding: '25px', borderRadius: '12px', width: '500px', maxWidth: '90%', maxHeight: '90vh', overflowY: 'auto' }}>
            <h3 style={{ margin: '0 0 20px 0', color: '#f0f0f0' }}>Plan Settings: {selectedPlan.name}</h3>
            
            {/* Auto Mode */}
            <div style={{ background: '#0f172a', padding: '15px', borderRadius: '8px', marginBottom: '15px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px' }}>
                <input type="checkbox" id="settingsAutoMode" checked={planSettings.auto_mode} onChange={e => setPlanSettings({...planSettings, auto_mode: e.target.checked})} />
                <label htmlFor="settingsAutoMode" style={{ color: '#f0f0f0', fontWeight: 'bold' }}>🤖 Auto Mode</label>
              </div>
              
              {planSettings.auto_mode && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', color: '#94a3b8', fontSize: '12px' }}>Send Hour</label>
                    <input type="number" min="0" max="23" value={planSettings.send_hour} onChange={e => setPlanSettings({...planSettings, send_hour: parseInt(e.target.value) || 0})} style={{ width: '100%', padding: '8px', background: '#1e293b', border: '1px solid #334155', borderRadius: '4px', color: '#f0f0f0' }} />
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', color: '#94a3b8', fontSize: '12px' }}>Send Minute</label>
                    <input type="number" min="0" max="59" value={planSettings.send_minute} onChange={e => setPlanSettings({...planSettings, send_minute: parseInt(e.target.value) || 0})} style={{ width: '100%', padding: '8px', background: '#1e293b', border: '1px solid #334155', borderRadius: '4px', color: '#f0f0f0' }} />
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', color: '#94a3b8', fontSize: '12px' }}>Recipient List</label>
                    <select value={planSettings.recipient_list_id} onChange={e => setPlanSettings({...planSettings, recipient_list_id: e.target.value})} style={{ width: '100%', padding: '8px', background: '#1e293b', border: '1px solid #334155', borderRadius: '4px', color: '#f0f0f0' }}>
                      <option value="">Select List</option>
                      {lists.map(list => (
                        <option key={list.id} value={list.id}>{list.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', color: '#94a3b8', fontSize: '12px' }}>Email Content</label>
                    <select value={planSettings.content_id} onChange={e => setPlanSettings({...planSettings, content_id: e.target.value})} style={{ width: '100%', padding: '8px', background: '#1e293b', border: '1px solid #334155', borderRadius: '4px', color: '#f0f0f0' }}>
                      <option value="">Select Content</option>
                      {contents.map(content => (
                        <option key={content.id} value={content.id}>{content.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', color: '#94a3b8', fontSize: '12px' }}>From Email</label>
                    <input type="email" value={planSettings.from_email} onChange={e => setPlanSettings({...planSettings, from_email: e.target.value})} style={{ width: '100%', padding: '8px', background: '#1e293b', border: '1px solid #334155', borderRadius: '4px', color: '#f0f0f0' }} />
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', color: '#94a3b8', fontSize: '12px' }}>From Name</label>
                    <input type="text" value={planSettings.from_name} onChange={e => setPlanSettings({...planSettings, from_name: e.target.value})} style={{ width: '100%', padding: '8px', background: '#1e293b', border: '1px solid #334155', borderRadius: '4px', color: '#f0f0f0' }} />
                  </div>
                </div>
              )}
            </div>

            {/* Quality Thresholds */}
            <div style={{ background: '#0f172a', padding: '15px', borderRadius: '8px', marginBottom: '15px' }}>
              <h4 style={{ margin: '0 0 15px 0', color: '#f0f0f0', fontSize: '14px' }}>Quality Thresholds</h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', color: '#94a3b8', fontSize: '12px' }}>Max Bounce Rate (%)</label>
                  <input type="number" step="0.1" value={planSettings.max_bounce_rate} onChange={e => setPlanSettings({...planSettings, max_bounce_rate: parseFloat(e.target.value) || 5})} style={{ width: '100%', padding: '8px', background: '#1e293b', border: '1px solid #334155', borderRadius: '4px', color: '#f0f0f0' }} />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', color: '#94a3b8', fontSize: '12px' }}>Max Complaint Rate (%)</label>
                  <input type="number" step="0.01" value={planSettings.max_complaint_rate} onChange={e => setPlanSettings({...planSettings, max_complaint_rate: parseFloat(e.target.value) || 0.1})} style={{ width: '100%', padding: '8px', background: '#1e293b', border: '1px solid #334155', borderRadius: '4px', color: '#f0f0f0' }} />
                </div>
              </div>
              <div style={{ marginTop: '10px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#f0f0f0', cursor: 'pointer' }}>
                  <input type="checkbox" checked={planSettings.auto_pause_on_issues} onChange={e => setPlanSettings({...planSettings, auto_pause_on_issues: e.target.checked})} />
                  Auto-pause when thresholds exceeded
                </label>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button onClick={() => setShowSettingsModal(false)} style={{ background: '#334155', color: '#f0f0f0', border: 'none', padding: '10px 20px', borderRadius: '6px', cursor: 'pointer' }}>Cancel</button>
              <button onClick={updatePlanSettings} disabled={loading} style={{ background: '#3b82f6', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '6px', cursor: 'pointer', opacity: loading ? 0.5 : 1 }}>
                {loading ? 'Saving...' : 'Save Settings'}
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};

export default SESWarmup;
