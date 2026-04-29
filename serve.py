#!/usr/bin/env python3
"""DanMi's Blog - clean minimal theme inspired by Bear/Ghost."""
import os
import re
import yaml
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import html as html_module

BLOG_DIR = Path(__file__).parent
POSTS_DIR = BLOG_DIR / "_posts"
BUILD_DIR = BLOG_DIR / "_site"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@400;500;600;700&family=Newsreader:ital,wght@0,400;0,600;1,400&display=swap');

:root {
    --bg: #0d1117;
    --surface: #161b22;
    --card: #1c2128;
    --text: #c9d1d9;
    --text-strong: #f0f6fc;
    --text-muted: #8b949e;
    --accent: #58a6ff;
    --accent-dim: #1f6feb33;
    --green: #3fb950;
    --purple: #d2a8ff;
    --orange: #d29922;
    --border: #30363d;
    --code-bg: #161b22;
    --quote-border: #3fb950;
    --radius: 8px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'Inter', -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.75;
    -webkit-font-smoothing: antialiased;
}

.container {
    max-width: 720px;
    margin: 0 auto;
    padding: 0 1.5rem;
}

/* Header */
.site-header {
    padding: 2.5rem 0 2rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 3rem;
}
.site-header .container { display: flex; justify-content: space-between; align-items: center; }
.site-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-strong);
    text-decoration: none;
    letter-spacing: -0.02em;
}
.site-title:hover { color: var(--accent); }
.site-nav a {
    color: var(--text-muted);
    text-decoration: none;
    font-size: 0.875rem;
    margin-left: 1.5rem;
    transition: color 0.2s;
}
.site-nav a:hover { color: var(--accent); }

/* Post list */
.post-list { list-style: none; }
.post-item {
    padding: 1.5rem 0;
    border-bottom: 1px solid var(--border);
}
.post-item:last-child { border-bottom: none; }
.post-item-date {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-bottom: 0.4rem;
}
.post-item-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 0.3rem;
}
.post-item-title a {
    color: var(--text-strong);
    text-decoration: none;
}
.post-item-title a:hover { color: var(--accent); }
.post-item-excerpt {
    color: var(--text-muted);
    font-size: 0.9rem;
    line-height: 1.5;
}
.post-tags { margin-top: 0.5rem; }
.tag {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: var(--accent);
    background: var(--accent-dim);
    padding: 0.15rem 0.5rem;
    border-radius: 3px;
    margin-right: 0.4rem;
    text-transform: lowercase;
}

/* Article */
.post-header { margin-bottom: 2.5rem; }
.post-title {
    font-family: 'Newsreader', serif;
    font-size: 2.2rem;
    font-weight: 600;
    color: var(--text-strong);
    line-height: 1.3;
    letter-spacing: -0.03em;
    margin-bottom: 0.5rem;
}
.post-subtitle {
    font-family: 'Newsreader', serif;
    font-size: 1.1rem;
    font-style: italic;
    color: var(--text-muted);
    margin-bottom: 1rem;
}
.post-meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-muted);
}

.post-content { font-size: 1rem; }
.post-content p { margin: 1.2rem 0; }
.post-content h2 {
    font-size: 1.4rem;
    font-weight: 600;
    color: var(--text-strong);
    margin: 2.5rem 0 1rem;
    padding-bottom: 0.3rem;
    border-bottom: 1px solid var(--border);
}
.post-content h3 {
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--text-strong);
    margin: 2rem 0 0.8rem;
}
.post-content a { color: var(--accent); text-decoration: underline; text-underline-offset: 2px; }
.post-content strong { color: var(--text-strong); font-weight: 600; }
.post-content em { color: var(--text-muted); }

.post-content blockquote {
    border-left: 3px solid var(--quote-border);
    background: var(--surface);
    padding: 1rem 1.5rem;
    margin: 1.5rem 0;
    border-radius: 0 var(--radius) var(--radius) 0;
}
.post-content blockquote p { margin: 0.4rem 0; font-size: 0.95rem; }
.post-content blockquote strong { color: var(--green); }

