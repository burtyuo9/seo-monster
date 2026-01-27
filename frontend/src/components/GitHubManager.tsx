import React, { useState, useEffect } from 'react';

interface Repo {
  name: string;
  full_name: string;
  description: string;
  url: string;
  private: boolean;
  updated_at: string;
}

interface Collaborator {
  id: string;
  name: string;
  github_username: string;
  capabilities: string[];
  status: string;
  last_activity: string;
}

interface Project {
  id: string;
  name: string;
  description: string;
  repo_full_name: string;
  collaborators: string[];
  status: string;
  tasks: Task[];
}

interface Task {
  id: string;
  title: string;
  description: string;
  assigned_to: string | null;
  status: string;
}

interface Stats {
  repos_count: number;
  collaborators_count: number;
  active_collaborators: number;
  projects_count: number;
  active_projects: number;
  total_tasks: number;
  pending_tasks: number;
}

const GitHubManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'repos' | 'collaborators' | 'projects' | 'sync'>('repos');
  const [repos, setRepos] = useState<Repo[]>([]);
  const [collaborators, setCollaborators] = useState<Collaborator[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Forms
  const [showRepoForm, setShowRepoForm] = useState(false);
  const [showCollaboratorForm, setShowCollaboratorForm] = useState(false);
  const [showProjectForm, setShowProjectForm] = useState(false);
  const [showTokenForm, setShowTokenForm] = useState(false);
  
  // Form data
  const [repoForm, setRepoForm] = useState({ name: '', description: '', private: true });
  const [collaboratorForm, setCollaboratorForm] = useState({ 
    id: '', name: '', github_username: '', capabilities: '' 
  });
  const [projectForm, setProjectForm] = useState({ 
    name: '', description: '', repo_full_name: '', collaborator_ids: '' 
  });
  const [token, setToken] = useState('');
  const [syncForm, setSyncForm] = useState({ owner: '', repo: '', local_path: '' });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [reposRes, collaboratorsRes, projectsRes, statsRes] = await Promise.all([
        fetch('/api/github/repos').then(r => r.json()),
        fetch('/api/github/collaborators').then(r => r.json()),
        fetch('/api/github/projects').then(r => r.json()),
        fetch('/api/github/stats').then(r => r.json()),
      ]);
      
      setRepos(reposRes.repos || []);
      setCollaborators(collaboratorsRes.collaborators || []);
      setProjects(projectsRes.projects || []);
      setStats(statsRes);
    } catch (err) {
      setError('Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  };

  const createRepo = async () => {
    try {
      const response = await fetch('/api/github/repos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(repoForm),
      });
      
      if (response.ok) {
        setShowRepoForm(false);
        setRepoForm({ name: '', description: '', private: true });
        loadData();
      } else {
        const data = await response.json();
        setError(data.detail || 'Ошибка создания репозитория');
      }
    } catch (err) {
      setError('Ошибка создания репозитория');
    }
  };

  const addCollaborator = async () => {
    try {
      const response = await fetch('/api/github/collaborators', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...collaboratorForm,
          capabilities: collaboratorForm.capabilities.split(',').map(c => c.trim()),
        }),
      });
      
      if (response.ok) {
        setShowCollaboratorForm(false);
        setCollaboratorForm({ id: '', name: '', github_username: '', capabilities: '' });
        loadData();
      }
    } catch (err) {
      setError('Ошибка добавления коллаборатора');
    }
  };

  const createProject = async () => {
    try {
      const response = await fetch('/api/github/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...projectForm,
          collaborator_ids: projectForm.collaborator_ids.split(',').map(c => c.trim()).filter(Boolean),
        }),
      });
      
      if (response.ok) {
        setShowProjectForm(false);
        setProjectForm({ name: '', description: '', repo_full_name: '', collaborator_ids: '' });
        loadData();
      }
    } catch (err) {
      setError('Ошибка создания проекта');
    }
  };

  const setGitHubToken = async () => {
    try {
      const response = await fetch('/api/github/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
      });
      
      if (response.ok) {
        setShowTokenForm(false);
        setToken('');
        loadData();
      }
    } catch (err) {
      setError('Ошибка установки токена');
    }
  };

  const syncKnowledge = async (direction: 'upload' | 'download') => {
    try {
      const response = await fetch(`/api/github/sync/${direction}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(syncForm),
      });
      
      const data = await response.json();
      if (response.ok) {
        alert(`Синхронизация завершена!\n${direction === 'upload' ? 'Загружено' : 'Скачано'}: ${data.results?.uploaded?.length || data.downloaded?.length || 0} файлов`);
      } else {
        setError(data.detail || 'Ошибка синхронизации');
      }
    } catch (err) {
      setError('Ошибка синхронизации');
    }
  };

  const removeCollaborator = async (id: string) => {
    if (!confirm('Удалить коллаборатора?')) return;
    
    try {
      await fetch(`/api/github/collaborators/${id}`, { method: 'DELETE' });
      loadData();
    } catch (err) {
      setError('Ошибка удаления');
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">GitHub Integration</h1>
        <button
          onClick={() => setShowTokenForm(true)}
          className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
        >
          🔑 Настроить токен
        </button>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-lg">
          {error}
          <button onClick={() => setError(null)} className="ml-4 text-red-500">✕</button>
        </div>
      )}

      {/* Статистика */}
      {stats && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-3xl font-bold text-blue-600">{stats.repos_count}</div>
            <div className="text-gray-600">Репозиториев</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-3xl font-bold text-green-600">{stats.active_collaborators}</div>
            <div className="text-gray-600">AI Коллабораторов</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-3xl font-bold text-purple-600">{stats.active_projects}</div>
            <div className="text-gray-600">Активных проектов</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-3xl font-bold text-orange-600">{stats.pending_tasks}</div>
            <div className="text-gray-600">Задач в работе</div>
          </div>
        </div>
      )}

      {/* Табы */}
      <div className="flex space-x-4 mb-6">
        {['repos', 'collaborators', 'projects', 'sync'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as any)}
            className={`px-4 py-2 rounded-lg ${
              activeTab === tab
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {tab === 'repos' && '📁 Репозитории'}
            {tab === 'collaborators' && '🤖 AI Коллабораторы'}
            {tab === 'projects' && '📋 Проекты'}
            {tab === 'sync' && '🔄 Синхронизация'}
          </button>
        ))}
      </div>

      {/* Репозитории */}
      {activeTab === 'repos' && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Репозитории</h2>
            <button
              onClick={() => setShowRepoForm(true)}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              + Создать репозиторий
            </button>
          </div>

          {loading ? (
            <div className="text-center py-8">Загрузка...</div>
          ) : repos.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Нет репозиториев. Создайте первый или настройте GitHub токен.
            </div>
          ) : (
            <div className="space-y-4">
              {repos.map((repo) => (
                <div key={repo.full_name} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold text-lg">
                        <a href={repo.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                          {repo.full_name}
                        </a>
                        {repo.private && <span className="ml-2 text-xs bg-gray-200 px-2 py-1 rounded">Private</span>}
                      </h3>
                      <p className="text-gray-600">{repo.description || 'Нет описания'}</p>
                    </div>
                    <div className="text-sm text-gray-500">
                      Обновлён: {new Date(repo.updated_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* AI Коллабораторы */}
      {activeTab === 'collaborators' && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">AI Коллабораторы</h2>
            <button
              onClick={() => setShowCollaboratorForm(true)}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              + Добавить AI
            </button>
          </div>

          <p className="text-gray-600 mb-4">
            Добавляйте других AI-агентов для совместной работы над проектами через GitHub.
          </p>

          {collaborators.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Нет AI-коллабораторов. Добавьте первого для совместной работы.
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4">
              {collaborators.map((collab) => (
                <div key={collab.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold">{collab.name}</h3>
                      <p className="text-sm text-gray-600">@{collab.github_username}</p>
                      <div className="mt-2 flex flex-wrap gap-1">
                        {collab.capabilities.map((cap) => (
                          <span key={cap} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                            {cap}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`w-3 h-3 rounded-full ${collab.status === 'active' ? 'bg-green-500' : 'bg-gray-400'}`}></span>
                      <button
                        onClick={() => removeCollaborator(collab.id)}
                        className="text-red-500 hover:text-red-700"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Проекты */}
      {activeTab === 'projects' && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Совместные проекты</h2>
            <button
              onClick={() => setShowProjectForm(true)}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              + Создать проект
            </button>
          </div>

          {projects.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Нет проектов. Создайте первый для совместной работы с AI.
            </div>
          ) : (
            <div className="space-y-4">
              {projects.map((project) => (
                <div key={project.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-semibold text-lg">{project.name}</h3>
                      <p className="text-gray-600">{project.description}</p>
                      <p className="text-sm text-gray-500">Репозиторий: {project.repo_full_name}</p>
                    </div>
                    <span className={`px-2 py-1 rounded text-sm ${
                      project.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                    }`}>
                      {project.status}
                    </span>
                  </div>
                  
                  {project.tasks.length > 0 && (
                    <div className="mt-4">
                      <h4 className="font-medium mb-2">Задачи:</h4>
                      <div className="space-y-2">
                        {project.tasks.map((task) => (
                          <div key={task.id} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                            <div>
                              <span className="font-medium">{task.title}</span>
                              {task.assigned_to && (
                                <span className="ml-2 text-sm text-gray-500">→ {task.assigned_to}</span>
                              )}
                            </div>
                            <span className={`px-2 py-1 rounded text-xs ${
                              task.status === 'completed' ? 'bg-green-100 text-green-700' :
                              task.status === 'in_progress' ? 'bg-blue-100 text-blue-700' :
                              'bg-yellow-100 text-yellow-700'
                            }`}>
                              {task.status}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Синхронизация */}
      {activeTab === 'sync' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Синхронизация знаний</h2>
          
          <p className="text-gray-600 mb-4">
            Синхронизируйте базу знаний AI-агента с GitHub репозиторием для совместной работы с другими AI.
          </p>

          <div className="grid grid-cols-3 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Owner</label>
              <input
                type="text"
                value={syncForm.owner}
                onChange={(e) => setSyncForm({ ...syncForm, owner: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
                placeholder="username"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Repository</label>
              <input
                type="text"
                value={syncForm.repo}
                onChange={(e) => setSyncForm({ ...syncForm, repo: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
                placeholder="repo-name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Локальный путь</label>
              <input
                type="text"
                value={syncForm.local_path}
                onChange={(e) => setSyncForm({ ...syncForm, local_path: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
                placeholder="/home/ubuntu/seo_monster/backend/data/knowledge"
              />
            </div>
          </div>

          <div className="flex space-x-4">
            <button
              onClick={() => syncKnowledge('upload')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              ⬆️ Загрузить в GitHub
            </button>
            <button
              onClick={() => syncKnowledge('download')}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              ⬇️ Скачать из GitHub
            </button>
          </div>

          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-medium mb-2">Рекомендуемый путь для синхронизации:</h3>
            <code className="text-sm bg-gray-200 px-2 py-1 rounded">
              /home/ubuntu/seo_monster/backend/data/knowledge
            </code>
          </div>
        </div>
      )}

      {/* Модальные окна */}
      {showRepoForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Создать репозиторий</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Название</label>
                <input
                  type="text"
                  value={repoForm.name}
                  onChange={(e) => setRepoForm({ ...repoForm, name: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Описание</label>
                <textarea
                  value={repoForm.description}
                  onChange={(e) => setRepoForm({ ...repoForm, description: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  rows={3}
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={repoForm.private}
                  onChange={(e) => setRepoForm({ ...repoForm, private: e.target.checked })}
                  className="mr-2"
                />
                <label className="text-sm text-gray-700">Приватный репозиторий</label>
              </div>
            </div>
            <div className="flex justify-end space-x-4 mt-6">
              <button onClick={() => setShowRepoForm(false)} className="px-4 py-2 text-gray-600">
                Отмена
              </button>
              <button onClick={createRepo} className="px-4 py-2 bg-blue-600 text-white rounded-lg">
                Создать
              </button>
            </div>
          </div>
        </div>
      )}

      {showCollaboratorForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Добавить AI-коллаборатора</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ID</label>
                <input
                  type="text"
                  value={collaboratorForm.id}
                  onChange={(e) => setCollaboratorForm({ ...collaboratorForm, id: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="ai_agent_1"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Имя</label>
                <input
                  type="text"
                  value={collaboratorForm.name}
                  onChange={(e) => setCollaboratorForm({ ...collaboratorForm, name: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="Claude AI"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">GitHub Username</label>
                <input
                  type="text"
                  value={collaboratorForm.github_username}
                  onChange={(e) => setCollaboratorForm({ ...collaboratorForm, github_username: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="ai-assistant"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Возможности (через запятую)</label>
                <input
                  type="text"
                  value={collaboratorForm.capabilities}
                  onChange={(e) => setCollaboratorForm({ ...collaboratorForm, capabilities: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="coding, seo, content"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-4 mt-6">
              <button onClick={() => setShowCollaboratorForm(false)} className="px-4 py-2 text-gray-600">
                Отмена
              </button>
              <button onClick={addCollaborator} className="px-4 py-2 bg-blue-600 text-white rounded-lg">
                Добавить
              </button>
            </div>
          </div>
        </div>
      )}

      {showProjectForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Создать проект</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Название</label>
                <input
                  type="text"
                  value={projectForm.name}
                  onChange={(e) => setProjectForm({ ...projectForm, name: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Описание</label>
                <textarea
                  value={projectForm.description}
                  onChange={(e) => setProjectForm({ ...projectForm, description: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  rows={3}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Репозиторий (owner/repo)</label>
                <input
                  type="text"
                  value={projectForm.repo_full_name}
                  onChange={(e) => setProjectForm({ ...projectForm, repo_full_name: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="username/repo-name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ID коллабораторов (через запятую)</label>
                <input
                  type="text"
                  value={projectForm.collaborator_ids}
                  onChange={(e) => setProjectForm({ ...projectForm, collaborator_ids: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="ai_1, ai_2"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-4 mt-6">
              <button onClick={() => setShowProjectForm(false)} className="px-4 py-2 text-gray-600">
                Отмена
              </button>
              <button onClick={createProject} className="px-4 py-2 bg-blue-600 text-white rounded-lg">
                Создать
              </button>
            </div>
          </div>
        </div>
      )}

      {showTokenForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Настройка GitHub токена</h3>
            <p className="text-gray-600 mb-4">
              Создайте Personal Access Token на GitHub с правами repo и введите его здесь.
            </p>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">GitHub Token</label>
              <input
                type="password"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg"
                placeholder="ghp_xxxxxxxxxxxx"
              />
            </div>
            <div className="flex justify-end space-x-4 mt-6">
              <button onClick={() => setShowTokenForm(false)} className="px-4 py-2 text-gray-600">
                Отмена
              </button>
              <button onClick={setGitHubToken} className="px-4 py-2 bg-blue-600 text-white rounded-lg">
                Сохранить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GitHubManager;
