import os
import shutil
import glob
import markdown
import frontmatter
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

# --- 設定 ---
TEMPLATES_DIR = 'templates'  # スペルミス修正済み
OUTPUT_DIR = 'dist'
STATIC_DIR = 'static'        # src/static を指す
CONTENT_DIR = 'content/posts'

# Jinja2の設定
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def load_posts():
    posts = []
    # 記事ファイルを探す
    md_files = glob.glob(os.path.join(CONTENT_DIR, '*.md'))
    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            post_data = frontmatter.load(f)
            html_content = markdown.markdown(post_data.content, extensions=['fenced_code', 'tables'])
            posts.append({
                "slug": os.path.splitext(os.path.basename(file_path))[0],
                "content": html_content,
                **post_data.metadata 
            })
    return posts

def validate_and_filter_posts(posts):
    valid_posts = []
    seen_slugs = set()
    for post in posts:
        if post.get('draft'): continue
        if not post.get('title'): continue
        slug = post.get('slug')
        if not slug or slug in seen_slugs: continue
        seen_slugs.add(slug)
        try:
            post['date_obj'] = datetime.strptime(str(post['date']), '%Y-%m-%d')
        except (ValueError, KeyError):
            continue
        if not isinstance(post.get('tags'), list):
            post['tags'] = []
        valid_posts.append(post)
    return sorted(valid_posts, key=lambda x: str(x['date']), reverse=True)

def build():
    # 1. distフォルダを真っさらにする
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    
    # 2. 必要なフォルダを作成
    os.makedirs(os.path.join(OUTPUT_DIR, 'articles'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'tags'), exist_ok=True)

    # 3. 静的ファイルをコピー (src/static -> dist/static)
    if os.path.exists(STATIC_DIR):
        shutil.copytree(STATIC_DIR, os.path.join(OUTPUT_DIR, STATIC_DIR))
        print(f"✅ Static files copied to {os.path.join(OUTPUT_DIR, STATIC_DIR)}")

    # 4. 記事データの処理
    raw_posts = load_posts() 
    posts = validate_and_filter_posts(raw_posts)

    # 5. 記事詳細ページ (articles/xxx.html) の生成
    # post.html または article.html、手元にあるファイル名に合わせてください
    try:
        article_tmpl = env.get_template('post.html')
    except:
        article_tmpl = env.get_template('article.html')

    for post in posts:
        output_path = os.path.join(OUTPUT_DIR, 'articles', f"{post['slug']}.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(article_tmpl.render(post=post))

    # 6. トップページ (index.html) の生成
    index_tmpl = env.get_template('index.html')
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_tmpl.render(posts=posts))

    print(f"🚀 Build Completed! Total {len(posts)} posts processed.")

if __name__ == '__main__':
    build()