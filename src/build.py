import os
import shutil
import glob
import markdown
import frontmatter
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

# --- 設定 ---
TEMPLATES_DIR = 'templates'
OUTPUT_DIR = 'dist'
STATIC_DIR = 'static'
CONTENT_DIR = 'content/posts'

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def load_posts():
    posts = []
    md_files = glob.glob(os.path.join(CONTENT_DIR, '*.md'))
    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            post_data = frontmatter.load(f)
            html_content = markdown.markdown(post_data.content, extensions=['fenced_code', 'tables'])
            
            print(f"--- チェック: {file_path} ---")
            print(f"タイトル: {post_data.metadata.get('title')}")
            print(f"本文の文字数: {len(post_data.content)}")

            posts.append({
                "content": html_content,
                **post_data.metadata,
                "slug": os.path.splitext(os.path.basename(file_path))[0]
            })
    return posts

def validate_and_filter_posts(posts):
    valid_posts = []
    # 重複チェックを外すため seen_slugs は使わない
    for post in posts:
        if post.get('draft'): continue
        if not post.get('title'): continue
        
        # 重複を許可するために continue ロジックを削除
        
        try:
            # 日付が文字列の場合は変換、日付オブジェクトならそのまま使う
            dt = post.get('date')
            if isinstance(dt, str):
                post['date_obj'] = datetime.strptime(dt, '%Y-%m-%d')
            else:
                post['date_obj'] = dt
        except Exception:
            # 日付がない場合は今日の日付を仮に入れる
            post['date_obj'] = datetime.now()
            
        if not isinstance(post.get('tags'), list):
            post['tags'] = []
            
        valid_posts.append(post)
    
    # 日付順に並べ替え
    return sorted(valid_posts, key=lambda x: str(x.get('date', '')), reverse=True)

def build():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    os.makedirs(os.path.join(OUTPUT_DIR, 'articles'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'tags'), exist_ok=True)

    if os.path.exists(STATIC_DIR):
        shutil.copytree(STATIC_DIR, os.path.join(OUTPUT_DIR, STATIC_DIR))
        print(f"✅ Static files copied to {os.path.join(OUTPUT_DIR, STATIC_DIR)}")

    raw_posts = load_posts() 
    posts = validate_and_filter_posts(raw_posts)

    try:
        article_tmpl = env.get_template('post.html')
    except:
        article_tmpl = env.get_template('article.html')

    for post in posts:
        output_path = os.path.join(OUTPUT_DIR, 'articles', f"{post['slug']}.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(article_tmpl.render(post=post))

    index_tmpl = env.get_template('index.html')
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_tmpl.render(posts=posts))

    print(f"🚀 Build Completed! Total {len(posts)} posts processed.")

if __name__ == '__main__':
    build()