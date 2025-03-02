"""
データ関連のモジュール
サンプル画像情報、プロンプトテンプレートなどデータ関連の情報を管理
"""

import os
import sys
from utils import download_sample_images

# サンプル画像の準備
SAMPLE_IMAGE_OPTIONS = {
    "Socks.jpg": "靴下",
    "Vegetables.jpg": "野菜",
    "Japanese_bento.png": "お弁当",
    "Cupcakes.jpg": "カップケーキ",
    "Origamis.jpg": "折り紙",
    "Fruits.jpg": "フルーツ",
    "Cat.jpg": "猫",
    "Pumpkins.jpg": "カボチャ",
    "Breakfast.jpg": "朝食",
    "Bookshelf.jpg": "本棚",
    "Spill.jpg": "こぼれたコーヒー"
}

# サンプルプロンプトの準備
SAMPLE_PROMPTS = {
    "Socks.jpg": [
        "すべての靴下を検出",
        "虹色の靴下を検出",
        "顔のある靴下の位置を検出",
        "上部にある靴下と対になる靴下を検出"
    ],
    "Vegetables.jpg": [
        "すべての野菜を検出し、名前をラベル付け",
        "緑色の野菜だけを検出",
        "調理法の説明をラベルとして野菜を検出",
        "アレルギーのある野菜を検出して注意喚起"
    ],
    "Japanese_bento.png": [
        "食べ物を検出し、日本語と英語で説明",
        "ヴィーガン料理を検出",
        "5語の説明付きで料理を検出",
        "アレルゲンがある料理を検出してラベル付け"
    ],
    "Cupcakes.jpg": [
        "カップケーキのトッピングの説明とともに検出",
        "チョコレートのカップケーキだけを検出",
        "カップケーキの材料を推測してラベル付け",
        "最も甘そうなカップケーキを検出"
    ],
    "Origamis.jpg": [
        "2つの折り紙の動物を検出",
        "折り紙の影を検出",
        "キツネの影の周りに四角を描画",
        "折り紙の色と形状を説明"
    ],
    "Fruits.jpg": [
        "すべての果物を検出し種類別にラベル付け",
        "最も熟している果物を検出",
        "ビタミンCが豊富な果物を検出",
        "果物のカロリーを推定してラベル付け"
    ],
    "Cat.jpg": [
        "猫の顔を検出",
        "猫の体の部位を検出してラベル付け",
        "猫の感情を推測してラベル付け",
        "猫の品種を推測してラベル付け"
    ],
    "Pumpkins.jpg": [
        "すべてのカボチャを検出",
        "最も重そうなカボチャを検出",
        "ハロウィン向けのカボチャを検出",
        "カボチャの特徴を説明してラベル付け"
    ],
    "Breakfast.jpg": [
        "朝食の全アイテムを検出",
        "タンパク質が多い食品を検出",
        "最も健康的な食品を検出してラベル付け",
        "カロリーを推定して食品をラベル付け"
    ],
    "Bookshelf.jpg": [
        "本棚のすべての本を検出",
        "推定ジャンル別に本をラベル付け",
        "タイトルを推測して本をラベル付け",
        "最も興味深そうな本を検出"
    ],
    "Spill.jpg": [
        "こぼれたコーヒーの場所を検出",
        "掃除方法の説明をラベルとして表示",
        "問題の原因となっているものを検出",
        "掃除に必要なアイテムを提案してラベル付け"
    ]
}

def ensure_images_directory():
    """
    サンプル画像ディレクトリの確認と作成
    存在しない場合は作成しサンプル画像をダウンロード
    """
    if not os.path.exists("images"):
        os.makedirs("images")
        # サンプル画像のダウンロード
        for cmd in download_sample_images():
            os.system(cmd)
    
    # ディレクトリが空の場合もダウンロード
    if not os.listdir("images"):
        for cmd in download_sample_images():
            os.system(cmd)

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
    else:
        return "画像内のすべてのオブジェクトを検出して分類"
