"""
API роуты для GitHub Integration
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
sys.path.append('/home/ubuntu/seo_monster/backend')

from services.github_integration import github_integration

router = APIRouter(prefix="/api/github", tags=["GitHub Integration"])


# ==================== МОДЕЛИ ====================

class CreateRepoRequest(BaseModel):
    name: str
    description: str = ""
    private: bool = True


class FileRequest(BaseModel):
    owner: str
    repo: str
    path: str
    content: str
    message: str
    branch: str = "main"


class BranchRequest(BaseModel):
    owner: str
    repo: str
    branch_name: str
    from_branch: str = "main"


class PullRequestRequest(BaseModel):
    owner: str
    repo: str
    title: str
    body: str
    head: str
    base: str = "main"


class CollaboratorRequest(BaseModel):
    id: str
    name: str
    github_username: str
    capabilities: List[str]


class ProjectRequest(BaseModel):
    name: str
    description: str
    repo_full_name: str
    collaborator_ids: List[str] = []


class TaskRequest(BaseModel):
    project_id: str
    title: str
    description: str
    assigned_to: Optional[str] = None


class SyncRequest(BaseModel):
    owner: str
    repo: str
    local_path: str


class SetTokenRequest(BaseModel):
    token: str


# ==================== РЕПОЗИТОРИИ ====================

@router.post("/repos")
async def create_repository(request: CreateRepoRequest):
    """Создание нового репозитория"""
    result = await github_integration.create_repo(
        request.name,
        request.description,
        request.private
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.get("/repos")
async def list_repositories(username: Optional[str] = None):
    """Получение списка репозиториев"""
    repos = await github_integration.list_repos(username)
    return {"repos": repos}


@router.get("/repos/{owner}/{repo}")
async def get_repository(owner: str, repo: str):
    """Получение информации о репозитории"""
    result = await github_integration.get_repo(owner, repo)
    if not result:
        raise HTTPException(status_code=404, detail="Repository not found")
    return result


@router.delete("/repos/{owner}/{repo}")
async def delete_repository(owner: str, repo: str):
    """Удаление репозитория"""
    success = await github_integration.delete_repo(owner, repo)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete repository")
    return {"success": True}


# ==================== ФАЙЛЫ ====================

@router.get("/files/{owner}/{repo}")
async def list_files(owner: str, repo: str, path: str = "", branch: str = "main"):
    """Получение списка файлов в репозитории"""
    files = await github_integration.list_files(owner, repo, path, branch)
    return {"files": files}


@router.get("/files/{owner}/{repo}/content")
async def get_file_content(owner: str, repo: str, path: str, branch: str = "main"):
    """Получение содержимого файла"""
    result = await github_integration.get_file(owner, repo, path, branch)
    if not result:
        raise HTTPException(status_code=404, detail="File not found")
    return result


@router.post("/files")
async def create_or_update_file(request: FileRequest):
    """Создание или обновление файла"""
    result = await github_integration.create_or_update_file(
        request.owner,
        request.repo,
        request.path,
        request.content,
        request.message,
        request.branch
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


# ==================== ВЕТКИ ====================

@router.get("/branches/{owner}/{repo}")
async def list_branches(owner: str, repo: str):
    """Получение списка веток"""
    branches = await github_integration.list_branches(owner, repo)
    return {"branches": branches}


@router.post("/branches")
async def create_branch(request: BranchRequest):
    """Создание новой ветки"""
    result = await github_integration.create_branch(
        request.owner,
        request.repo,
        request.branch_name,
        request.from_branch
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


# ==================== КОММИТЫ ====================

@router.get("/commits/{owner}/{repo}")
async def get_commits(owner: str, repo: str, branch: str = "main", limit: int = 30):
    """Получение истории коммитов"""
    commits = await github_integration.get_commits(owner, repo, branch, limit)
    return {"commits": commits}


# ==================== PULL REQUESTS ====================

@router.get("/pulls/{owner}/{repo}")
async def list_pull_requests(owner: str, repo: str, state: str = "open"):
    """Получение списка Pull Requests"""
    prs = await github_integration.list_pull_requests(owner, repo, state)
    return {"pull_requests": prs}


@router.post("/pulls")
async def create_pull_request(request: PullRequestRequest):
    """Создание Pull Request"""
    result = await github_integration.create_pull_request(
        request.owner,
        request.repo,
        request.title,
        request.body,
        request.head,
        request.base
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


# ==================== AI КОЛЛАБОРАЦИЯ ====================

@router.get("/collaborators")
async def list_collaborators():
    """Получение списка AI-коллабораторов"""
    return {"collaborators": github_integration.list_collaborators()}


@router.post("/collaborators")
async def add_collaborator(request: CollaboratorRequest):
    """Добавление AI-коллаборатора"""
    result = github_integration.add_collaborator(
        request.id,
        request.name,
        request.github_username,
        request.capabilities
    )
    return result


@router.delete("/collaborators/{collaborator_id}")
async def remove_collaborator(collaborator_id: str):
    """Удаление AI-коллаборатора"""
    success = github_integration.remove_collaborator(collaborator_id)
    if not success:
        raise HTTPException(status_code=404, detail="Collaborator not found")
    return {"success": True}


@router.get("/collaborators/{collaborator_id}")
async def get_collaborator(collaborator_id: str):
    """Получение информации о коллабораторе"""
    collaborator = github_integration.get_collaborator(collaborator_id)
    if not collaborator:
        raise HTTPException(status_code=404, detail="Collaborator not found")
    return collaborator


# ==================== ПРОЕКТЫ ====================

@router.get("/projects")
async def list_projects():
    """Получение списка проектов"""
    return {"projects": github_integration.list_projects()}


@router.post("/projects")
async def create_project(request: ProjectRequest):
    """Создание совместного проекта"""
    result = github_integration.create_project(
        request.name,
        request.description,
        request.repo_full_name,
        request.collaborator_ids
    )
    return result


@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Получение информации о проекте"""
    project = github_integration.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/projects/tasks")
async def add_task(request: TaskRequest):
    """Добавление задачи в проект"""
    result = github_integration.add_task_to_project(
        request.project_id,
        request.title,
        request.description,
        request.assigned_to
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.put("/projects/{project_id}/tasks/{task_id}")
async def update_task(project_id: str, task_id: str, status: str):
    """Обновление статуса задачи"""
    success = github_integration.update_task_status(project_id, task_id, status)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True}


# ==================== СИНХРОНИЗАЦИЯ ====================

@router.post("/sync/upload")
async def sync_knowledge_upload(request: SyncRequest):
    """Синхронизация локальных файлов с репозиторием"""
    result = await github_integration.sync_knowledge(
        request.owner,
        request.repo,
        request.local_path
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.post("/sync/download")
async def sync_knowledge_download(request: SyncRequest):
    """Скачивание файлов из репозитория"""
    result = await github_integration.download_knowledge(
        request.owner,
        request.repo,
        request.local_path
    )
    return result


# ==================== НАСТРОЙКИ ====================

@router.post("/token")
async def set_github_token(request: SetTokenRequest):
    """Установка GitHub токена"""
    github_integration.token = request.token
    return {"success": True, "message": "Token updated"}


@router.get("/stats")
async def get_stats():
    """Получение статистики интеграции"""
    return github_integration.get_stats()
