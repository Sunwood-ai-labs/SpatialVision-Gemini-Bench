"""
UIコンポーネント関連のモジュール
StreamlitのウィジェットやレイアウトなどのUI関連処理を管理
"""

import streamlit as st
import json
from PIL import Image
import os

from config import MODEL_OPTIONS, DEFAULT_MODEL, DEFAULT_TEMPERATURE, get_api_key
from data import SAMPLE_IMAGE_OPTIONS, SAMPLE_PROMPTS, get_default_prompt, IMAGE_CATEGORIES
from utils import parse_json, plot_bounding_boxes

def show_header():
    """
    アプリケーションのヘッダーを表示
    """
    st.markdown(
        """
        <div style="text-align:center">
            <img src="assets/header.svg" alt="Spatial Vision Gemini" width="700">
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.title("オブジェクト検出と空間理解")

def show_sidebar():
    """
    サイドバーの設定UIを表示
    
    Returns:
        dict: サイドバーの設定値
    """
    with st.sidebar:
        st.title("🔍 オブジェクト検出設定")
        
        # 環境変数からAPIキーを取得
        env_api_key = get_api_key()
        placeholder = "（環境変数から読み込み済み）" if env_api_key else "APIキーを入力してください"
        
        # API Keyの入力
        api_key = st.text_input(
            "Google API Key", 
            value=env_api_key if env_api_key else "",
            placeholder=placeholder,
            type="password", 
            help="Google AI StudioからAPI Keyを取得できます。.envファイルに設定することも可能です。"
        )
        
        st.markdown("---")
        
        # モデル選択
        st.subheader("モデル選択")
        model_option = st.selectbox(
            "使用するモデルを選択",
            MODEL_OPTIONS,
            index=MODEL_OPTIONS.index(DEFAULT_MODEL) if DEFAULT_MODEL in MODEL_OPTIONS else 0,
            help="Geminiモデルを選択します。パフォーマンスはgemini-2.0-flashが最も高いです。"
        )
        
        st.markdown("---")
        
        # ユーザー定義プロンプト
        st.subheader("検出設定")
        custom_prompt = st.text_area(
            "プロンプトをカスタマイズ (空白の場合はデフォルト)",
            help="例: 「赤いりんごだけを検出」「犬の顔を検出」など"
        )
        
        # 温度パラメータ
        temperature = st.slider(
            "温度 (多様性)", 
            min_value=0.0, 
            max_value=1.0, 
            value=DEFAULT_TEMPERATURE, 
            step=0.1,
            help="値が高いほど多様な結果になります。低いと一貫性が高まります。"
        )
        
        st.markdown("---")
        
        # サンプル画像か自分の画像かを選択
        img_source = st.radio("画像の選択方法", ["サンプル画像", "画像をアップロード"])
    
    return {
        "api_key": api_key,
        "model_option": model_option,
        "custom_prompt": custom_prompt,
        "temperature": temperature,
        "img_source": img_source
    }

def show_sample_image_selector():
    """
    サンプル画像の選択UIを表示
    
    Returns:
        tuple: (選択された画像のパス, 選択されたプロンプト)
    """
    # カテゴリ選択
    selected_category = st.selectbox(
        "カテゴリを選択してください",
        list(IMAGE_CATEGORIES.keys()),
        format_func=lambda x: f"{IMAGE_CATEGORIES[x]}"
    )
    
    # カテゴリ内の画像をフィルタリング
    category_images = {k: v for k, v in SAMPLE_IMAGE_OPTIONS.items() if k.startswith(selected_category)}
    
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
        image_path = os.path.join("images", selected_sample)
        if os.path.exists(image_path):
            image = Image.open(image_path)
        else:
            st.error(f"画像ファイルが見つかりません: {image_path}")
    except Exception as e:
        st.error(f"画像の読み込みエラー: {e}")
    
    return image_path, image, selected_prompt

def show_image_uploader():
    """
    画像アップロードUIを表示
    
    Returns:
        PIL.Image: アップロードされた画像
    """
    uploaded_file = st.file_uploader("画像をアップロードしてください", type=["jpg", "jpeg", "png"])
    image = None
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
    
    return image

def show_detection_results(response, img_resized):
    """
    検出結果を表示
    
    Args:
        response: Gemini APIからのレスポンス
        img_resized: 検出に使用した画像
    """
    if response.text:
        st.subheader("APIレスポンス")
        st.code(response.text, language="json")
        
        # バウンディングボックスの描画
        try:
            result_image = plot_bounding_boxes(img_resized, response.text)
            st.subheader("検出結果")
            st.image(result_image, caption="検出結果", use_column_width=True)
            
            # 検出されたオブジェクトの数を表示
            try:
                json_text = parse_json(response.text)
                bounding_boxes = json.loads(json_text)
                st.success(f"{len(bounding_boxes)}個のオブジェクトが検出されました")
                
                # 検出されたラベル一覧
                labels = [box.get("label", "不明") for box in bounding_boxes]
                st.subheader("検出されたオブジェクト")
                for i, label in enumerate(labels, 1):
                    st.write(f"{i}. {label}")
            except Exception as e:
                st.warning(f"検出オブジェクトのカウントに失敗しました: {e}")
        except Exception as e:
            st.error(f"バウンディングボックスの描画に失敗しました: {e}")
    else:
        st.error("APIからの応答がありませんでした")

def show_footer():
    """
    フッター情報を表示
    """
    st.markdown("---")
    st.markdown("""
    ### 使い方
    1. サイドバーでGemini API Keyを入力
    2. 使用するモデルを選択
    3. サンプル画像のカテゴリと画像を選択
    4. プロンプトをカスタマイズ（任意）
    5. 「オブジェクト検出を実行」ボタンをクリック

    ### 注意
    - このアプリはGemini APIを使用しています。有効なAPIキーが必要です。
    - 画像サイズが大きい場合は自動的にリサイズされます。
    - 検出結果はモデルによって異なる場合があります。
    """)