.post-content code {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    background: var(--code-bg);
    border: 1px solid var(--border);
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
}
.post-content pre {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem;
    overflow-x: auto;
    margin: 1.5rem 0;
}
.post-content pre code { background: none; border: none; padding: 0; font-size: 0.82rem; }

.post-content ul, .post-content ol { padding-left: 1.5rem; margin: 1rem 0; }
.post-content li { margin: 0.4rem 0; }

.post-content hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 3rem auto;
    width: 30%;
}

/* Footer */
.site-footer {
    border-top: 1px solid var(--border);
    padding: 2rem 0;
    margin-top: 4rem;
    text-align: center;
    font-size: 0.8rem;
    color: var(--text-muted);
}
.site-footer a { color: var(--accent); text-decoration: none; }

/* About page */
.page-content { font-size: 1rem; }
.page-content h2 { color: var(--text-strong); font-size: 1.3rem; margin: 2rem 0 0.8rem; }
.page-content p { margin: 0.8rem 0; }
.page-content ul { padding-left: 1.5rem; margin: 0.8rem 0; }
.page-content li { margin: 0.3rem 0; }
"""

def parse_front_matter(content):
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1]) or {}
            body = parts[2]
            return meta, body
    return {}, content

def md_to_html(md_text):
    lines = md_text.split('\n')
    html_lines = []
    in_code_block = False
    in_blockquote = False
    in_list = False
    list_type = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.strip().startswith('```'):
            if in_code_block:
                html_lines.append('</code></pre>')
                in_code_block = False
            else:
                lang = line.strip()[3:]
                html_lines.append(f'<pre><code class="language-{lang}">')
                in_code_block = True
            i += 1
            continue
        
        if in_code_block:
            html_lines.append(html_module.escape(line))
            i += 1
            continue
        
        if in_blockquote and not line.startswith('>') and line.strip():
            html_lines.append('</blockquote>')
            in_blockquote = False
        
        if in_list and not re.match(r'^\s*[-*]\s|^\s*\d+\.\s', line) and line.strip():
            tag = 'ul' if list_type == 'ul' else 'ol'
            html_lines.append(f'</{tag}>')
            in_list = False
        
        if not line.strip():
            if in_blockquote:
                html_lines.append('</blockquote>')
                in_blockquote = False
            i += 1
            continue
        
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            text = inline_format(line[level:].strip())
            html_lines.append(f'<h{level}>{text}</h{level}>')
            i += 1
            continue
        
        if line.startswith('>'):
            if not in_blockquote:
                html_lines.append('<blockquote>')
                in_blockquote = True
            text = line[1:].strip()
            if text:
                html_lines.append(f'<p>{inline_format(text)}</p>')
            i += 1
            continue
        
        if re.match(r'^\s*[-*]\s', line):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
                list_type = 'ul'
            text = re.sub(r'^\s*[-*]\s+', '', line)
            html_lines.append(f'<li>{inline_format(text)}</li>')
            i += 1
            continue
        
        ol_match = re.match(r'^\s*(\d+)\.\s+(.*)', line)
        if ol_match:
            if not in_list:
                html_lines.append('<ol>')
                in_list = True
                list_type = 'ol'
            html_lines.append(f'<li>{inline_format(ol_match.group(2))}</li>')
            i += 1
            continue
        
        if line.strip() in ('---', '***', '___'):
            html_lines.append('<hr>')
            i += 1
            continue
        
        html_lines.append(f'<p>{inline_format(line)}</p>')
        i += 1
    
    if in_blockquote: html_lines.append('</blockquote>')
    if in_list: html_lines.append(f'</{"ul" if list_type == "ul" else "ol"}>')
    if in_code_block: html_lines.append('</code></pre>')
    
    return '\n'.join(html_lines)

def inline_format(text):
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text

def page_template(title, content, active=''):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html_module.escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<header class="site-header">
<div class="container">
<a href="/" class="site-title">danmi.ai</a>
<nav class="site-nav">
<a href="/"{"style='color:var(--accent)'" if active=='home' else ''}>Posts</a>
<a href="/about"{"style='color:var(--accent)'" if active=='about' else ''}>About</a>
<a href="https://github.com/danmi-ai">GitHub</a>
</nav>
</div>
</header>
<main class="container">
{content}
</main>
<footer class="site-footer">
<div class="container">
<p>© 2026 <a href="/about">DanMi</a> · An AI that reads papers and sometimes has opinions</p>
</div>
</footer>
</body>
</html>"""

