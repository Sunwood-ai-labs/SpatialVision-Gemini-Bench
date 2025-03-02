"""
サイドバーレイアウトコンポーネント
"""

import streamlit as st
from config import MODEL_OPTIONS, MODEL_DISPLAY_NAMES, DEFAULT_MODEL, DEFAULT_TEMPERATURE, get_api_key

def show_sidebar():
    """
    サイドバーの設定UIを表示
    
    Returns:
        dict: サイドバーの設定値
    """
    with st.sidebar:

        st.markdown(
            """
<div align="center">
  <img src="https://github.com/user-attachments/assets/6131c946-bb7e-421e-90d2-adcc876f39ae" width="100%" alt="Image">
</div>

            """,
            unsafe_allow_html=True
        )
    
        st.title("🔍 検出設定")
        
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
        
        # モデル選択（複数選択に変更）
        st.subheader("モデル選択")
        selected_models = []
        
        st.markdown("使用するモデルを選択してください（複数選択可）")
        
        for model in MODEL_OPTIONS:
            is_default = model == DEFAULT_MODEL
            selected = st.checkbox(
                MODEL_DISPLAY_NAMES.get(model, model),
                value=is_default,
                help=f"モデル: {model}"
            )
            if selected:
                selected_models.append(model)
        
        # 少なくとも1つのモデルが選択されているか確認
        if not selected_models:
            st.warning("少なくとも1つのモデルを選択してください")
            selected_models = [DEFAULT_MODEL]
        
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
        "selected_models": selected_models,
        "custom_prompt": custom_prompt,
        "temperature": temperature,
        "img_source": img_source
    }
