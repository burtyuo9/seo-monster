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
