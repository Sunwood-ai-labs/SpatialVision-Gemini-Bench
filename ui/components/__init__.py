"""
UIコンポーネントパッケージ
"""

import streamlit as st
from ui.components.image_selector import show_sample_image_selector
from ui.components.image_uploader import show_image_uploader

def show_header():
    """アプリケーションヘッダーを表示"""
    st.title("🔍 SpatialVision - Gemini による物体検出")
    st.caption("Google Gemini APIを使用したオブジェクト検出サンプル")

def show_footer():
    """アプリケーションフッターを表示"""
    st.markdown("---")
    st.caption("© 2023 SpatialVision - Gemini Bench プロジェクト")

def show_sidebar():
    """サイドバーを表示し設定値を返す"""
    with st.sidebar:
        st.title("⚙️ 設定")
        
        # APIキー入力
        api_key = st.text_input(
            "Google API Key", 
            value=st.session_state.get("api_key", ""), 
            type="password"
        )
        st.session_state["api_key"] = api_key
        
        # 画像ソース選択
        img_source = st.radio(
            "画像ソース",
            ["アップロード", "サンプル画像"],
            index=0
        )
        
        # 選択可能なモデル
        models = {
            "gemini-pro-vision": "Gemini Pro Vision",
            "gemini-1.5-pro-latest": "Gemini 1.5 Pro",
        }
        
        # モデル選択（複数選択可能）
        selected_models = st.multiselect(
            "使用モデルを選択",
            options=list(models.keys()),
            default=[list(models.keys())[0]],
            format_func=lambda x: models[x]
        )
        
        # モデルが選択されていない場合はデフォルトを設定
        if not selected_models:
            selected_models = [list(models.keys())[0]]
        
        # プロンプトカスタマイズ
        custom_prompt = st.text_area(
            "カスタムプロンプト", 
            value=st.session_state.get("custom_prompt", ""),
            help="空白の場合はデフォルトのプロンプトが使用されます"
        )
        st.session_state["custom_prompt"] = custom_prompt
        
        # 温度設定
        temperature = st.slider(
            "温度 (Temperature)", 
            min_value=0.0, 
            max_value=1.0, 
            value=st.session_state.get("temperature", 0.4),
            step=0.1,
            help="値が高いほど創造的な回答になります"
        )
        st.session_state["temperature"] = temperature
        
        # 高度な設定
        with st.expander("高度な設定", expanded=False):
            # 表示オプション
            st.checkbox(
                "オリジナル画像を表示", 
                value=st.session_state.get("show_original", True),
                key="show_original"
            )
            
            # レポートオプション
            st.checkbox(
                "レポートに画像を埋め込む", 
                value=st.session_state.get("include_images", True),
                key="include_images"
            )
            st.checkbox(
                "レポートに生JSONを含める", 
                value=st.session_state.get("include_raw_json", True),
                key="include_raw_json"
            )
    
    # 設定値を辞書形式で返す
    return {
        "api_key": api_key,
        "selected_models": selected_models,
        "custom_prompt": custom_prompt,
        "temperature": temperature,
        "img_source": img_source
    }

# 他のコンポーネントをエクスポート
__all__ = [
    'show_header', 
    'show_footer', 
    'show_sidebar',
    'show_sample_image_selector',
    'show_image_uploader'
]
