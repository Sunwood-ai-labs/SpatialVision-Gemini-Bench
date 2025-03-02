"""
サンプル画像選択コンポーネント
"""

import os
import streamlit as st
from PIL import Image
from data import SAMPLE_IMAGE_OPTIONS, SAMPLE_PROMPTS, IMAGE_CATEGORIES, ensure_images_directory

def show_simple_sample_selector():
    """
    簡易バージョンのサンプル画像選択UI
    
    Returns:
        tuple: (選択された画像のパス, 選択された画像オブジェクト, 選択されたプロンプト)
    """
    image_dir = ensure_images_directory()
    
    # サンプル画像リスト
    sample_images = {
        "室内写真": {
            "path": os.path.join(image_dir, "urban/Bookshelf.jpg"),
            "prompt": "室内の本棚を検出してください。"
        },
        "風景写真": {
            "path": os.path.join(image_dir, "nature/Pumpkins.jpg"),
            "prompt": "この風景写真内のすべての自然物を検出してください。"
        },
        "食べ物写真": {
            "path": os.path.join(image_dir, "food/Fruits.jpg"),
            "prompt": "この写真内のすべての果物を検出し、栄養価を評価してください。"
        }
    }
    
    # 画像が存在するかチェック
    available_images = []
    for name, info in sample_images.items():
        if os.path.exists(info["path"]):
            available_images.append(name)
    
    if not available_images:
        st.warning("サンプル画像が見つかりません。`images`ディレクトリにサンプル画像を追加してください。")
        return None, None, ""
    
    # 画像選択
    selected_image = st.selectbox("サンプル画像を選択", available_images)
    
    if selected_image:
        image_info = sample_images[selected_image]
        image_path = image_info["path"]
        try:
            image = Image.open(image_path)
            return image_path, image, image_info["prompt"]
        except Exception as e:
            st.error(f"画像のロードに失敗しました: {e}")
    
    return None, None, ""
