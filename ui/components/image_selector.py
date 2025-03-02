"""
サンプル画像選択コンポーネント
"""

import os
import streamlit as st
from PIL import Image
from data import SAMPLE_IMAGE_OPTIONS, SAMPLE_PROMPTS, IMAGE_CATEGORIES, ensure_images_directory

def show_sample_image_selector():
    """
    サンプル画像の選択UIを表示
    
    Returns:
        tuple: (選択された画像のパス, 選択された画像オブジェクト, 選択されたプロンプト)
    """
    # 画像ディレクトリの確認
    ensure_images_directory()
    image_dir = os.path.join(os.getcwd(), "images")
    
    # カテゴリ選択
    selected_category = st.selectbox(
        "カテゴリを選択してください",
        list(IMAGE_CATEGORIES.keys()),
        format_func=lambda x: f"{IMAGE_CATEGORIES[x]}"
    )
    
    # カテゴリ内の画像をフィルタリング
    category_images = {k: v for k, v in SAMPLE_IMAGE_OPTIONS.items() if k.startswith(selected_category)}
    
    # 画像がない場合
    if not category_images:
        st.warning(f"{IMAGE_CATEGORIES[selected_category]}カテゴリの画像が見つかりません。")
        return None, None, ""
    
    # サンプル画像選択
    selected_sample = st.selectbox(
        "サンプル画像を選択してください",
        list(category_images.keys()),
        format_func=lambda x: f"{os.path.basename(x)} ({category_images[x]})"
    )
    
    # サンプル画像に対応するプロンプト選択
    selected_prompt = ""
    if selected_sample in SAMPLE_PROMPTS:
        prompt_options = SAMPLE_PROMPTS[selected_sample]
        selected_prompt_idx = st.selectbox(
            "サンプルプロンプトを選択するか、カスタムプロンプトを使用",
            range(len(prompt_options)),
            format_func=lambda i: prompt_options[i]
        )
        
        selected_prompt = prompt_options[selected_prompt_idx]
    
    # 画像の読み込み
    image_path = None
    image = None
    try:
        image_path = os.path.join(image_dir, selected_sample)
        if os.path.exists(image_path):
            image = Image.open(image_path)
            st.image(image, caption=f"選択画像: {os.path.basename(selected_sample)}", use_column_width=True)
        else:
            st.error(f"画像ファイルが見つかりません: {image_path}")
    except Exception as e:
        st.error(f"画像の読み込みエラー: {e}")
    
    return image_path, image, selected_prompt

# シンプルなサンプル画像選択機能（新しいapp.pyとの互換性用）
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
