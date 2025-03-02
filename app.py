"""
空間認識オブジェクト検出アプリケーション
Gemini APIを使用して画像内のオブジェクトを検出し、バウンディングボックスで可視化する
"""

import streamlit as st
import os
from PIL import Image

# 分割したモジュールのインポート
from config import PAGE_CONFIG, get_api_key
from models import get_genai_client, resize_image, detect_objects, detect_objects_with_multiple_models
from data import ensure_images_directory, get_default_prompt, SAMPLE_PROMPTS
from ui import (
    show_header, show_sidebar, show_sample_image_selector, 
    show_image_uploader, show_detection_results, show_footer
)

# ページ設定
st.set_page_config(**PAGE_CONFIG)

# メイン処理
def main():
    """アプリケーションのメインロジック"""
    
    # ヘッダー表示
    show_header()
    
    # サイドバー表示と設定取得
    settings = show_sidebar()
    api_key = settings["api_key"] or get_api_key()
    selected_models = settings["selected_models"]
    custom_prompt = settings["custom_prompt"]
    temperature = settings["temperature"]
    img_source = settings["img_source"]
    
    # サンプル画像ディレクトリの確認
    ensure_images_directory()
    
    # 画像の準備
    image = None
    selected_prompt = ""
    
    if img_source == "サンプル画像":
        # サンプル画像選択
        image_path, image, selected_prompt = show_sample_image_selector()
    else:  # 画像をアップロード
        image = show_image_uploader()
    
    # 画像がロードされている場合の処理
    if image:
        # 画像を表示
        st.image(image, caption="元の画像", use_column_width=True)
        
        # プロンプトの準備
        prompt = custom_prompt or selected_prompt
        if not prompt:
            prompt = get_default_prompt(str(image))
        
        st.subheader("使用するプロンプト")
        st.write(prompt)
        
        # 実行ボタン
        if st.button("オブジェクト検出を実行"):
            if not api_key:
                st.error("API Keyを入力してください")
            else:
                with st.spinner("Gemini APIでオブジェクト検出を実行中..."):
                    # クライアント取得
                    client = get_genai_client(api_key)
                    
                    # 画像をリサイズ
                    img_resized = resize_image(image)
                    
                    # 選択されたモデルが複数の場合
                    if len(selected_models) > 1:
                        st.info(f"{len(selected_models)}個のモデルで順次処理を行います")
                        
                        # 複数モデルでのオブジェクト検出
                        results = detect_objects_with_multiple_models(
                            client,
                            selected_models, 
                            prompt,
                            img_resized,
                            temperature
                        )
                        
                        # 複数モデルの結果を表示
                        show_detection_results(results, img_resized)
                    
                    # 選択されたモデルが1つの場合
                    else:
                        model = selected_models[0]
                        response = detect_objects(
                            client, 
                            model, 
                            prompt, 
                            img_resized, 
                            temperature
                        )
                        
                        # 単一モデルの結果も辞書形式で渡す
                        show_detection_results({model: response}, img_resized)
    
    # フッター表示
    show_footer()

if __name__ == "__main__":
    main()