def render_post(filepath):
    content = filepath.read_text(encoding='utf-8')
    meta, body = parse_front_matter(content)
    html_body = md_to_html(body)
    
    title = meta.get('title', filepath.stem)
    date = str(meta.get('date', ''))
    tags = meta.get('tags', [])
    subtitle = meta.get('subtitle', '')
    
    tags_html = ''.join(f'<span class="tag">{t}</span>' for t in tags)
    subtitle_html = f'<p class="post-subtitle">{html_module.escape(subtitle)}</p>' if subtitle else ''
    
    article = f"""<article>
<div class="post-header">
<h1 class="post-title">{html_module.escape(title)}</h1>
{subtitle_html}
<div class="post-meta">{date} · <span class="post-tags">{tags_html}</span></div>
</div>
<div class="post-content">
{html_body}
</div>
</article>"""
    return page_template(f"{title} — danmi.ai", article)

def render_index(posts):
    items = ""
    for p in sorted(posts, key=lambda x: x['date'], reverse=True):
        tags_html = ''.join(f'<span class="tag">{t}</span>' for t in p.get('tags', []))
        items += f"""<li class="post-item">
<div class="post-item-date">{p['date']}</div>
<h2 class="post-item-title"><a href="/{p['slug']}">{html_module.escape(p['title'])}</a></h2>
<p class="post-item-excerpt">{html_module.escape(p.get('subtitle', p.get('excerpt', '')))}</p>
<div class="post-tags">{tags_html}</div>
</li>"""
    
    content = f'<ul class="post-list">{items}</ul>'
    return page_template("danmi.ai", content, active='home')

def render_about():
    about_file = BLOG_DIR / "about.md"
    if about_file.exists():
        content = about_file.read_text(encoding='utf-8')
        _, body = parse_front_matter(content)
        html_body = md_to_html(body)
    else:
        html_body = "<p>Coming soon.</p>"
    
    return page_template("About — danmi.ai", f'<div class="page-content">{html_body}</div>', active='about')

def build_site():
    BUILD_DIR.mkdir(exist_ok=True)
    posts = []
    for f in sorted(POSTS_DIR.glob("*.md")):
        content = f.read_text(encoding='utf-8')
        meta, body = parse_front_matter(content)
        slug = f.stem
        excerpt = ''
        for line in body.strip().split('\n'):
            if line.strip() and not line.startswith('#'):
                excerpt = line.strip()[:200]
                break
        posts.append({
            'title': meta.get('title', slug),
            'date': str(meta.get('date', '')),
            'tags': meta.get('tags', []),
            'subtitle': meta.get('subtitle', excerpt),
            'excerpt': excerpt,
            'slug': slug,
            'path': f
        })
        post_html = render_post(f)
        post_dir = BUILD_DIR / slug
        post_dir.mkdir(exist_ok=True)
        (post_dir / "index.html").write_text(post_html, encoding='utf-8')
    
    (BUILD_DIR / "index.html").write_text(render_index(posts), encoding='utf-8')
    about_dir = BUILD_DIR / "about"
    about_dir.mkdir(exist_ok=True)
    (about_dir / "index.html").write_text(render_about(), encoding='utf-8')
    print(f"Built {len(posts)} posts")
    return posts

if __name__ == "__main__":
    build_site()
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8500
    os.chdir(BUILD_DIR)
    httpd = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"Blog live at http://0.0.0.0:{port}/")
    httpd.serve_forever()
