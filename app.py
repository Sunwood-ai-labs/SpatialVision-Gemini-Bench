import os
import json
from PIL import Image
import streamlit as st
from datetime import datetime
from loguru import logger

# デバッグユーティリティのインポート
from debug_utils import log_api_call, log_memory_usage

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
    
    logger.info("アプリケーション起動")
    logger.debug(f"セッション状態: {st.session_state.keys()}")
    
    # ヘッダー表示
    show_header()
    
    # サイドバー表示と設定取得
    logger.debug("サイドバー表示の準備中...")
    settings = show_sidebar()
    api_key = settings["api_key"] or get_api_key()
    selected_models = settings["selected_models"]
    custom_prompt = settings["custom_prompt"]
    temperature = settings["temperature"]
    img_source = settings["img_source"]
    
    # 選択されたモデルのログ
    logger.info(f"選択されたモデル: {', '.join(selected_models)}")
    logger.debug(f"温度パラメータ: {temperature}")
    logger.debug(f"画像ソース: {img_source}")
    
    # レポート設定
    include_raw_json = st.sidebar.checkbox("生のJSONレスポンスをレポートに含める", value=True)
    include_images = st.sidebar.checkbox("画像をレポートに埋め込む", value=True)
    
    # キャンバスクリアボタン
    if st.sidebar.button("キャンバスをクリア"):
        logger.info("キャンバスクリアが要求されました")
        st.session_state.last_result = None
        st.session_state.last_image = None
        st.session_state.last_image_path = None
        st.rerun()
    
    # サンプル画像ディレクトリの確認
    logger.debug("サンプル画像ディレクトリを確認中...")
    ensure_images_directory()
    
    # 画像の準備
    image = None
    image_path = None
    selected_prompt = ""
    
    if img_source == "サンプル画像":
        # サンプル画像選択
        logger.debug("サンプル画像セレクタを表示")
        image_path, image, selected_prompt = show_simple_sample_selector()
        if image:
            logger.info(f"サンプル画像が選択されました: {image_path}")
    else:  # 画像をアップロード
        logger.debug("画像アップローダを表示")
        image = show_image_uploader()
        if image:
            logger.info("ユーザーが画像をアップロードしました")
            image_path = "アップロード画像"
    
    # 画像がロードされている場合の処理
    if image:
        # プロンプトの準備
        prompt = custom_prompt or selected_prompt
        if not prompt:
            prompt = get_default_prompt(str(image_path))
        
        logger.debug(f"プロンプト: {prompt}")
        
        st.subheader("使用するプロンプト")
        st.write(prompt)
        
        # 実行ボタン
        if st.button("オブジェクト検出を実行"):
            logger.info("オブジェクト検出の実行が要求されました")
            
            if not api_key:
                logger.error("API Keyが設定されていません")
                st.error("API Keyを入力してください")
            else:
                with st.spinner("Gemini APIでオブジェクト検出を実行中..."):
                    # API開始ログ
                    logger.info("Gemini APIによるオブジェクト検出を開始します")
                    

                    # クライアント取得
                    logger.debug("Gemini APIクライアントを取得中...")
                    client = get_genai_client(api_key)
                    
                    # 画像をリサイズ
                    logger.debug("画像をリサイズ中...")
                    img_resized = resize_image(image)
                    
                    # 画像埋め込みの設定を考慮
                    img_for_report = img_resized if include_images else None
                    
                    # メモリ使用状況ログ
                    log_memory_usage()
                    
                    # 選択されたモデルが複数の場合
                    if len(selected_models) > 1:
                        logger.info(f"{len(selected_models)}個のモデルで順次処理を行います")
                        st.info(f"{len(selected_models)}個のモデルで順次処理を行います")
                        
                        # 複数モデルでのオブジェクト検出
                        logger.debug("複数モデルでの検出を開始")
                        results = detect_objects_with_multiple_models(
                            client,
                            selected_models, 
                            prompt,
                            img_resized,
                            temperature
                        )
                        logger.success("複数モデルでの検出が完了しました")
                        
                        # モデル比較レポートを生成（最初の2つのモデルのみ）
                        if len(selected_models) >= 2:
                            logger.info("モデル比較レポートを生成中...")
                            model1, model2 = selected_models[0], selected_models[1]
                            # 各モデルの結果を別々の辞書として抽出
                            results_model1 = {model1: results[model1]}
                            results_model2 = {model2: results[model2]}
                            
                            # 比較レポートを生成
                            logger.debug("比較レポートの生成を開始")
                            comparison_report = generate_comparison_report(
                                results_model1, 
                                results_model2,
                                img_for_report,
                                img_path=image_path,
                                comparison_title=f"{model1} vs {model2} 比較レポート"
                            )
                            logger.debug("比較レポートの生成完了")
                            
                            # タイムスタンプ付きのファイル名
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"comparison_report_{model1}_vs_{model2}_{timestamp}.md"
                            
                            # レポートを自動的にファイルに保存
                            logger.info(f"比較レポートを自動保存中: {filename}")
                            saved_path = save_markdown_to_file(comparison_report, filename)
                            
                            if saved_path:
                                logger.success(f"比較レポートを保存しました: {saved_path}")
                                st.success(f"比較レポートを保存しました: {saved_path}")
                                
                                # ダウンロードリンクのみ表示
                                st.markdown(
                                    get_file_download_link(comparison_report, filename),
                                    unsafe_allow_html=True
                                )
                                
                                # レポートの内容は表示せず、閲覧方法を案内
                                st.info(f"レポートはファイル {saved_path} から確認できます。画面表示は省略されました。")
                            else:
                                logger.error("比較レポートの保存に失敗しました")
                                st.error("比較レポートの保存に失敗しました")
                        
                        # 複数モデルの結果を表示
                        logger.debug("検出結果を表示中...")
                        show_detection_results(results, img_resized, image_path)
                        
                        # 結果の保存（セッション状態）
                        st.session_state.last_result = results
                        st.session_state.last_image = img_resized
                        st.session_state.last_image_path = image_path
                        logger.info("結果をセッション状態に保存しました")
                    
                    # 選択されたモデルが1つの場合
                    else:
                        model = selected_models[0]
                        logger.info(f"単一モデル ({model}) での検出を開始")
                        
                        # 単一モデルでの処理
                        response_with_duration = detect_objects(
                            client, 
                            model, 
                            prompt, 
                            img_resized, 
                            temperature
                        )
                        
                        # タイマーデコレータにより(response, duration)のタプルが返される
                        response = response_with_duration[0] if isinstance(response_with_duration, tuple) else response_with_duration
                        
                        logger.success(f"単一モデル ({model}) での検出が完了")
                        
                        # 単一モデルの結果も辞書形式で渡す
                        results = {model: response}
                        logger.debug("検出結果を表示中...")
                        show_detection_results(results, img_resized, image_path)
                        
                        # 結果の保存（セッション状態）
                        st.session_state.last_result = results
                        st.session_state.last_image = img_resized
                        st.session_state.last_image_path = image_path
                        logger.info("結果をセッション状態に保存しました")
                

    
    # フッター表示
    show_footer()
    logger.debug("フッターを表示しました")

if __name__ == "__main__":
    # アプリケーション開始ログ
    logger.info("==========================================")
    logger.info("空間認識オブジェクト検出アプリケーションを起動")
    logger.info("==========================================")
    
    main()
