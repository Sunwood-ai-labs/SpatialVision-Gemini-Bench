"""
データ関連のモジュール
サンプル画像情報、プロンプトテンプレートなどデータ関連の情報を管理
"""

import os
import sys
from utils import download_sample_images

# サンプル画像の準備
SAMPLE_IMAGE_OPTIONS = {
    # 食べ物カテゴリ
    "food/Vegetables.jpg": "野菜",
    "food/Japanese_bento.png": "お弁当",
    "food/Cupcakes.jpg": "カップケーキ",
    "food/Fruits.jpg": "フルーツ",
    "food/Breakfast.jpg": "朝食",
    
    # 自然カテゴリ
    "nature/Cat.jpg": "猫",
    "nature/Pumpkins.jpg": "カボチャ",
    
    # 都市・生活カテゴリ
    "urban/Bookshelf.jpg": "本棚",
    "urban/Origamis.jpg": "折り紙", 
    "urban/Socks.jpg": "靴下",
    "urban/Spill.jpg": "こぼれたコーヒー"
}

# サンプルプロンプトの準備
SAMPLE_PROMPTS = {
    "urban/Socks.jpg": [
        "すべての靴下を検出",
        "虹色の靴下を検出",
        "顔のある靴下の位置を検出",
        "上部にある靴下と対になる靴下を検出"
    ],
    "food/Vegetables.jpg": [
        "すべての野菜を検出し、名前をラベル付け",
        "緑色の野菜だけを検出",
        "調理法の説明をラベルとして野菜を検出",
        "アレルギーのある野菜を検出して注意喚起"
    ],
    "food/Japanese_bento.png": [
        "食べ物を検出し、日本語と英語で説明",
        "ヴィーガン料理を検出",
        "5語の説明付きで料理を検出",
        "アレルゲンがある料理を検出してラベル付け"
    ],
    "food/Cupcakes.jpg": [
        "カップケーキのトッピングの説明とともに検出",
        "チョコレートのカップケーキだけを検出",
        "カップケーキの材料を推測してラベル付け",
        "最も甘そうなカップケーキを検出"
    ],
    "urban/Origamis.jpg": [
        "2つの折り紙の動物を検出",
        "折り紙の影を検出",
        "キツネの影の周りに四角を描画",
        "折り紙の色と形状を説明"
    ],
    "food/Fruits.jpg": [
        "すべての果物を検出し種類別にラベル付け",
        "最も熟している果物を検出",
        "ビタミンCが豊富な果物を検出",
        "果物のカロリーを推定してラベル付け"
    ],
    "nature/Cat.jpg": [
        "猫の顔を検出",
        "猫の体の部位を検出してラベル付け",
        "猫の感情を推測してラベル付け",
        "猫の品種を推測してラベル付け"
    ],
    "nature/Pumpkins.jpg": [
        "すべてのカボチャを検出",
        "最も重そうなカボチャを検出",
        "ハロウィン向けのカボチャを検出",
        "カボチャの特徴を説明してラベル付け"
    ],
    "food/Breakfast.jpg": [
        "朝食の全アイテムを検出",
        "タンパク質が多い食品を検出",
        "最も健康的な食品を検出してラベル付け",
        "カロリーを推定して食品をラベル付け"
    ],
    "urban/Bookshelf.jpg": [
        "本棚のすべての本を検出",
        "推定ジャンル別に本をラベル付け",
        "タイトルを推測して本をラベル付け",
        "最も興味深そうな本を検出"
    ],
    "urban/Spill.jpg": [
        "こぼれたコーヒーの場所を検出",
        "掃除方法の説明をラベルとして表示",
        "問題の原因となっているものを検出",
        "掃除に必要なアイテムを提案してラベル付け"
    ]
}

# 画像カテゴリの定義
IMAGE_CATEGORIES = {
    "food": "食べ物・料理",
    "nature": "自然・動物",
    "urban": "都市・生活"
}

def ensure_images_directory():
    """
    サンプル画像ディレクトリの確認と作成
    存在しない場合は作成しサンプル画像をダウンロード
    
    Returns:
        str: 画像ディレクトリの絶対パス
    """
    # 画像ディレクトリのパス
    image_dir = os.path.join(os.getcwd(), "images")
    
    # 親ディレクトリの確認
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
        os.makedirs(os.path.join(image_dir, "food"))
        os.makedirs(os.path.join(image_dir, "nature"))
        os.makedirs(os.path.join(image_dir, "urban"))
        # サンプル画像のダウンロード
        for cmd in download_sample_images():
            os.system(cmd)
    
    # サブディレクトリの確認
    for category in ["food", "nature", "urban"]:
        category_dir = os.path.join(image_dir, category)
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)
    
    # ディレクトリが空の場合もダウンロード
    food_dir = os.path.join(image_dir, "food")
    nature_dir = os.path.join(image_dir, "nature")
    urban_dir = os.path.join(image_dir, "urban")
    
    if not os.listdir(food_dir) and not os.listdir(nature_dir) and not os.listdir(urban_dir):
        for cmd in download_sample_images():
            os.system(cmd)
    
    return image_dir

def get_default_prompt(image_path):
    """
    画像に対するデフォルトプロンプトを取得
    
    Args:
        image_path: 画像パス
        
    Returns:
        デフォルトプロンプト
    """
    # 画像ファイル名の取得
    image_filename = os.path.basename(image_path)
    
    if "Cupcakes" in image_filename:
        return "カップケーキのトッピングの説明とともに検出"
    elif "Cat" in image_filename:
        return "猫の品種と特徴を検出"
    elif "Bookshelf" in image_filename:
        return "本棚の本を検出して分類"
    else:
        return "画像内のすべてのオブジェクトを検出して分類"
