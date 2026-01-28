"""
Landing Page Generator Service
Generates SEO-optimized HTML landing pages from articles for publishing on MANUS.im subdomains
"""

import re
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
import json


class LandingGenerator:
    """Generates SEO-optimized HTML landing pages from articles"""
    
    def __init__(self):
        self.template_styles = {
            "glassmorphism_dark": self._get_glassmorphism_dark_template,
            "minimal_light": self._get_minimal_light_template,
            "tech_modern": self._get_tech_modern_template,
        }
    
    def generate_landing(
        self,
        title: str,
        content: str,
        language: str = "ru",
        style: str = "glassmorphism_dark",
        keywords: Optional[list] = None,
        author: str = "SEO Monster",
        meta_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete HTML landing page from article content
        
        Args:
            title: Article title
            content: Article content (can be markdown or plain text)
            language: Language code (ru, en, etc.)
            style: Template style to use
            keywords: SEO keywords
            author: Author name
            meta_description: Custom meta description
            
        Returns:
            Dict with html, slug, metadata
        """
        # Generate slug from title
        slug = self._generate_slug(title)
        
        # Parse content into sections
        sections = self._parse_content(content)
        
        # Generate meta description if not provided
        if not meta_description:
            meta_description = self._generate_meta_description(content)
        
        # Get template generator
        template_fn = self.template_styles.get(style, self._get_glassmorphism_dark_template)
        
        # Generate HTML
        html = template_fn(
            title=title,
            sections=sections,
            language=language,
            keywords=keywords or [],
            author=author,
            meta_description=meta_description,
            slug=slug
        )
        
        return {
            "html": html,
            "slug": slug,
            "title": title,
            "meta_description": meta_description,
            "keywords": keywords or [],
            "language": language,
            "style": style,
            "generated_at": datetime.utcnow().isoformat(),
            "word_count": len(content.split())
        }
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        # Transliterate Russian to Latin
        translit_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
        }
        
        slug = title.lower()
        for ru, en in translit_map.items():
            slug = slug.replace(ru, en)
        
        # Remove special characters and replace spaces with hyphens
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        
        # Add unique hash suffix
        hash_suffix = hashlib.md5(f"{title}{datetime.utcnow().timestamp()}".encode()).hexdigest()[:6]
        
        return f"{slug[:50]}-{hash_suffix}"
    
    def _parse_content(self, content: str) -> list:
        """Parse content into sections for landing page"""
        sections = []
        
        # Split by headers (## or ###)
        parts = re.split(r'\n(#{2,3})\s+(.+)\n', content)
        
        if len(parts) == 1:
            # No headers found, treat as single section
            sections.append({
                "type": "intro",
                "title": None,
                "content": content.strip()
            })
        else:
            # First part is intro
            if parts[0].strip():
                sections.append({
                    "type": "intro",
                    "title": None,
                    "content": parts[0].strip()
                })
            
            # Process header sections
            i = 1
            while i < len(parts) - 2:
                header_level = parts[i]
                header_title = parts[i + 1]
                header_content = parts[i + 2] if i + 2 < len(parts) else ""
                
                sections.append({
                    "type": "section",
                    "level": len(header_level),
                    "title": header_title.strip(),
                    "content": header_content.strip()
                })
                i += 3
        
        return sections
    
    def _generate_meta_description(self, content: str, max_length: int = 160) -> str:
        """Generate meta description from content"""
        # Remove markdown formatting
        clean = re.sub(r'[#*_`\[\]]', '', content)
        clean = re.sub(r'\n+', ' ', clean)
        clean = clean.strip()
        
        if len(clean) <= max_length:
            return clean
        
        # Truncate at word boundary
        truncated = clean[:max_length]
        last_space = truncated.rfind(' ')
        if last_space > max_length - 30:
            truncated = truncated[:last_space]
        
        return truncated + "..."
    
    def _get_glassmorphism_dark_template(
        self,
        title: str,
        sections: list,
        language: str,
        keywords: list,
        author: str,
        meta_description: str,
        slug: str
    ) -> str:
        """Generate glassmorphism dark theme landing page"""
        
        keywords_meta = ", ".join(keywords) if keywords else title
        
        # Generate sections HTML
        sections_html = ""
        for i, section in enumerate(sections):
            if section["type"] == "intro":
                sections_html += f'''
                <section class="py-12">
                    <div class="glass-card p-8">
                        <p class="text-lg text-gray-300 leading-relaxed">{self._format_content(section["content"])}</p>
                    </div>
                </section>
                '''
            else:
                sections_html += f'''
                <section class="py-8">
                    <h2 class="text-2xl md:text-3xl font-bold text-white mb-6">{section["title"]}</h2>
                    <div class="glass-card p-6">
                        <div class="text-gray-300 leading-relaxed">{self._format_content(section["content"])}</div>
                    </div>
                </section>
                '''
        
        html = f'''<!DOCTYPE html>
<html lang="{language}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_description}">
    <meta name="keywords" content="{keywords_meta}">
    <meta name="author" content="{author}">
    <meta name="robots" content="index, follow">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta_description}">
    <meta property="og:type" content="article">
    <link rel="canonical" href="https://{slug}.manus.space/">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', system-ui, sans-serif;
            background: linear-gradient(135deg, #0a0f1a 0%, #0f1629 50%, #1a1f2e 100%);
            color: #e5e7eb;
            min-height: 100vh;
            line-height: 1.7;
        }}
        h1, h2, h3, h4, h5, h6 {{ font-family: 'Space Grotesk', system-ui, sans-serif; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 0 1.5rem; }}
        .glass-card {{
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 1.5rem;
        }}
        .gradient-text {{
            background: linear-gradient(135deg, #00d4ff, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .glow {{ box-shadow: 0 0 40px rgba(0, 212, 255, 0.2); }}
        header {{ padding: 2rem 0; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        .hero {{ padding: 4rem 0; text-align: center; }}
        .hero h1 {{ font-size: clamp(2rem, 5vw, 3.5rem); margin-bottom: 1.5rem; }}
        .hero .meta {{ color: #9ca3af; font-size: 0.9rem; }}
        footer {{ padding: 3rem 0; border-top: 1px solid rgba(255,255,255,0.1); text-align: center; color: #6b7280; }}
        p {{ margin-bottom: 1rem; }}
        ul, ol {{ margin: 1rem 0; padding-left: 1.5rem; }}
        li {{ margin-bottom: 0.5rem; }}
        a {{ color: #00d4ff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        @media (max-width: 640px) {{
            .container {{ padding: 0 1rem; }}
            .glass-card {{ padding: 1.5rem !important; border-radius: 1rem; }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <a href="/" style="display: flex; align-items: center; gap: 0.75rem; text-decoration: none;">
                <div style="width: 40px; height: 40px; border-radius: 12px; background: linear-gradient(135deg, #00d4ff, #a855f7); display: flex; align-items: center; justify-content: center;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                        <path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z"/>
                        <path d="M5 19l1 3 3-1-1-3-3 1z"/>
                        <path d="M19 19l-1 3-3-1 1-3 3 1z"/>
                    </svg>
                </div>
                <span style="font-size: 1.25rem; font-weight: 600; color: white;">SEO Monster</span>
            </a>
        </div>
    </header>

    <main class="container">
        <div class="hero">
            <h1 class="gradient-text">{title}</h1>
            <p class="meta">
                <span>{author}</span> • 
                <span>{datetime.utcnow().strftime("%d.%m.%Y")}</span> •
                <span>{language.upper()}</span>
            </p>
        </div>

        {sections_html}
    </main>

    <footer>
        <div class="container">
            <p>© {datetime.utcnow().year} SEO Monster. Автономная AI система для SEO продвижения.</p>
            <p style="margin-top: 0.5rem; font-size: 0.85rem;">Powered by MANUS.im</p>
        </div>
    </footer>
</body>
</html>'''
        
        return html
    
    def _get_minimal_light_template(self, **kwargs) -> str:
        """Generate minimal light theme landing page"""
        # Similar structure but with light colors
        return self._get_glassmorphism_dark_template(**kwargs)  # Placeholder
    
    def _get_tech_modern_template(self, **kwargs) -> str:
        """Generate tech modern theme landing page"""
        return self._get_glassmorphism_dark_template(**kwargs)  # Placeholder
    
    def _format_content(self, content: str) -> str:
        """Format markdown content to HTML"""
        if not content:
            return ""
        
        # Convert markdown to HTML
        html = content
        
        # Bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # Italic
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        
        # Links
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
        
        # Lists
        lines = html.split('\n')
        in_list = False
        result = []
        
        for line in lines:
            if line.strip().startswith('- ') or line.strip().startswith('* '):
                if not in_list:
                    result.append('<ul>')
                    in_list = True
                result.append(f'<li>{line.strip()[2:]}</li>')
            elif line.strip().startswith(('1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ')):
                if not in_list:
                    result.append('<ol>')
                    in_list = True
                result.append(f'<li>{line.strip()[3:]}</li>')
            else:
                if in_list:
                    result.append('</ul>' if result[-2].startswith('<li>') else '</ol>')
                    in_list = False
                if line.strip():
                    result.append(f'<p>{line}</p>')
        
        if in_list:
            result.append('</ul>')
        
        return '\n'.join(result)


# Singleton instance
landing_generator = LandingGenerator()
