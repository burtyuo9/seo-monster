"""
GitHub Integration Module для SEO Monster
Позволяет AI-агентам совместно работать над проектами через GitHub
"""

import os
import json
import asyncio
import aiohttp
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
import base64


@dataclass
class GitHubRepo:
    """Репозиторий GitHub"""
    name: str
    full_name: str
    description: str
    url: str
    clone_url: str
    default_branch: str
    private: bool
    created_at: str
    updated_at: str


@dataclass
class GitHubFile:
    """Файл в репозитории"""
    path: str
    name: str
    sha: str
    size: int
    type: str  # file, dir
    content: Optional[str] = None


@dataclass
class GitHubCommit:
    """Коммит в репозитории"""
    sha: str
    message: str
    author: str
    date: str
    files_changed: int


@dataclass
class AICollaborator:
    """AI-коллаборатор для совместной работы"""
    id: str
    name: str
    github_username: str
    capabilities: List[str]
    status: str  # active, inactive
    last_activity: str


class GitHubIntegration:
    """Интеграция с GitHub для AI-агентов"""
    
    def __init__(self, token: str = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.data_dir = Path("/home/ubuntu/seo_monster/backend/data/github")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Файлы данных
        self.repos_file = self.data_dir / "repos.json"
        self.collaborators_file = self.data_dir / "collaborators.json"
        self.projects_file = self.data_dir / "projects.json"
        self.sync_log_file = self.data_dir / "sync_log.json"
        
        self._load_data()
    
    def _load_data(self):
        """Загрузка данных из файлов"""
        self.repos = self._load_json(self.repos_file, [])
        self.collaborators = self._load_json(self.collaborators_file, [])
        self.projects = self._load_json(self.projects_file, [])
        self.sync_log = self._load_json(self.sync_log_file, [])
    
    def _load_json(self, path: Path, default: Any) -> Any:
        """Загрузка JSON файла"""
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return default
    
    def _save_json(self, path: Path, data: Any):
        """Сохранение JSON файла"""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _get_headers(self) -> Dict[str, str]:
        """Получение заголовков для API запросов"""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "SEO-Monster-AI"
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers
    
    # ==================== РЕПОЗИТОРИИ ====================
    
    async def create_repo(
        self,
        name: str,
        description: str = "",
        private: bool = True,
        auto_init: bool = True
    ) -> Dict[str, Any]:
        """Создание нового репозитория"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/user/repos",
                headers=self._get_headers(),
                json={
                    "name": name,
                    "description": description,
                    "private": private,
                    "auto_init": auto_init
                }
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    repo = {
                        "name": data["name"],
                        "full_name": data["full_name"],
                        "description": data.get("description", ""),
                        "url": data["html_url"],
                        "clone_url": data["clone_url"],
                        "default_branch": data.get("default_branch", "main"),
                        "private": data["private"],
                        "created_at": datetime.now().isoformat()
                    }
                    self.repos.append(repo)
                    self._save_json(self.repos_file, self.repos)
                    return {"success": True, "repo": repo}
                else:
                    error = await response.text()
                    return {"success": False, "error": error}
    
    async def list_repos(self, username: str = None) -> List[Dict]:
        """Получение списка репозиториев"""
        url = f"{self.base_url}/user/repos" if not username else f"{self.base_url}/users/{username}/repos"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._get_headers()) as response:
                if response.status == 200:
                    repos = await response.json()
                    return [
                        {
                            "name": r["name"],
                            "full_name": r["full_name"],
                            "description": r.get("description", ""),
                            "url": r["html_url"],
                            "private": r["private"],
                            "updated_at": r["updated_at"]
                        }
                        for r in repos
                    ]
                return []
    
    async def get_repo(self, owner: str, repo: str) -> Optional[Dict]:
        """Получение информации о репозитории"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/repos/{owner}/{repo}",
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None
    
    async def delete_repo(self, owner: str, repo: str) -> bool:
        """Удаление репозитория"""
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.base_url}/repos/{owner}/{repo}",
                headers=self._get_headers()
            ) as response:
                return response.status == 204
    
    # ==================== ФАЙЛЫ ====================
    
    async def get_file(self, owner: str, repo: str, path: str, branch: str = "main") -> Optional[Dict]:
        """Получение содержимого файла"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/repos/{owner}/{repo}/contents/{path}",
                headers=self._get_headers(),
                params={"ref": branch}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("content"):
                        content = base64.b64decode(data["content"]).decode('utf-8')
                        return {
                            "path": data["path"],
                            "name": data["name"],
                            "sha": data["sha"],
                            "size": data["size"],
                            "content": content
                        }
                return None
    
    async def create_or_update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str = "main",
        sha: str = None
    ) -> Dict[str, Any]:
        """Создание или обновление файла"""
        # Получаем SHA если файл существует
        if not sha:
            existing = await self.get_file(owner, repo, path, branch)
            if existing:
                sha = existing["sha"]
        
        payload = {
            "message": message,
            "content": base64.b64encode(content.encode()).decode(),
            "branch": branch
        }
        if sha:
            payload["sha"] = sha
        
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{self.base_url}/repos/{owner}/{repo}/contents/{path}",
                headers=self._get_headers(),
                json=payload
            ) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    return {
                        "success": True,
                        "sha": data["content"]["sha"],
                        "url": data["content"]["html_url"]
                    }
                else:
                    error = await response.text()
                    return {"success": False, "error": error}
    
    async def delete_file(
        self,
        owner: str,
        repo: str,
        path: str,
        message: str,
        sha: str,
        branch: str = "main"
    ) -> bool:
        """Удаление файла"""
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.base_url}/repos/{owner}/{repo}/contents/{path}",
                headers=self._get_headers(),
                json={
                    "message": message,
                    "sha": sha,
                    "branch": branch
                }
            ) as response:
                return response.status == 200
    
    async def list_files(self, owner: str, repo: str, path: str = "", branch: str = "main") -> List[Dict]:
        """Получение списка файлов в директории"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/repos/{owner}/{repo}/contents/{path}",
                headers=self._get_headers(),
                params={"ref": branch}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        return [
                            {
                                "path": f["path"],
                                "name": f["name"],
                                "type": f["type"],
                                "size": f.get("size", 0),
                                "sha": f["sha"]
                            }
                            for f in data
                        ]
                return []
    
    # ==================== КОММИТЫ ====================
    
    async def get_commits(self, owner: str, repo: str, branch: str = "main", limit: int = 30) -> List[Dict]:
        """Получение истории коммитов"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/repos/{owner}/{repo}/commits",
                headers=self._get_headers(),
                params={"sha": branch, "per_page": limit}
            ) as response:
                if response.status == 200:
                    commits = await response.json()
                    return [
                        {
                            "sha": c["sha"][:7],
                            "full_sha": c["sha"],
                            "message": c["commit"]["message"],
                            "author": c["commit"]["author"]["name"],
                            "date": c["commit"]["author"]["date"]
                        }
                        for c in commits
                    ]
                return []
    
    # ==================== ВЕТКИ ====================
    
    async def list_branches(self, owner: str, repo: str) -> List[Dict]:
        """Получение списка веток"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/repos/{owner}/{repo}/branches",
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    branches = await response.json()
                    return [
                        {
                            "name": b["name"],
                            "sha": b["commit"]["sha"][:7],
                            "protected": b.get("protected", False)
                        }
                        for b in branches
                    ]
                return []
    
    async def create_branch(self, owner: str, repo: str, branch_name: str, from_branch: str = "main") -> Dict:
        """Создание новой ветки"""
        # Получаем SHA исходной ветки
        branches = await self.list_branches(owner, repo)
        source_sha = None
        for b in branches:
            if b["name"] == from_branch:
                # Получаем полный SHA
                commits = await self.get_commits(owner, repo, from_branch, 1)
                if commits:
                    source_sha = commits[0]["full_sha"]
                break
        
        if not source_sha:
            return {"success": False, "error": "Source branch not found"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/repos/{owner}/{repo}/git/refs",
                headers=self._get_headers(),
                json={
                    "ref": f"refs/heads/{branch_name}",
                    "sha": source_sha
                }
            ) as response:
                if response.status == 201:
                    return {"success": True, "branch": branch_name}
                else:
                    error = await response.text()
                    return {"success": False, "error": error}
    
    # ==================== PULL REQUESTS ====================
    
    async def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str = "main"
    ) -> Dict:
        """Создание Pull Request"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/repos/{owner}/{repo}/pulls",
                headers=self._get_headers(),
                json={
                    "title": title,
                    "body": body,
                    "head": head,
                    "base": base
                }
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    return {
                        "success": True,
                        "number": data["number"],
                        "url": data["html_url"]
                    }
                else:
                    error = await response.text()
                    return {"success": False, "error": error}
    
    async def list_pull_requests(self, owner: str, repo: str, state: str = "open") -> List[Dict]:
        """Получение списка Pull Requests"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/repos/{owner}/{repo}/pulls",
                headers=self._get_headers(),
                params={"state": state}
            ) as response:
                if response.status == 200:
                    prs = await response.json()
                    return [
                        {
                            "number": pr["number"],
                            "title": pr["title"],
                            "state": pr["state"],
                            "author": pr["user"]["login"],
                            "created_at": pr["created_at"],
                            "url": pr["html_url"]
                        }
                        for pr in prs
                    ]
                return []
    
    # ==================== AI КОЛЛАБОРАЦИЯ ====================
    
    def add_collaborator(
        self,
        collaborator_id: str,
        name: str,
        github_username: str,
        capabilities: List[str]
    ) -> Dict:
        """Добавление AI-коллаборатора"""
        collaborator = {
            "id": collaborator_id,
            "name": name,
            "github_username": github_username,
            "capabilities": capabilities,
            "status": "active",
            "last_activity": datetime.now().isoformat(),
            "added_at": datetime.now().isoformat()
        }
        
        # Проверяем, не существует ли уже
        for i, c in enumerate(self.collaborators):
            if c["id"] == collaborator_id:
                self.collaborators[i] = collaborator
                self._save_json(self.collaborators_file, self.collaborators)
                return {"success": True, "action": "updated", "collaborator": collaborator}
        
        self.collaborators.append(collaborator)
        self._save_json(self.collaborators_file, self.collaborators)
        return {"success": True, "action": "added", "collaborator": collaborator}
    
    def remove_collaborator(self, collaborator_id: str) -> bool:
        """Удаление AI-коллаборатора"""
        for i, c in enumerate(self.collaborators):
            if c["id"] == collaborator_id:
                del self.collaborators[i]
                self._save_json(self.collaborators_file, self.collaborators)
                return True
        return False
    
    def list_collaborators(self) -> List[Dict]:
        """Получение списка AI-коллабораторов"""
        return self.collaborators
    
    def get_collaborator(self, collaborator_id: str) -> Optional[Dict]:
        """Получение информации о коллабораторе"""
        for c in self.collaborators:
            if c["id"] == collaborator_id:
                return c
        return None
    
    # ==================== ПРОЕКТЫ ====================
    
    def create_project(
        self,
        name: str,
        description: str,
        repo_full_name: str,
        collaborator_ids: List[str] = None
    ) -> Dict:
        """Создание совместного проекта"""
        project = {
            "id": f"project_{len(self.projects) + 1}",
            "name": name,
            "description": description,
            "repo_full_name": repo_full_name,
            "collaborators": collaborator_ids or [],
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "tasks": []
        }
        
        self.projects.append(project)
        self._save_json(self.projects_file, self.projects)
        return {"success": True, "project": project}
    
    def add_task_to_project(
        self,
        project_id: str,
        task_title: str,
        task_description: str,
        assigned_to: str = None
    ) -> Dict:
        """Добавление задачи в проект"""
        for i, p in enumerate(self.projects):
            if p["id"] == project_id:
                task = {
                    "id": f"task_{len(p['tasks']) + 1}",
                    "title": task_title,
                    "description": task_description,
                    "assigned_to": assigned_to,
                    "status": "pending",
                    "created_at": datetime.now().isoformat()
                }
                self.projects[i]["tasks"].append(task)
                self.projects[i]["updated_at"] = datetime.now().isoformat()
                self._save_json(self.projects_file, self.projects)
                return {"success": True, "task": task}
        
        return {"success": False, "error": "Project not found"}
    
    def update_task_status(self, project_id: str, task_id: str, status: str) -> bool:
        """Обновление статуса задачи"""
        for i, p in enumerate(self.projects):
            if p["id"] == project_id:
                for j, t in enumerate(p["tasks"]):
                    if t["id"] == task_id:
                        self.projects[i]["tasks"][j]["status"] = status
                        self.projects[i]["updated_at"] = datetime.now().isoformat()
                        self._save_json(self.projects_file, self.projects)
                        return True
        return False
    
    def list_projects(self) -> List[Dict]:
        """Получение списка проектов"""
        return self.projects
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Получение информации о проекте"""
        for p in self.projects:
            if p["id"] == project_id:
                return p
        return None
    
    # ==================== СИНХРОНИЗАЦИЯ ====================
    
    async def sync_knowledge(self, owner: str, repo: str, local_path: str) -> Dict:
        """Синхронизация базы знаний с репозиторием"""
        results = {
            "uploaded": [],
            "downloaded": [],
            "errors": []
        }
        
        local_dir = Path(local_path)
        if not local_dir.exists():
            return {"success": False, "error": "Local path does not exist"}
        
        # Загружаем локальные файлы в репозиторий
        for file_path in local_dir.glob("**/*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                relative_path = file_path.relative_to(local_dir)
                content = file_path.read_text(encoding='utf-8')
                
                result = await self.create_or_update_file(
                    owner, repo,
                    str(relative_path),
                    content,
                    f"Sync: Update {relative_path}"
                )
                
                if result["success"]:
                    results["uploaded"].append(str(relative_path))
                else:
                    results["errors"].append({
                        "file": str(relative_path),
                        "error": result.get("error", "Unknown error")
                    })
        
        # Логируем синхронизацию
        sync_entry = {
            "timestamp": datetime.now().isoformat(),
            "repo": f"{owner}/{repo}",
            "local_path": local_path,
            "results": results
        }
        self.sync_log.append(sync_entry)
        self._save_json(self.sync_log_file, self.sync_log[-100:])  # Храним последние 100
        
        return {"success": True, "results": results}
    
    async def download_knowledge(self, owner: str, repo: str, local_path: str, path: str = "") -> Dict:
        """Скачивание файлов из репозитория"""
        results = {
            "downloaded": [],
            "errors": []
        }
        
        local_dir = Path(local_path)
        local_dir.mkdir(parents=True, exist_ok=True)
        
        files = await self.list_files(owner, repo, path)
        
        for file_info in files:
            if file_info["type"] == "file":
                file_data = await self.get_file(owner, repo, file_info["path"])
                if file_data and file_data.get("content"):
                    file_path = local_dir / file_info["path"]
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(file_data["content"], encoding='utf-8')
                    results["downloaded"].append(file_info["path"])
                else:
                    results["errors"].append({
                        "file": file_info["path"],
                        "error": "Could not download"
                    })
            elif file_info["type"] == "dir":
                # Рекурсивно скачиваем директории
                sub_results = await self.download_knowledge(
                    owner, repo, local_path, file_info["path"]
                )
                results["downloaded"].extend(sub_results.get("downloaded", []))
                results["errors"].extend(sub_results.get("errors", []))
        
        return results
    
    # ==================== ЛОКАЛЬНЫЙ GIT ====================
    
    def clone_repo(self, clone_url: str, local_path: str) -> Dict:
        """Клонирование репозитория локально"""
        try:
            result = subprocess.run(
                ["git", "clone", clone_url, local_path],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return {"success": True, "path": local_path}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def git_pull(self, repo_path: str) -> Dict:
        """Pull изменений из удалённого репозитория"""
        try:
            result = subprocess.run(
                ["git", "pull"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def git_push(self, repo_path: str, message: str = "Auto commit") -> Dict:
        """Commit и push изменений"""
        try:
            # Add all changes
            subprocess.run(["git", "add", "-A"], cwd=repo_path, capture_output=True)
            
            # Commit
            commit_result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            # Push
            push_result = subprocess.run(
                ["git", "push"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            return {
                "success": push_result.returncode == 0,
                "commit_output": commit_result.stdout,
                "push_output": push_result.stdout,
                "error": push_result.stderr if push_result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== СТАТИСТИКА ====================
    
    def get_stats(self) -> Dict:
        """Получение статистики интеграции"""
        return {
            "repos_count": len(self.repos),
            "collaborators_count": len(self.collaborators),
            "active_collaborators": len([c for c in self.collaborators if c["status"] == "active"]),
            "projects_count": len(self.projects),
            "active_projects": len([p for p in self.projects if p["status"] == "active"]),
            "total_tasks": sum(len(p.get("tasks", [])) for p in self.projects),
            "pending_tasks": sum(
                len([t for t in p.get("tasks", []) if t["status"] == "pending"])
                for p in self.projects
            ),
            "sync_operations": len(self.sync_log),
            "last_sync": self.sync_log[-1]["timestamp"] if self.sync_log else None
        }


# Глобальный экземпляр
github_integration = GitHubIntegration()
