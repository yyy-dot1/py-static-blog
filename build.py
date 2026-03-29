import os
from jinja2 import Environment, FileSystemLoader

# テンプレートの読み込み設定
env = Environment(loader=FileSystemLoader('templete'))
template = env.get_template('index.html')

# 仮データ（Aさんが作るプログラムの代わり）
dummy_posts = [
    {
        "title": "吉祥寺で見つけた隠れ家！「Cafe Sample」の絶品プリン",
        "date": "2026-03-29",
        "area": "📍吉祥寺",
        "summary": "裏路地にある静かなカフェ。Wi-Fiもあって作業が捗りました。",
        "tags": ["プリン", "Wi-Fiあり", "おひとりさま"]
    },
    {
        "title": "【代官山】テラス席が気持ちいい！朝活におすすめのベーカリー",
        "date": "2026-03-28",
        "area": "📍代官山",
        "summary": "焼きたてのクロワッサンとコーヒーの香りに包まれる至福の朝食。",
        "tags": ["朝活", "テラス席", "パン"]
    }
]

# HTMLを生成して保存
with open('debug_index.html', 'w', encoding='utf-8') as f:
    # index.htmlに渡す変数（postsなど）をここで指定
    f.write(template.render(posts=dummy_posts))

print("debug_index.html を作成しました。ブラウザで開いて確認してください！")
