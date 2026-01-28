"""
Publishing Routes - API endpoints for publishing articles to MANUS.im subdomains
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json
import os

# Import landing generator
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.landing_generator import landing_generator

router = APIRouter(prefix="/api/publishing", tags=["Publishing"])

# In-memory storage for published landings (in production, use database)
published_landings = []


class PublishRequest(BaseModel):
    """Request model for publishing an article"""
    title: str
    content: str
    language: str = "ru"
    style: str = "glassmorphism_dark"
    keywords: Optional[List[str]] = None
    author: str = "SEO Monster"
    meta_description: Optional[str] = None


class PublishResponse(BaseModel):
    """Response model for published landing"""
    success: bool
    slug: str
    url: str
    preview_url: str
    title: str
    meta_description: str
    word_count: int
    generated_at: str
    message: str


class PublishedLanding(BaseModel):
    """Model for a published landing page"""
    id: str
    slug: str
    url: str
    title: str
    meta_description: str
    language: str
    style: str
    word_count: int
    created_at: str
    status: str  # draft, published, archived


@router.post("/generate-landing", response_model=dict)
async def generate_landing(request: PublishRequest):
    """
    Generate HTML landing page from article content
    Returns the generated HTML and metadata without publishing
    """
    try:
        result = landing_generator.generate_landing(
            title=request.title,
            content=request.content,
            language=request.language,
            style=request.style,
            keywords=request.keywords,
            author=request.author,
            meta_description=request.meta_description
        )
        
        return {
            "success": True,
            "html": result["html"],
            "slug": result["slug"],
            "title": result["title"],
            "meta_description": result["meta_description"],
            "word_count": result["word_count"],
            "generated_at": result["generated_at"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate landing: {str(e)}")


@router.post("/publish", response_model=PublishResponse)
async def publish_landing(request: PublishRequest):
    """
    Generate and publish landing page to MANUS.im subdomain
    
    This endpoint:
    1. Generates SEO-optimized HTML from article content
    2. Creates a unique subdomain slug
    3. Stores the landing for deployment
    4. Returns the URL for the published page
    
    Note: Actual deployment to MANUS.im requires the Manus publish API
    which is triggered from the frontend after this endpoint returns
    """
    try:
        # Generate the landing page
        result = landing_generator.generate_landing(
            title=request.title,
            content=request.content,
            language=request.language,
            style=request.style,
            keywords=request.keywords,
            author=request.author,
            meta_description=request.meta_description
        )
        
        # Create landing record
        landing_id = f"landing_{len(published_landings) + 1}_{result['slug'][:20]}"
        
        landing_record = {
            "id": landing_id,
            "slug": result["slug"],
            "url": f"https://{result['slug']}.manus.space",
            "preview_url": f"/api/publishing/preview/{result['slug']}",
            "title": result["title"],
            "content": request.content,
            "html": result["html"],
            "meta_description": result["meta_description"],
            "keywords": result["keywords"],
            "language": result["language"],
            "style": result["style"],
            "word_count": result["word_count"],
            "author": request.author,
            "created_at": datetime.utcnow().isoformat(),
            "status": "ready_to_publish"
        }
        
        # Store landing
        published_landings.append(landing_record)
        
        # Save HTML to file for deployment
        landings_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "landings")
        os.makedirs(landings_dir, exist_ok=True)
        
        html_path = os.path.join(landings_dir, f"{result['slug']}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(result["html"])
        
        # Save metadata
        meta_path = os.path.join(landings_dir, f"{result['slug']}.json")
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump({
                "id": landing_id,
                "slug": result["slug"],
                "title": result["title"],
                "meta_description": result["meta_description"],
                "keywords": result["keywords"],
                "language": result["language"],
                "word_count": result["word_count"],
                "created_at": landing_record["created_at"]
            }, f, ensure_ascii=False, indent=2)
        
        return PublishResponse(
            success=True,
            slug=result["slug"],
            url=f"https://{result['slug']}.manus.space",
            preview_url=f"/api/publishing/preview/{result['slug']}",
            title=result["title"],
            meta_description=result["meta_description"],
            word_count=result["word_count"],
            generated_at=result["generated_at"],
            message="Landing page generated successfully. Ready for deployment to MANUS.im"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish landing: {str(e)}")


@router.get("/preview/{slug}")
async def preview_landing(slug: str):
    """
    Preview a generated landing page by slug
    Returns the HTML content for preview
    """
    # Find landing by slug
    landing = next((l for l in published_landings if l["slug"] == slug), None)
    
    if not landing:
        # Try to load from file
        landings_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "landings")
        html_path = os.path.join(landings_dir, f"{slug}.html")
        
        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            from fastapi.responses import HTMLResponse
            return HTMLResponse(content=html_content)
        
        raise HTTPException(status_code=404, detail="Landing not found")
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=landing["html"])


@router.get("/list", response_model=List[dict])
async def list_landings():
    """
    List all generated landing pages
    """
    # Get from memory
    landings = []
    for l in published_landings:
        landings.append({
            "id": l["id"],
            "slug": l["slug"],
            "url": l["url"],
            "title": l["title"],
            "language": l["language"],
            "word_count": l["word_count"],
            "created_at": l["created_at"],
            "status": l["status"]
        })
    
    # Also check landings directory
    landings_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "landings")
    if os.path.exists(landings_dir):
        for filename in os.listdir(landings_dir):
            if filename.endswith('.json'):
                slug = filename[:-5]
                if not any(l["slug"] == slug for l in landings):
                    meta_path = os.path.join(landings_dir, filename)
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        meta = json.load(f)
                    landings.append({
                        "id": meta.get("id", slug),
                        "slug": slug,
                        "url": f"https://{slug}.manus.space",
                        "title": meta.get("title", "Unknown"),
                        "language": meta.get("language", "ru"),
                        "word_count": meta.get("word_count", 0),
                        "created_at": meta.get("created_at", ""),
                        "status": "saved"
                    })
    
    return landings


@router.delete("/{slug}")
async def delete_landing(slug: str):
    """
    Delete a landing page by slug
    """
    global published_landings
    
    # Remove from memory
    published_landings = [l for l in published_landings if l["slug"] != slug]
    
    # Remove files
    landings_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "landings")
    html_path = os.path.join(landings_dir, f"{slug}.html")
    meta_path = os.path.join(landings_dir, f"{slug}.json")
    
    if os.path.exists(html_path):
        os.remove(html_path)
    if os.path.exists(meta_path):
        os.remove(meta_path)
    
    return {"success": True, "message": f"Landing {slug} deleted"}


@router.get("/styles")
async def get_available_styles():
    """
    Get list of available landing page styles
    """
    return {
        "styles": [
            {
                "id": "glassmorphism_dark",
                "name": "Glassmorphism Dark",
                "description": "Modern dark theme with frosted glass effects"
            },
            {
                "id": "minimal_light",
                "name": "Minimal Light",
                "description": "Clean, minimal light theme"
            },
            {
                "id": "tech_modern",
                "name": "Tech Modern",
                "description": "Modern tech-focused design"
            }
        ]
    }


# === Manus Integration Endpoints ===

@router.get("/pending")
async def get_pending_landings():
    """
    Get all landings pending publication to MANUS.space
    This endpoint is called by Manus Scheduled Task to fetch content for publishing
    
    Returns:
        List of landings with status 'ready_to_publish' including full HTML content
    """
    pending = []
    
    # Check in-memory landings
    for landing in published_landings:
        if landing.get("status") == "ready_to_publish":
            pending.append({
                "id": landing["id"],
                "slug": landing["slug"],
                "title": landing["title"],
                "html": landing["html"],
                "meta_description": landing["meta_description"],
                "keywords": landing.get("keywords", []),
                "language": landing["language"],
                "word_count": landing["word_count"],
                "created_at": landing["created_at"]
            })
    
    # Also check landings directory for saved but not published
    landings_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "landings")
    if os.path.exists(landings_dir):
        for filename in os.listdir(landings_dir):
            if filename.endswith('.json'):
                slug = filename[:-5]
                # Skip if already in pending list
                if any(p["slug"] == slug for p in pending):
                    continue
                
                meta_path = os.path.join(landings_dir, filename)
                html_path = os.path.join(landings_dir, f"{slug}.html")
                
                if os.path.exists(html_path):
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        meta = json.load(f)
                    with open(html_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    # Check if not yet published (no published_at field)
                    if not meta.get("published_at"):
                        pending.append({
                            "id": meta.get("id", slug),
                            "slug": slug,
                            "title": meta.get("title", "Unknown"),
                            "html": html_content,
                            "meta_description": meta.get("meta_description", ""),
                            "keywords": meta.get("keywords", []),
                            "language": meta.get("language", "en"),
                            "word_count": meta.get("word_count", 0),
                            "created_at": meta.get("created_at", "")
                        })
    
    return {
        "count": len(pending),
        "landings": pending
    }


@router.post("/mark-published/{slug}")
async def mark_as_published(slug: str, published_url: str = None):
    """
    Mark a landing as published after Manus successfully deploys it
    
    Args:
        slug: The landing slug
        published_url: The actual published URL on MANUS.space
    """
    global published_landings
    
    # Update in-memory
    for landing in published_landings:
        if landing["slug"] == slug:
            landing["status"] = "published"
            landing["published_at"] = datetime.utcnow().isoformat()
            if published_url:
                landing["published_url"] = published_url
            break
    
    # Update in file
    landings_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "landings")
    meta_path = os.path.join(landings_dir, f"{slug}.json")
    
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        meta["status"] = "published"
        meta["published_at"] = datetime.utcnow().isoformat()
        if published_url:
            meta["published_url"] = published_url
        
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
    
    return {
        "success": True,
        "slug": slug,
        "status": "published",
        "published_url": published_url
    }


@router.get("/stats")
async def get_publishing_stats():
    """
    Get publishing statistics for dashboard
    """
    total = 0
    published = 0
    pending = 0
    
    # Count in-memory
    for landing in published_landings:
        total += 1
        if landing.get("status") == "published":
            published += 1
        elif landing.get("status") == "ready_to_publish":
            pending += 1
    
    # Count in files
    landings_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "landings")
    if os.path.exists(landings_dir):
        for filename in os.listdir(landings_dir):
            if filename.endswith('.json'):
                slug = filename[:-5]
                # Skip if already counted
                if any(l["slug"] == slug for l in published_landings):
                    continue
                
                total += 1
                meta_path = os.path.join(landings_dir, filename)
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                
                if meta.get("published_at"):
                    published += 1
                else:
                    pending += 1
    
    return {
        "total": total,
        "published": published,
        "pending": pending,
        "success_rate": round(published / total * 100, 1) if total > 0 else 0
    }
