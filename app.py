import os
import json
from PIL import Image
import streamlit as st
from datetime import datetime

# 外部ファイルからユーティリティと構成要素をインポート
from utils import (
    download_sample_images
)
from ui.utils.image_processing import (
    parse_json, plot_bounding_boxes
)
from models import (
    resize_image, get_genai_client, detect_objects, detect_objects_with_multiple_models
)
from config import PAGE_CONFIG, get_api_key
from data import ensure_images_directory, get_default_prompt

# UI関連のモジュールをインポート（個別のレイアウトファイルから直接インポート）
from ui.layouts.header import show_header
from ui.layouts.sidebar import show_sidebar
from ui.layouts.footer import show_footer
from ui.layouts.image_uploader import show_image_uploader
from ui.layouts.image_selector import show_simple_sample_selector

# マークダウンレポート生成関連のモジュールをインポート
from ui.utils.file_utils import (
    create_reports_directory, 
    get_image_as_base64, 
    save_image, 
    get_file_download_link
)
from ui.utils.markdown_generator import (
    generate_object_detection_report, 
    generate_comparison_report, 
    save_markdown_to_file
)
from ui.reports.detection_results import (
    show_detection_results, 
    generate_markdown_report, 
    save_markdown_report
)

# ページ設定
st.set_page_config(**PAGE_CONFIG)

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
    
    # レポート設定
    include_raw_json = st.sidebar.checkbox("生のJSONレスポンスをレポートに含める", value=True)
    include_images = st.sidebar.checkbox("画像をレポートに埋め込む", value=True)
    
    # キャンバスクリアボタン
    if st.sidebar.button("キャンバスをクリア"):
        st.session_state.last_result = None
        st.session_state.last_image = None
        st.session_state.last_image_path = None
        st.rerun()
    
    # サンプル画像ディレクトリの確認
    ensure_images_directory()
    
    # 画像の準備
    image = None
    image_path = None
    selected_prompt = ""
    
    if img_source == "サンプル画像":
        # サンプル画像選択
        image_path, image, selected_prompt = show_simple_sample_selector()
    else:  # 画像をアップロード
        image = show_image_uploader()
        if image:
            image_path = "アップロード画像"
    
    # 画像がロードされている場合の処理
    if image:
        # プロンプトの準備
        prompt = custom_prompt or selected_prompt
        if not prompt:
            prompt = get_default_prompt(str(image_path))
        
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
                    
                    # 画像埋め込みの設定を考慮
                    img_for_report = img_resized if include_images else None
                    
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
                        
                        # モデル比較レポートを生成（最初の2つのモデルのみ）
                        if len(selected_models) >= 2:
                            model1, model2 = selected_models[0], selected_models[1]
                            # 各モデルの結果を別々の辞書として抽出
                            results_model1 = {model1: results[model1]}
                            results_model2 = {model2: results[model2]}
                            
                            # 比較レポートを生成
                            comparison_report = generate_comparison_report(
                                results_model1, 
                                results_model2,
                                img_for_report,
                                img_path=image_path,
                                comparison_title=f"{model1} vs {model2} 比較レポート"
                            )
                            
                            # 比較レポート表示用のエクスパンダーを追加
                            with st.expander("モデル比較レポート", expanded=False):
                                st.markdown(comparison_report)
                                
                                # レポート保存ボタン
                                col1, col2 = st.columns([1, 3])
                                
                                # タイムスタンプ付きのファイル名
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"comparison_report_{model1}_vs_{model2}_{timestamp}.md"
                                
                                with col1:
                                    if st.button("比較レポートを保存"):
                                        saved_path = save_markdown_to_file(comparison_report, filename)
                                        if saved_path:
                                            st.success(f"比較レポートを保存しました: {saved_path}")
                                
                                with col2:
                                    # ダウンロードリンク
                                    st.markdown(
                                        get_file_download_link(comparison_report, filename),
                                        unsafe_allow_html=True
                                    )
                        
                        # 複数モデルの結果を表示
                        show_detection_results(results, img_resized, image_path)
                        
                        # 結果の保存（セッション状態）
                        st.session_state.last_result = results
                        st.session_state.last_image = img_resized
                        st.session_state.last_image_path = image_path
                    
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
                        results = {model: response}
                        show_detection_results(results, img_resized, image_path)
                        
                        # 結果の保存（セッション状態）
                        st.session_state.last_result = results
                        st.session_state.last_image = img_resized
                        st.session_state.last_image_path = image_path
    
    # フッター表示
    show_footer()

if __name__ == "__main__":
    main()
